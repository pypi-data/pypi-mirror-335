#!/usr/bin/env python
# coding: utf-8

# Installing and Loading Libraries
pip install -r requirements.txt

import pandas as pd
import numpy as np
import re
from datetime import datetime
import unidecode
from tqdm import tqdm
from joblib import Parallel, delayed
from scipy.sparse import csr_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report
import torch
import torch.multiprocessing as mp
from torch.utils.data import DataLoader, TensorDataset
import concurrent.futures
import jellyfish
from concurrent.futures import ThreadPoolExecutor
import sagemaker
import boto3
from sagemaker import get_execution_role
import os

# Importing data from S3 bucket
sess = sagemaker.Session()
role = get_execution_role()
bucket = 'mdp-scope-gold-sandbox-bucket'
prefix = 'DOM/scope_person/'
filename = 'part-00000-7f463879-ff47-4553-b867-ac90054f3be6-c000.snappy.parquet'
s3_object_key = f"{prefix}{filename}"
s3 = boto3.client("s3")
s3.download_file(bucket, s3_object_key, filename)
df=pd.read_parquet('part-00000-7f463879-ff47-4553-b867-ac90054f3be6-c000.snappy.parquet')

# Helping Functions
ARABIC_REPLACEMENTS = {
    'ا': 'a', 'أ': 'a', 'آ': 'a', 'إ': '2i', 'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': '7', 'خ': 'kh',
    'د': 'd', 'ذ': 'dh', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z',
    'ع': '3', 'غ': 'gh', 'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'a', 'ة': 'a',
    'و': 'ow', 'ؤ': '2o', 'ي': 'y', 'ئ': '2e', 'ء': '2', 'ى': 'a'
}

replacement_pattern = re.compile('|'.join([re.escape(key) for key in ARABIC_REPLACEMENTS.keys()]))

# Function to replace Arabic characters with their mapped replacements
def replace_arabic(match):
    return ARABIC_REPLACEMENTS[match.group(0)]

def clean_text(text):
    """Clean text for similarity comparison."""
    if pd.isna(text):
        return ""
    
    # Convert the input text to string (if it's not already)
    text = str(text)
    
    # Apply Arabic character replacements in one pass using a compiled regex
    text = replacement_pattern.sub(replace_arabic, text)
    
    text = unidecode.unidecode(text)

    # Remove non-alphanumeric characters and normalize whitespace in one pass
    text = re.sub(r'[^a-zA-Z0-9\s]+|\s+', ' ', text).lower().strip()
    
    return text


def calculate_age(dob_series):
    """Calculates age based on date of birth."""
    today = pd.to_datetime(datetime.today())
    dob_series = pd.to_datetime(dob_series, errors='coerce')
    age = (today - dob_series).dt.days // 365
    return age.where(dob_series.notna(), None)

def phonetic_encoding(names):
    """
    Compute phonetic encodings for names using the NYSIIS algorithm.
    
    Parameters:
    names (str or pandas.Series): A single name (string) or a pandas Series of names.
    
    Returns:
    str or pandas.Series: The NYSIIS phonetic encoding(s).
    """
    def encode(name):
        # Handle empty or missing values gracefully
        if pd.isna(name) or name == "":
            return ""
        # Compute the NYSIIS encoding
        return jellyfish.nysiis(name)

    if isinstance(names, pd.Series):  # If the input is a pandas Series
        # Apply the encoding to the entire series
        return names.apply(encode)
    else:  # If it's a single string
        return encode(names)

def is_valid_name_vectorized(names):
    """Optimized vectorized function to check if names are valid."""
    # Precondition checks
    names = names.astype(str).str.strip()
    
    # Check for the presence of 'person' in the name
    valid_names = ~names.str.contains('person', case=False, na=False)
    
    # Check if the name length is at least 3
    valid_names &= names.str.len() >= 3
    
    # Check if the name contains only alphabets and spaces
    valid_names &= names.str.match(r'^[a-zA-Z\s327]*$', na=False)
    
    return valid_names

def to_tensor(series, dtype=torch.float32, device='cuda'):
    """Converts a pandas Series to a PyTorch tensor."""
    return torch.tensor(series.values, dtype=dtype, device=device)

