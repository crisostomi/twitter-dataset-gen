
class ScraperState:

    def __init__(self, origin_user, users=None, edges=None):
        self.origin_user = origin_user
        self.users = users
        self.edges = edges
        self.users_to_persist = []
        self.edges_to_persist = []

    @staticmethod
    def load(users_path, edges_path):
        with open(users_path, 'r') as f:
            print('lmao')
        with open(edges_path, 'r') as f:
            print('lmao')
        origin_user = ''
        users = []
        edges = []
        return ScraperState(origin_user, users, edges)

    def persist(self, path):
        # save self.users_to_persist
        # save self.edges_to_persist
        self.users_to_persist = []
        self.edges_to_persist = []
