import socket
import threading
import json
from models import Character, Enemy, Location
from utils import roll_dice, setup_logging, log_event

class ConsoleClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_dm = False
        self.player_number = 1
        self.character = None
        self.player_stats = {}

    def select_role(self):
        print("Select Role:")
        print("1. Player")
        print("2. DM")
        choice = input("Enter choice (1 or 2): ").strip()
        self.is_dm = choice == "2"
        self.player_number = int(input("Player Number (1-4): ").strip() or "1")
        if self.is_dm:
            self.player_stats = {}

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        threading.Thread(target=self.receive_messages).start()

    def send_message(self, message):
        self.client_socket.send(message.encode())
        log_event(f"Message sent: {message}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                print(f"Received: {message}")
            except:
                break

    def run_player(self):
        while True:
            print("\nCommands:")
            print("1. Send chat message")
            print("2. Save character")
            print("3. Roll initiative")
            print("4. Exit")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                msg = input("Enter message: ")
                self.send_message(msg)
            elif choice == "2":
                self.save_character()
            elif choice == "3":
                roll = roll_dice(20)
                msg = f"{self.character.name if self.character else f'Player {self.player_number}'} rolled a {roll} for initiative."
                print(msg)
                self.send_message(msg)
            elif choice == "4":
                break

    def run_dm(self):
        while True:
            print("\nDM Commands:")
            print("1. Send narration")
            print("2. Edit player stat")
            print("3. Create enemy")
            print("4. Create location")
            print("5. Exit")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                narration = input("Enter narration: ")
                msg = f"DM: {narration}"
                self.send_message(msg)
            elif choice == "2":
                player_name = input("Player name: ")
                stat = input("Stat (hp/mp/str/dex/con/int/wis/cha): ")
                value = input("New value: ")
                command = f"/edit_{stat} {player_name} {value}"
                self.send_message(command)
            elif choice == "3":
                name = input("Enemy name: ")
                enemy_type = input("Enemy type: ")
                level = int(input("Level: ") or "1")
                hp = int(input("HP: ") or "10")
                ac = int(input("AC: ") or "10")
                description = input("Description: ")
                enemy_data = f"ENEMY_DATA {name} {enemy_type} {level} {hp} {ac} {description.replace(' ', '_')}"
                self.send_message(enemy_data)
            elif choice == "4":
                name = input("Location name: ")
                location_type = input("Location type: ")
                description = input("Description: ")
                location_data = f"LOCATION_DATA {name} {location_type} {description.replace(' ', '_')}"
                self.send_message(location_data)
            elif choice == "5":
                break

    def save_character(self):
        name = input("Name: ")
        race = input("Race: ")
        class_type = input("Class: ")
        level = int(input("Level: ") or "1")
        hp = int(input("HP: ") or "10")
        mp = int(input("MP: ") or "10")
        stats = {}
        for stat in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
            stats[stat] = int(input(f"{stat}: ") or "10")
        special_skills = input("Special Skills (comma separated): ").split(',') if input("Special Skills (comma separated): ") else []
        self.character = Character(name, race, class_type, level)
        self.character.hp = hp
        self.character.mp = mp
        self.character.stats = stats
        self.character.special_skills = special_skills
        skills_str = ','.join(special_skills) if special_skills else ''
        stats_str = ' '.join(str(stats[s]) for s in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'])
        data = f"PLAYER_DATA {name} {race} {class_type} {level} {hp} {mp} {stats_str} {skills_str}"
        self.send_message(data)
        print("Character saved.")

    def run(self):
        setup_logging()
        self.select_role()
        self.connect()
        if self.is_dm:
            self.run_dm()
        else:
            self.run_player()

if __name__ == "__main__":
    host = input("Server IP (default localhost): ").strip() or "localhost"
    client = ConsoleClient(host=host)
    client.run()
