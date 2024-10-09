from openai import OpenAI
import random
import json
import os 
from dotenv import load_dotenv
import math 
"""
TO_DO: Remake model to abide by DND model 
"""

# Initial Variables 
biome_list = ["Plains", "Forest", "Desert", "Savanna", "Taiga", "Swamp", "Jungle", "Mountains"]

structure_knowledge = ["lake","ocean","river","beach","house","tower","tree","cave","mountain","well"]

action_knowledge = ["break","right_click","attack","walk","run","place","craft","eat","drop","build","pick_up","take","place_in","wear"]

with open("data/food.json", 'r') as file:
    food_json = json.load(file)

with open("data/entity.json", 'r') as file: 
    entity_json = json.load(file)

with open("data/weapons.json", 'r') as file: 
    weapon_json = json.load(file)

with open("data/builds.json", 'r') as file: 
    build_json = json.load(file)

# Remember to deep copy current chunk to world chunks if the player goes to a different chunk 
current_chunk = {"Biome": "Plains", "Structures": [], "Mobs": [], "Span": []}
world_chunks = []

"""
Functions: pick_up_item, drop_item, take_damage, eat_item, place_block, walk, run, place_in, wear_armor
Inventory Schema: [{"Name":"n/a","Count":"n/a"}]
Armor Schema: {"Helmet":"n/a","Chestplate":"n/a","Leggings":"n/a","Boots":"n/a"}
Location: {"x": 0, "y": 0}
Properties: name, health, hunger, inventory, armor, location, memories 
"""
class Player:
    def __init__(self, name, health, hunger, inventory, armor, location, memories, current_chunk):
        self.name = name
        self.health = health
        self.hunger = hunger 
        self.inventory = inventory
        self.armor = armor
        self.location = location
        self.memories = memories 
        self.rotation = 0
        self.tokens = 0 
        self.chunk = current_chunk 

    # Item stuff 
    def pick_up_item(self, item_name, count):
        item = self.search_inventory(item_name)
        if len(self.inventory) == 10 or item["Count"] == 64: 
            return False
        while count > 0 or item["Count"] < 64: 
            count -= 1
            item["Count"] += 1 
        return True 
    
    def drop_item(self, item_name, count):
        item = self.search_inventory(item_name)
        if item["Count"] == count: 
            self.inventory.remove(item)
            return True 
        else:
            item["Count"] -= count
            return True 
    
    def eat_item(self, item_name):
        self.hunger += food_json[item_name]
        if self.hunger > 20: 
            self.hunger = 20 
            return
        return 
    
    def wear_armor(self, armor_name, slot):
        if slot == "Helmet":
            self.armor["Helmet"] = armor_name
            return 
        if slot == "Chestplate":
            self.armor["Chestplate"] = armor_name 
            return 
        if slot == "Leggings":
            self.armor["Leggings"] = armor_name 
            return 
        if slot == "Boots":
            self.armor["Boots"] = armor_name 
            return 
    
    # Movement 
    def rotate(self, direction):
        if direction == "left": 
            self.rotation += 0.25
        if direction == "right": 
            self.rotation -= 0.25
        if self.rotation < 0: 
            self.rotation += 2 
        if self.rotation > 2: 
            self.rotation -= 2 
    
    def walk(self, distance): 
        x_align = math.cos(self.rotation * math.pi)
        y_align = math.sin(self.rotation * math.pi)
        if x_align > 0: 
            x_align = 1 
        elif x_align < 0: 
            x_align = -1 
        if y_align > 0: 
            y_align = 1
        elif y_align < 0: 
            y_align = -1 
        self.location["x"] += x_align * distance 
        self.location["y"] += y_align * distance 
        self.lower_hunger(0.05 * distance)
    
    def run(self, distance): 
        x_align = math.cos(self.rotation * math.pi)
        y_align = math.sin(self.rotation * math.pi)
        if x_align > 0: 
            x_align = 1 
        elif x_align < 0: 
            x_align = -1 
        if y_align > 0: 
            y_align = 1
        elif y_align < 0: 
            y_align = -1 
        self.location["x"] += x_align * distance 
        self.location["y"] += y_align * distance 
        self.lower_hunger(0.1*distance)
    
    # Attack 
    def attack(self, entity, item_name):
        if abs(self.location["x"] - entity.location["x"]) < 2 and abs(self.location["y"] - entity.location["y"]) < 2: 
            entity.health -= weapon_json[item_name]
            return True 
        return False 

    # Build
    def place(self, current_chunk, thing):
        self.search_inventory(thing)["Count"] -= 1 
        if self.rotation == 0: 
            current_chunk.place(thing, {self.location["x"]+1, self.location["y"]})
            return True 
        elif self.rotation == 0.25: 
            current_chunk.place(thing, {self.location["x"]+1, self.location["y"]+1})
            return True 
        elif self.rotation == 0.5: 
            current_chunk.place(thing, {self.location["x"], self.location["y"]+1})
            return True 
        elif self.rotation == 0.75: 
            current_chunk.place(thing, {self.location["x"]-1, self.location["y"]+1})
            return True 
        elif self.rotation == 1: 
            current_chunk.place(thing, {self.location["x"]-1, self.location["y"]})
            return True 
        elif self.rotation == 1.25: 
            current_chunk.place(thing, {self.location["x"]-1, self.location["y"]-1})
            return True 
        elif self.rotation == 1.5: 
            current_chunk.place(thing, {self.location["x"], self.location["y"]-1})
            return True 
        elif self.rotation == 1.75: 
            current_chunk.place(thing, {self.location["x"]+1, self.location["y"]-1})
            return True 
        return False
    """
    Builds: {"house":[{"block":"wood","count":0},{"block":"wood","count":0}],"house":[{"block":"wood","count":0},{"block":"wood","count":0}]}
    """
    def build(self, current_chunk, thing):
        for resource in build_json[thing]:
            if self.search_inventory(resource["block"])["count"] < resource["count"]:
                return False 
            self.drop_item(resource["block"],resource["count"])
        if self.rotation == 0: 
            current_chunk.place(thing, {self.location["x"]+1, self.location["y"]})
            return True
        elif self.rotation == 0.25: 
            current_chunk.place(thing, {self.location["x"]+1, self.location["y"]+1})
            return True
        elif self.rotation == 0.5: 
            current_chunk.place(thing, {self.location["x"], self.location["y"]+1})
            return True
        elif self.rotation == 0.75: 
            current_chunk.place(thing, {self.location["x"]-1, self.location["y"]+1})
            return True
        elif self.rotation == 1: 
            current_chunk.place(thing, {self.location["x"]-1, self.location["y"]})
            return True
        elif self.rotation == 1.25: 
            current_chunk.place(thing, {self.location["x"]-1, self.location["y"]-1})
            return True
        elif self.rotation == 1.5: 
            current_chunk.place(thing, {self.location["x"], self.location["y"]-1})
            return True
        elif self.rotation == 1.75: 
            current_chunk.place(thing, {self.location["x"]+1, self.location["y"]-1}) 
            return True
    
    # For Specialty Blocks such as furnaces, crafting table
    def use_block(self, block_name, resources): 
        return 
    def search_inventory(self, item_name):
        for search_item in self.inventory: 
            if search_item["Name"] == item_name: 
                return search_item

    def use_tokens(self, amount):
        self.tokens -= amount 

    def lower_hunger(self, amount):
        self.hunger -= amount 
    
    def __str__(self):
        return f"Player {self.name} has {self.health} health and {self.hunger} hunger and inventory: {self.inventory}"

"""
Properties: Biome, Space, Span 
Space Schema: [{"Name": "n/a", "Coordinate": [0,0], "Span": [1,1]}]
"""
class Chunk: 
    def __init__(self, biome, space, span):
        self.biome = biome 
        self.space = space
        self.span = span 
    
    def place(self, thing, location): 
        self.space.append({"Name": thing["Name"], "Coordinate": location, "Span": thing["Span"]})
    
    def destroy(self, thing):
        self.space.remove(thing)
    
"""
Properties: Health, Attack, Location
"""
class Entity: 
    def __init__(self, preset, location):
        self.health = entity_json[preset]["Health"]
        self.attack = entity_json[preset]["Attack"]
        self.location = location 

"""
TO-DO: Use MRE on Windows to retrieve all the crafting recipes and convert them to my format 
Properties: 
"""
class CraftingTable: 
    def __init__(self, location):  
        self.location = location 
    def craft(self, resources): 
        return 