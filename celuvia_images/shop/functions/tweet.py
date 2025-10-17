import requests
from django.conf import settings


def post_tweet(text: str):
    access_token = settings.TWITTER_ACCESS_TOKEN
    if not access_token:
        raise ValueError("Missing ACCESS_TOKEN in Django settings")

    url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {"text": text}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print("✅ Tweet posted successfully.")
        return response.json()
    else:
        print("❌ Tweet failed:", response.status_code, response.text)
        return None