# Deduplication Helping Functions
def process_batch_on_gpu(start, end, batch_size, threshold, df, df_tensors, device='cuda'):
    """Processes a batch of records on GPU."""
    person_ids = df['PERSON_ID'].values
    full_names = df['full_name'].values
    location_names = df['LOCATION_NAME'].values
    batch_size = end - start

    # Move batch tensors to GPU
    batch_age = df_tensors['age'][start:end].to(device)
    batch_gender = df_tensors['gender'][start:end].to(device)
    batch_country = df_tensors['country'][start:end].to(device)
    batch_phonetic_first_name = df_tensors['phonetic_first_name'][start:end].to(device)
    batch_phonetic_last_name = df_tensors['phonetic_last_name'][start:end].to(device)
    batch_phonetic_full_name = df_tensors['phonetic_full_name'][start:end].to(device)  
    batch_phonetic_location_name = df_tensors['phonetic_location_name'][start:end].to(device)

    # Move full tensors to GPU
    full_age = df_tensors['age'].to(device)
    full_gender = df_tensors['gender'].to(device)
    full_country = df_tensors['country'].to(device)
    full_phonetic_first_name = df_tensors['phonetic_first_name'].to(device)
    full_phonetic_last_name = df_tensors['phonetic_last_name'].to(device)
    full_phonetic_full_name = df_tensors['phonetic_full_name'].to(device)
    full_phonetic_location_name = df_tensors['phonetic_location_name'].to(device)

    # Compute gender and age similarity
    gender_similarity = batch_gender.unsqueeze(1) == full_gender
    age_similarity = (torch.abs(batch_age.unsqueeze(1) - full_age) <= 2) | (torch.abs(batch_age.unsqueeze(1) - full_age) >= 900)

    # Phonetic and Country matching matrices
    phonetic_first_name_matches = (batch_phonetic_first_name.unsqueeze(1) == full_phonetic_first_name)
    phonetic_last_name_matches = (batch_phonetic_last_name.unsqueeze(1) == full_phonetic_last_name)
    phonetic_full_name_matches = (batch_phonetic_full_name.unsqueeze(1) == full_phonetic_full_name)
    phonetic_location_name_matches = (batch_phonetic_location_name.unsqueeze(1) == full_phonetic_location_name)
    country_matches = (batch_country.unsqueeze(1) == full_country)

    # Combine masks
    compatible_rows_mask = gender_similarity & age_similarity
    phonetic_first_name_matches &= compatible_rows_mask
    phonetic_last_name_matches &= compatible_rows_mask
    phonetic_full_name_matches &= compatible_rows_mask
    phonetic_location_name_matches &= compatible_rows_mask
    country_matches &= compatible_rows_mask

    # Collect duplicates
    batch_duplicates = []
    for i in range(batch_size):
        # Compare current row (i) against all previous rows (from start to i-1)
        potential_matches = torch.where(
             phonetic_first_name_matches[i, :start + i] & phonetic_last_name_matches[i, :start + i]
        )[0]

        if len(potential_matches) == 0:
            continue

        # Only calculate similarity scores for rows where both phonetic names match
        combined_score_matrix = torch.zeros_like(phonetic_full_name_matches[i, :start + i], dtype=torch.float32)
        valid_indices = potential_matches

        combined_score_matrix[valid_indices] = (
            phonetic_first_name_matches[i, valid_indices] * 0.05 +
            phonetic_last_name_matches[i, valid_indices] * 0.05 +
            phonetic_full_name_matches[i, valid_indices] * 0.70 + 
            #age_similarity[i, valid_indices] * 0.10 + \
            phonetic_location_name_matches[i, valid_indices] * 0.10 + \
            country_matches[i, valid_indices] * 0.10)

        duplicate_indices = torch.where(combined_score_matrix > threshold)[0]

        for idx in duplicate_indices:
                i_idx = int(i)  # Ensure i is an integer for indexing
                j_idx = int(idx)  # Ensure j is an integer for indexing
                if person_ids[start + i_idx] == person_ids[j_idx]:
                    continue
                    
                similarity_score = combined_score_matrix[j_idx].item()

                # Flags for Household and Biometrics ID comparison
                household_id_flag = (
                    "Identical" if df['PERSON_HOUSEHOLD_ID'].iloc[start + i_idx] == df['PERSON_HOUSEHOLD_ID'].iloc[j_idx]
                    else "Not available" if pd.isna(df['PERSON_HOUSEHOLD_ID'].iloc[start + i_idx]) or pd.isna(df['PERSON_HOUSEHOLD_ID'].iloc[j_idx])
                    else "Different"
                )
                biometrics_id_flag = (
                    "Identical" if df['PERSON_BIOMETRICS_INDIVIDUAL_ID'].iloc[start + i_idx] == df['PERSON_BIOMETRICS_INDIVIDUAL_ID'].iloc[j_idx]
                    else "Not available" if pd.isna(df['PERSON_BIOMETRICS_INDIVIDUAL_ID'].iloc[start + i_idx]) or pd.isna(df['PERSON_BIOMETRICS_INDIVIDUAL_ID'].iloc[j_idx])
                    else "Different"
                )
                registration_date_flag = (
                    "Identical" if df['PERSON_REGISTRATION_DATE'].iloc[start + i_idx] == df['PERSON_REGISTRATION_DATE'].iloc[j_idx]
                    else "Not available" if pd.isna(df['PERSON_REGISTRATION_DATE'].iloc[start + i_idx]) or pd.isna(df['PERSON_REGISTRATION_DATE'].iloc[j_idx])
                    else "Different"
                )

                # Flags for Document Number comparison
                document_number_flag = (
                    "Identical" if df['DOCUMENT_NUM'].iloc[start + i_idx] == df['DOCUMENT_NUM'].iloc[j_idx]
                    else "Not available" if pd.isna(df['DOCUMENT_NUM'].iloc[start + i_idx]) or pd.isna(df['DOCUMENT_NUM'].iloc[j_idx])
                    else "Different"
                )

                batch_duplicates.append({
                    'PERSON_ID_1': person_ids[start + i_idx],
                    'PERSON_ID_2': person_ids[j_idx],
                    'Full_Name_1': full_names[start + i_idx],
                    'Full_Name_2': full_names[j_idx],
                    'Age_1': batch_age[i_idx].item(),
                    'Age_2': full_age[j_idx].item(),
                    'Location_Name_1': location_names[start + i_idx],
                    'Location_Name_2': location_names[j_idx],
                    'Similarity_Score': similarity_score,
                    'Biometrics_ID_Flag': biometrics_id_flag,  # Include Biometrics_ID_Flag
                    'Household_ID_Flag': household_id_flag,  # Include Household_ID_Flag
                    'Registration_Date_Flag': registration_date_flag,  # Include Registration Date Flag
                    'Document_Number_Flag': document_number_flag  # Include Document Number Flag
                })

    return batch_duplicates

