import json

import boto3


def lambda_handler(event, context):
    dynamo_client = boto3.client("dynamodb")
    table_name = "Inventory"

    try:
        items = []
        response = dynamo_client.scan(TableName=table_name)

        items.extend(response.get("Items", []))

        # Handle pagination (if scan returns more than 1MB of data)
        while "LastEvaluatedKey" in response:
            response = dynamo_client.scan(
                TableName=table_name,
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            items.extend(response.get("Items", []))

        return {
            "statusCode": 200,
            "body": json.dumps(items, default=str),
        }

    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error scanning table: {str(e)}"),
        }
