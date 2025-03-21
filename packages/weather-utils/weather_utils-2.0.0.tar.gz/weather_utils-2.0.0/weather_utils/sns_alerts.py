import boto3
import os

# Fetch SNS Topic ARN from environment variable
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", None)

# Initialize SNS client
sns_client = boto3.client("sns", region_name=os.getenv("AWS_REGION", "us-east-1"))


def create_sns_topic(topic_name="WeatherAlerts"):
    try:
        if SNS_TOPIC_ARN:
            print(f"Using existing SNS Topic: {SNS_TOPIC_ARN}")
            return SNS_TOPIC_ARN

        response = sns_client.create_topic(Name=topic_name)
        topic_arn = response["TopicArn"]
        print(f"SNS Topic Created: {topic_arn}")
        return topic_arn
    except Exception as e:
        print(f"❌ Error creating SNS topic: {e}")
        raise


def send_weather_alert(city, lat, lon, weather_data):
    """
    Sends an SNS alert for extreme weather conditions.
    """
    topic_arn = SNS_TOPIC_ARN or create_sns_topic()

    temperature = weather_data["main"]["temp"]
    wind_speed = weather_data["wind"]["speed"]
    weather_condition = weather_data["weather"][0]["main"]

    alert_message = None

    if temperature < -10 or temperature > 40:
        alert_message = f"⚠️ Extreme Temperature Alert: {temperature}°C in {city}!"
    elif wind_speed > 80:
        alert_message = f"🌪️ High Wind Speed Alert: {wind_speed} km/h in {city}!"
    elif weather_condition in ["Thunderstorm", "Tornado", "Hurricane"]:
        alert_message = f"⛈️ Severe Weather Alert: {weather_condition} in {city}!"

    if alert_message:
        sns_client.publish(
            TopicArn=topic_arn,
            Message=alert_message,
            Subject=f"Weather Alert for {city}",
        )
        print(f"✅ Alert Sent: {alert_message}")
    else:
        print(f"No severe weather detected in {city}. No alert sent.")
    return None

def subscribe_user_to_alerts(email):
    try:
        response = sns_client.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol="email",
            Endpoint=email
        )
        print(f"✅ Subscription request sent to {email}. User must confirm subscription.")
        print(f"Confirmation status: {response.get('SubscriptionArn', 'PendingConfirmation')}")
        return response
    except Exception as e:
        print(f"❌ Error subscribing user: {e}")
        raise


def list_subscriptions():
    try:
        response = sns_client.list_subscriptions_by_topic(TopicArn=SNS_TOPIC_ARN)
        subscriptions = response.get("Subscriptions", [])
        if not subscriptions:
            print("No subscriptions found for the SNS topic.")
        return subscriptions
    except Exception as e:
        print(f"❌ Error listing subscriptions: {e}")
        raise