def preprocess_dataframe(df, column_mapping):
    """Preprocesses the DataFrame by renaming, cleaning, and preparing data."""
    # Rename columns
    
    # Rename the DataFrame columns to match the required names
    df = df.rename(columns=column_mapping)

    # Select the relevant columns after renaming
    required_columns = [
        'PERSON_FIRST_NAME', 'PERSON_MIDDLE_NAME', 'PERSON_LAST_NAME', 
        'LOCATION_NAME', 'PERSON_DATE_OF_BIRTH', 'PERSON_GENDER', 
        'COUNTRY_ISO_CODE', 'PERSON_HOUSEHOLD_ID', 'PERSON_BIOMETRICS_INDIVIDUAL_ID', 'PERSON_ID','PERSON_REGISTRATION_DATE','DOCUMENT_NUM'
    ]
    df = df[required_columns].copy()
    potential_duplicates = []
    with tqdm(total=5, desc="Preparing data and calculating features") as pbar:

        # Clean and vectorize text columns
        df['PERSON_FIRST_NAME'] = df['PERSON_FIRST_NAME'].map(clean_text)
        df['PERSON_MIDDLE_NAME'] = df['PERSON_MIDDLE_NAME'].map(clean_text)
        df['PERSON_LAST_NAME'] = df['PERSON_LAST_NAME'].map(clean_text)
        df['LOCATION_NAME'] = df['LOCATION_NAME'].map(clean_text)
        pbar.update(1)
        
        df['combined_last_name'] = np.where(
            df['PERSON_MIDDLE_NAME'] == df['PERSON_LAST_NAME'],
            df['PERSON_LAST_NAME'],
            (df['PERSON_MIDDLE_NAME'] + '' + df['PERSON_LAST_NAME']).str.strip()
        )
        df['full_name'] = (df['PERSON_FIRST_NAME'] + ' '+ df['PERSON_MIDDLE_NAME'] + ' ' + df['PERSON_LAST_NAME']).str.strip()
        

        # Filter out invalid names
        valid_first_names = is_valid_name_vectorized(df['PERSON_FIRST_NAME'])
        valid_last_names = is_valid_name_vectorized(df['combined_last_name'])
        df = df[valid_first_names & valid_last_names].reset_index(drop=True)
        pbar.update(1)
    
        # Precompute age, phonetic encodings, and numerical data 
        df['age'] = calculate_age(df['PERSON_DATE_OF_BIRTH'])
        df['age'].fillna(1000, inplace=True)
        df['FIRST_NAME'] = df['PERSON_FIRST_NAME'].str.split().str[0]
        df['LAST_NAME'] = df['combined_last_name'].str.split().str[-1]
        pbar.update(1)
    
        df['phonetic_first_name'] = df['FIRST_NAME'].map(phonetic_encoding)
        df['phonetic_last_name'] = df['LAST_NAME'].map(phonetic_encoding)
        df['phonetic_full_name'] = df['full_name'].map(phonetic_encoding)
        df['phonetic_location_name'] = df['LOCATION_NAME'].map(phonetic_encoding)
        df['phonetic_full_name'] = df['phonetic_full_name'].str.replace(" ", "", regex=False)
        pbar.update(1)
        phonetic_encoder = LabelEncoder()
        df['phonetic_first_name'] = phonetic_encoder.fit_transform(df['phonetic_first_name'])
        df['phonetic_last_name'] = phonetic_encoder.fit_transform(df['phonetic_last_name'])
        df['phonetic_full_name'] = phonetic_encoder.fit_transform(df['phonetic_full_name'])
        df['phonetic_location_name'] = phonetic_encoder.fit_transform(df['phonetic_location_name'])
        # Encode categorical columns
        gender_le = LabelEncoder()
        country_le = LabelEncoder()
        df['PERSON_GENDER'] = gender_le.fit_transform(df['PERSON_GENDER'])
        df['COUNTRY_ISO_CODE'] = country_le.fit_transform(df['COUNTRY_ISO_CODE'])
        pbar.update(1)

    return df

