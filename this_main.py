import os
import json

from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.aws_lambda import SlackRequestHandler

import logging
logging.basicConfig(level=logging.DEBUG)

from dotenv import load_dotenv
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
#SLACK_APP_TOKEN= os.getenv("SLACK_APP_TOKEN")
#SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")

app = App(
    # https://api.slack.com/authentication/verifying-requests-from-slack
    # Initializes your app with your bot token and signing secret
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

def generateBlocksMessage(manager,workmate,external_user,channel,invite_id,json_file):
    # Approve/Decline message for manager
    text_message = f"Hello {manager}, {workmate} is being invited by {external_user} to join {channel} using Slack Connect.\n\n *Please review this invitation:*"
    with open(json_file) as f:
        json_file = json.load(f)
        json_file["blocks"][0]["text"]["text"]=text_message
        json_file["blocks"][1]["elements"][0]["value"]=invite_id # approve_button
        json_file["blocks"][1]["elements"][1]["value"]=invite_id # decline_button
    return json.dumps(json_file["blocks"])

def getUsersManager(user_id):
    # Gets user_id's manager info
    # The user["profile"]["fields"] payload code needs to be verified
    # https://api.slack.com/methods/users.profile.get
    # https://api.slack.com/methods/users.lookupByEmail
    try:
        manager_info = app.client.users_profile_get(user=user_id)["profile"]["fields"]["people"]["manager"]
        manager_user_id = app.client.users_lookupByEmail(email=manager_info["email"])["user"]["id"]
        return manager_user_id
    except SlackApiError as e:
        assert e.response["error"]

def pendingSlackConnectInvites():
    # https://api.slack.com/methods/conversations.listConnectInvites
    # Lists all pending incoming invites, i.e. invites from external to user
    try:
        all_invites = app.client.conversations_listConnectInvites(team_id=os.getenv("EXTERNAL"))["invites"]
        pending_invites = []
        for invite in all_invites:
            criteria = invite["acceptances"][0]["approval_status"] == "pending_approval" and invite["direction"] == "incoming"
            if criteria == True:
                invite_cust_obj = {
                    "invite":invite["invite"],
                    "channel":invite["channel"],
                    "workmate":invite["acceptances"]["accepting_user"]
                }
                pending_invites.append(invite_cust_obj)
        return pending_invites
    except SlackApiError as e:
        assert e.response["error"]

# Event: https://api.slack.com/events/shared_channel_invite_accepted
@app.action("shared_channel_invite_accepted")
def shared_channel_invite_accepted(ack, body):
    ack()
    invite_cust_obj = {
        "invite":body["invite"],
        "channel":body["channel"],
        "workmate":body["accepting_user"]
    }
    workmate_name = body["accepting_user"]["name"]
    workmate_id = body["accepting_user"]["id"]
    external_user = body["invite"]["inviting_user"]["profile"]["email"]
    invite_id = body["invite"]["id"]
    channel_name=body["channel"]["name"]
    manager_test = body["accepting_user"]["id"]
    request_msg = generateBlocksMessage(manager_test,workmate_name,external_user,channel_name,invite_id,"request_message.json")
    app.client.chat_postMessage(channel=manager_test, attachment=request_msg) # send request message
    app.client.chat_postMessage(channel=workmate_id, text=f"Your invite from {external_user} to join {channel_name} is under review by <@{manager_test}>")


@app.message("wake me up")
def say_hello(ack, message):
    ack()
    channel_id = message["channel"]
    app.client.chat_postMessage(
        channel=channel_id,
        text="Summer has come and passed"
    )

# Needs events listener on
@app.action("approve_button")
def approve_invitation(ack, body):
    ack()
    invite_id = body["actions"][0]["value"]
    app.client.conversations_approveSharedInvite(invite_id=invite_id)
    # TO DO: Add workmate_id to value
    #app.client.chat_postMessage(channel=workmate_id, text=f"Your invite from {external_user} to join {channel_name} has been approved.")

# Needs events listener on
@app.action("decline_button")
def decline_invitation(ack, body):
    ack()
    invite_id = body["actions"][0]["value"]
    app.client.conversations_declineSharedInvite(invite_id=invite_id)
    # TO DO: Add workmate_id to value
    #app.client.chat_postMessage(channel=workmate_id, text=f"Your invite from {external_user} to join {channel_name} has been declined.")

def main():
    pending_invites = pendingSlackConnectInvites()
    
    for invite in pending_invites:
        workmate_name = invite["workmate"]["name"]
        workmate_id = invite["workmate"]["id"]
        external_user = invite["inviting_user"]["profile"]["email"]
        invite_id = invite["invite"]["id"]
        channel_name=invite["channel"]["name"]
        manager_id = getUsersManager(invite["workmate"]["id"])
        request_msg = generateBlocksMessage(manager_id, workmate_name, external_user, manager_id, invite_id, "request_message.json")
        #app.client.chat_postMessage(channel=manager_id, attachment=request_msg) # send request message
        #app.client.chat_postMessage(channel=workmate_id, text=f"Your invite from {external_user} to join {channel_name} is under review by <@{manager_id}>")

@app.event("app_home_opened")
def handle_app_home_opened(client, event, logger):
    # Respond to the app_home_opened event
    pass

def handler(event, context):
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)

app.client.chat_postMessage(
        channel="C08UZG1A11S",
        text="Summer has come and passed"
    )
    

