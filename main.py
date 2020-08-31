import tweepy
import os
from utils import *
from state import ScraperState

DATA_PATH = 'data'
USERS_FILE = os.path.join(DATA_PATH, 'users.json')
EDGES_FILE = os.path.join(DATA_PATH, 'edges.json')

AUTH_DETAILS_FILE = 'config.txt'
auth_details = parse_auth_details(AUTH_DETAILS_FILE)
curr_auth = auth_details[0]

auth = tweepy.OAuthHandler(curr_auth['CONSUMER_KEY'], curr_auth['CONSUMER_SECRET'])
auth.set_access_token(curr_auth['ACCESS_TOKEN'], curr_auth['ACCESS_TOKEN_SECRET'])
api = tweepy.API(auth)

MAX_USERS = 100000
MAX_CONNECTIONS = 3000

users = set()
edges = set()

COLD_START = True
REQUESTS_SO_FAR = 0

if COLD_START:
    origin_user = get_origin_user(api)
    scraper_state = ScraperState(origin_user, users, edges)
else:
    scraper_state = ScraperState.load(USERS_FILE, EDGES_FILE)

queue = [scraper_state.origin_user]
visited_ids = set()

while len(users) < 3:
    print(f'Reached {len(users)} users')
    user = queue.pop(0)
    print(user)
    users.add(user)
    visited_ids.add(user.id)

    followers_list = list()
    followers = limit_handler(tweepy.Cursor(api.followers, id=user.id).pages())
    for follower_page in followers:
        for follower in follower_page:
            if follower.friends_count > MAX_CONNECTIONS or follower.followers_count > MAX_CONNECTIONS:
                continue
            followers_list.append(follower)
    print(followers_list)

    followees_list = list()
    followees = limit_handler(tweepy.Cursor(api.friends, id=user.id).pages())
    for followee_page in followees:
        for followee in followee_page:
            if followee.friends_count > MAX_CONNECTIONS or followee.followers_count > MAX_CONNECTIONS:
                continue

            followees_list.append(followee)
    print(followees_list)

    for follower in followers_list:
        if follower.id not in visited_ids:
            queue.append(follower)
            edges.add((follower, user))

    for followee in followees_list:
        if followee.id not in visited_ids:
            queue.append(followee)
            edges.add((user, followee))