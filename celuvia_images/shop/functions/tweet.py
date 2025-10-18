import tweepy
from django.conf import settings


def post_tweet(text: str, media_path=None):
    """
    Use tweepy to authenticate and send tweets.
    If product has an image, include the image in the tweet.
    """
    print("sending tweet")
    auth = tweepy.OAuth1UserHandler(
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_SECRET,
        settings.TWITTER_ACCESS_TOKEN,
        settings.TWITTER_ACCESS_TOKEN_SECRET,
    )
    api = tweepy.API(auth)

    client = tweepy.Client(
        consumer_key=settings.TWITTER_API_KEY,
        consumer_secret=settings.TWITTER_API_SECRET,
        access_token=settings.TWITTER_ACCESS_TOKEN,
        access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
    )

    try:
        if media_path:
            media = api.media_upload(media_path)
            media_id = media.media_id
            response = client.create_tweet(text=text, media_ids=[media_id])
        else:
            response = client.create_tweet(text=text)

        print("✅ Tweet posted:", response)
        return response

    except Exception as e:
        print("❌ Failed to post tweet:", str(e))
        return None
