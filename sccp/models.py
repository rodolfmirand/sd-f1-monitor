class CarData:
    def __init__(self, id, name, team, front_left, front_right, rear_left, rear_right, position, timestamp):
        self.id = id
        self.name = name
        self.team = team
        self.front_left = front_left
        self.front_right = front_right
        self.rear_left = rear_left
        self.rear_right = rear_right
        self.position = position
        self.timestamp = timestamp

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return CarData(**d)