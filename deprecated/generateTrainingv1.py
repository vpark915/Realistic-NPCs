from openai import OpenAI
import random
import json
import os 
from dotenv import load_dotenv
"""DEPRECATED"""
# Env Variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initial Variables 
biome_list = ["Plains", "Forest", "Desert", "Savanna", "Taiga", "Swamp", "Jungle", "Mountains", "Snowy Tundra", "Badlands", "Mushroom Fields", "End", "Nether Waste", "Warped Forest", "Crimson Forest"]

random_biome = random.choice(biome_list)

object_knowledge = ["lake","ocean","river","beach","house","tower","self","tree","cave","mountain","well", "Plains_Biome", "Forest_Biome", "Desert_Biome", "Savanna_Biome", "Taiga_Biome", "Swamp_Biome", "Jungle_Biome", "Mountains_Biome", "Snowy_Tundra_Biome", "Badlands_Biome", "End_Biome", "Nether_Waste_Biome", "Warped_Forest_Biome", "Crimson_Forest_Biome"]

action_knowledge = ["break","right_click","kill","walk","run","place","craft","eat","drop"]
client = OpenAI(api_key=openai_api_key)

# Generate scenario and goal details [FOR NOW NO BUILDING TASKS] 
initial_task_completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": f"You are an AI bot that generates a scenario that involves multiple instantaneous goals for a player in Minecraft to reach a certain goal. The scale of this goal should be fairly small. You can make it so it is just a smaller step to another harder goal if you want to. You will be given a biome to make the setting for this goal. Then generate a list of smaller goals to achieve this goal. Make sure each smaller goal is one action without any elaboration. Goal filename should be an easy to read filename for this scenario and goal. Generate as many goals as needed but length of \"Small_Goals\" and \"Small_Goals_File_Name\" must match. Return in JSON format: {{\"Scenario\": scenario, \"Small_Goals\": [goal0,goal1,goal2...], \"Small_Goals_File_Name\": [goal0 filename no .json, goal1 filename, goal2 filename...,\"Goal_Name\": put a filename that works for the goal]}}. Consult the internet to fact and spell check to make sure this data is accurate and realistic to minecraft's rules and world. You aren't allowed to have goals that has the player build a structure unless it is within this knowledge list: {object_knowledge}."},
        {
            "role": "user",
            "content": random_biome
        }
    ],
    response_format = {"type": "json_object"}
)

task_json = initial_task_completion.choices[0].message.content

revised_task_completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role":"system","content":f"You are an AI bot who is an expert in Minecraft who evaluates a JSON that has a minecraft scenario, small goals for this scenario, the file names that correspond to these goals, and an overall singular goal. Edit this to be factually correct in minecraft. Also make it achievable within 30 minutes of playtime. Respond in a JSON in the same exact format. This goal can be a goal that leads as a step into a bigger goal."},
        {"role":"user","content":task_json}
    ],
    response_format = {"type":"json_object"}
)

task_json = revised_task_completion.choices[0].message.content
print(task_json)

