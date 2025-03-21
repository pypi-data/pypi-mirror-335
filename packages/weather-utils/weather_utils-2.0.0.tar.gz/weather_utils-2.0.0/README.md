### Environment Variables for `weather_utils` Library  

The `weather_utils` library relies on environment variables for configuration. Before using the library, ensure the required environment variables are properly set.  

**Required Environment Variables:**  

- `DYNAMODB_TABLE_NAME` → The name of the DynamoDB table where weather data is stored.  
- `SNS_TOPIC_ARN` → The ARN of the SNS topic used for sending weather alerts.  

**Setting Environment Variables:**  

For **Linux/macOS**, run:  
`export DYNAMODB_TABLE_NAME="WeatherDataTable"`  
`export SNS_TOPIC_ARN="arn:aws:sns:us-east-1:123456789012:WeatherAlerts"`  

For **Windows PowerShell**, run:  
`$env:DYNAMODB_TABLE_NAME="WeatherDataTable"`  
`$env:SNS_TOPIC_ARN="arn:aws:sns:us-east-1:123456789012:WeatherAlerts"`  

For **AWS Lambda**, set these variables in the **Lambda function environment variables** section.  

**Usage in `weather_utils`:**  

The library reads these environment variables dynamically:  

`import os`  
`DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "DefaultWeatherTable")`  
`SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "default_sns_topic")`  

Ensure these variables are configured before using the library in your application.