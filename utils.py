import json
import jsonpickle
import os
import tweepy
import random
import time
import traceback
from user import User
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

def save_json(data, path):
    with open(path, 'w+') as f:
        encoded_data = jsonpickle.encode(data)
        json.dump(encoded_data, f)

def load_json(path):
    with open(path, 'r') as f:
        encoded_data = json.load(f)
        data = jsonpickle.decode(encoded_data)
    return data
