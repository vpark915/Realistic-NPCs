from openai import OpenAI
import random
import json
import os 
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
"""
TO_DO: Remake model to abide by DND model 
"""
# Env Variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initial Variables 
biome_list = ["Plains", "Forest", "Desert", "Savanna", "Taiga", "Swamp", "Jungle", "Mountains"]

structure_knowledge = ["lake","ocean","river","beach","house","tower","tree","cave","mountain","well"]

action_knowledge = ["break","right_click","attack","walk","run","place","craft","eat","drop","build","pick_up","take","place_in","wear"]
client = OpenAI(api_key=openai_api_key)

gptModel = "gpt-4o"

def generate_training_data(task_json,structure_knowledge,action_knowledge):
    # Player movement 
    # Player action 
    # Update state 
    # Environment movement 
    # Envirnoment action 
    # Update state 
    print("hi")