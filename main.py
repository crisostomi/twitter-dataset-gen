from utils import *
from users_scraper import UserScraper, UserScraperState
from tweet_scraper import TweetScraper, TweetScraperState
from datetime import datetime, timedelta

from user import User
import tweepy

DATA_PATH = './data'
AUTH_DETAILS_FILE = 'config.txt'

### User scraping params ###
MAX_USERS = 10000
MAX_CONNECTIONS = 1000

COLD_START = True
SAVE_INTERVAL = 10

### Tweet scraping params ###
TIME_PERIOD = 3 # days

def scrape_users(apis):
    if COLD_START:
        print("Cold start. Looking for origin user...")
        origin_user = UserScraper.get_origin_user(apis[1], max_connections=MAX_CONNECTIONS)
        scraper_state = UserScraperState(first_state=True, origin_user=origin_user)
    else:
        print("Loading scraper state...")
        scraper_state = UserScraperState(first_state=False, data_path=DATA_PATH)

    scraper = UserScraper(
        data_path=DATA_PATH,
        state=scraper_state,
        max_users=MAX_USERS,
        max_connections=MAX_CONNECTIONS,
        save_interval=SAVE_INTERVAL
    )

    print("Done.")

    scraper.scrape(apis)

def scrape_tweets(apis):
    if COLD_START:
        print("Cold start. Creating empy state...")
        te = datetime.now()
        ts = te - timedelta(days=TIME_PERIOD)
        time_window = (ts, te)

        users_path = os.path.join(DATA_PATH, "users.json")
        users = load_json(users_path)
        users = [User(user) for user in users]
        users_queue = [user.id for user in users]
        scraper_state = TweetScraperState(
            users_queue=users_queue,
            time_window=time_window,
            tweets=dict()
        )
    else:
        print("Loading scraper state...")
        scraper_state = TweetScraperState.load(DATA_PATH)

    scraper = TweetScraper(
        DATA_PATH,
        state=scraper_state,
        save_interval=SAVE_INTERVAL
    )
    print("Done.")

    scraper.scrape(apis)

if __name__ == '__main__':
    auth_details = parse_auth_details(AUTH_DETAILS_FILE)

    auths = []
    for item in auth_details:
        consumer_key = item['CONSUMER_KEY']
        consumer_secret = item['CONSUMER_SECRET']
        access_key = item['ACCESS_TOKEN']
        access_secret = item['ACCESS_TOKEN_SECRET']

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        auths.append(auth)

    print("Creating API handler(s)...")
    apis = [
        tweepy.API(auths[0], wait_on_rate_limit=True, wait_on_rate_limit_notify=True),
        tweepy.API(auths[1], wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    ]
    print("Done.")

    # user_scraping(apis)
    scrape_tweets(apis)