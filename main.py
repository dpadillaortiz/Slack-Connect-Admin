import os
import json

from slack_bolt import App
from slack_sdk.errors import SlackApiError




import logging
logging.basicConfig(level=logging.DEBUG)

from dotenv import load_dotenv
load_dotenv()
"""
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_APP_TOKEN= os.getenv("SLACK_APP_TOKEN")
SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")

# https://api.slack.com/authentication/verifying-requests-from-slack
# Initializes your app with your bot token and signing secret
app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# Slack Connect API reference
# https://api.slack.com/apis/connect-reference

# print_this = app.client.team_externalTeams_list(connection_status_filter="CONNECTED")

def isChannelInExternal(channel_id):
    # https://api.slack.com/methods/conversations.info
    EXTERNAL = os.getenv("EXTERNAL")
    workspace_id = app.client.conversations_info(channel=channel_id)["channel"]["context_team_id"]
    return workspace_id == EXTERNAL

def isChannelPrivate(channel_id):
    # https://api.slack.com/methods/conversations.info
    is_private = app.client.conversations_info(channel=channel_id)["channel"]["is_private"] 
    if is_private == 'false':
        return False
    else:
        return True

def convert_to_private(channel_id):
    # https://api.slack.com/methods/conversations.join, 
    # https://api.slack.com/methods/admin.conversations.convertToPrivate
    app.client.conversations_join(channel=channel_id)
    app.client.admin_conversations_convertToPrivate(channel_id=channel_id, token=SLACK_USER_TOKEN)
    return isChannelPrivate(channel_id)

def create_channel(channel_name):
    # https://api.slack.com/methods/conversations.create
    EXTERNAL = os.getenv("EXTERNAL")
    app.client.conversations_create(name=channel_name, is_private = True, team_id=EXTERNAL)
    return "Channel created."

def add_to_channel(user_ids, channel_id):
    # https://api.slack.com/methods/conversations.invite
    for user_id in user_ids.split(","):
        try:
            app.client.conversations_invite(channel=channel_id, users=user_id)
            return "User added."
        except SlackApiError as e:
            assert e.response["error"] 

def list_connected_orgs():
    # https://api.slack.com/methods/team.externalTeams.list
    try:
        connected_orgs = app.client.team_externalTeams_list(connection_status_filter="CONNECTED")["organizations"]
        list_connected_orgs = {}
        for org in connected_orgs:
            list_connected_orgs[org["team_domain"]] = org["team_id"]
        return list_connected_orgs
    except SlackApiError as e:
            assert e.response["error"]

def list_pending_connect_invites():
    # https://api.slack.com/methods/conversations.listConnectInvites
    try:
        all_invites = app.client.conversations_listConnectInvites(team_id=os.getenv("EXTERNAL"))["invites"]
        pending_invites = []
        for invite in all_invites:
            criteria = invite["acceptances"][0]["approval_status"] == "pending_approval" and invite["direction"] == "incoming"
            if criteria == True:
                invite_cust_obj = {
                    "direction": invite["direction"],
                    "invite_type":invite["invite_type"],
                    "invite_id": invite["id"],
                    "channel_id": invite["channel"]["id"],
                    "channel_is_private": invite["channel"]["is_private"],
                    "channel_name": invite["channel"]["name"],
                    "is_im": invite["channel"]["is_im"],
                    "recipient_email": invite["recipient_email"],
                    "inviting_team_id": invite["inviting_team"]["id"],
                    "inviting_team_domain": invite["inviting_team"]["domain"],
                    "inviting_user": invite["inviting_user"]["profile"]["email"],
                    "accepting_sub_team_id": invite["acceptances"][0]["accepting_sub_team"]["id"],
                    "accepting_sub_team_domain": invite["acceptances"][0]["accepting_sub_team"]["domain"]
                }
                pending_invites.append(invite_cust_obj)
        return pending_invites
    except SlackApiError as e:
            assert e.response["error"]

if __name__ == "__main__":

    
    CONNECTED_DOMAINS={"sandbox":"", "the-rebels":"E08P5P1JH09"} #test
    DENIED_DOMAINS = []
    DENIED_EMAILS = []

    pending_invites = list_pending_connect_invites()

    for invite in pending_invites:
        if CONNECTED_DOMAINS.get(invite["inviting_team_domain"]) is not None:
            print(f'{invite["inviting_team_domain"]} is a key.')
            if invite["channel_is_private"] == True:
                # https://api.slack.com/methods/conversations.approveSharedInvite
                app.client.conversations_approveSharedInvite(
                    invite_id=invite["invite_id"]
                )

"""


def generateBlocksMessage(manager,workmate,external_user,channel, invite_id, json_file):
    text_message = f"Hello {manager}, {workmate} is being invited by {external_user} to join {channel} using Slack Connect.\n\n *Please review this invitation:*"
    with open(json_file) as f:
        json_file = json.load(f)
        json_file["blocks"][0]["text"]["text"]=text_message
        json_file["blocks"][1]["elements"][0]["value"]=invite_id # approve_button
        json_file["blocks"][1]["elements"][1]["value"]=invite_id # decline_button
    return json.dumps(json_file["blocks"])



# When user clicks approve do this
@app.action("approve_button")
def approve_invitation(ack, body):
    ack()

    pass

# When user clicks decline do this
@app.event("team_join")
def log_message_change(logger, event):
    pass

