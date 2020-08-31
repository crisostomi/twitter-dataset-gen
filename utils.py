import tweepy
import random
import time
import traceback
from User import User
from ssl import SSLError
from requests.exceptions import Timeout, ConnectionError
from urllib3.exceptions import ReadTimeoutError


def parse_auth_details(auth_details_file):
    with open(auth_details_file, 'r') as f:
        content = f.readlines()
    auth_details = []
    for i in range(0, len(content), 4):
        auth_detail_i = { t.split(':')[0]: t.split(':')[1].strip() for t in content[i:i+4] }
        auth_details.append(auth_detail_i)
    return auth_details


def get_origin_user(api):
    n_random_tweets = 100

    places = api.geo_search(query="USA", granularity="country")
    place_id = places[0].id

    cursor = tweepy.Cursor(
        api.search,
        q=f"place:{place_id}").items(n_random_tweets)

    tweets = limit_handler(cursor)

    users = [tweet.user for tweet in tweets]

    random_user = users[random.randint(0, len(users) - 1)]

    print(f"Id: {random_user.id}")
    print(f"Screen name: {random_user.screen_name}")
    print(f"Location: {random_user.location}")
    print(f"Number of followers: {random_user.followers_count}")
    print(f"Number of followees: {random_user.friends_count}")
    print(f"Number of tweets:", {random_user.statuses_count})

    return User(random_user.id, random_user)


def limit_handler(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            print("Limit exceeded!")
            time.sleep(15 * 60)
        except (Timeout, SSLError, ReadTimeoutError, ConnectionError) as e:
            print(f"Network error occurred. {str(e)}")
            time.sleep(1)
        except StopIteration:
            break
        except Exception:
            print(traceback.format_exc())
            exit(0)
