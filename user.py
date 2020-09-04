import tweepy

class User(dict):
    def __init__(self, user):
        if isinstance(user, dict):
            self.id = user['id']
            if 'py/object' in user['attrs'].keys():
                self.attrs = user['attrs']['py/state']
            else:
                self.attrs = user['attrs']
        elif isinstance(user, User):
            super().__init__(self, id=user.id, attrs=user.attrs)
            self.id = user.id
            self.attrs = user.attrs
        elif isinstance(user, tweepy.models.User):
            super().__init__(self, id=user.id, attrs=user)
            self.id = user.id
            self.attrs = user

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, User):
            return False
        return self.id == o.id

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return object.__hash__(self.id)

    def __repr__(self) -> str:
        return str(self.id)




