import random


def random_ending(name):
    return random.choice([
        f"Is there anything else I can do for you?",
        f"Can I assist you with something else?",
        f"Do you need help with anything else?",
        f"Let me know if there's anything else you'd like!",
        f"Is there another task I can help with?",
        f"Anything else you'd like to check?",
        f"Feel free to ask if you need anything else!",
        f"Do you have any other requests?",
        f"I'm here if you need further assistance!",
        f"Let me know if there's more I can do for you!"
    ])


def random_food_ending(name):
    return random.choice([
        f"Enjoy your meal, {name}!",
        f"Bon appétit, {name}!",
        f"Hope you like your rations, {name}!",
        f"Stay healthy, {name}!",
        f"Fuel up, {name}!",
        f"Eat well, {name}!",
        f"Take care of yourself, {name}!",
        f"Don't forget to hydrate, {name}!",
        f"Keep your energy up, {name}!",
        f"Here's to good health, {name}!",
        f"Make the most of your rations, {name}!",
        f"Stay strong, {name}!",
        f"Enjoy every bite, {name}!",
        f"Your rations are ready, {name}!",
        f"Time to eat, {name}!",
        f"Keep going, {name}!",
        f"Stay nourished, {name}!",
        f"Take a break and enjoy, {name}!",
        f"Here's to another great week, {name}!",
        f"Your health is your wealth, {name}!"
    ]) + " " + random_ending(name)
