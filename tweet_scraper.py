import tweepy
from tweet import Tweet
from utils import save_json, load_json
import os
from datetime import datetime, timedelta

class TweetScraperState:
    def __init__(
            self,
            tweets=None,
            users_queue=None,
            time_window=None,
    ):
        """
        :param tweets: Tweets scraped so far
        :param users_queue: Queue of users to be processed
        :param time_window: Time window of reference for the tweets
        """
        self.tweets = tweets
        self.users_queue = users_queue
        self.time_window = time_window

    @staticmethod
    def load(folder):
        tweets_path = os.path.join(folder, "tweets.json")
        users_queue_path = os.path.join(folder, "users_queue.json")
        time_window_path = os.path.join(folder, "time_window.json")

        tweets = []
        users_queue = []
        time_window = None

        # load users
        try:
            tweets = load_json(tweets_path)
        except Exception as exc:
            print("ERROR ON TWEET LOADING!")
            print(exc)
        try:
            users_queue = load_json(users_queue_path)
        except Exception as exc:
            print("ERROR ON USERS QUEUE LOADING!")
            print(exc)
        try:
            time_window = load_json(time_window_path)
        except Exception as exc:
            print("ERROR ON TIME WINDOW LOADING!")
            print(exc)

        return TweetScraperState(tweets=tweets, users_queue=users_queue, time_window=time_window)

    def save(self, folder):
        tweets_path = os.path.join(folder, "tweets.json")
        users_queue_path = os.path.join(folder, "users_queue.json")
        time_window_path = os.path.join(folder, "time_window.json")

        save_json(self.tweets, tweets_path)
        save_json(self.users_queue, users_queue_path)
        save_json(self.time_window, time_window_path)


class TweetScraper:
    def __init__(
            self,
            data_path,
            state=None,
            save_interval=10,
    ):
        self.data_path = data_path
        self.state = state
        self.save_interval = save_interval

    def scrape(self, apis):
        assert not (self.data_path is None or self.state is None)
        assert not (self.state.tweets is None or self.state.users_queue is None or self.state.time_window is None)

        api_idx = 0

        tweets, users_id_queue, time_window = self.state.tweets, self.state.users_queue, self.state.time_window
        ts, te = time_window

        try:
            iterations = 0
            tweets_count = sum([len(v) for k, v in tweets.items()])
            while len(users_id_queue) > 0:
                user_id = users_id_queue.pop(0)
                print(f"\n\nUsers left: {len(users_id_queue)}.\nTweets so far: {tweets_count}.\n")
                api = apis[api_idx]

                # Getting tweets
                user_tweets = []
                try:
                    for tweet_page in tweepy.Cursor(api.user_timeline, id=user_id, tweet_mode="extended").pages():
                        user_tweets.extend(tweet_page)
                        last_timestamp = user_tweets[-1].created_at

                        if last_timestamp < ts:
                            break
                except tweepy.error.TweepError as exc:
                    print(f"\nCatched TweepError ({exc.response.title}: {exc.response.detail})."
                          f"\nIgnoring user.")
                    continue

                # Retaining only tweets in [t_s, t_e]
                user_tweets_list = []
                for tweet in user_tweets:
                    if tweet.created_at >= ts and tweet.created_at <= te:
                        user_tweets_list.append(tweet)

                # Register user tweets
                tweets[user_id] = user_tweets_list
                tweets_count += len(user_tweets_list)

                # Switch api to balance load
                api_idx = (api_idx + 1) % 2

                # Save progress
                iterations += 1
                if iterations % self.save_interval == 0:
                    scraper_state = TweetScraperState(
                        tweets=tweets,
                        users_queue=users_id_queue,
                        time_window=time_window
                    )
                    scraper_state.save(self.data_path)

        except KeyboardInterrupt:
            print("\n\nInterrupt received. Terminating...")
        finally:
            print("Saving scraper state...")
            scraper_state = TweetScraperState(
                tweets=tweets,
                users_queue=users_id_queue,
                time_window=time_window
            )
            scraper_state.save(self.data_path)
            print("Done.")