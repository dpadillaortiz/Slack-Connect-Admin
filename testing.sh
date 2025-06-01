#!/bin/bash

# This script invites users to a shared Slack channel.

# IMPORTANT: Replace these placeholder values with your actual information.
# It's recommended to use environment variables for sensitive data like tokens in production.
SLACK_API_TOKEN=""
CHANNEL_ID=""
USER_IDS=""
EMAILS="

curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer ${SLACK_API_TOKEN}" \
     -d "{
           \"channel\": \"${CHANNEL_ID}\",
           \"emails\": \"${EMAILS}\"
         }" \
     https://slack.com/api/conversations.inviteShared
