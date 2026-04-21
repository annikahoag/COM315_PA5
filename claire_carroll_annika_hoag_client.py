
import json
import socket
import sys
import time

from strategy import decide


def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <host> <port> <name>")
        sys.exit(1)

    host, port, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.sendall(f"JOIN {name}\n".encode())


    # Read the WELCOME response and parse the JSON.
    welcome_response = sock.recv(1024).decode()
    # print("Initial welcome response: ", welcome_response.decode())

    data = json.loads(welcome_response.split(" ", 1)[1])
    id = data["id"]
    position = data["pos"]
    map = data["map"]
    walls = data["walls"]

    # In a loop, read data from the socket and process messages.
    while True:

        game_state = b''
        gs_data = ''
        while b'\n' not in game_state:
            game_state = game_state + sock.recv(1024)

        message = game_state.decode().strip()

        if message.startswith("GAMESTATE"):
            gs_data = json.loads(message.split(" ", 1)[1])

            sock.sendall(b"PLAYERS\n")

            command = decide(gs_data)
            if command:
                sock.sendall((command + "\n").encode())

        elif message.startswith("PLAYERS"):
        #Cyberattack meant to remove fog of war
        #We now have knowledge of all known players and could potentially add to stragety
        #Possibly further use cases include: Going after leaderboard "ruler", going after players with less hp,
        #and avoid players nearby
            try:
                all_players = json.loads(message.split(" ", 1)[1])
                print("KNOWN PLAYERS:", len(all_players), "players", all_players)
                if isinstance(gs_data, dict):
                    gs_data["players"] = [p for p in all_players if p.get("id") != id]
                    command = decide(gs_data)
                    if command:
                        sock.sendall((command + "\n").encode())
            except (json.JSONDecodeError, IndexError):
                pass

        elif message.startswith("HIT"):
            print("Hit : ", message)
        elif message.startswith("DEATH"):
            print("Died: ", message)
        elif message.startswith("KILL"):
            print("Killed: ", message)
        elif message.startswith("RESPAWN"):
            print("Respawned: ", message)
        elif message.startswith("ERROR"):
            print("ERROR: ", message)
        elif message.startswith("CHAT"):
            print("You have a new chat!")
        elif message.startswith("HP"):
            print("HP: ", message)
        elif message.startswith("HEALTH"):
            print("Health: ", message)
        elif message.startswith("SCORE"):
            print("Score: ", message)
        else:
            print("ELSE: ", message)

    sock.close()


if __name__ == "__main__":
    main()