# Deduplication Function
def deduplication(df, threshold=0.80, batch_size=500, device='cuda'):
    """Computes similarity using selective filtering with PyTorch and GPU acceleration."""

    column_mapping = {
        'Person First Name': 'PERSON_FIRST_NAME',
        'Person Middle Name': 'PERSON_MIDDLE_NAME',
        'Person Last Name': 'PERSON_LAST_NAME',
        'Location Name': 'LOCATION_NAME',
        'Person Date of Birth': 'PERSON_DATE_OF_BIRTH',
        'Person Gender': 'PERSON_GENDER',
        'Country ISO Code2': 'COUNTRY_ISO_CODE',
        'Person Household ID': 'PERSON_HOUSEHOLD_ID',
        'Person Biometrics Individual ID': 'PERSON_BIOMETRICS_INDIVIDUAL_ID',
        'Person ID': 'PERSON_ID',
        'Document Number':'DOCUMENT_NUM',
        'Person Registration Date' : 'PERSON_REGISTRATION_DATE'
    }

    # Preprocess the DataFrame
    df = preprocess_dataframe(df, column_mapping)
    
    # Prepare tensors
    df_tensors = {
        'age': to_tensor(df['age'], device=device),
        'gender': to_tensor(df['PERSON_GENDER'], dtype=torch.int32, device=device),
        'country': to_tensor(df['COUNTRY_ISO_CODE'], dtype=torch.int32, device=device),
        'phonetic_first_name': to_tensor(df['phonetic_first_name'], dtype=torch.int32, device=device),
        'phonetic_last_name': to_tensor(df['phonetic_last_name'], dtype=torch.int32, device=device),
        'phonetic_location_name': to_tensor(df['phonetic_location_name'], dtype=torch.int32, device=device),
        'phonetic_full_name': to_tensor(df['phonetic_full_name'], dtype=torch.int32, device=device)
    }

    # Process batches
    batch_indices = [(start, min(start + batch_size, len(df))) for start in range(0, len(df), batch_size)]
    results = []
    for start, end in tqdm(batch_indices, desc="Processing Batches"):
        results.extend(process_batch_on_gpu(start, end, batch_size, threshold, df, df_tensors, device))

    # Return duplicates DataFrame
    duplicates_df = pd.DataFrame(results)
    return duplicates_df

# test=deduplication(final_data,threshold=0.9)
# test

