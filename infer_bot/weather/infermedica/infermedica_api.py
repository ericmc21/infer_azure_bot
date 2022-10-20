
import os
import aiohttp

from dotenv import load_dotenv
from requests import head
from config import DefaultConfig


# POST request
import os
from dotenv import load_dotenv
load_dotenv()
APP_ID = os.environ["APP_ID"]
APP_KEY = os.environ["APP_KEY"]
URL = os.environ["API_URL"]


class InfermedicaApi:

    
    async def parse(age, gender, utterance):
       
        headers={"App-Id": APP_ID, "App-Key": APP_KEY}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(
                URL + "/parse", json={"age": {"value": age },"sex": gender.lower(),"text": utterance}
            ) as resp:
                return await resp.json()

    async def get_risk_factors(age, gender):
        headers={"App-Id": APP_ID, "App-Key": APP_KEY}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(
                URL + "/suggest", json={"age": {"value": age }, "sex": gender.lower(), "suggest_method": "demographic_risk_factors"}
            ) as resp:
                return await resp.json()