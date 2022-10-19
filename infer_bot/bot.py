# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import aiohttp

from botbuilder.core import (
    ActivityHandler,
    TurnContext,
)
from botbuilder.schema import (
    ChannelAccount,
)
from dotenv import load_dotenv
from requests import head

# POST request
URL = "https://api.infermedica.com/v3"
ENV_APP_ID="APP_ID"
ENV_APP_KEY="APP_KEY"

load_dotenv(".env")

APP_ID = os.getenv(ENV_APP_ID)
APP_KEY = os.getenv(ENV_APP_KEY)


class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.

    async def on_message_activity(self, turn_context: TurnContext):
        utterance = turn_context.activity.text
        result = await self.parse(utterance)
        symptom = result["mentions"][0]["common_name"]

        await turn_context.send_activity(f"I understood: '{ symptom }'")

    async def on_members_added_activity(
        self, members_added: ChannelAccount, turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Parse API")

    async def parse(self, utterance):
        headers={"App-Id": APP_ID, "App-Key": APP_KEY}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(
                URL + "/parse", json={"age": {"value": 30 },"text": utterance}
            ) as resp:
                return await resp.json()
