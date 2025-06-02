import os
from slack_bolt import App
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

app = App(signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))

@app.event("app_home_opened")
def handle_app_home_opened(client, event, logger):
    # Respond to the app_home_opened event
    pass

def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)
