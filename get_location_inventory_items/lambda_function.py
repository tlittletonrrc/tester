import json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "Inventory"


# Convert DynamoDB Decimal types to native int/float
def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj


def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    pk_value = "Location1"  # Currently static

    try:
        items = []
        response = table.query(KeyConditionExpression=Key("PK").eq(pk_value))

        items.extend(response.get("Items", []))

        # Continue querying if data is paginated
        while "LastEvaluatedKey" in response:
            response = table.query(
                KeyConditionExpression=Key("PK").eq(pk_value),
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))

        items = convert_decimals(items)

    except ClientError as e:
        error_message = e.response.get("Error", {}).get("Message", "Unknown error")
        print(f"Query failed: {error_message}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": error_message}),
        }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(items),
    }