# Identify Helping Functions
def process_batch_on_gpu_identify(start, end, threshold, df, df_tensors, device='cuda'):
    """Processes a batch of new records against the entire dataframe on GPU."""
    # Ensure `is_new` tensor is on the correct device
    person_ids = df['PERSON_ID'].values
    combined_names = df['combined_last_name'].values
    full_names = df['full_name'].values
    location_names = df['LOCATION_NAME'].values
    is_new = df['is_new'].values

    if isinstance(is_new, np.ndarray):
        is_new = torch.tensor(is_new, device=device)
    else:
        is_new = is_new.to(device)

    # Get indices of new records and move to the correct device
    new_indices = torch.where(is_new[start:end])[0].to(device)
    if len(new_indices) == 0:
        return []  # No new records to process

    # Slice tensors for the current batch and move to the correct device
    batch_age = df_tensors['age'][start:end].to(device)[new_indices]
    batch_gender = df_tensors['gender'][start:end].to(device)[new_indices]
    batch_country = df_tensors['country'][start:end].to(device)[new_indices]
    batch_phonetic_first_name = df_tensors['phonetic_first_name'][start:end].to(device)[new_indices]
    batch_phonetic_last_name = df_tensors['phonetic_last_name'][start:end].to(device)[new_indices]
    batch_phonetic_location_name = df_tensors['phonetic_location_name'][start:end].to(device)[new_indices]
    batch_phonetic_full_name = df_tensors['phonetic_full_name'][start:end].to(device)[new_indices]


    # Move full dataset tensors to the device
    full_age = df_tensors['age'].to(device)
    full_gender = df_tensors['gender'].to(device)
    full_country = df_tensors['country'].to(device)
    full_phonetic_first_name = df_tensors['phonetic_first_name'].to(device)
    full_phonetic_last_name = df_tensors['phonetic_last_name'].to(device)
    full_phonetic_location_name = df_tensors['phonetic_location_name'].to(device)
    full_phonetic_full_name = df_tensors['phonetic_full_name'].to(device)


    # Compute similarity matrices
    gender_similarity = batch_gender.unsqueeze(1) == full_gender
    age_similarity = (torch.abs(batch_age.unsqueeze(1) - full_age) <= 2) | (torch.abs(batch_age.unsqueeze(1) - full_age) >= 900)
    phonetic_first_name_matches = batch_phonetic_first_name.unsqueeze(1) == full_phonetic_first_name
    phonetic_last_name_matches = batch_phonetic_last_name.unsqueeze(1) == full_phonetic_last_name
    phonetic_full_name_matches = (batch_phonetic_full_name.unsqueeze(1) == full_phonetic_full_name)
    phonetic_location_name_matches = batch_phonetic_location_name.unsqueeze(1) == full_phonetic_location_name
    country_matches = batch_country.unsqueeze(1) == full_country

    # Combine masks
    compatible_rows_mask = gender_similarity & age_similarity
    phonetic_first_name_matches &= compatible_rows_mask
    phonetic_last_name_matches &= compatible_rows_mask
    phonetic_full_name_matches &= compatible_rows_mask
    phonetic_location_name_matches &= compatible_rows_mask
    country_matches &= compatible_rows_mask

    # Collect duplicates
    batch_duplicates = []
    for i, new_idx in enumerate(new_indices):
        # Calculate the similarity score for the new record
        combined_score_matrix = (
            phonetic_first_name_matches[i] * 0.05 +
            phonetic_last_name_matches[i] * 0.05 +
            phonetic_full_name_matches[i] * 0.70 + 
            # age_similarity[i] * 0.10 + \
            phonetic_location_name_matches[i] * 0.10 + \
            country_matches[i] * 0.10)

        duplicate_indices = torch.where(combined_score_matrix > threshold)[0]

        # Append results for valid duplicates
        for idx in duplicate_indices:
            if person_ids[start + new_idx] == person_ids[idx]:
                continue

            similarity_score = combined_score_matrix[idx].item()
            household_id_flag = (
                "Identical" if df['PERSON_HOUSEHOLD_ID'].iloc[start + new_idx.item()] == df['PERSON_HOUSEHOLD_ID'].iloc[idx.item()]
                else "Not available" if pd.isna(df['PERSON_HOUSEHOLD_ID'].iloc[start + new_idx.item()]) or pd.isna(df['PERSON_HOUSEHOLD_ID'].iloc[idx.item()])
                else "Different"
            )
            biometrics_id_flag = (
                "Identical" if df['PERSON_BIOMETRICS_INDIVIDUAL_ID'].iloc[start + new_idx.item()] == df['PERSON_BIOMETRICS_INDIVIDUAL_ID'].iloc[idx.item()]
                else "Not available" if pd.isna(df['PERSON_BIOMETRICS_INDIVIDUAL_ID'].iloc[start + new_idx.item()]) or pd.isna(df['PERSON_BIOMETRICS_INDIVIDUAL_ID'].iloc[idx.item()])
                else "Different"
            )
            registration_date_flag = (
                "Identical" if df['PERSON_REGISTRATION_DATE'].iloc[start + new_idx.item()] == df['PERSON_REGISTRATION_DATE'].iloc[idx.item()]
                else "Not available" if pd.isna(df['PERSON_REGISTRATION_DATE'].iloc[start + new_idx.item()]) or pd.isna(df['PERSON_REGISTRATION_DATE'].iloc[idx.item()])
                else "Different"
            )
            document_number_flag = (
                "Identical" if df['DOCUMENT_NUM'].iloc[start + new_idx.item()] == df['DOCUMENT_NUM'].iloc[idx.item()]
                else "Not available" if pd.isna(df['DOCUMENT_NUM'].iloc[start + new_idx.item()]) or pd.isna(df['DOCUMENT_NUM'].iloc[idx.item()])
                else "Different"
            )

            batch_duplicates.append({
                'PERSON_ID_1': person_ids[start + new_idx],
                'PERSON_ID_2': person_ids[idx],
                'Full_Name_1': full_names[start + new_idx],
                'Full_Name_2': full_names[idx],
                'Age_1': batch_age[i].item(),
                'Age_2': full_age[idx].item(),
                'Location_Name_1': location_names[start + new_idx],
                'Location_Name_2': location_names[idx],
                'Similarity_Score': similarity_score,
                'Biometrics_ID_Flag': biometrics_id_flag,
                'Household_ID_Flag': household_id_flag,
                'Registration_Date_Flag': registration_date_flag,
                'Document_Number_Flag': document_number_flag
            })

    return batch_duplicates


