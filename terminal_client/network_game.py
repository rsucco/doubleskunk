from game import Game
import socket


class NetworkGameHost(Game):
    def __init__(self, num_players=1, difficulty=3, debug=False):
        super().__init__(num_players, difficulty, debug)
        self.players = []
        self.conn, self.addr = self.get_client()
        with self.conn:
            print('Connected by', self.addr)
            while True:
                data = self.conn.recv(1024)
                if not data:
                    break
                self.conn.sendall(data)

    def get_client(self):
        HOST = '127.0.0.1'
        PORT = 64789
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            return conn, addr


class NetworkGameGuest(Game):
    def __init__(self, num_players=1, difficulty=3, debug=False, server_ip='127.0.0.1'):
        super().__init__(num_players, difficulty, debug)
        self.server_ip = server_ip
        self.players = []
        self.connect_to_server()

    def connect_to_server(self):
        PORT = 64789
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.server_ip, PORT))
            s.sendall(b'Hello, world')
            data = s.recv(1024)

        print('Received', repr(data))
