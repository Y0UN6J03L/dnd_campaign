import tkinter as tk
from tkinter import scrolledtext, ttk
import socket
import threading
import json
import random
from models import Character, Enemy, Location
from utils import roll_dice, setup_logging, log_event

class DNDClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.root = tk.Tk()
        self.root.title("D&D Campaign Client")
        self.root.geometry("800x600")
        self.root.attributes('-alpha', 0.95)  # 50% opacity for glassy effect
        self.root.configure(bg='#F0F0F0')

        # Style configuration for glassy look
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook', background='#F0F0F0', borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#D0D0D0', foreground='black', font=('Arial', 10, 'bold'), padding=[10, 5])
        self.style.map('TNotebook.Tab', background=[('selected', '#B0B0B0')])
        self.style.configure('TButton', background='#4CAF50', foreground='white', font=('Arial', 10, 'bold'), padding=[10, 5])
        self.style.map('TButton', background=[('active', '#45A049')])
        self.style.configure('TLabel', background='#F0F0F0', foreground='black', font=('Arial', 10))
        self.style.configure('TEntry', fieldbackground='#E0E0E0', borderwidth=1, relief='solid')
        self.style.configure('TCombobox', fieldbackground='#E0E0E0', background='#E0E0E0')

        self.is_dm = False
        self.player_number = 1
        self.races = ['Human', 'Elf', 'Dwarf', 'Orc', 'Halfling', 'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling', 'Dragonborn']
        self.classes = ['Fighter', 'Wizard', 'Rogue', 'Cleric', 'Barbarian', 'Bard', 'Druid', 'Monk', 'Paladin', 'Ranger', 'Sorcerer', 'Warlock']
        self.select_role()
        if self.is_dm:
            self.player_stats = {}
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Chat Tab
        self.chat_frame = tk.Frame(self.notebook, bg='#2E2E2E')
        self.notebook.add(self.chat_frame, text='Chat')
        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, height=20, width=50, bg='#4A4A4A', fg='white', insertbackground='white', state='disabled')
        self.chat_area.pack(pady=10)
        self.message_entry = tk.Entry(self.chat_frame, width=40, bg='#4A4A4A', fg='white', insertbackground='white')
        self.message_entry.pack(pady=5)
        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.send_button.pack()

        # Character Tab
        self.char_frame = tk.Frame(self.notebook, bg='#2E2E2E')
        self.notebook.add(self.char_frame, text='Character Sheet')
        self.create_character_gui()
        self.character = None

        # Combat Tab
        self.combat_frame = tk.Frame(self.notebook, bg='#2E2E2E')
        self.notebook.add(self.combat_frame, text='Combat')
        self.create_combat_gui()

        # DM Tab
        if self.is_dm:
            self.dm_frame = tk.Frame(self.notebook, bg='#2E2E2E')
            self.notebook.add(self.dm_frame, text='DM Tools')
            self.create_dm_gui()

        # Setup logging
        setup_logging()

    def create_character_gui(self):
        # Center the content
        self.char_frame.columnconfigure(0, weight=1)
        self.char_frame.columnconfigure(1, weight=1)
        self.char_frame.rowconfigure(14, weight=1)

        # Container frame for centering
        container = tk.Frame(self.char_frame, bg='#F0F0F0')
        container.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=20, pady=20)

        # Labels and Entries
        tk.Label(container, text="Name:").grid(row=0, column=0, sticky='e', pady=5)
        self.name_entry = tk.Entry(container, bg='#E0E0E0', fg='black', insertbackground='black')
        self.name_entry.grid(row=0, column=1, sticky='ew', pady=5)

        tk.Label(container, text="Race:").grid(row=1, column=0, sticky='e', pady=5)
        self.race_combo = ttk.Combobox(container, values=self.races)
        self.race_combo.grid(row=1, column=1, sticky='ew', pady=5)

        tk.Label(container, text="Class:").grid(row=2, column=0, sticky='e', pady=5)
        self.class_combo = ttk.Combobox(container, values=self.classes)
        self.class_combo.grid(row=2, column=1, sticky='ew', pady=5)

        tk.Label(container, text="Level:").grid(row=3, column=0, sticky='e', pady=5)
        self.level_entry = tk.Entry(container, bg='#E0E0E0', fg='black', insertbackground='black')
        self.level_entry.grid(row=3, column=1, sticky='ew', pady=5)

        # HP and MP
        tk.Label(container, text="HP:").grid(row=4, column=0, sticky='e', pady=5)
        self.hp_entry = tk.Entry(container, bg='#E0E0E0', fg='black', insertbackground='black')
        self.hp_entry.grid(row=4, column=1, sticky='ew', pady=5)

        tk.Label(container, text="MP:").grid(row=5, column=0, sticky='e', pady=5)
        self.mp_entry = tk.Entry(container, bg='#E0E0E0', fg='black', insertbackground='black')
        self.mp_entry.grid(row=5, column=1, sticky='ew', pady=5)

        # Stats
        stats = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        self.stat_entries = {}
        for i, stat in enumerate(stats):
            tk.Label(container, text=f"{stat}:").grid(row=6+i, column=0, sticky='e', pady=5)
            entry = tk.Entry(container, bg='#E0E0E0', fg='black', insertbackground='black')
            entry.grid(row=6+i, column=1, sticky='ew', pady=5)
            self.stat_entries[stat] = entry

        # Special Skills
        tk.Label(container, text="Special Skills:").grid(row=12, column=0, sticky='ne', pady=5)
        self.skills_text = tk.Text(container, height=4, width=30, bg='#E0E0E0', fg='black', insertbackground='black')
        self.skills_text.grid(row=12, column=1, sticky='ew', pady=5)

        # Buttons
        button_frame = tk.Frame(container, bg='#F0F0F0')
        button_frame.grid(row=13, column=0, columnspan=2, pady=10)
        self.save_button = tk.Button(button_frame, text="Save Character", command=self.save_character, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.generate_button = tk.Button(button_frame, text="Generate Random Race/Class", command=self.generate_random, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # Display Area
        self.char_display = scrolledtext.ScrolledText(container, wrap=tk.WORD, height=10, width=40, bg='#E0E0E0', fg='black', insertbackground='black')
        self.char_display.grid(row=14, column=0, columnspan=2, sticky='nsew', pady=10)

        # Configure container for responsiveness
        container.columnconfigure(1, weight=1)
        container.rowconfigure(14, weight=1)

    def save_character(self):
        name = self.name_entry.get()
        race = self.race_combo.get()
        class_type = self.class_combo.get()
        level = int(self.level_entry.get()) if self.level_entry.get() else 1
        hp = int(self.hp_entry.get()) if self.hp_entry.get() else 10
        mp = int(self.mp_entry.get()) if self.mp_entry.get() else 10
        stats = {stat: int(entry.get()) if entry.get() else 10 for stat, entry in self.stat_entries.items()}
        special_skills = self.skills_text.get("1.0", tk.END).strip().split('\n') if self.skills_text.get("1.0", tk.END).strip() else []
        self.character = Character(name, race, class_type, level)
        self.character.hp = hp
        self.character.mp = mp
        self.character.stats = stats
        self.character.special_skills = special_skills
        self.display_character()
        # Send player data to server
        skills_str = ','.join(special_skills) if special_skills else ''
        stats_str = ' '.join(str(stats[s]) for s in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'])
        data = f"PLAYER_DATA {name} {race} {class_type} {level} {hp} {mp} {stats_str} {skills_str}"
        self.client_socket.send(data.encode())
        log_event(f"Character saved: {name}, {race}, {class_type}, Level {level}")

    def generate_random(self):
        self.race_combo.set(random.choice(self.races))
        self.class_combo.set(random.choice(self.classes))

    def display_character(self):
        if self.character:
            skills_str = '\n'.join(self.character.special_skills) if self.character.special_skills else 'None'
            info = f"Name: {self.character.name}\nRace: {self.character.race}\nClass: {self.character.class_type}\nLevel: {self.character.level}\nStats: {self.character.stats}\nSpecial Skills:\n{skills_str}"
            self.char_display.delete(1.0, tk.END)
            self.char_display.insert(tk.END, info)

    def create_combat_gui(self):
        # Basic combat GUI with initiative order and dice roll button
        tk.Label(self.combat_frame, text="Initiative Order:").pack()
        self.initiative_list = tk.Listbox(self.combat_frame, height=10, width=30)
        self.initiative_list.pack(pady=5)

        self.roll_button = tk.Button(self.combat_frame, text="Roll d20 for Initiative", command=self.roll_initiative)
        self.roll_button.pack(pady=10)

        self.combat_log = scrolledtext.ScrolledText(self.combat_frame, wrap=tk.WORD, height=10, width=50)
        self.combat_log.pack(pady=10)

    def roll_initiative(self):
        roll = roll_dice(20)
        player_name = self.character.name if self.character else f"Player {self.player_number}"
        message = f"{player_name} rolled a {roll} for initiative."
        self.combat_log.insert(tk.END, message + '\n')
        self.combat_log.see(tk.END)
        self.client_socket.send(message.encode())
        log_event(f"Initiative roll: {roll}")

    def create_dm_gui(self):
        # Configure DM frame for proper layout
        self.dm_frame.columnconfigure(0, weight=1)
        self.dm_frame.rowconfigure(0, weight=1)

        # Create a canvas and scrollbar for scrolling
        canvas = tk.Canvas(self.dm_frame, bg='#2E2E2E', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.dm_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2E2E2E')

        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def configure_canvas(event):
            canvas.itemconfig(scrollable_window, width=event.width)

        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas)

        scrollable_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # DM narration area
        tk.Label(scrollable_frame, text="DM Narration:", bg='#2E2E2E', fg='white').pack(pady=(10, 5))
        self.narration_entry = tk.Entry(scrollable_frame, width=50, bg='#4A4A4A', fg='white', insertbackground='white')
        self.narration_entry.pack(pady=5)
        self.narrate_button = tk.Button(scrollable_frame, text="Narrate", command=self.send_narration, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.narrate_button.pack(pady=5)

        # DM Edit Player Status
        tk.Label(scrollable_frame, text="Edit Player Status", bg='#2E2E2E', fg='white', font=('Arial', 12, 'bold')).pack(pady=(20, 10))
        edit_frame = tk.Frame(scrollable_frame, bg='#2E2E2E')
        edit_frame.pack(pady=5)

        tk.Label(edit_frame, text="Player Name:", bg='#2E2E2E', fg='white').grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.edit_player_entry = tk.Entry(edit_frame, bg='#4A4A4A', fg='white', insertbackground='white')
        self.edit_player_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(edit_frame, text="Stat:", bg='#2E2E2E', fg='white').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.edit_stat_combo = ttk.Combobox(edit_frame, values=['hp', 'mp', 'str', 'dex', 'con', 'int', 'wis', 'cha'])
        self.edit_stat_combo.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(edit_frame, text="New Value:", bg='#2E2E2E', fg='white').grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.edit_value_entry = tk.Entry(edit_frame, bg='#4A4A4A', fg='white', insertbackground='white')
        self.edit_value_entry.grid(row=2, column=1, padx=5, pady=2)

        self.edit_button = tk.Button(edit_frame, text="Update Status", command=self.send_edit_command, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.edit_button.grid(row=3, column=0, columnspan=2, pady=10)

        # DM tools
        self.next_turn_button = tk.Button(scrollable_frame, text="Next Turn", command=self.next_turn, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.next_turn_button.pack(pady=10)

        self.dm_log = scrolledtext.ScrolledText(scrollable_frame, wrap=tk.WORD, height=8, width=60, bg='#4A4A4A', fg='white', insertbackground='white')
        self.dm_log.pack(pady=10)

        # Player Stats Log
        tk.Label(scrollable_frame, text="Player Stats Log:", bg='#2E2E2E', fg='white').pack(pady=(10, 5))
        self.player_stats_log = scrolledtext.ScrolledText(scrollable_frame, wrap=tk.WORD, height=8, width=60, bg='#4A4A4A', fg='white', insertbackground='white')
        self.player_stats_log.pack(pady=10)

        # Enemy Creation Section
        tk.Label(scrollable_frame, text="Create Enemy:", bg='#2E2E2E', fg='white', font=('Arial', 12, 'bold')).pack(pady=(20, 10))
        enemy_frame = tk.Frame(scrollable_frame, bg='#2E2E2E')
        enemy_frame.pack(pady=5)

        tk.Label(enemy_frame, text="Name:", bg='#2E2E2E', fg='white').grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.enemy_name_entry = tk.Entry(enemy_frame, bg='#4A4A4A', fg='white', insertbackground='white')
        self.enemy_name_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(enemy_frame, text="Type:", bg='#2E2E2E', fg='white').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.enemy_type_entry = tk.Entry(enemy_frame, bg='#4A4A4A', fg='white', insertbackground='white')
        self.enemy_type_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(enemy_frame, text="Level:", bg='#2E2E2E', fg='white').grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.enemy_level_entry = tk.Entry(enemy_frame, bg='#4A4A4A', fg='white', insertbackground='white')
        self.enemy_level_entry.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(enemy_frame, text="HP:", bg='#2E2E2E', fg='white').grid(row=3, column=0, sticky='e', padx=5, pady=2)
        self.enemy_hp_entry = tk.Entry(enemy_frame, bg='#4A4A4A', fg='white', insertbackground='white')
        self.enemy_hp_entry.grid(row=3, column=1, padx=5, pady=2)

        tk.Label(enemy_frame, text="AC:", bg='#2E2E2E', fg='white').grid(row=4, column=0, sticky='e', padx=5, pady=2)
        self.enemy_ac_entry = tk.Entry(enemy_frame, bg='#4A4A4A', fg='white', insertbackground='white')
        self.enemy_ac_entry.grid(row=4, column=1, padx=5, pady=2)

        tk.Label(enemy_frame, text="Description:", bg='#2E2E2E', fg='white').grid(row=5, column=0, sticky='ne', padx=5, pady=2)
        self.enemy_desc_text = tk.Text(enemy_frame, height=3, width=30, bg='#4A4A4A', fg='white', insertbackground='white')
        self.enemy_desc_text.grid(row=5, column=1, padx=5, pady=2)

        self.create_enemy_button = tk.Button(enemy_frame, text="Create Enemy", command=self.create_enemy, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.create_enemy_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Location Creation Section
        tk.Label(scrollable_frame, text="Create Location:", bg='#2E2E2E', fg='white', font=('Arial', 12, 'bold')).pack(pady=(20, 10))
        location_frame = tk.Frame(scrollable_frame, bg='#2E2E2E')
        location_frame.pack(pady=5)

        tk.Label(location_frame, text="Name:", bg='#2E2E2E', fg='white').grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.location_name_entry = tk.Entry(location_frame, bg='#4A4A4A', fg='white', insertbackground='white')
        self.location_name_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(location_frame, text="Type:", bg='#2E2E2E', fg='white').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.location_type_entry = tk.Entry(location_frame, bg='#4A4A4A', fg='white', insertbackground='white')
        self.location_type_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(location_frame, text="Description:", bg='#2E2E2E', fg='white').grid(row=2, column=0, sticky='ne', padx=5, pady=2)
        self.location_desc_text = tk.Text(location_frame, height=3, width=30, bg='#4A4A4A', fg='white', insertbackground='white')
        self.location_desc_text.grid(row=2, column=1, padx=5, pady=2)

        self.create_location_button = tk.Button(location_frame, text="Create Location", command=self.create_location, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
        self.create_location_button.grid(row=3, column=0, columnspan=2, pady=10)

    def send_narration(self):
        narration = self.narration_entry.get()
        if narration:
            message = f"DM: {narration}"
            self.client_socket.send(message.encode())
            self.narration_entry.delete(0, tk.END)
            log_event(f"DM narration: {narration}")

    def next_turn(self):
        self.dm_log.insert(tk.END, "Next turn.\n")
        self.dm_log.see(tk.END)
        log_event("Next turn initiated")

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        threading.Thread(target=self.receive_messages).start()

    def send_message(self):
        message = self.message_entry.get()
        if message:
            # Display the message in our own chat log
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, f"You: {message}\n")
            self.chat_area.see(tk.END)
            self.chat_area.config(state='disabled')

            # Send to server
            self.client_socket.send(message.encode())
            self.message_entry.delete(0, tk.END)
            log_event(f"Message sent: {message}")

    def send_edit_command(self):
        player_name = self.edit_player_entry.get()
        stat = self.edit_stat_combo.get().lower()
        value = self.edit_value_entry.get()
        if player_name and stat and value.isdigit():
            command = f"/edit_{stat} {player_name} {value}"
            self.client_socket.send(command.encode())
            self.edit_player_entry.delete(0, tk.END)
            self.edit_stat_combo.set('')
            self.edit_value_entry.delete(0, tk.END)
            log_event(f"Sent DM edit command: {command}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                self.root.after(0, self.update_chat, message)
            except:
                break

    def update_chat(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.see(tk.END)
        self.chat_area.config(state='disabled')
        # Update HP/MP display if message contains DM update
        if message.startswith("DM updated"):
            parts = message.split()
            if len(parts) >= 5:
                player_name = parts[2].strip("'s")
                stat = parts[3]
                value = parts[5]
                if self.character and self.character.name == player_name:
                    stat_upper = stat.upper()
                    if stat == 'hp':
                        self.character.hp = int(value)
                        self.hp_entry.delete(0, tk.END)
                        self.hp_entry.insert(0, value)
                    elif stat == 'mp':
                        self.character.mp = int(value)
                        self.mp_entry.delete(0, tk.END)
                        self.mp_entry.insert(0, value)
                    elif stat_upper in self.character.stats:
                        self.character.stats[stat_upper] = int(value)
                        self.stat_entries[stat_upper].delete(0, tk.END)
                        self.stat_entries[stat_upper].insert(0, value)
                # Also update DM's player stats log automatically
                if self.is_dm and player_name in self.player_stats:
                    if stat in ['hp', 'mp']:
                        self.player_stats[player_name][stat] = value
                    elif stat_upper in self.player_stats[player_name].get('stats', {}):
                        self.player_stats[player_name]['stats'][stat_upper] = int(value)
                    # Refresh the log with updated stats
                    self.player_stats_log.delete(1.0, tk.END)
                    for name, data in self.player_stats.items():
                        skills_display = ', '.join(data.get('special_skills', [])) if data.get('special_skills') else 'None'
                        stats = data.get('stats', {})
                        stats_display = f"STR{stats.get('STR', 10)} DEX{stats.get('DEX', 10)} CON{stats.get('CON', 10)} INT{stats.get('INT', 10)} WIS{stats.get('WIS', 10)} CHA{stats.get('CHA', 10)}"
                        self.player_stats_log.insert(tk.END, f"Player: {name}, Race: {data['race']}, Class: {data['class']}, Level: {data['level']}, HP: {data['hp']}, MP: {data['mp']}, Stats: {stats_display}, Skills: {skills_display}\n")
                    self.player_stats_log.see(tk.END)
        # Update player stats log if message contains player data
        if self.is_dm and message.startswith("PLAYER_DATA"):
            parts = message.split()
            if len(parts) >= 9:
                name, race, class_type, level, hp, mp, stats_str, skills_str = parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7], ' '.join(parts[8:])
                skills = skills_str.split(',') if skills_str else []
                str_val, dex, con, int_val, wis, cha = stats_str.split()
                stats = {'STR': int(str_val), 'DEX': int(dex), 'CON': int(con), 'INT': int(int_val), 'WIS': int(wis), 'CHA': int(cha)}
                self.player_stats[name] = {'race': race, 'class': class_type, 'level': level, 'hp': hp, 'mp': mp, 'stats': stats, 'special_skills': skills}
                skills_display = ', '.join(skills) if skills else 'None'
                stats_display = f"STR{str_val} DEX{dex} CON{con} INT{int_val} WIS{wis} CHA{cha}"
                self.player_stats_log.insert(tk.END, f"Player: {name}, Race: {race}, Class: {class_type}, Level: {level}, HP: {hp}, MP: {mp}, Stats: {stats_display}, Skills: {skills_display}\n")
                self.player_stats_log.see(tk.END)

        # Handle enemy data for players
        if message.startswith("ENEMY_DATA"):
            parts = message.split()
            if len(parts) >= 6:
                name, enemy_type, level, hp, ac, description = parts[1], parts[2], parts[3], parts[4], parts[5], ' '.join(parts[6:]).replace('_', ' ')
                enemy_info = f"DM created enemy: {name} ({enemy_type}) - Level {level}, HP {hp}, AC {ac}\nDescription: {description}"
                self.chat_area.insert(tk.END, enemy_info + '\n', 'enemy')
                self.chat_area.tag_config('enemy', foreground='red', font=('Arial', 10, 'bold'))
                self.chat_area.see(tk.END)

        # Handle location data for players
        if message.startswith("LOCATION_DATA"):
            parts = message.split()
            if len(parts) >= 4:
                name, location_type, description = parts[1], parts[2], ' '.join(parts[3:]).replace('_', ' ')
                location_info = f"DM created location: {name} ({location_type})\nDescription: {description}"
                self.chat_area.insert(tk.END, location_info + '\n', 'location')
                self.chat_area.tag_config('location', foreground='blue', font=('Arial', 10, 'bold'))
                self.chat_area.see(tk.END)

    def select_role(self):
        # Create a selection window
        select_win = tk.Toplevel(self.root)
        select_win.title("Select Role")
        select_win.geometry("300x250")

        tk.Label(select_win, text="Server IP:").pack(pady=5)
        server_ip_var = tk.StringVar(value="localhost")
        server_ip_entry = tk.Entry(select_win, textvariable=server_ip_var)
        server_ip_entry.pack()

        tk.Label(select_win, text="Are you a Player or DM?").pack(pady=10)

        role_var = tk.StringVar(value="Player")
        tk.Radiobutton(select_win, text="Player", variable=role_var, value="Player").pack()
        tk.Radiobutton(select_win, text="DM", variable=role_var, value="DM").pack()

        tk.Label(select_win, text="Player Number (1-4):").pack(pady=5)
        player_num_var = tk.StringVar(value="1")
        player_num_entry = tk.Entry(select_win, textvariable=player_num_var)
        player_num_entry.pack()

        def confirm():
            self.host = server_ip_var.get()
            self.is_dm = role_var.get() == "DM"
            self.player_number = int(player_num_var.get()) if player_num_var.get().isdigit() else 1
            select_win.destroy()

        tk.Button(select_win, text="Confirm", command=confirm).pack(pady=10)

        self.root.wait_window(select_win)

    def create_enemy(self):
        name = self.enemy_name_entry.get()
        enemy_type = self.enemy_type_entry.get()
        level = int(self.enemy_level_entry.get()) if self.enemy_level_entry.get() else 1
        hp = int(self.enemy_hp_entry.get()) if self.enemy_hp_entry.get() else 10
        ac = int(self.enemy_ac_entry.get()) if self.enemy_ac_entry.get() else 10
        description = self.enemy_desc_text.get("1.0", tk.END).strip()

        enemy = Enemy(name, enemy_type, level, hp, ac, description)
        enemy_data = f"ENEMY_DATA {name} {enemy_type} {level} {hp} {ac} {description.replace(' ', '_')}"
        self.client_socket.send(enemy_data.encode())

        # Clear the form
        self.enemy_name_entry.delete(0, tk.END)
        self.enemy_type_entry.delete(0, tk.END)
        self.enemy_level_entry.delete(0, tk.END)
        self.enemy_hp_entry.delete(0, tk.END)
        self.enemy_ac_entry.delete(0, tk.END)
        self.enemy_desc_text.delete("1.0", tk.END)

        log_event(f"Enemy created: {name}, {enemy_type}, Level {level}")

    def create_location(self):
        name = self.location_name_entry.get()
        location_type = self.location_type_entry.get()
        description = self.location_desc_text.get("1.0", tk.END).strip()

        location = Location(name, location_type, description)
        location_data = f"LOCATION_DATA {name} {location_type} {description.replace(' ', '_')}"
        self.client_socket.send(location_data.encode())

        # Clear the form
        self.location_name_entry.delete(0, tk.END)
        self.location_type_entry.delete(0, tk.END)
        self.location_desc_text.delete("1.0", tk.END)

        log_event(f"Location created: {name}, {location_type}")



    def run(self):
        self.connect()
        self.root.mainloop()

if __name__ == "__main__":
    client = DNDClient()
    client.run()