def preprocess_dataframe_identify(df, column_mapping):
    """Preprocesses the DataFrame by renaming, cleaning, and preparing data."""
    # Rename columns
    
    # Rename the DataFrame columns to match the required names
    df = df.rename(columns=column_mapping)

    # Select the relevant columns after renaming
    required_columns = [
        'PERSON_FIRST_NAME', 'PERSON_MIDDLE_NAME', 'PERSON_LAST_NAME', 
        'LOCATION_NAME', 'PERSON_DATE_OF_BIRTH', 'PERSON_GENDER', 
        'COUNTRY_ISO_CODE', 'PERSON_HOUSEHOLD_ID', 'PERSON_BIOMETRICS_INDIVIDUAL_ID', 'PERSON_ID','PERSON_REGISTRATION_DATE','DOCUMENT_NUM','is_new'
    ]
    df = df[required_columns].copy()
    potential_duplicates = []
    with tqdm(total=5, desc="Preparing data and calculating features") as pbar:

        # Clean and vectorize text columns
        df['PERSON_FIRST_NAME'] = df['PERSON_FIRST_NAME'].map(clean_text)
        df['PERSON_MIDDLE_NAME'] = df['PERSON_MIDDLE_NAME'].map(clean_text)
        df['PERSON_LAST_NAME'] = df['PERSON_LAST_NAME'].map(clean_text)
        df['LOCATION_NAME'] = df['LOCATION_NAME'].map(clean_text)
        pbar.update(1)
        
        df['combined_last_name'] = np.where(
            df['PERSON_MIDDLE_NAME'] == df['PERSON_LAST_NAME'],
            df['PERSON_LAST_NAME'],
            (df['PERSON_MIDDLE_NAME'] + ' ' + df['PERSON_LAST_NAME']).str.strip()
        )        
        df['full_name'] = (df['PERSON_FIRST_NAME'] + ' '+ df['PERSON_MIDDLE_NAME'] + ' ' + df['PERSON_LAST_NAME']).str.strip()

        # Filter out invalid names
        valid_first_names = is_valid_name_vectorized(df['PERSON_FIRST_NAME'])
        valid_last_names = is_valid_name_vectorized(df['combined_last_name'])
        df = df[valid_first_names & valid_last_names].reset_index(drop=True)
        pbar.update(1)
    
        # Precompute age, phonetic encodings, and numerical data 
        df['age'] = calculate_age(df['PERSON_DATE_OF_BIRTH'])
        df['age'].fillna(1000, inplace=True)
        df['FIRST_NAME'] = df['PERSON_FIRST_NAME'].str.split().str[0]
        df['LAST_NAME'] = df['combined_last_name'].str.split().str[-1]
        pbar.update(1)
    
        df['phonetic_first_name'] = df['FIRST_NAME'].map(phonetic_encoding)
        df['phonetic_last_name'] = df['LAST_NAME'].map(phonetic_encoding)
        df['phonetic_full_name'] = df['full_name'].map(phonetic_encoding)
        df['phonetic_location_name'] = df['LOCATION_NAME'].map(phonetic_encoding)
        df['phonetic_full_name'] = df['phonetic_full_name'].str.replace(" ", "", regex=False)
        pbar.update(1)
        phonetic_encoder = LabelEncoder()
        df['phonetic_first_name'] = phonetic_encoder.fit_transform(df['phonetic_first_name'])
        df['phonetic_last_name'] = phonetic_encoder.fit_transform(df['phonetic_last_name'])
        df['phonetic_full_name'] = phonetic_encoder.fit_transform(df['phonetic_full_name'])
        df['phonetic_location_name'] = phonetic_encoder.fit_transform(df['phonetic_location_name'])
        # Encode categorical columns
        gender_le = LabelEncoder()
        country_le = LabelEncoder()
        df['PERSON_GENDER'] = gender_le.fit_transform(df['PERSON_GENDER'])
        df['COUNTRY_ISO_CODE'] = country_le.fit_transform(df['COUNTRY_ISO_CODE'])
        pbar.update(1)

    return df

# Identify Function

