from openai import OpenAI
import random
import json
import os 
from dotenv import load_dotenv
from pydantic import BaseModel, Field, conlist
from typing import List, Tuple
"""
TO_DO: ADD Text and create diagrams 
"""
# Env Variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initial Variables 
biome_list = ["Plains", "Forest", "Desert", "Savanna", "Taiga", "Swamp", "Jungle", "Mountains"]

object_knowledge = ["lake","ocean","river","beach","house","tower","self","tree","cave","mountain","well", "Plains_Biome", "Forest_Biome", "Desert_Biome", "Savanna_Biome", "Taiga_Biome", "Swamp_Biome", "Jungle_Biome", "Mountains_Biome", "Snowy_Tundra_Biome", "Badlands_Biome", "End_Biome", "Nether_Waste_Biome", "Warped_Forest_Biome", "Crimson_Forest_Biome"]


action_knowledge = ["break","right_click","attack","walk","run","place","craft","eat","drop","build","pick_up","take","put_in","wear"]
client = OpenAI(api_key=openai_api_key)

gptModel = "gpt-4o"

def generate_training_data(random_biome,object_knowledge,action_knowledge):
    ### Deprecated Shit ###
    """
     Generate scenario and goal details [FOR NOW NO BUILDING TASKS] 
    initial_task_completion = client.chat.completions.create(
        model=gptModel,
        messages=[
            {"role": "system", "content": f"You are an AI bot that generates a scenario that involves multiple instantaneous goals for a player in Minecraft to reach a certain goal. The scale of this goal should be fairly small. You can make it so it is just a smaller step to another harder goal if you want to. You will be given a biome to make the setting for this goal. Then generate a list of smaller goals to achieve this goal. Make sure each smaller goal is one action without any elaboration. Goal filename should be an easy to read filename for this scenario and goal. Generate only the necessary small goals to reach this larger goal. Length of \"Small_Goals\" and \"Small_Goals_File_Name\" must match. Small goals much have quantities in their name that would complete them. Return in JSON format: {{\"Biome\": biome, \"Scenario\": scenario, \"Small_Goals\": [goal0,goal1,goal2...], \"Small_Goals_File_Name\": [goal0 filename no .json, goal1 filename, goal2 filename...,\"Goal_Name\": put a filename that works for the goal]}}. Consult the internet to fact and spell check to make sure this data is accurate and realistic to minecraft's rules and world. You aren't allowed to have goals that has the player build a structure unless it is within this knowledge list: {object_knowledge}."},
            {
                "role": "user",
                "content": random_biome
            }
        ],
        response_format = {"type": "json_object"}
    )

    task_json = initial_task_completion.choices[0].message.content

    revised_task_completion = client.chat.completions.create(
        model=gptModel,
        messages=[
            {"role":"system","content":f"You are an AI bot who is an expert in Minecraft who evaluates a JSON that has a minecraft scenario, small goals for this scenario, the file names that correspond to these goals, and an overall singular goal. Edit this to be factually correct in minecraft. Also make it achievable within 30 minutes of playtime. Respond in a JSON in the same exact format. This goal can be a goal that leads as a step into a bigger goal."},
            {"role":"user","content":task_json}
        ],
        response_format = {"type":"json_object"}
    )

    task_json = revised_task_completion.choices[0].message.content
    """
    
    ### Start Game Flow 
    game_completion = client.chat.completions.create(
        model=gptModel,
        messages=[
            {"role": "system", "content": f"You are an AI bot that generates a large list of Minecraft goals that lead to killing the ender dragon. You will be given a biome where the player spawns in and return small goals that will lead this newly spawned player to defeating the enderdragon. Goal filename should be an easy to read filename for this scenario and goal. Generate only the necessary small goals to reach this larger goal. Length of \"Small_Goals\" and \"Small_Goals_File_Name\" must match. Small goals much have quantities in their name that would complete them. Make as many goals as you need. Return in JSON format: {{\"Biome\": biome, \"Scenario\": scenario, \"Small_Goals\": [goal0,goal1,goal2...], \"Small_Goals_File_Name\": [goal0 filename no .json, goal1 filename, goal2 filename...,\"Goal_Name\": put a filename that works for the goal]}}. Consult the internet to fact and spell check to make sure this data is accurate and realistic to minecraft's rules and world. You aren't allowed to have goals that has the player build a structure unless it is within this knowledge list: {object_knowledge}."},
            {
                "role": "user",
                "content": random_biome
            }
        ],
        response_format = {"type": "json_object"}
    )

    task_json = game_completion.choices[0].message.content

    # Create a directory for all this training data 
    directory = f"./training_data/{json.loads(task_json)["Goal_Name"]}"
    os.makedirs(directory)
    os.makedirs(directory + "/summary")
    with open(directory + "/summary/summary.jsonl", 'w') as file:
        file.write(json.dumps(json.loads(task_json)) + "\n\n")

    # Generate personal data to begin the loop of data generation 
    personal_completion = client.chat.completions.create(
        model=gptModel,
        messages=[
            {"role": "system", "content": f"You are an AI bot that generates data, more specifically an environment and personal variables for a Minecraft player in this JSON format: {{\"Biome\": biome, \"Environment\": [[object0, location0],[object1, location1], [object2, location2], [object3, location3]], \"Health\": health, \"Hunger\": hunger, \"Inventory\":[[item0, count], [item1, count],[item2, count],[item3, count],[item4, count],...], \"Armor\": [armor0,armor1,armor2,armor3]]}} where the environment is limited to 4 objects, inventory is limited to 10 items, and armor is limited to 4 items. The user will give a goal, and you are meant to take the perspective of a player and return these corresponding fields that **would be realistic to Minecraft in the context of this scenario for this player to pursue this goal**.\n\nThis is the player's word bank for non-singular minecraft objects: {object_knowledge}.\n\nLocations must be relative using a term: [left, right, above, below, infront, behind, upperleft, upperright, upperbackright, upperbackleft, lowerleft, lowerright, lowerbackleft, lowerbackright] and any variation given distances [close, semi-close, far, distant] (eg. close_left, far_lowerleft) which will be before the directions. You cannot use locations outside these provided word banks. Objects in environment must be in the player's visible range. They can either be any block, entity, or provided in the word bank. Make sure the names are accurate with their name ID on the internet (coal_ore, deepslate_coal_ore). The environment can only be length 4, and they must be the 4 objects the player notices the most in this scenario.\n\nFor the player’s goals to feel meaningful, the inventory and environment must be coherent and contextually relevant to motivate them to achieve this goal. For example, if a player finds themselves in a cave without a bow, they should be motivated to craft one from available resources. Do not give the player anything that would complete anything within all-goal-steps. If the player has an empty inventory slot, put the item as \"n/a\" with count 0. For empty armor slots, put the armor as \"n/a\". \n\nThe max health is 20. The max hunger is 20. The word bank is the limit of the player's knowledge and no words outside of it should be used. Only return the JSON. Your purpose is to generate realistic data for what a player in Minecraft would realistically have in a given scenario. Consult the internet to fact check to make sure this data is accurate and realistic to minecraft's rules and world. DO NOT PUT \"SELF\" IN ENVIRONMENT."},
            {
                "role": "user",
                "content": f"current goal: {json.loads(task_json)["Small_Goals"][0]}. overall larger goal: {json.loads(task_json)["Goal_Name"]}. all-goal-steps: {json.loads(task_json)["Small_Goals"]}. biome: {json.loads(task_json)["Biome"]}. scenario: {json.loads(task_json)["Scenario"]}"
            }
        ],
        response_format = {"type": "json_object"}
    )

    personal_json = personal_completion.choices[0].message.content
    memories = []

    for goal_index in range(0, len(json.loads(task_json)["Small_Goals"])):
        # Check if the mini goal has been completed 
        mini_goal_completed = False 
        while mini_goal_completed == False: 
            # Check if this index of a mini goal exists 
            mini_goal_directory = f"{directory}/{json.loads(task_json)["Small_Goals"][goal_index]}"
            if not os.path.exists(mini_goal_directory):
                os.makedirs(mini_goal_directory)
            mini_goal_index = 0
            file_path = f"{mini_goal_directory}/{json.loads(task_json)["Small_Goals"][goal_index]}_0.jsonl"
            while os.path.exists(file_path):
                file_path = f"{mini_goal_directory}/{json.loads(task_json)["Small_Goals"][goal_index]}_{mini_goal_index}.jsonl"
                mini_goal_index += 1

            # Create a local task json that just describes the scenario and goal 
            local_task_json = json.loads(json.dumps({"Biome": f"{json.loads(task_json)["Biome"]}", "Goal": f"{json.loads(task_json)["Small_Goals"][goal_index]}", "Larger_Goal": f"{json.loads(task_json)["Goal_Name"]}"}))

            # JSON to Semantic Generation
            translation_completion = client.chat.completions.create(
                model=gptModel,
                messages=[
                    {"role": "system", "content": "You are an AI bot that summarizes Minecraft related JSON data into sentences that will be fed into another AI bot to dictate what the player would do in that situation given a current step in a larger goal. \"Environment\" gives you the objects and orientation that grabbed the attention of the player in that situation. \"Inventory\" gives you the [item, count] of each inventory slot. If there is a 0 count, don't say the item exists in the inventory. Format your response like this: Player's Current Step: <The User’s current step>, Player's Overall Goal: <The larger goal>, Inventory: <The player's inventory>, Armor Slots: <The armor slots of the player>, Player Personal Data: <The variable values of their heath and hunger>, Environment: <Describe the environment in this scenario> (for environment add clear separators between different object location pairs), Biome: <current biome>. Consult the internet to fact check to make sure this data is accurate and realistic to minecraft's rules and world."},
                    {
                        "role": "user",
                        "content": f"Current Step: {local_task_json["Goal"]}. Larger Goal: {local_task_json["Larger_Goal"]}. Personal Data: {personal_json}."
                    }
                ]
            )

            translated_data = translation_completion.choices[0].message.content

            # Initial Behavior Generation 
            initial_Behavior_completion = client.chat.completions.create(
                model=gptModel,
                messages=[
                    {"role": "system", "content": f"You are an AI bot that predicts Minecraft player’s response Behavior given an overall goal, current step in that goal, personal data, environment. Come up with realistic Behavior for the player within this JSON: {{\"Behavior\":[Action, Object, Location, How],\"reasoning\": the reason you chose these}}.\n\nThis is the player's word bank for non-singular minecraft objects: {object_knowledge}. This is the player's word bank for actions: {action_knowledge}.\n\n\"Build\" means to build something within the object word bank. \"Drop\" means to drop whatever item you specify. \"pick_up\" means to pick up an item. If your inventory is full, \"pick_up\" will automatically replace the 10th slot in your inventory. \"pick_up\" and \"drop\" are the only ways to modify your inventory. If your inventory is full and you want to pick something up, you must drop an item first. \"Use\" means to use any object within the player's inventory that isn't a block. \"Place\" means to place a block. You are only in range to break, kill, right_click, or put_in if the location of <object> is \"close\" which is said in the environment. If it is \"semi-close\" or further then you can't use those actions on it and have to get closer. \"Put_in\" puts the item in your hand in <object>. For example, [\"put_in\",furnace,iron_ore] puts iron_ore into a furnace. \"Wear\" means to wear armor that is already in your inventory. \n\nMake sure the names are accurate with their name ID on the internet (coal_ore, deepslate_coal_ore). If your action is run or walk, you must make <Object> the target and the location and <Object> must exist within the environment given. \n\n<Location> is the location of the object as specified in the data you are given that you want to action on. You must use the proximity and direction where the spaces between words in proximity are separated by - and proximity and direction are separated by _ (eg. close_right, semi-close_left).\n\n<How> is whatever is in your hand during the action. For <How> you are limited to items in the inventory. If your action is \"Craft\", <How> must be a \"crafting_table\". If you aren't using an item for this action then put in \"n/a\". Your inventory only has 5 slots. Only return this JSON. Given your \"Reason\" value, consult the internet to make sure this makes sense in Minecraft and edit your answer. DO NOT USE WORDS OUTSIDE OF THE WORD BANK EXCEPT FOR EXISTING MINECRAFT ITEMS."},
                    {
                        "role": "user",
                        "content": translated_data
                    }
                ],
                response_format = {"type": "json_object"}
            )

            initial_Behavior_data = initial_Behavior_completion.choices[0].message.content
            
            # Create memory retrieval given an action, environment, and current list of memories.
            memory_retrieval_completion = client.chat.completions.create(
                model=gptModel,
                messages=[
                    {"role": "system", "content": f"You are an AI bot that picks out the most relevant Minecraft memories a player would have and puts them into a list. You will be given an action the player instinctively makes given a context. Along with this you will be given a list of possible memories to choose from. This is format of the JSON: [\"Memories\": [[Subject, Action, Object, [[thing0, location],[thing1, location],[thing2, location],[thing3, location]], How],[Subject, Action, Object, [[thing0, location],[thing1, location],[thing2, location],[thing3, location]], How], [Subject, Action, Object, [[thing0, location],[thing1, location],[thing2, location],[thing3, location]], How], [Subject, Action, Object, [[thing0, location],[thing1, location],[thing2, location],[thing3, location]], How]]. \n\nThis is the player's word bank for non-singular minecraft objects: {object_knowledge}. This is the player's word bank for actions: {action_knowledge}.\n\n<Subject> is the actor of this action which can be any minecraft entity or self. <Action> is the action that the subject does. <Object> is the object of the action the subject does. <How> is whatever is in the subject's hand during this action. If there is nothing fill in \"n/a\" for <How>.\n\nFor [thing, location] pairs <thing> is limited to the object word bank or any minecraft entity/block. The list of [thing, location] pairs can only be length 4 per memory. Copy this over from the memory that you choose for each.\n\nThe overall memories list is limited to 4 memories. Only pick memories from the list the user gives you. If there aren't enough memories, fill out each field as \"n/a\"."},
                    {
                        "role": "user",
                        "content": f"<<<User Instinctive Behavior>>>: {json.loads(initial_Behavior_data)["Behavior"]}. <<<Context>>>: {translated_data}. <<<All Memories>>>: {memories}"
                    }
                ],
                response_format = {"type": "json_object"}
            )

            memory_data = memory_retrieval_completion.choices[0].message.content

            # Translate Memory Data 
            translated_memory = client.chat.completions.create(
                model=gptModel,
                messages=[
                    {"role": "system", "content": f"You are an AI bot that translates minecraft memory JSON to normal descriptions of memories. This is format of the JSON that the user will give {{\"Memories\": [[Subject, Action, Object, [[thing0, location],[thing1, location],[thing2, location],[thing3, location]], How],[Subject, Action, Object, [[thing0, location],[thing1, location],[thing2, location],[thing3, location]], How], [Subject, Action, Object, [[thing0, location],[thing1, location],[thing2, location],[thing3, location]], How], [Subject, Action, Object, [[thing0, location],[thing1, location],[thing2, location],[thing3, location]], How]]}}. \n\nThe list in the third index is the environment of the memory at the moment such as the things that were around the player at that time. <How> is what is in <Subject>'s hand in that memory. Translate this JSON into this template: Memory 1: description of memory 1, Memory 2: description of memory 2, Memory 3: description of memory 3, Memory 4: description of memory 4"},
                    {
                        "role": "user",
                        "content": f"Memory JSON: {memory_data}"
                    }
                ]
            )

            translated_memory = translated_memory.choices[0].message.content

            # Final Behavior Generation 
            final_Behavior_completion = client.chat.completions.create(
                model=gptModel,
                messages=[
                    {"role": "system", "content": f"You are an AI bot that predicts Minecraft player’s response Behavior given an overall goal, current step in that goal, personal data, environment, and memories. Come up with realistic Behavior for the player within this JSON: {{\"Behavior\":[Action, Object, Location, How],\"reasoning\": the reason you chose these}}. Do not double bracket \"Behavior\"'s list. \n\nThis is the player's word bank for non-singular minecraft objects: {object_knowledge}. This is the player's word bank for actions: {action_knowledge}.\n\n\"Build\" means to build something within the object word bank. \"Drop\" means to drop whatever item you specify. \"pick_up\" means to pick up an item. \"pick_up\" and \"drop\" are the only ways to modify your inventory. If your inventory is full and you want to pick something up, you must drop an item first. \"Use\" means to use any object within the player's inventory that isn't a block. \"Place\" means to place a block. You are only in range to break, kill, right_click, or put_in if the location of <object> is \"close\" which is said in the environment. If it is \"semi-close\" or further then you can't use those actions on it and have to get closer. \"Put_in\" puts the item in your hand in <object>. For example, [\"put_in\",furnace,close_left,iron_ore] puts iron_ore into a furnace. \n\nMake sure the names are accurate with their name ID on the internet (coal_ore, deepslate_coal_ore). If your action is run or walk, you must make <Object> the target and the location and <Object> must exist within the environment given. \n\n<Location> is the location of the object as specified in the data you are given that you want to action on. You must use the proximity and direction where the spaces between words in proximity are separated by - and proximity and direction are separated by _ (eg. close_right, semi-close_left). \n\n<How> is whatever is in your hand during the action. For <How> you are limited to items in the inventory. If your action is \"Craft\", <How> must be a \"crafting_table\". You must have the proper number of items to \"Craft\" a given object. If you aren't using an item for this action then put in \"n/a\". Your inventory only has 5 slots. You cannot use any items that aren't in your inventory. Only return this JSON. Given your \"Reason\" value, consult the internet to make sure this makes sense in Minecraft and edit your answer. DO NOT ADD BRACKETS THAT AREN'T IN THE JSON. DO NOT USE WORDS OUTSIDE OF THE WORD BANK EXCEPT FOR EXISTING MINECRAFT ITEMS."},
                    {
                        "role": "user",
                        "content": f"Player Data: {translated_data}. Memory Data: {translated_memory}"
                    }
                ],
                response_format = {"type": "json_object"}
            )

            final_Behavior_data = final_Behavior_completion.choices[0].message.content
            print(final_Behavior_data)
            # Translate action to semantic 
            translated_action = client.chat.completions.create(
                model=gptModel,
                messages=[
                    {"role":"system","content":f"You will be given a list in this format: [Action, Object, Location, How]. This is an action a player does in the game Minecraft. Action is the action, Object is the object of the action, Location is the direction of the action, How is what item was in the player's hand. Convert this to one short and concise sentence"},
                    {"role":"user","content":f"{json.loads(final_Behavior_data)["Behavior"]}"}
                ]
            )
            translated_action = translated_action.choices[0].message.content
            
            # Update memories
            memories.append(["Self",json.loads(final_Behavior_data)["Behavior"][0],json.loads(final_Behavior_data)["Behavior"][1],json.loads(personal_json)["Environment"],json.loads(final_Behavior_data)["Behavior"][3]])

            # Environment's turn 
            environment_behavior = client.chat.completions.create(
                model=gptModel,
                messages=[
                    {"role":"system","content":f"You will be given environmental data from a Minecraft player's point of view. You must determine what actions things in the environment will do. The format environment will be given to you is this: [[thing0, location0],[thing1, location1], [thing2, location2], [thing3, location3]] from the point of view of the player. Give your response in this JSON format: {{\"Environment_Behaviors\":[[Subject, Action, Object, How], [Subject, Action, Object, How], [Subject, Action, Object, How], [Subject, Action, Object, How]]}}.\n\nThis is the word bank for actions: {action_knowledge}.\n\nEach subject will be a <thing> in the environment given by user. If the <thing> doesn't/can't do an action, replace each field that isn't Subject or environment list for that behavior with \"n/a\". Action is the action <thing> does. Object is the object of that action. If <object> is the player fill that field out with \"Player\". How is whatever is in <Subject>'s hand when they do the action. If there is nothing then fill that field with \"n/a\". For example, if there was a zombie close to the player, then you can make that zombie \"attack\" \"Player\" meaning the zombie attacks the player. Make sure all information and behavior is completely accurate to minecraft."},
                    {"role":"user","content":f"Environment: {json.loads(personal_json)["Environment"]}."}
                ],
                response_format = {"type": "json_object"}
            )
            environment_behavior = environment_behavior.choices[0].message.content

            # Update memories from environment
            for action in json.loads(environment_behavior)["Environment_Behaviors"]:
                memories.append([action[0],action[1],action[2],json.loads(personal_json)["Environment"],action[3]])

            # Update Environment after all behaviors have finished
            update_environment = client.chat.completions.create(
                model=gptModel,
                messages=[
                    {"role":"system","content":f"You will be given a previous \"environment\", its actions, biome, player's small goal, player's larger goal, and an action from a player in minecraft, and must change the \"environment\" to reflect these criteria. The environment must be given in a JSON format: {{\"Biome\": biome, \"Environment\": [[thing0, location0],[thing1, location1], [thing2, location2], [thing3, location3]]}}. The environment list must be 4 items long. Thing and location generation must be realistic to Minecraft and be within the player's field of view. These things are what are noticed most in this area to achieve the small goal to achieve the larger goal. Things can only be entities, blocks, naturally spawned minecraft structures, or anything from this list: {object_knowledge}. Update the environment that takes into account the previous environment, environment action, and the player's action. Locations must be relative using a term: [around, left, right, above, below, infront, behind, upperleft, upperright, upperbackright, upperbackleft, lowerleft, lowerright, lowerbackleft, lowerbackright] and any variation given distances [all (such as all around), close, semi-close, far, distant] (eg. close_left, far_lowerleft) which will be before the directions, and the relative locations should make sense in Minecraft. If the player walks/runs, change the environment realistically to minecraft given the location they are walking to. If something like a zombie walks towards player, change the environment to make the zombie closer. DO NOT USE WORDS OUTSIDE OF THE WORD BANK EXCEPT FOR EXISTING MINECRAFT ITEMS. DO NOT PUT \"SELF\" IN ENVIRONMENT."},
                    {"role":"user","content":f"Previous Environment: {json.loads(personal_json)["Environment"]}. Biome: {json.loads(personal_json)["Biome"]}. Environment Behavior: {environment_behavior}. Small goal: {json.loads(task_json)["Small_Goals"][goal_index]}. Larger goal: {json.loads(task_json)["Goal_Name"]}.Action: {translated_action}"}
                ],
                response_format={"type": "json_object"}
            )
            update_environment = update_environment.choices[0].message.content

            # Translate environment behavior into semantic
            translated_environment_behavior = client.chat.completions.create(
                model=gptModel,
                messages=[
                    {"role":"system","content":f"You will be given environmental data in a JSON from a Minecraft player's point of view that contains actions of the environment. You must translate this JSON to descriptive text. The formatted json will be given to you is this: {{\"Environment_Behaviors\":[[Subject, Action, Object, How], [Subject, Action, Object, How], [Subject, Action, Object, How], [Subject, Action, Object, How]]}}.\n\n<Action> is the action <Subject> does. <Object> is the object of that action. How is whatever is in <Subject>'s hand when they do the action. If there \"n/a\" in a field, it means that there is nothing to be there. Make sure to clearly separate the behaviors of each environmental Subject. If the object is \"Player\" then the Subject is targeting the player."},
                    {"role":"user","content":f"{environment_behavior}."}
                ]
            )
            
            translated_environment_behavior = translated_environment_behavior.choices[0].message.content
                
            # Update Personal Data after this event so loop can continue or break loop if goal has been completed 
            update_completion = client.chat.completions.create(
                model=gptModel,
                messages=[
                    {"role": "system", "content": f"You are an AI bot that reads a Minecraft player's previous action, their personal data, and the actions of their surroundings. Determine what the player's new inventory/possession/personal data would look like based on this data. Finally, given the current step and larger overall goal, determine whether or not the player has completed the current step with a true or false. \"Goal_Completed\" cannot be true unless the player's inventory clearly show the player has completed the current step. You must respond in this JSON format: {{\"Goal_Completed\": true/false, \"Health\": health, \"Hunger\": hunger, \"Inventory\":[[item0, count], [item1, count],[item2, count],[item3, count],[item4, count],...],\"Armor\": [helmet,chestplate,pants,boots]}}. \n\n\"Inventory\" is the player's inventory which is limited to 10 slots. Make sure to update it given the user actions or environment actions. \"Armor\" are the player's armor slots. The max health is 20. The max hunger is 20. One example: if a spider attacked the player, the player would lose some health. Another example: if the player picked up one iron ore close to them, their inventory would have one iron ore. If there is <count> 0 of an item, you must replace [item#, count] with [\"n/a\"]. If an armor slot is empty, put \"n/a\" in that slot. Never remove items in the player's inventory unless the player did the action \"drop\" or \"put_in\" on it. Never add items in the player's inventory unless the player did the action \"pick_up\" on it with an empty slot available. Consult the internet to fact check to make sure this data is accurate and realistic to minecraft's rules and world.  DO NOT ADD BRACKETS THAT AREN'T IN THE JSON."},
                    {"role": "user","content": f"<<<Long-Term Goal: {json.loads(task_json)["Goal_Name"]}>>> <<<Current Step: {json.loads(task_json)["Small_Goals"][goal_index]}>>> <<<Player Personal Data/Environment: {json.loads(personal_json)}>>> <<<Player Action: {translated_action}>>> <<<Environment Actions: {translated_environment_behavior}>>>"}
                ],
                response_format = {"type": "json_object"}
            )
            
            updated_personal_data = update_completion.choices[0].message.content

            # Verify the personal data 
            verify_personal = client.chat.completions.create(
                model=gptModel,
                messages=[
                    {"role": "system", "content": f"You are an AI bot that reads a Minecraft player's personal data. It will be given in this JSON format: {{\"Goal_Completed\": true/false, \"Health\": health, \"Hunger\": hunger, \"Inventory\":[[item0, count], [item1, count],[item2, count],[item3, count],[item4, count],...]}}. Make sure that each item in \"Inventory\" has a count larger than 0 if the item name isn't \"n/a\". If the count is 0 then convert [item,count] into [\"n/a\"]. Make the necessary edits if there are counts that say 0 and return the edited JSON. DO NOT ADD BRACKETS THAT AREN'T IN THE JSON"},
                    {"role": "user","content": updated_personal_data}
                ],
                response_format = {"type": "json_object"}
            )

            updated_personal_data = verify_personal.choices[0].message.content

            # Update everything 
            personal_json = json.dumps({"Biome": json.loads(update_environment)["Biome"], "Environment": json.loads(update_environment)["Environment"], "Health": json.loads(updated_personal_data)["Health"],"Hunger": json.loads(updated_personal_data)["Hunger"], "Inventory": json.loads(updated_personal_data)["Inventory"],"Armor": json.loads(updated_personal_data)["Armor"]})
            mini_goal_completed = json.loads(updated_personal_data)["Goal_Completed"]

            # Write everything to file 
            with open(file_path, 'w') as file:
                file.write(json.dumps(json.loads(final_Behavior_data)) + "\n\n")
                file.write(json.dumps(json.loads(personal_json)) + "\n\n")
                file.write(json.dumps(json.loads(memory_data)) + "\n\n")
                file.write(json.dumps(json.loads(environment_behavior)) + "\n\n")

for i in range(0,5):
    random_biome = random.choice(biome_list)
    generate_training_data(random_biome, object_knowledge, action_knowledge)