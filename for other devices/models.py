import json

class Character:
    def __init__(self, name, race, class_type, level=1):
        self.name = name
        self.race = race
        self.class_type = class_type
        self.level = level
        self.stats = {'STR': 10, 'DEX': 10, 'CON': 10, 'INT': 10, 'WIS': 10, 'CHA': 10}
        self.hp = 10
        self.mp = 10
        self.ac = 10
        self.special_skills = []

    def to_json(self):
        return json.dumps(self.__dict__)

class Encounter:
    def __init__(self, name):
        self.name = name
        self.characters = []
        self.initiative = []

    def add_character(self, character):
        self.characters.append(character)

    def to_json(self):
        return json.dumps({'name': self.name, 'characters': [c.__dict__ for c in self.characters]})

class Enemy:
    def __init__(self, name, enemy_type, level=1, hp=10, ac=10, description=""):
        self.name = name
        self.enemy_type = enemy_type
        self.level = level
        self.hp = hp
        self.ac = ac
        self.description = description
        self.stats = {'STR': 10, 'DEX': 10, 'CON': 10, 'INT': 10, 'WIS': 10, 'CHA': 10}
        self.special_abilities = []

    def to_json(self):
        return json.dumps(self.__dict__)

class Location:
    def __init__(self, name, location_type, description="", npcs=None, points_of_interest=None):
        self.name = name
        self.location_type = location_type
        self.description = description
        self.npcs = npcs or []
        self.points_of_interest = points_of_interest or []

    def to_json(self):
        return json.dumps(self.__dict__)
