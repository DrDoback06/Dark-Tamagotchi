# tamagotchi/utils/database.py - Game save/load functionality

import json
import os

class CharacterManager:
    def __init__(self):
        self.creatures = []
        self.load_characters()

    def load_characters(self):
        data = self.load_creature_list()
        self.creatures = []
        for cdata in data:
            # We need to import Creature here to avoid circular imports
            from tamagotchi.core.creatures import Creature
            creature = Creature(chosen_type=cdata["creature_type"])
            creature.max_hp = cdata["max_hp"]
            creature.attack = cdata["attack"]
            creature.defense = cdata["defense"]
            creature.speed = cdata["speed"]
            creature.current_hp = cdata["current_hp"]
            creature.level = cdata["level"]
            creature.xp = cdata["xp"]
            creature.evolution_stage = cdata["evolution_stage"]
            creature.age = cdata["age"]
            creature.is_alive = cdata["is_alive"]
            creature.hunger = cdata.get("hunger", 0)
            creature.energy = cdata.get("energy", 100)

            # Reconstruct abilities from saved dictionaries
            from tamagotchi.core.abilities import ability_from_dict
            creature.abilities = [ability_from_dict(a_dict) for a_dict in cdata["abilities"]]
            creature.inventory = cdata.get("inventory", [])
            self.creatures.append(creature)

    def add_creature(self, creature):
        self.creatures.append(creature)
        self.save_characters()

    def delete_creature(self, creature):
        if creature in self.creatures:
            self.creatures.remove(creature)
            self.save_characters()
            print(f"[CharacterManager] Creature {creature.creature_type} deleted.")

    def save_creature_list(self, filename="data/saves/creatures.json"):
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        data = [creature.to_dict() for creature in self.creatures]
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_creature_list(self, filename="data/saves/creatures.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print("[Database] No creature data found:", e)
            return []

    def get_creature(self, index):
        if 0 <= index < len(self.creatures):
            return self.creatures[index]
        return None

    def get_all_creatures(self):
        return self.creatures

    def save_characters(self):
        self.save_creature_list()

    # ------------------------------------------
    # Tombstone functions for XP Transfer
    # ------------------------------------------
    def load_tombstones(self, filename="data/saves/tombstones.json"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    tombstones = json.load(f)
                return tombstones
            except Exception as e:
                print("[CharacterManager] Error loading tombstones:", e)
                return []
        else:
            return []

    def save_tombstones(self, tombstones, filename="data/saves/tombstones.json"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w") as f:
            json.dump(tombstones, f, indent=4)

    def transfer_bonus_xp(self, tombstone_index, target_creature):
        """
        Transfers bonus XP from the tombstone at tombstone_index to target_creature.
        Returns True if transfer was successful; otherwise, False.
        """
        filename = "data/saves/tombstones.json"
        tombstones = self.load_tombstones(filename)
        if tombstone_index < 0 or tombstone_index >= len(tombstones):
            print("Invalid tombstone index.")
            return False

        tombstone_record = tombstones[tombstone_index]
        if tombstone_record.get("xp_transferred", False):
            print("Bonus XP already transferred.")
            return False

        bonus_xp = tombstone_record.get("bonus_xp", 0)
        if bonus_xp <= 0:
            print("No bonus XP available in tombstone.")
            return False

        target_creature.xp += bonus_xp
        print(f"Transferred {bonus_xp} bonus XP to {target_creature.creature_type}.")
        tombstone_record["xp_transferred"] = True
        self.save_tombstones(tombstones, filename)

        # Check if target creature now levels up
        from tamagotchi.utils.config import XP_MULTIPLIER
        xp_threshold = target_creature.level * XP_MULTIPLIER
        if target_creature.xp >= xp_threshold:
            target_creature.level_up()
        return True


def save_dead_creature(creature):
    """Helper function to save a dead creature to the graveyard"""
    filename = "data/saves/dead_creatures.json"

    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    creature_data = creature.to_dict()

    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(creature_data)

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)