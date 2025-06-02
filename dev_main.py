import os
import json

from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler

import logging
logging.basicConfig(level=logging.DEBUG)

from dotenv import load_dotenv
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_APP_TOKEN= os.getenv("SLACK_APP_TOKEN")
#SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")

app = App(
    # https://api.slack.com/authentication/verifying-requests-from-slack
    # Initializes your app with your bot token and signing secret
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

def generateBlocksMessage(accepting_user,invite,channel,json_file):
    workmate_name = accepting_user["name"]
    workmate_id = accepting_user["id"]
    external_user = invite["inviting_user"]["profile"]["email"]
    invite_id = invite["id"]
    # channel_name=channel["name"] Not in the payload like it is in documentation
    # manager_test = accepting_user["id"]

    # Approve/Decline message for manager
    text_message = f"Hello, *Please review this invitation:*"
    with open(json_file) as f:
        json_file = json.load(f)
        json_file["blocks"][0]["text"]["text"]=text_message
        json_file["blocks"][1]["elements"][0]["value"]=invite_id # approve_button
        json_file["blocks"][1]["elements"][1]["value"]=invite_id # decline_button
    return json.dumps(json_file["blocks"])

 
# Event: https://api.slack.com/events/shared_channel_invite_accepted
@app.event("shared_channel_invite_accepted")
# This is triggered when a user in the org accepts a Slack Connect invite
# Note: The invitivation may still require an approval flow depending on the settings
def shared_channel_invite_accepted(ack, body):
    ack()
    print("\nshared_channel_invite_accepted event has happened.\n")
    request_message = generateBlocksMessage(body["event"]["accepting_user"],body["event"]["invite"],body["event"]["channel"],"request_message.json")
    app.client.chat_postMessage(
        channel="U08NY9QJZ34", 
        blocks=request_message
    )

@app.event("shared_channel_invite_approved")
def shared_channel_invite_approved(ack, body):
    print("shared_channel_invite_approved event has happened.")

@app.event("shared_channel_invite_declined")
def shared_channel_invite_declined(ack, body):
    print("shared_channel_invite_declined event has happened.")

@app.event("shared_channel_invite_received")
def shared_channel_invite_received(ack, body):
    print("shared_channel_invite_received event has happened.")

@app.event("shared_channel_invite_requested")
def shared_channel_invite_requested(ack, body):
    print("shared_channel_invite_requested event has happened.")

# Needs events listener on
@app.action("approve_button")
def approve_invitation(ack, body):
    ack()
    invite_id = body["actions"][0]["value"]
    app.client.conversations_approveSharedInvite(invite_id=invite_id)

# Needs events listener on
@app.action("decline_button")
def decline_invitation(ack, body):
    ack()
    invite_id = body["actions"][0]["value"]
    app.client.conversations_declineSharedInvite(invite_id=invite_id)


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()