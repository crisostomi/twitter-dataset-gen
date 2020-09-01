import tweepy
import os
from utils import *
from state import ScraperState

DATA_PATH = './data'
# USERS_FILE = os.path.join(DATA_PATH, 'users.json')
# EDGES_FILE = os.path.join(DATA_PATH, 'edges.json')

AUTH_DETAILS_FILE = 'config.txt'
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

api1 = tweepy.API(auths[0], wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
api2 = tweepy.API(auths[1], wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

MAX_USERS = 100000
MAX_CONNECTIONS = 1000

COLD_START = False
SAVE_INTERVAL = 10

if COLD_START:
    origin_user = get_origin_user(api1)
    scraper_state = ScraperState(origin_user=origin_user)
else:
    scraper_state = ScraperState.load(DATA_PATH)

queue = scraper_state.queue
visited_ids = scraper_state.visited_ids
users = scraper_state.users
edges = scraper_state.edges

iterations = 0

while len(users) < MAX_USERS and len(queue) > 0:
    try:
        print(f'\n\nUsers: {len(users)}.\nEdges: {len(edges)}.\nQueue: {len(queue)}.')
        user_id = queue.pop(0)
        if isinstance(user_id, User):
            user = user_id
        else:
            user = api1.get_user(user_id)
            user = User(user)

        users.append(user)
        visited_ids.add(user.id)

        if len(users) > 1 and (user.attrs.friends_count > MAX_CONNECTIONS or user.attrs.followers_count > MAX_CONNECTIONS):
            continue

        followers_list = list()
        followers = tweepy.Cursor(api2.followers_ids, id=user.id).pages()
        try:
            for follower_page in followers:
                followers_list.extend(follower_page)
        except tweepy.error.TweepError:
            print("\nCatched TweepError. Ignoring user.")
            continue

        # print(len(followers_list))

        followees_list = list()
        followees = tweepy.Cursor(api1.friends_ids, id=user.id).pages()
        try:
            for followee_page in followees:
                followees_list.extend(followee_page)
        except tweepy.error.TweepError:
            print("\nCatched TweepError. Ignoring user.")
            continue

        # print(len(followees_list))

        for follower_id in followers_list:
            if follower_id not in visited_ids:
                edges.append((follower_id, user.id))
                queue.append(follower_id)

        for followee_id in followees_list:
            if followee_id not in visited_ids:
                edges.append((user.id, followee_id))
                queue.append(followee_id)

        iterations += 1

        # Switch apis to balance load
        tmp = api1
        api1 = api2
        api2 = tmp

        if iterations % SAVE_INTERVAL == 0:
            scraper_state = ScraperState(
                queue=queue,
                visited_ids=visited_ids,
                users=users,
                edges=edges
            )
            scraper_state.save(DATA_PATH)
    except KeyboardInterrupt:
        print("\n\nInterrupt received. Terminating...")
    finally:
        scraper_state = ScraperState(
            queue=queue,
            visited_ids=visited_ids,
            users=users,
            edges=edges
        )
        scraper_state.save(DATA_PATH)