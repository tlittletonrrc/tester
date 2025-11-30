import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "Inventory"

def convert_decimals(obj):
    """Convert DynamoDB Decimal types to native int/float."""
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    return obj


def lambda_handler(event, context):
    """Lambda entry point."""
    table = dynamodb.Table(TABLE_NAME)

    pk_value = event.get("pathParameters", {}).get("location")
    if not pk_value:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": "Missing 'location' path parameter"}),
        }

    try:
        response = table.query(
            KeyConditionExpression=Key("PK").eq(pk_value)
        )
        items = response.get("Items", [])

        while "LastEvaluatedKey" in response:
            response = table.query(
                KeyConditionExpression=Key("PK").eq(pk_value),
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))

        items = convert_decimals(items)

    except ClientError as err:
        error_message = (
            err.response.get("Error", {}).get("Message", "Unknown error")
        )
        print(f"Query failed: {error_message}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
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
