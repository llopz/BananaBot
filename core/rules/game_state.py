class GameState:

    def __init__(
        self,
        obstacle_ahead=False,
        obstacle_distance=None,
        banana=False,
        banana_distance=None,
    ):
        self.obstacle_ahead = obstacle_ahead
        self.obstacle_distance = obstacle_distance
        self.banana = banana
        self.banana_distance = banana_distance
