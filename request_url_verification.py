import json

def lambda_handler(event, context):
    if event.get("body"):
        body = json.loads(event["body"])
        
        # Slack URL verification
        if body.get("type") == "url_verification":
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "text/plain"
                },
                "body": body["challenge"]  # Return the challenge string directly
            }

    return {
        "statusCode": 400,
        "body": "Bad Request"
    }
