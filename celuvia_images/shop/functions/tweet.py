import tweepy
from django.conf import settings


class Tweet:
    """
    Class to send tweets when new Stores or Products are added to the site.
    """
    _instance = None

    def __init__(self):
        auth = tweepy.OAuth1UserHandler(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET,
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_SECRET
        )
        self.api = tweepy.API(auth)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = Tweet()
        return cls._instance

    def make_tweet(self, text: str, image_path: str = None):
        try:
            if image_path:
                self.api.update_status_with_media(
                    filename=image_path, status=text
                    )
            else:
                self.api.update_status(status=text)
        except Exception as e:
            print("Tweet failed:", e)
