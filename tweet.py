import tweepy

class Tweet(dict):
    def __init__(self, tweet):
        assert isinstance(tweet, tweepy.models.Status)

        super().__init__(self, id=tweet.id, author=tweet.user.id, attrs=tweet)
        self.id = tweet.id
        self.author = tweet.user.id
        self.attrs = tweet

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Tweet):
            return False
        return self.id == o.id

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return object.__hash__(self.id)

    def __repr__(self) -> str:
        return f"Tweet {self.id} from {self.author}"




