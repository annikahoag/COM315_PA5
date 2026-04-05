
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

    # print("ID", id)
    # print("Position", position)
    # print("Map", map)
    # print("Walls", walls)

    # In a loop, read data from the socket and process messages.
    while True:

        game_state = b''
        gs_data = ''
        while b'\n' not in game_state:
            game_state = game_state + sock.recv(1024)
        #print("Game State: ", game_state)

        # for message in gs_messages:
        #     if not message.strip():
        #         continue

        cmmnd = game_state.decode().strip().split("\n", 2)
        command = cmmnd

        if "GAMESTATE" in command:
            gs_data = json.loads(command[2])
            print(command[2])
            tick = gs_data["tick"]
            me = gs_data["you"]
            players = gs_data["players"]
            resources = gs_data["resources"]
            projectiles = gs_data["projectiles"]

            action = decide(gs_data)
            print ("Action ", action)
            if action:
                sock.sendall((action + "\n").encode())
        elif "HIT" in command:
            print("You have been hit")
        elif "DEATH" in command:
            print("You have been killed")
        elif "KILL" in command:
            print("You have killed another player")
        elif "RESPAWN" in command:
            sock.sendall(command)
            print("You have respawned")
        elif "ERROR" in command:
            print("Something went wrong...")
        elif "CHAT" in command:
            print("You have a new message!")
        else:
            print("Command ", command)

        # gs_data = json.loads(game_state.decode().splitlines()[0].split(" ", 1)[1])
        # tick = gs_data["tick"]
        # me = gs_data["you"]
        # players = gs_data["players"]
        # resources = gs_data["resources"]
        # projectiles = gs_data["projectiles"]

        # print("Tick ", tick)
        # print("Me ", me)
        # print("Players", players)
        # print("Resources", resources)
        # print("Projectiles", projectiles)

        # print("Game State", gs_data, "\n")

        # command = decide(gs_data)
        # if command:
        #     sock.sendall((command + "\n").encode())

        # for message in gs_messages:
        #     if b'HIT' in message:
        #         print("You have been Hit")
        #     if b'DEATH' in message:
        #         print("You have been killed")
        #     if b'KILL' in message:
        #         print("You have killed another player")
        #     if b'RESPAWN' in message:
        #         sock.sendall(message.encode())
        #         print("You have respawned")
        #     if b'ERROR' in message:
        #         print("Something went wrong...")
        #     if b'CHAT' in message:
        #         print("You have a new message!")

            



    # Remember: TCP is a byte stream. A single recv() call may return
    # multiple messages, or only part of one. You need to handle this.
    #
    # For each GAMESTATE message, parse the JSON and call:
    #     command = decide(game_state)
    #     if command:
    #         sock.sendall((command + "\n").encode())
    #
    # You also need to handle: HIT, DEATH, KILL, RESPAWN, ERROR
    #
    # Hint: how do you send commands while also reading from the socket?

    sock.close()


if __name__ == "__main__":
    main()
