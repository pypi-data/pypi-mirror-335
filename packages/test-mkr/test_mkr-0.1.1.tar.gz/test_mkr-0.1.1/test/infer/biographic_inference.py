import argparse
import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
import logging
from botocore.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

conf = Config(
    region_name="eu-west-1",
    signature_version="v4",
    retries={"max_attempts": 10, "mode": "standard"},
)

cloudwatch = boto3.client("cloudwatch", config=conf)


def put_metric(name, value, unit):
    cloudwatch.put_metric_data(
        Namespace="BiographicDeduplication",
        MetricData=[{"MetricName": name, "Value": value, "Unit": unit}],
    )


def get_opensearch_credentials(secret_arn):
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", config=conf)
    secret_value = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(secret_value["SecretString"])
    return secret


def parse_args():
    import sys
    if "ipykernel" in sys.modules:
        return argparse.Namespace(
            secret_arn=None,
            opensearch_host="search-dedup-opensearch-sandbox-v3-bvb7niv5ndx2f4nokvzrc6vrpe.eu-west-1.es.amazonaws.com",
            opensearch_port="443",
            opensearch_user="admin",
            opensearch_pass="Y](\\{r3>JKi$oCF'OlGQJpU42U0Z0?b|",
            opensearch_index="biographic_dedup",
            target_id="195136",  # Provide a default target ID
            threshold=0.8
        )
    parser = argparse.ArgumentParser(description="Biographic deduplication with script_score query")
    parser.add_argument("--secret-arn", type=str, help="ARN of the secret containing OpenSearch credentials")
    parser.add_argument("--opensearch-host", type=str, help="OpenSearch host")
    parser.add_argument("--opensearch-port", type=str, default="443", help="OpenSearch port")
    parser.add_argument("--opensearch-user", type=str, help="OpenSearch username")
    parser.add_argument("--opensearch-pass", type=str, help="OpenSearch password")
    parser.add_argument("--opensearch-index", type=str, default="biographic_dedup", help="OpenSearch index name")
    parser.add_argument("--target-id", type=str, required=True, help="ID of the record to find duplicates for")
    parser.add_argument("--threshold", type=float, default=0.8, help="Similarity threshold for duplicates")
    return parser.parse_args()


def connect_opensearch(host, port, user, password):
    try:
        client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=(user, password),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=6000
        )
        logger.info("Successfully connected to OpenSearch")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to OpenSearch: {e}")
        raise


def compare_and_flag(target_record, matched_record):
    return {
        "household_id_flag": (
            "Identical"
            if target_record.get("household_id") == matched_record.get("household_id")
            else "Different"
        ),
        "biometrics_id_flag": (
            "Identical"
            if target_record.get("biometrics_id") == matched_record.get("biometrics_id")
            else "Different"
        ),
        "registration_date_flag": (
            "Identical"
            if target_record.get("registration_date")
            == matched_record.get("registration_date")
            else "Different"
        ),
        "document_number_flag": (
            "Identical"
            if target_record.get("document_id") == matched_record.get("document_id")
            else "Different"
        ),
    }


def fetch_record_by_id(client, index_name, record_id):
    try:
        response = client.get(index=index_name, id=record_id)
        logger.info(f"Fetched record ID {record_id} from OpenSearch")
        return response["_source"]
    except Exception as e:
        logger.error(f"Error fetching record ID {record_id} from OpenSearch: {e}")
        raise


