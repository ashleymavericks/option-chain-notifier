import requests
from http import HTTPStatus
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import pandas as pd
import sys
import time
import os
import datetime

load_dotenv()

API_KEY = os.getenv("PUSHBULLET_API_KEY")
TIME_VALUE_THRESHOLD = 8
ITM_DEPTH = 0.04 # Strike price till 4% below Nifty


url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
headers = {
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.5",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0",
}
retries = 3
retry_codes = [
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
    HTTPStatus.UNAUTHORIZED
]

for n in range(retries):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        break

    except HTTPError as err:
        code = err.response.status_code

        if code in retry_codes:
            # retry after n seconds
            print(f"Retrying count: {n}")
            time.sleep(n)
            continue

        sys.exit(f"Status Code: {response.status_code} | Reason: {response.reason}")

entire_data = response.json()["records"]
filtered_data = response.json()["filtered"]["data"]

nifty_price = entire_data["underlyingValue"]
fetched_timestamp = entire_data["timestamp"]

ocdata = []

for i in filtered_data:
    for type, info in i.items():
        if type == "CE":
            info["optionType"] = "CE"
            info["delimiter"] = "|"
            ocdata.append(info)

# with open("dumps.json", "w") as f:
#     json.dump(ocdata, f)


df = pd.DataFrame(ocdata)

# Calculate Option time premium and % from Nifty LTP
df["timeValue"] = df["lastPrice"] - (df["underlyingValue"] - df["strikePrice"])
df["percentageFromNifty"] = (
    (df["underlyingValue"] - df["strikePrice"]) / df["underlyingValue"]
) * 100
df["percentageFromNifty"] = df["percentageFromNifty"].round(2)
df["percentageFromNifty"] = df["percentageFromNifty"].astype(str) + "%"


# 3 represents Thursday -> Nifty Expiry
today = datetime.date.today()
current_day_of_week = today.weekday()

days_ahead = (3 - current_day_of_week) % 7
thursday = today + datetime.timedelta(days=days_ahead)
next_thursday = thursday + datetime.timedelta(days=7)

formatted_thursday = thursday.strftime("%d-%b-%Y")
formatted_next_thursday = next_thursday.strftime("%d-%b-%Y")

df = df.loc[
    (df["strikePrice"] > nifty_price - (nifty_price * ITM_DEPTH))
    & (df["strikePrice"] < nifty_price)
    & (df["strikePrice"] % 100 == 0)
]

print(
    df.loc[
        :,
        [
            "expiryDate",
            "strikePrice",
            "optionType",
            "timeValue",
            "lastPrice",
            "percentageFromNifty",
        ],
    ]
)


# Convert DataFrame to plain text
def dataframe_to_text(option_df):
    option_text = option_df.loc[
        :,
        [
            "expiryDate",
            "strikePrice",
            "optionType",
            "timeValue",
            "delimiter",
            "lastPrice",
            "delimiter",
            "percentageFromNifty",
        ],
    ].to_string(index=False, header=False)

    option_text = option_text.replace("-2023", "")
    option_text = option_text.replace("CE ", "CE -> ")
    option_text = option_text.replace("|", " | ")
    return option_text


def send_pushbullet_notification(api_key, title, message):
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {"Access-Token": API_KEY, "Content-Type": "application/json"}

    data = {
        "type": "note",
        "title": title,
        "body": message,
        "channel_tag": "niftyoptions",
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Notification sent successfully")
    else:
        print("Failed to send notification")
        print(response)


option_text = dataframe_to_text(df)

for value in df["timeValue"]:
    if value > TIME_VALUE_THRESHOLD:
        notification_title = f"Nifty50: {nifty_price} @ {fetched_timestamp[:-3]}"
        notification_message = (
            f"Option Details        Time Value | LTP | % diff \n{option_text}"
        )
    else:
        notification_title = f"                ⚠️Alert for Sold Call⚠️ \nNifty50: {nifty_price} @ {fetched_timestamp[:-3]}"
        
        notification_message = (
            f"Option Details        Time Value | LTP | % diff \n{option_text}"
        )
        print("Buy alert is initiated")
        break

send_pushbullet_notification(API_KEY, notification_title, notification_message)
