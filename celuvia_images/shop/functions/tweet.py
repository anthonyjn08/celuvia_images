import tweepy
from django.conf import settings


def post_tweet(text: str):
    print("sending tweet")
    client = tweepy.Client(
        consumer_key=settings.TWITTER_API_KEY,
        consumer_secret=settings.TWITTER_API_SECRET,
        access_token=settings.TWITTER_ACCESS_TOKEN,
        access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
    )

    try:
        response = client.create_tweet(text=text)
        print("✅ Tweet posted:", response)
        return response
    except Exception as e:
        print("❌ Failed to post tweet:", str(e))
        return None
