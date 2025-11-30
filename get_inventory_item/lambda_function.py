import boto3
import json
from boto3.dynamodb.conditions import Key
from decimal import Decimal


def decimal_to_str(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError


def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("Inventory")

    # Validate path parameter
    path_params = event.get("pathParameters", {})
    key_value = path_params.get("id")

    if not key_value:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing 'id' path parameter"}),
        }

    try:
        response = table.get_item(Key={"_id": key_value})
        item = response.get("Item")

        if not item:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Item not found"}),
            }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(item, default=decimal_to_str),
        }

    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
