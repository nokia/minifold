#!/usr/bin/env python3
#
# Twitter connector
#
# This file is part of the minifold project.
# https://github.com/nokia/minifold

import datetime
from .connector import Connector
from .query import ACTION_READ, Query

try:
    import tweepy
except ImportError as e:
    from .log import Log
    Log.warning(
        "Please install requests-cache.\n"
        "  APT: sudo apt install python3-tweepy\n"
        "  PIP: sudo pip3 install --upgrade tweepy\n"
    )
    raise e


def tweet_to_dict(tweet) -> dict:
    """
    Converts a tweet to a dictionary.

    Args:
        tweet: The input tweet.

    Returns:
        The corresponding dictionary.
    """
    # Fetch tweet
    try:
        content = tweet._json["full_text"]
    except KeyError:
        content = tweet._json["text"]
    if content:
        content = content.split(" https://t.co/")[0]

    # Get tweet image
    image = None
    try:
        image = tweet._json["entities"]["media"][0]["media_url"]
    except Exception:
        # Try to get image from youtube, e.g: https://img.youtube.com/vi/iZCyv0e2RLM/1.jpg
        try:
            if "youtu" in tweet._json["entities"]["urls"][0]["display_url"]:
                image = (
                    "https://img.youtube.com/vi/%s/1.jpg"
                    % tweet._json["entities"]["urls"][0]["display_url"].split("/")[-1]
                )
        except Exception:
            Log.warning("No image found for tweet %s" % content)

    # Get author name
    author_name = None
    try:
        author_name = tweet._json["user"]["name"]
    except KeyError:
        Log.warning("No author name found for tweet %s" % content)

    # Get author image
    author_image = None
    try:
        author_image = tweet._json["user"]["profile_image_url"]
    except KeyError:
        Log.warning("No author image found for tweet %s" % content)

    # Get tweet date
    date_list = tweet._json["created_at"].split()
    display_date = "%(m)s %(d)s, %(y)s" % {
        "d": date_list[2],
        "m": date_list[1],
        "y": date_list[5]
    }
    date = datetime.datetime.strptime(display_date, "%b %d, %Y")
    display_date = date.strftime("%d/%m/%Y")

    # Return entry
    return {
        "text": content,
        "image": image,
        "date": date,
        "display_date": display_date,
        "author_name": author_name,
        "author_image": author_image,
    }


class TwitterConnector(Connector):
    """
    The :py:class:`TwitterConnector` is a gateway minifold allowing
    to fetch tweets from Twitter.
    """
    def __init__(
        self,
        twitter_id: str,
        consumer_key: str,
        consumer_secret: str,
        access_token: str,
        access_token_secret: str
    ):
        """
        Constructor.

        Args:
            twitter_id (str): The Twitter identifier.
            consumer_key (str): The Twitter API Key.
            consumer_secret (str): The Twitter secret.
            access_token (str): The Twitter access token.
            access_token_secret: The Twitter access token secret.
        """
        super().__init__()
        self.twitter_id = twitter_id
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.api = None
        self.connect()

    def attributes(self, object: str) -> set:
        """
        Lists the available attributes related to a given collection of
        minifold entries exposed by this :py:class:`WhereConnector` instance.

        Args:
            object (str): The name of the collection.
                Valid collections are ``"self"`` and ``"feed"``.

        Returns:
            The set of corresponding attributes.
        """

        return {
            "text",
            "image",
            "date",
            "display_date",
            "author_name",
            "author_image"
        } if object in {"self", "feed"} else set()

    def connect(self):
        """
        Connect to the Twitter API.
        """
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth)

    def query(self, q: Query) -> list:
        """
        Handles an input :py:class:`Query` instance.

        Args:
            query (Query): The handled query.

        Returns:
            The list of entries matching the input query.
        """
        if not self.api:
            raise RuntimeError("Not connected to twitter")

        if q.action == ACTION_READ:
            if q.object in {"self", "feed"}:
                # Retrieve Tweets
                assert q.limit > 0
                size = q.limit
                if q.object == "self":
                    tweets = self.api.user_timeline(
                        id=self.twitter_id,
                        tweet_mode="extended",
                        count=size
                    )
                elif q.object == "feed":
                    tweets = self.api.home_timeline(
                        id=self.twitter_id,
                        tweet_mode="extended",
                        count=size
                    )
                else:
                    tweets = list()
                entries = [tweet_to_dict(tweet) for tweet in tweets]
            else:
                raise ValueError(f"Invalid object '{q.object}'")
        else:
            raise RuntimeError(f"Query {q}: action {q.action} not implemented")
        return self.answer(q, entries)