def find_duplicates_with_script_score(client, index_name, target_record, threshold):
    query = {
        "size": 10000,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": """
                        double score = 0.0;
                        // Phonetic first name
                        if (doc['phonetic_first_name.keyword'].size() > 0 && 
                            doc['phonetic_first_name.keyword'].value == params.phonetic_first_name) {
                            score += 0.05;
                        }

                        // Phonetic last name
                        if (doc['phonetic_last_name.keyword'].size() > 0 && 
                            doc['phonetic_last_name.keyword'].value == params.phonetic_last_name) {
                            score += 0.05;
                        }
                        // Phonetic full name
                        if (doc['phonetic_full_name.keyword'].size() > 0 && 
                            doc['phonetic_full_name.keyword'].value == params.phonetic_full_name) {
                            score += 0.70;
                        }
                        // Age difference
                        double age_diff = Math.abs(doc['age'].value - params.age);
                        if (age_diff <= 2 || age_diff >= 900) {
                            score += 0.00;
                        }
                        // Phonetic location
                        if (doc['phonetic_location_name.keyword'].size() > 0 && 
                            doc['phonetic_location_name.keyword'].value == params.phonetic_location_name) {
                            score += 0.10;
                        }
                        // Country
                        if (doc['country.keyword'].size() > 0 && 
                            doc['country.keyword'].value == params.country) {
                            score += 0.10;
                        }
                        return score;
                    """,
                    "params": {
                        "phonetic_first_name": target_record["phonetic_first_name"],
                        "phonetic_last_name": target_record["phonetic_last_name"],
                        "phonetic_full_name": target_record["phonetic_full_name"],
                        "gender": target_record["gender"],
                        "age": target_record["age"],
                        "phonetic_location_name": target_record[
                            "phonetic_location_name"
                        ],
                        "age": target_record["age"],
                        "country": target_record["country"],
                    },
                },
            },
        },
    }

    # Log query parameters for debugging
    logger.info("Query parameters:")
    logger.info(
        json.dumps(query["query"]["script_score"]["script"]["params"], indent=2)
    )

    try:
        response = client.search(index=index_name, body=query)
        duplicates = []

        logger.info("Debugging scores for records:")
        for hit in response["hits"]["hits"]:
            record_id = hit["_id"]
            score = hit["_score"]
            record = hit["_source"]

            # logger.info(f"Record ID: {record_id}")
            # logger.info(f"Score: {score}")
            # logger.info(f"Record Details: {json.dumps(record, indent=2)}")

            if score >= threshold:
                flags = compare_and_flag(target_record, record)
                duplicates.append(
                    {
                        "record_id": record_id,
                        "similarity_score": score,
                        "record": record,
                        **flags,
                    }
                )

        logger.info(f"Found {len(duplicates)} potential duplicates")
        return duplicates
    except Exception as e:
        logger.error(f"Error executing script_score query: {e}")
        raise


def main():
    args = parse_args()

    # Fetch credentials from Secrets Manager if secret ARN is provided
    if args.secret_arn:
        logger.info("Fetching OpenSearch credentials from Secrets Manager")
        creds = get_opensearch_credentials(args.secret_arn)
        host = creds.get("host")
        port = creds.get("port", "443")
        user = creds.get("username")
        password = creds.get("password")
    else:
        logger.info("Using provided OpenSearch credentials")
        host = args.opensearch_host
        port = args.opensearch_port
        user = args.opensearch_user
        password = args.opensearch_pass

    if not all([host, user, password]):
        logger.error("Missing required OpenSearch credentials")
        raise ValueError("OpenSearch host, username, and password are required")

    # Connect to OpenSearch
    client = connect_opensearch(host, port, user, password)

    # Fetch the target record by ID
    target_record = fetch_record_by_id(client, args.opensearch_index, args.target_id)

    # Find duplicates using script_score
    duplicates = find_duplicates_with_script_score(
        client, args.opensearch_index, target_record, args.threshold
    )

    # Output results
    logger.info(f"Found {len(duplicates)} duplicates for record ID {args.target_id}")
    output_file = "biographic_script_score_duplicates.json"
    with open(output_file, "w") as f:
        json.dump(duplicates, f, indent=2)
    logger.info(f"Duplicate records written to {output_file}")

    put_metric("TotalDuplicates", len(duplicates), "Count")


if __name__ == "__main__":
    main()
