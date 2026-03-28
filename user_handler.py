import uuid
from pathlib import Path
import json

# The file that has the user's data
user_data = Path('user_data.json')

# Checks if user data exists
if not user_data.exists():
    with open(user_data, 'w') as f:
        json.dump({"users": {}}, f, indent=4)


# Loads the data
def load_data():
    try:
        with open(user_data, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"users": {}}


# Writes the data back with updates
def write_data(data):
    with open(user_data, 'w') as file:
        json.dump(data, file, indent=4)


class User:

    def __init__(self, name):
        """Internal use only — use User.get_or_create(name) instead."""
        # Checks if the name exists
        data = load_data()
        for user in data["users"].values():
            if user["name"] == name:
                raise ValueError(f"User '{name}' already exists!")

        self.name = name
        self.id = str(uuid.uuid4())
        self.xp = 0
        self.balance = 0
        self.total_trees = 0
        self.alive_trees = 0
        self.dead_trees = 0
        self.trees = {}
        self._save()

    # This is the main entry point. If it exists, gets it, or it creates it
    @classmethod
    def get(cls, name):
        data = load_data()
        for user_id, user in data["users"].items():
            if user["name"] == name:
                return cls._from_data(user_id, user)
        return cls(name)

    # Builds a user object from saved data
    @classmethod
    def _from_data(cls, user_id, user):
        obj = cls.__new__(cls)
        obj.id = user_id
        obj.name = user["name"]
        obj.xp = user["xp"]
        obj.balance = user["balance"]
        obj.total_trees = user["total_trees"]
        obj.alive_trees = user["alive_trees"]
        obj.dead_trees = user["dead_trees"]
        obj.trees = user.get("trees", {})
        return obj

    # Loads the data for that name
    @classmethod
    def load(cls, name):
        data = load_data()
        for user_id, user in data["users"].items():
            if user["name"] == name:
                return cls._from_data(user_id, user)
        raise ValueError(f"User '{name}' not found!")

    # Saves the data made
    def _save(self):
        data = load_data()
        data["users"][self.id] = {
            "name": self.name,
            "xp": self.xp,
            "balance": self.balance,
            "total_trees": self.total_trees,
            "alive_trees": self.alive_trees,
            "dead_trees": self.dead_trees,
            "trees": self.trees
        }
        write_data(data)

    # Updates the balance by an amount
    def update_balance(self, amount):
        self.balance += amount
        self._save()

    # Updates the XP
    def update_xp(self, amount):
        self.xp += amount
        self._save()

    # Add a tree
    def add_tree(self, tree):
        self.total_trees += 1
        # TODO: Updates the amount of dead or alive trees and to the individual tree section

    # Deletes the whole data
    def delete(self):
        data = load_data()
        del data["users"][self.id]
        write_data(data)

    # Resets the data
    def reset(self):
        self.xp = 0
        self.balance = 0
        self.total_trees = 0
        self.alive_trees = 0
        self.dead_trees = 0
        self.trees = {}
        self._save()

    # Gets all the usernames
    @classmethod
    def all_usernames(cls):
        data = load_data()
        return [user["name"] for user in data["users"].values()]

    # Sees if a name exists
    @classmethod
    def exists(cls, name):
        data = load_data()
        for user in data["users"].values():
            if user["name"] == name:
                return True
        return False

    # Gives it in a better form
    def __repr__(self):
        return (f"User(name={self.name}, xp={self.xp}, balance={self.balance}, total_trees={self.total_trees},"
                f" dead_trees={self.dead_trees}, alive_trees={self.alive_trees})")


lebron = User.get('LeBron')
print(User.load('LeBron'))





