from player import Player


class NetworkPlayer(Player):
    def __init__(self, victory_callback, player_num, server_callback):
        super().__init__(victory_callback, player_num)
        self.server_callback = server_callback