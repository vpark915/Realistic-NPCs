from openai import OpenAI
client = OpenAI()

def generate_scenario_data(): 
    # Generate the general scenario 
    scenarios = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI that generates a list of scenarios that a minecraft villager would be in where they clearly observe, feel, and hear. These scenarios will vary with interactions with the minecraft world, a player, and entities. All scenarios should be unique and vary from bland to interesting. Generate this list in this json format: {\"scenarios\": [\"scenario1\", \"scenario2\", \"scenario3\"]}. This must be completely accurate to minecraft's available interactions and entities but make sure to mix in uncommon/rare scenarios."},
            {"role": "user", "content": "Generate 10 scenarios."}
        ],
        response_format={"type":"json_object"},
        max_tokens=4096
    )
    print(scenarios.choices[0].message.content)

    # Create the visual data for the scenario
    visual = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI that generates custom visual data lists given a minecraft villager scenario. Given the list of scenarios, generate a visual representation of the scenario in this json format: {\"visual\": [[entity/item number, [xpos, ypos, zpos]], ]. This visual data must be accurate to minecraft's available interactions and entities but make sure to mix in uncommon/rare visuals."},
            {"role": "user", "content": "Hello!"}
        ]
    )

    # print(visual.choices[0].message)

generate_scenario_data()