def generate_training_data(task_json, object_knowledge,action_knowledge):
    # Create a directory for all this training data 
    directory = f"./training_data/{json.loads(task_json)["Goal_Name"]}"
    os.makedirs(directory)
    os.makedirs(directory + "/summary")
    with open(directory + "/summary/summary.jsonl", 'w') as file:
        file.write(json.dumps(json.loads(task_json)) + "\n")

    # Generate personal data to begin the loop of data generation 
    personal_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are an AI bot that generates data, more specifically an environment and personal variables for a Minecraft player in this JSON format: {{\"Environment\": [[object0, location0],[object1, location1], [object2, location2], [object3, location3]], \"Health\": health, \"Hunger\": hunger, \"Inventory\":[[block/object0, count], [block/object1, count],[block/object2, count],[block/object3, count],[block/object4, count]]}} where the environment is limited to 5 objects and inventory is limited to 5 items. The user will give a scenario, and you are meant to take the perspective of a player and return these corresponding fields that **would be realistic to Minecraft in the context of this scenario**. Locations must be relative using a term: [left, right, above, below, infront, behind, upperleft, upperright, upperbackright, upperbackleft, lowerleft, lowerright, lowerbackleft, lowerbackright] and any variation given distances [close, semi-close, far, distant] (eg. close_left, far_lowerleft) which will be right infront of the directions, and the relative locations should make sense in Minecraft. <Objects in environment must be in the player's visible range. They can either be any block, entity, or one of these: [{object_knowledge}].> Make sure the names are accurate with their name ID on the internet (coal_ore, deepslate_coal_ore). The environment can only be length 4, and they must be the 4 objects the player notices the most in this scenario. Inventory can contain any block/tool but it must make sense in the context of the scenario given and the max length is 5. Do not give the player everything they need to complete the task. The max health is 20. The max hunger is 20. Do not use anything that isn’t provided in the word bank and only return the JSON. Your purpose is to generate realistic data for what a player in Minecraft would realistically have in a given scenario. Consult the internet to fact check to make sure this data is accurate and realistic to minecraft's rules and world."},
            {
                "role": "user",
                "content": task_json
            }
        ],
        response_format = {"type": "json_object"}
    )

    personal_json = personal_completion.choices[0].message.content

    for goal_index in range(0, len(json.loads(task_json)["Small_Goals"])):
        # Check if the mini goal has been completed 
        mini_goal_completed = False 
        while mini_goal_completed == False: 
            # Check if this index of a mini goal exists 
            mini_goal_directory = f"{directory}/{json.loads(task_json)["Small_Goals_File_Name"][goal_index]}"
            if not os.path.exists(mini_goal_directory):
                os.makedirs(mini_goal_directory)
            mini_goal_index = 0
            file_path = f"{mini_goal_directory}/{json.loads(task_json)["Small_Goals_File_Name"][goal_index]}_0.jsonl"
            while os.path.exists(file_path):
                file_path = f"{mini_goal_directory}/{json.loads(task_json)["Small_Goals_File_Name"][goal_index]}_{mini_goal_index}.jsonl"
                mini_goal_index += 1

            # Create a local task json that just describes the scenario and goal 
            local_task_json = json.dumps({"Scenario": f"{json.loads(task_json)["Scenario"]}", "Goal": f"{json.loads(task_json)["Small_Goals"][goal_index]}"})

            # Short term memory generation 
            short_term_completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are an AI bot that generates data, more specifically memories for a Minecraft player in this JSON format: {{\"short_term_memories\": [[Actor0, Action0, Object0, How0, Time0, Environment0], [Actor1, Action1, Object1, How1, Time1, Environment1], ...]}} where the number of memories is 4. The user will give a scenario, and you are meant to take the perspective of a player and return a specified array of “memory lists” that reflect **memories from last hour that got them to this situation**. There is no purpose for these memories but just what objectively happened. Fill out the memory template with words or names that would correspond to past memories that occurred before the current scenario. <For Actor, you are limited to these words: [\"self\", \"mother\",\"father\"]>. <For Action, you are limited to: {action_knowledge}>. \"Use\" means to use any object within the player's inventory that isn't a block. \"Place\" means to place a block. \"Drop\" means to drop all of object specified. <Objects in environment must be in the player's visible range. They can either be any block, entity, or one of these: [{object_knowledge}].>  Make sure the names are accurate with their name ID on the internet (coal_ore, deepslate_coal_ore). If your action is run or walk, you must make the object the target.> <For how, put the item that the actor has in their hand during this action. If there is nothing, leave this \"n/a\". If the action is craft, how must be a \"crafting_table\" if the player is within range of one>. <For time, order the events with integers>. <For environment, provide a list of objects/blocks/entities that were within the player’s senses at the time of the memory. Each environment must have exactly 4 elements in the format: [[thing0, location0],[thing1, location1], [thing2, location2], [thing3, location3]]. Things at these locations are limited to items in the object list or any minecraft mob or block.> <Locations must be relative using a term: [left, right, above, below, infront, behind, upperleft, upperright, upperbackright, upperbackleft, lowerleft, lowerright, lowerbackleft, lowerbackright] and any variation given distances [close, semi-close, far, distant] (eg. close_left, far_lowerleft) which will be right infront of the directions, and the relative locations should make sense in Minecraft>. Do not use words that weren't given within these lists. You cannot craft uncraftable items. Consult the internet to fact check to make sure this data is accurate and realistic to minecraft's rules and world."},
                    {
                        "role": "user",
                        "content": local_task_json + personal_json,
                    }
                ],
                response_format = {"type": "json_object"}
            )

            short_term_json = short_term_completion.choices[0].message.content

            # Long term memory generation 
            long_term_completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are an AI bot that generates data, more specifically memories for a Minecraft player in this JSON format: {{\"long_term_memories\": [[Actor0, Action0, Object0, How0, Time0, Environment0], [Actor1, Action1, Object1, How1, Time1, Environment1], ...]}} where the number of memories is 4. The user will give a scenario, and you are meant to take the perspective of a player and return a specified array of “memory lists” that reflect **life memories that would be retrieved to help the player achieve their goal given the scenario**. These are memories the player is accessing to complete the goal within this setting/scenario. Fill out the memory template with words or names that would correspond to past memories that occurred before the current scenario.<For Actor, you are limited to these words: [\"self\", \"mother\",\"father\"]>. <For Action, you are limited to: {action_knowledge}>. \"Use\" means to use any object within the player's inventory that isn't a block. \"Place\" means to place a block. <Objects in environment must be in the player's visible range. They can either be any block, entity, or one of these: [{object_knowledge}].> Make sure the names are accurate with their name ID on the internet (coal_ore, deepslate_coal_ore). If your action is run or walk, you must make the object the target.> <For how, put the item that the actor has in their hand during this action. If there is nothing, leave this \"n/a\". If the action is craft, how must be a \"crafting_table\" if the player is within range of one>. <For time, use these terms: [today, yesterday, a_while_ago, a_long_time_ago]>. <For environment, provide a list of objects/blocks/entities that were within the player’s senses at the time of the memory. Each environment must have exactly 4 elements in the format: [[thing0, location0],[thing1, location1], [thing2, location2], [thing3, location3]]. Things at these locations are limited to items in the object list or any minecraft mob or block.> <Locations must be relative using a term: [left, right, above, below, infront, behind, upperleft, upperright, upperbackright, upperbackleft, lowerleft, lowerright, lowerbackleft, lowerbackright] and any variation given distances [close, semi-close, far, distant] (eg. close_left, far_lowerleft) which will be right infront of the directions, and the relative locations should make sense in Minecraft>. Do not use words that weren't given within these lists. You cannot craft uncraftable items. Consult the internet to fact check to make sure this data is accurate and realistic to minecraft's rules and world."},
                    {
                        "role": "user",
                        "content": local_task_json + personal_json,
                    }
                ],
                response_format = {"type": "json_object"}
            )

            long_term_json = long_term_completion.choices[0].message.content

            # JSON to Semantic Generation
            translation_completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an AI bot that summarizes Minecraft related JSON data into sentences that will be fed into another AI bot to dictate what the player would do in that situation. “Memories” field gives the memories formatted like this: {\"memories\": [[Actor0, Action0, Object0, Time0, How0, Environment0], [Actor1, Action1, Object1, Time1, How1, Environment1], ...]} and I want you to convert that into descriptive sentences. “Environment” gives you the objects and orientation that grabbed the attention of the player in that memory and situation. Format your response like this: Player Goal: <The User’s Goal>, Scenario Summary: <A summary of the scenario>, Inventory: <The player's inventory>, Player Personal Data: <The variable values of their heath and hunger>, Environment: <Describe the environment in this scenario> (for environment add clear separators between different object location pairs), Short Term Memories: <Sentences describing the short term memories>, Long Term Memories: <Sentences describing the long term memories>. Consult the internet to fact check to make sure this data is accurate and realistic to minecraft's rules and world."},
                    {
                        "role": "user",
                        "content": local_task_json + personal_json + short_term_json + long_term_json
                    }
                ]
            )

            translated_data = translation_completion.choices[0].message.content

            # Behavior Generation 
            behavior_completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are an AI bot that generates data, more specifically on a Minecraft player’s response behavior given a scenario, goal, personal data, environment, short term memories, and long term memories. Based on whatever the player's knowledge is (long and short term memories), come up with realistic behavior for the player within this JSON: {{\"behavior\":[Action, Object, Location, How],\"reasoning\": the reason you chose these}}. <Action> is the action that the player will do, and you are limited to using these terms: {action_knowledge}. \"Drop\" means to drop whatever item you specify. \"Use\" means to use any object within the player's inventory that isn't a block. \"Place\" means to place a block. You are only in range to break, kill, or right_click if the location of that receiver is \"close\" which is said in the environment. If it is \"semi-close\" or further then you can't use those actions on it and have to get closer. <Objects in environment must be in the player's visible range. They can either be any block, entity, or one of these: [{object_knowledge}].> Make sure the names are accurate with their name ID on the internet (coal_ore, deepslate_coal_ore). If your action is run or walk, you must make \"Object\" the target. <Location> is the location of the object as specified in the data you are given that you want to action on. You must use the proximity and direction where the spaces between words in proximity are separated by - and proximity and direction are separated by _ (eg. close_right, semi-close_left). <How> is whatever is in your hand during the action, where you are limited to items in the inventory. If your action is \"Craft\", how must be a \"crafting_table\". If you aren't using an item for this action then put in \"n/a\". Your inventory only has 5 slots. Only return this JSON. Given your \"Reason\" value, consult the internet to make sure this makes sense in Minecraft and edit your answer."},
                    {
                        "role": "user",
                        "content": translated_data
                    }
                ],
                response_format = {"type": "json_object"}
            )

            behavior_data = behavior_completion.choices[0].message.content

            compiled_example = {"Environment":json.loads(personal_json)["Environment"],"Health":json.loads(personal_json)["Health"],"Hunger":json.loads(personal_json)["Hunger"],"Inventory":json.loads(personal_json)["Inventory"],"short_term_memories":json.loads(short_term_json)["short_term_memories"],"long_term_memories":json.loads(long_term_json)["long_term_memories"],"behavior":json.loads(behavior_data)["behavior"],"reasoning":json.loads(behavior_data)["reasoning"]}
            
            revision_completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role":"system","content":f"You are an AI that is an expert in Minecraft. You are evaluating a JSON that contains the environment, recent memories, life memories, and behavior/action and you must fact check, and correct it to be correct to minecraft. You will also receive the name of the file which gives the goal of this action is, along with whatever step it is on given the integer. Correct the information so it better matches the goal and desires of the player along with factual correctness. Return a JSON in an identical format to the \"current data JSON\" but with corrected information. <Action> is the action that the player will do, and you are limited to using these terms: {action_knowledge}. \"Drop\" means to drop whatever item you specify. \"Use\" means to use any object within the player's inventory that isn't a block. \"Place\" means to place a block. You are only in range to break, kill, or right_click if the location of that receiver is \"close\" which is said in the environment. If it is \"semi-close\" or further then you can't use those actions on it and have to get closer. <Objects in environment must be in the player's visible range. They can either be any block, entity, or one of these: {object_knowledge}.> Make sure the names are accurate with their name ID on the internet (coal_ore, deepslate_coal_ore). If your action is run or walk, you must make \"Object\" the target. <Location> is the location of the object as specified in the data you are given that you want to action on. You must use the proximity and direction where the spaces between words in proximity are separated by - and proximity and direction are separated by _ (eg. close_right, semi-close_left). <How> is whatever is in your hand during the action, where you are limited to items in the inventory. If your action is \"Craft\", how must be a \"crafting_table\". If you aren't using an item for this action then put in \"n/a\". Your inventory only has 5 slots. Do not add any new fields that weren't present in the \"current data JSON\"."},
                    {"role":"user","content":f"overall large goal: {json.loads(task_json)["Goal_Name"]}. small goal: {json.loads(task_json)["Small_Goals"][goal_index]}. current data JSON: {compiled_example}."}
                ],
                response_format={"type": "json_object"}
            )
            revised_data = revision_completion.choices[0].message.content
            # Write everything to file 
            with open(file_path, 'w') as file:
                file.write(json.dumps(json.loads(revised_data)) + "\n")

            # Update Personal Data after this event so loop can continue or break loop if goal has been completed 
            update_completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"You are an AI bot that reads a Minecraft player's previous situational data along with their action and what mini goal they are trying to achieve. Determine what their new situational data would look like based on whatever the current action was. Finally, given the goal in the previous situational data determine whether or not the player has completed this goal. You must respond in this JSON format: {{\"Goal_Completed\": true or false, \"Environment\": [[object0, location0],[object1, location1], [object2, location2], [object3, location3]], “Health”: health, “Hunger”: hunger, “Inventory”:[[block/object0, count], [block/object1, count],[block/object2, count],[block/object3, count],[block/object4, count]]}} where the environment is limited to 5 objects and inventory is limited to 5 items. Locations must be relative using a term: [left, right, above, below, infront, behind, upperleft, upperright, upperbackright, upperbackleft, lowerleft, lowerright, lowerbackleft, lowerbackright] and any variation given distances [close, semi-close, far, distant] (eg. close_left, far_lowerleft) which will be right infront of the directions, and the relative locations should make sense in Minecraft. For objects in environment, they can either be any block, entity, or one of these: {object_knowledge}. Make sure the names are accurate with their name ID on the internet (coal_ore, deepslate_coal_ore). The environment can only be length 4, and they must be the 4 objects the player notices the most in this scenario. Change the environment to given the previous situational data and action. When changing the environment, change it to lead the player to completing the current goal. Newly created convenient objects cannot be \"close\". <Inventory can contain any block/tool but it must be consistent in the context of the previous situational data and action given.> The max length is 5. The max health is 20. The max hunger is 20. Do not use anything that isn’t provided in the word bank and only return the JSON. Your purpose is to generate realistic data for what a player in Minecraft would realistically have in a given scenario. Consult the internet to fact check to make sure this data is accurate and realistic to minecraft's rules and world."},
                    {"role": "user","content": f"<<<previous_situational_data: {translated_data}>>> <<<current_action: {json.loads(revised_data)["behavior"]}>>>"}
                ],
                response_format = {"type": "json_object"}
            )

            updated_personal_data = update_completion.choices[0].message.content
            print("Previous Situation: " + personal_json + "\nCurrent Action: " + behavior_data + "\nNew Situation: " + updated_personal_data)

            # Update everything 
            personal_json = json.dumps({"Environment": json.loads(updated_personal_data)["Environment"], "Health": json.loads(updated_personal_data)["Health"],"Hunger": json.loads(updated_personal_data)["Hunger"], "Inventory": json.loads(updated_personal_data)["Inventory"]})
            mini_goal_completed = json.loads(updated_personal_data)["Goal_Completed"]

generate_training_data(task_json, object_knowledge, action_knowledge)