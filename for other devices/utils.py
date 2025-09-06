import random
import logging
import json

def roll_dice(sides, count=1):
    return sum(random.randint(1, sides) for _ in range(count))

def setup_logging():
    logging.basicConfig(filename='dnd_log.txt', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def log_event(event):
    logging.info(event)

def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_from_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
