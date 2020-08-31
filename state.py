import json
import os

import jsonpickle

from utils import save_json

class ScraperState:
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

        # load users
        with open(users_path, 'r') as f:
            encoded_data = json.load(f)
            users = jsonpickle.decode(encoded_data)

        # load edges
        with open(edges_path, 'r') as f:
            encoded_data = json.load(f)
            edges = jsonpickle.decode(encoded_data)

        # load queue
        with open(queue_path, 'r') as f:
            encoded_data = json.load(f)
            queue = jsonpickle.decode(encoded_data)

        # load visited
        with open(queue_path, 'r') as f:
            encoded_data = json.load(f)
            visited_ids = jsonpickle.decode(encoded_data)

        return ScraperState(queue=queue, visited_ids=set(visited_ids), users=users, edges=edges)

    def save(self, folder):
        ## Persist users and edges
        users_path = os.path.join(folder, "users.json")
        edges_path = os.path.join(folder, "edges.json")

        save_json(self.users, users_path)
        save_json(self.edges, edges_path)

        self.users_to_persist = []
        self.edges_to_persist = []

        ## Save state of queue and visited
        queue_path = os.path.join(folder, 'queue.json')
        save_json(self.queue, queue_path)

        visited_ids_path = os.path.join(folder, 'visited.json')
        save_json(list(self.visited_ids), visited_ids_path)

    # def persist(self, folder):
    #     ## Persist users and edges
    #     users_path = os.path.join(folder, "users.json")
    #     edges_path = os.path.join(folder, "edges.json")
    #
    #     save_json(self.users_to_persist, users_path)
    #     save_json(self.edges_to_persist, edges_path)
    #
    #     self.users_to_persist = []
    #     self.edges_to_persist = []
    #
    #     ## Save state of queue and visited
    #     queue_path = os.path.join(folder, 'queue.json')
    #     save_json(self.queue, queue_path)
    #
    #     visited_ids_path = os.path.join(folder, 'visited.json')
    #     save_json(list(self.visited_ids), visited_ids_path)

    def __repr__(self):
        return f"Queue: {self.queue}\n\n" \
               f"Visited IDs: {self.visited_ids}\n\n" \
               f"Users: {self.users}\n\n" \
               f"Edges: {self.edges}\n\n"
