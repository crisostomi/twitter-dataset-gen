class User(dict):
    def __init__(self, id, attrs):
        super().__init__(self, id=id, attrs=attrs)
        self.id = id
        self.attrs = attrs

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, User):
            return False
        return self.id == o.id

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def __hash__(self) -> int:
        return object.__hash__(self.id)

    def __str__(self) -> str:
        return str(self.id)




