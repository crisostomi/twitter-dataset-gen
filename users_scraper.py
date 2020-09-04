import tweepy
from user import User
from utils import save_json, load_json
import os

class UserScraperState:
    def __init__(self, origin_user=None,
                 queue=None, visited_ids=None, users=None, edges=None):
        if origin_user is not None:
            self.queue = [origin_user]
            self.visited_ids = set()
            self.users = []
            self.edges = []
        else:
            self.queue = queue
            self.visited_ids = visited_ids
            self.users = users
            self.edges = edges

    @staticmethod
    def load(folder):
        users_path = os.path.join(folder, "users.json")
        edges_path = os.path.join(folder, "edges.json")
        queue_path = os.path.join(folder, 'queue.json')
        visited_ids_path = os.path.join(folder, 'visited.json')

        users = []
        edges = []
        queue = []
        visited_ids = set()

        # load users
        try:
            users = load_json(users_path)
        except Exception as exc:
            print("ERROR ON USERS LOADING!")
            print(exc)
        try:
            edges = load_json(edges_path)
        except Exception as exc:
            print("ERROR ON EDGES LOADING!")
            print(exc)

        try:
            queue = load_json(queue_path)
        except Exception as exc:
            print("ERROR ON QUEUE LOADING!")
            print(exc)

        try:
            visited_ids = load_json(visited_ids_path)
        except Exception as exc:
            print("ERROR ON VISITED IDS LOADING!")
            print(exc)


        return UserScraperState(queue=queue, visited_ids=set(visited_ids), users=users, edges=edges)

    def save(self, folder):
        ## Persist users and edges
        users_path = os.path.join(folder, "users.json")
        edges_path = os.path.join(folder, "edges.json")

        save_json(self.users, users_path)
        save_json(self.edges, edges_path)

        ## Save state of queue and visited
        queue_path = os.path.join(folder, 'queue.json')
        save_json(self.queue, queue_path)

        visited_ids_path = os.path.join(folder, 'visited.json')
        save_json(list(self.visited_ids), visited_ids_path)

    def __repr__(self):
        return f"Queue: {self.queue}\n\n" \
               f"Visited IDs: {self.visited_ids}\n\n" \
               f"Users: {self.users}\n\n" \
               f"Edges: {self.edges}\n\n"

class UsersScraper:
    def __init__(
            self,
            data_path,
            state=None,
            max_users=100000,
            max_connections=1000,
            save_interval=10,
    ):
        self.data_path = data_path
        self.state = state
        self.max_users = max_users
        self.max_connections = max_connections
        self.save_interval = save_interval

    def scrape(self, apis):
        assert not (self.data_path is None or self.state is None)

        queue, visited_ids, users, edges = self.state.queue, self.state.visited_ids, self.state.users, self.state.edges

        followers_api = 0
        followees_api = 1
        print("Starting scraping...")
        iterations = 0
        try:
            while len(users) < self.max_users and len(queue) > 0:
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

                if len(users) > 1 and (user.attrs.friends_count > self.max_connections or user.attrs.followers_count > self.max_connections):
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

                if iterations % self.save_interval == 0:
                    scraper_state = UserScraperState(
                        queue=queue,
                        visited_ids=visited_ids,
                        users=users,
                        edges=edges
                    )
                    scraper_state.save(self.data_path)
        except KeyboardInterrupt:
            print("\n\nInterrupt received. Terminating...")
        finally:
            print("Saving scraper state...")
            scraper_state = UserScraperState(
                queue=queue,
                visited_ids=visited_ids,
                users=users,
                edges=edges
            )
            scraper_state.save(self.data_path)
            print("Done.")