def identify(new_records, old_records, threshold=0.80, batch_size=500, device='cuda'):
    """
    Computes similarity using selective filtering with PyTorch and GPU acceleration.
    It compares new records to the entire combined dataset (new + old records) but avoids comparing older records with each other.
    """

    # Combine new and old records, and add a marker to distinguish them
    new_records['is_new'] = True
    old_records['is_new'] = False
    df= pd.concat([old_records, new_records], ignore_index=True)

    column_mapping = {
        'Person First Name': 'PERSON_FIRST_NAME',
        'Person Middle Name': 'PERSON_MIDDLE_NAME',
        'Person Last Name': 'PERSON_LAST_NAME',
        'Location Name': 'LOCATION_NAME',
        'Person Date of Birth': 'PERSON_DATE_OF_BIRTH',
        'Person Gender': 'PERSON_GENDER',
        'Country ISO Code2': 'COUNTRY_ISO_CODE',
        'Person Household ID': 'PERSON_HOUSEHOLD_ID',
        'Person Biometrics Individual ID': 'PERSON_BIOMETRICS_INDIVIDUAL_ID',
        'Person ID': 'PERSON_ID',
        'Document Number':'DOCUMENT_NUM',
        'Person Registration Date' : 'PERSON_REGISTRATION_DATE'
    }

    # Preprocess the DataFrame
    df = preprocess_dataframe_identify(df, column_mapping)
    
    # Prepare tensors
    df_tensors = {
        'age': to_tensor(df['age'], device=device),
        'gender': to_tensor(df['PERSON_GENDER'], dtype=torch.int32, device=device),
        'country': to_tensor(df['COUNTRY_ISO_CODE'], dtype=torch.int32, device=device),
        'phonetic_first_name': to_tensor(df['phonetic_first_name'], dtype=torch.int32, device=device),
        'phonetic_last_name': to_tensor(df['phonetic_last_name'], dtype=torch.int32, device=device),
        'phonetic_location_name': to_tensor(df['phonetic_location_name'], dtype=torch.int32, device=device),
        'phonetic_full_name': to_tensor(df['phonetic_full_name'], dtype=torch.int32, device=device)
    }

    # Process batches
    batch_indices = [(start, min(start + batch_size, len(df))) for start in range(0, len(df), batch_size)]
    results = []
    for start, end in tqdm(batch_indices, desc="Processing Batches"):
        results.extend( process_batch_on_gpu_identify(start, end, threshold, df, df_tensors, device))

    # Return duplicates DataFrame
    duplicates_df = pd.DataFrame(results)
    return duplicates_df


# Parallel processing

def deduplication_parallel(df, threshold=0.80, batch_size=200):
    """Concurrent GPU computation using dynamic batch allocation and optimized data transfer."""
    # Preprocess the DataFrame and convert columns to tensors
    column_mapping = {
        'Person_First_Name': 'PERSON_FIRST_NAME',
        'Person_Middle_Name': 'PERSON_MIDDLE_NAME',
        'Person_Last_Name': 'PERSON_LAST_NAME',
        'Location_Name': 'LOCATION_NAME',
        'Person_Date_Of_Birth': 'PERSON_DATE_OF_BIRTH',
        'Person_Gender': 'PERSON_GENDER',
        'Country_ISO_Code2': 'COUNTRY_ISO_CODE',
        'Person_Household_ID': 'PERSON_HOUSEHOLD_ID',
        'Person_Biometrics_Individual_ID': 'PERSON_BIOMETRICS_INDIVIDUAL_ID',
        'Person_ID': 'PERSON_ID',
        'Document_Number': 'DOCUMENT_NUM',
        'Person_Registration_Date': 'PERSON_REGISTRATION_DATE',
    }

    # Preprocess DataFrame and create tensors
    df = preprocess_dataframe(df, column_mapping)
    df_tensors = {
        'age': to_tensor(df['age'], device='cpu'),  # Initially on CPU
        'gender': to_tensor(df['PERSON_GENDER'], dtype=torch.int32, device='cpu'),
        'country': to_tensor(df['COUNTRY_ISO_CODE'], dtype=torch.int32, device='cpu'),
        'phonetic_first_name': to_tensor(df['phonetic_first_name'], dtype=torch.int32, device='cpu'),
        'phonetic_last_name': to_tensor(df['phonetic_last_name'], dtype=torch.int32, device='cpu'),
        'phonetic_location_name': to_tensor(df['phonetic_location_name'], dtype=torch.int32, device='cpu'),
        'phonetic_full_name': to_tensor(df['phonetic_full_name'], dtype=torch.int32, device='cpu')

    }

    # Divide the data into batches
    batch_indices = [(start, min(start + batch_size, len(df))) for start in range(0, len(df), batch_size)]

    # Initialize task queue
    task_queue = Queue()
    for start, end in batch_indices:
        task_queue.put((start, end))

    results = []

    # Worker function for dynamic batch allocation
    def process_batches_dynamically(device_idx, task_queue, results, progress_bar):
        device = f'cuda:{device_idx}' if torch.cuda.is_available() else 'cpu'
        # Move tensors to GPU before processing
        device_tensors = {k: v.to(device) for k, v in df_tensors.items()}
        
        while not task_queue.empty():
            try:
                start, end = task_queue.get_nowait()
                batch_results = process_batch_on_gpu(
                    start, end, batch_size, threshold, df, df_tensors, device
                )
                results.extend(batch_results)
                progress_bar.update(1)
            except Exception as e:
                print(f"Error on device {device_idx}: {e}")
            finally:
                task_queue.task_done()

    # Process batches concurrently across devices
    device_count = torch.cuda.device_count() if torch.cuda.is_available() else 1
    with tqdm(total=len(batch_indices), desc="Processing batches") as progress_bar:
        threads = []
        for device_idx in range(device_count):
            thread = Thread(target=process_batches_dynamically, args=(device_idx, task_queue, results, progress_bar))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()

    # Convert results to a DataFrame
    duplicates_df = pd.DataFrame(results)
    return duplicates_df


