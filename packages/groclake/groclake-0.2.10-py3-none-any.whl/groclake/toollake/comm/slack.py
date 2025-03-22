from slack_sdk import WebClient
import os
from dotenv import load_dotenv

load_dotenv()

class Slack:
    def __init__(self):
        self.slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

    def send_message(self, payload):
        try:
            message=payload.get("message")
            channel=payload.get("channel")
            self.slack_client.chat_postMessage(channel=channel, text=message)
            return {"message":"Message Sent Successfully"}
        except Exception as e:
            return {"message":str(e)}
