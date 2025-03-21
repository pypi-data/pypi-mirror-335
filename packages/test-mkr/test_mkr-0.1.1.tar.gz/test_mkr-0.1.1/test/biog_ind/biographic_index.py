import argparse
import logging
import pandas as pd
from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection, helpers
# from biographic_dedup import preprocess_dataframe
import boto3
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Fetch OpenSearch credentials from Secrets Manager
def get_opensearch_credentials(secret_arn):
    try:
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager")
        secret_value = client.get_secret_value(SecretId=secret_arn)
        secret = json.loads(secret_value["SecretString"])
        return secret
    except Exception as e:
        logger.error(f"Failed to fetch OpenSearch credentials from Secrets Manager: {e}")
        raise

# Connect to OpenSearch
def connect_opensearch(host, port, user, password):
    try:
        client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=(user, password),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
        )
        logger.info("Successfully connected to OpenSearch")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to OpenSearch: {e}")
        raise

# Create the biographic index
def create_biographic_index(client, index_name="biographic_dedup"):
    logger.info(f"Creating OpenSearch index: {index_name}")
    index_body = {
        "mappings": {
            "properties": {
                "phonetic_first_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "phonetic_last_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "phonetic_full_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "age": {"type": "integer"},  
                "gender": {"type": "keyword"},  
                "country":{
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword", "ignore_above": 256}
                    }
                },
                "phonetic_location_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "document_id": {"type": "keyword"},  
                "created_at": {"type": "date"},
                "household_id": {"type": "keyword"},
                "biometrics_id": {"type": "keyword"},
                "registration_date": {"type": "date"}
            }
        }
    }
    try:
        client.indices.create(index=index_name, body=index_body)
        logger.info(f"Successfully created index: {index_name}")
    except Exception as e:
        if "already exists" in str(e):
            logger.warning(f"Index {index_name} already exists.")
        else:
            logger.error(f"Error creating index: {e}")
            raise

# Preprocess and index data
def index_biographic_data(client, index_name, data_file, column_mapping):
    logger.info(f"Loading data from {data_file}")
    df = pd.read_parquet(data_file)
    logger.info(f"Preprocessing data")
    df_cleaned = preprocess_dataframe(df, column_mapping)

    logger.info(f"Indexing {len(df_cleaned)} documents into OpenSearch index '{index_name}'")
    actions = []
    for _, row in df_cleaned.iterrows():
        doc = {
            "_index": index_name,
            "_id": row["PERSON_ID"],
            "phonetic_first_name": row["phonetic_first_name"],
            "phonetic_last_name": row["phonetic_last_name"],
            "phonetic_full_name": row["phonetic_full_name"],
            "age": row["age"],
            "gender": row["PERSON_GENDER"],
            "country": row["COUNTRY_ISO_CODE"],
            "phonetic_location_name": row["phonetic_location_name"],
            "document_id": row["DOCUMENT_NUM"],
            "created_at": datetime.now().isoformat(),
            "biometrics_id": row["PERSON_BIOMETRICS_INDIVIDUAL_ID"],
            "household_id": row["PERSON_HOUSEHOLD_ID"],
            "registration_date": row["PERSON_REGISTRATION_DATE"]
        }
        actions.append(doc)

    helpers.bulk(client, actions)
    logger.info(f"Successfully indexed {len(actions)} documents.")


import time

def main():
    parser = argparse.ArgumentParser(description="Create and manage the biographic_dedup index")
    parser.add_argument("--host", type=str, help="OpenSearch host")
    parser.add_argument("--port", type=str, default="443", help="OpenSearch port")
    parser.add_argument("--user", type=str, help="OpenSearch username")
    parser.add_argument("--password", type=str, help="OpenSearch password")
    parser.add_argument("--secret-arn", type=str, help="ARN of the secret containing OpenSearch credentials")
    parser.add_argument("--index-name", type=str, default="biographic_dedup", help="OpenSearch index name")
    parser.add_argument("--data-file", type=str, required=True, help="Path to the data file")
    
    args = parser.parse_args([
        "--host", "search-dedup-opensearch-sandbox-v3-bvb7niv5ndx2f4nokvzrc6vrpe.eu-west-1.es.amazonaws.com",
        "--port", "443",
        "--user", "admin",
        "--password", "Y](\\{r3>JKi$oCF'OlGQJpU42U0Z0?b|",
        "--index-name", "biographic_dedup",
        "--data-file", "Countries full data/SUDAN/part-00000-a58586da-b545-4258-b4cf-0609d96e7787-c000.snappy.parquet"
    ])

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
        'Person_Has_Photo': 'PERSON_HAS_PHOTO'
    }

    # Fetch credentials from Secrets Manager if secret ARN is provided
    if args.secret_arn:
        # logger.info("Fetching OpenSearch credentials from Secrets Manager")
        creds = get_opensearch_credentials(args.secret_arn)
        host = creds.get("host")
        port = creds.get("port", "443")
        user = creds.get("username")
        password = creds.get("password")
    else:
        # logger.info("Using provided OpenSearch credentials")
        host = args.host
        port = args.port
        user = args.user
        password = args.password

    if not all([host, user, password]):
        logger.error("Missing required OpenSearch credentials")
        raise ValueError("OpenSearch host, username, and password are required")

    # Connect to OpenSearch
    client = connect_opensearch(host, port, user, password)

    # Create the index
    create_biographic_index(client, args.index_name)

    # Measure time taken for indexing
    start_time = time.time()
    index_biographic_data(client, args.index_name, args.data_file, column_mapping)
    end_time = time.time()

    elapsed_time = end_time - start_time
    logger.info(f"Indexing completed in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()
