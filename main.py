import tweepy
import os
from tqdm import tqdm
from utils import *
from state import ScraperState

DATA_PATH = './data'

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

print("Creating API handler(s)...")
apis = [
    tweepy.API(auths[0], wait_on_rate_limit=True, wait_on_rate_limit_notify=True),
    tweepy.API(auths[1], wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
]
print("Done.")

followers_api = 0
followees_api = 1

MAX_USERS = 10000
MAX_CONNECTIONS = 1000

COLD_START = False
SAVE_INTERVAL = 10

if COLD_START:
    print("Cold start. Looking for origin user...")
    origin_user = get_origin_user(apis[1])
    scraper_state = ScraperState(origin_user=origin_user)
else:
    print("Loading scraper state...")
    scraper_state = ScraperState.load(DATA_PATH)

print("Done.")
queue = scraper_state.queue
visited_ids = scraper_state.visited_ids
users = scraper_state.users
edges = scraper_state.edges

# i = 0
# for i, user_id in tqdm(enumerate(visited_ids), total=len(visited_ids), desc="Recovering user info..."):
#     api = apis[i % 2]
#     user = api.get_user(user_id)
#     users.append(user)
#
# scraper_state.save(DATA_PATH)
print("Starting scraping...")
iterations = 0
try:
    while len(users) < MAX_USERS and len(queue) > 0:
        print(f'\n\nUsers: {len(users)}.\nEdges: {len(edges)}.\nQueue: {len(queue)}.')
        user_id = queue.pop(0)
        if isinstance(user_id, User):
            user = user_id
        else:
            try:
                user = apis[followers_api].get_user(user_id)
                user = User(user)
            except tweepy.error.TweepError as exc:
                print(f"\nCatched TweepError ({exc.response}). Ignoring user.")
                continue

        users.append(user)
        visited_ids.add(user.id)

        if len(users) > 1 and (user.attrs.friends_count > MAX_CONNECTIONS or user.attrs.followers_count > MAX_CONNECTIONS):
            continue

        followers_list = list()
        followers = tweepy.Cursor(apis[followers_api].followers_ids, id=user.id).pages()
        try:
            for follower_page in followers:
                followers_list.extend(follower_page)
        except tweepy.error.TweepError as exc:
            print(f"\nCatched TweepError ({exc.response}). Ignoring user.")
            continue

        # print(len(followers_list))

        followees_list = list()
        followees = tweepy.Cursor(apis[followees_api].friends_ids, id=user.id).pages()
        try:
            for followee_page in followees:
                followees_list.extend(followee_page)
        except tweepy.error.TweepError as exc:
            print(f"\nCatched TweepError ({exc.response}). Ignoring user.")
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
        followers_api = (followers_api + 1) % 2
        followees_api = (followees_api + 1) % 2

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
    print("Saving scraper state...")
    scraper_state = ScraperState(
        queue=queue,
        visited_ids=visited_ids,
        users=users,
        edges=edges
    )
    scraper_state.save(DATA_PATH)
    print("Done.")