def identify_parallel(new_records, old_records, threshold=0.80, batch_size=100, device='cuda'):
    """
    Computes similarity using selective filtering with PyTorch and GPU acceleration.
    It compares new records to the entire combined dataset (new + old records) but avoids comparing older records with each other.
    """
    # Combine new and old records, and add a marker to distinguish them
    new_records['is_new'] = True
    old_records['is_new'] = False
    df = pd.concat([old_records, new_records], ignore_index=True)
    """Concurrent GPU computation using dynamic batch allocation and optimized data transfer."""
    # Preprocess the DataFrame and convert columns to tensors
    column_mapping = {
        'Person First Name': 'PERSON_FIRST_NAME',
        'Person Middle Name': 'PERSON_MIDDLE_NAME',
        'Person Last Name': 'PERSON_LAST_NAME',
        'Location Name': 'LOCATION_NAME',
        'Person Date of Birth': 'PERSON_DATE_OF_BIRTH',
        'Person Gender': 'PERSON_GENDER',
        'Country ISO Code2': 'COUNTRY_ISO_CODE',
        'Person Household ID': 'PERSON_HOUSEHOLD_ID',
        'Person Biometrics Individual ID': 'PERSON_BIOMETRICS_INDIVIDUAL_ID',
        'Person ID': 'PERSON_ID',
        'Document Number': 'DOCUMENT_NUM',
        'Person Registration Date': 'PERSON_REGISTRATION_DATE',
    }

    # Preprocess DataFrame and create tensors
    df = preprocess_dataframe_identify(df, column_mapping)
    # is_new = torch.tensor(df['is_new'].values, device='cpu', dtype=torch.bool)  # Ensure `is_new` starts on CPU

    df_tensors = {
        'age': to_tensor(df['age'], device='cpu'),
        'is_new': to_tensor(df['is_new'],dtype=torch.bool, device='cpu'), # Initially on CPU
        'gender': to_tensor(df['PERSON_GENDER'], dtype=torch.int32, device='cpu'),
        'country': to_tensor(df['COUNTRY_ISO_CODE'], dtype=torch.int32, device='cpu'),
        'phonetic_first_name': to_tensor(df['phonetic_first_name'], dtype=torch.int32, device='cpu'),
        'phonetic_last_name': to_tensor(df['phonetic_last_name'], dtype=torch.int32, device='cpu'),
        'phonetic_location_name': to_tensor(df['phonetic_location_name'], dtype=torch.int32, device='cpu'),
        'phonetic_full_name': to_tensor(df['phonetic_full_name'], dtype=torch.int32, device='cpu')
    }
    
    # Divide the data into batches
    batch_indices = [(start, min(start + batch_size, len(df))) for start in range(0, len(df), batch_size)]

    # Initialize task queue
    task_queue = Queue()
    for start, end in batch_indices:
        task_queue.put((start, end))

    results = []

    # Worker function for dynamic batch allocation
    def process_batches_dynamically(device_idx, task_queue, results, progress_bar):
        device = f'cuda:{device_idx}' if torch.cuda.is_available() else 'cpu'
        # Move tensors to GPU before processing
        device_tensors = {k: v.to(device) for k, v in df_tensors.items()}
        
        while not task_queue.empty():
            try:
                start, end = task_queue.get_nowait()
                batch_results = process_batch_on_gpu_identify(start, end, threshold, df, df_tensors, device)
                results.extend(batch_results)
                progress_bar.update(1)
            except Exception as e:
                print(f"Error on device {device_idx}: {e}")
            finally:
                task_queue.task_done()

    # Process batches concurrently across devices
    device_count = torch.cuda.device_count() if torch.cuda.is_available() else 1
    with tqdm(total=len(batch_indices), desc="Processing batches") as progress_bar:
        threads = []
        for device_idx in range(device_count):
            thread = Thread(target=process_batches_dynamically, args=(device_idx, task_queue, results, progress_bar))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()

    # Convert results to a DataFrame
    duplicates_df = pd.DataFrame(results)
    return duplicates_df