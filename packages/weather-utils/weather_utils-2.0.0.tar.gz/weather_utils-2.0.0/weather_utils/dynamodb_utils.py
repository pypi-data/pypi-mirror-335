import boto3
from decimal import Decimal
import json
import os

# Fetch table name from environment variable
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE", "WeatherData")

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))


def create_dynamodb_table():
    """
    Creates a DynamoDB table for storing weather data if it doesn't exist.
    Table name is fetched from environment variables.
    """
    existing_tables = dynamodb.meta.client.list_tables()["TableNames"]
    if DYNAMODB_TABLE_NAME in existing_tables:
        print(f"✅ Table '{DYNAMODB_TABLE_NAME}' already exists.")
        return

    table = dynamodb.create_table(
        TableName=DYNAMODB_TABLE_NAME,
        KeySchema=[
            {"AttributeName": "lat_lon", "KeyType": "HASH"},  # Partition Key
            {"AttributeName": "timestamp", "KeyType": "RANGE"}  # Sort Key
        ],
        AttributeDefinitions=[
            {"AttributeName": "lat_lon", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "N"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
    print(f"✅ Table '{DYNAMODB_TABLE_NAME}' created successfully.")


def store_weather_in_dynamodb(city, lat, lon, weather_data):
    """
    Stores weather data in DynamoDB.
    """
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    lat_lon = f"{lat}_{lon}"
    timestamp = int(weather_data["dt"])  # Using OpenWeather API timestamp

    item = {
        "lat_lon": lat_lon,
        "timestamp": timestamp,
        "city": city,
        "weather": json.loads(json.dumps(weather_data), parse_float=Decimal),
    }

    table.put_item(Item=item)
    print(f"✅ Weather data stored for {city} ({lat}, {lon})")
    return item


def get_weather_from_dynamodb(lat, lon):
    """
    Retrieves weather data from DynamoDB if it is within the last 30 minutes.
    """
    print("Inside get_weather_from_dynamodb version 2")
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    lat_lon = f"{lat}_{lon}"

    response = table.query(
        KeyConditionExpression="lat_lon = :lat_lon",
        ExpressionAttributeValues={":lat_lon": lat_lon},
        ScanIndexForward=False,  # Get the latest record first
        Limit=1
    )

    if "Items" in response and response["Items"]:
        return response["Items"][0]

    return None  # No valid cached data found