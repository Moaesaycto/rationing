import random
from difflib import SequenceMatcher
from functions.status import generate_status
from functions.health import run_health
from functions.workout import run_workout_loop
from functions.helpers import random_ending
from functions.os import clear_console
from functions.recipes import run_recipe_loop
from functions.rations import update_rations

NAME = None
SID = None

# MAIN HANDLERS
COMMANDS = {
    "exit": {
        "triggers": [
            "quit", "exit", "end", "bye", "goodbye", "good bye", "see you later",
            "I'm leaving", "I'm done for now", "exit the program", "log me out",
            "quit the app", "shut it down", "I'm finished", "wrap this up",
            "close the session", "I'm heading off", "That'll be all", "I'm done", "no thanks",
            "terminate", "close app", "stop program", "halt", "finish up", "log out",
            "power down", "shut off", "end session", "finalize", "conclude", "cease", "no"
        ],
        "execute": lambda: random.choice([
            f"Goodbye, {NAME}",
            f"See you around, {NAME}!",
            "Be safe!",
            "Take care",
            f"Farewell, {NAME}!",
            f"Until next time, {NAME}!",
            f"Stay safe, {NAME}!",
            f"Catch you later, {NAME}!",
            f"Have a great day, {NAME}!",
            f"Peace out, {NAME}!",
            f"Adios, {NAME}!",
            f"Bye for now, {NAME}!",
            f"Take it easy, {NAME}!",
            f"Later, {NAME}!",
            f"Goodbye and good luck, {NAME}!"
        ]),
        "description": "Exit the program.",
    },
    "greet": {
        "triggers": [
            "hello", "hi", "hey", "greetings", "what's up", "howdy", "ahoy",
            "salutations", "hi there", "good morning", "good afternoon", "yo",
            "sup", "how's it going?", "nice to see you", "hey there", "g'day", "wassup",
            "good evening", "what's new?", "how are you?", "how's life?", "how's everything?",
            "how's your day?", "what's happening?", "what's good?", "what's cracking?",
            "how's it hanging?", "long time no see", "pleased to meet you", "how do you do?"
        ],
        "execute": lambda: random.choice([
            f"Hello, {NAME}!",
            f"Hi there, {NAME}!",
            f"Hey, {NAME}! How can I help?",
            f"Greetings, {NAME}!",
            f"Howdy, {NAME}!",
            f"Nice to see you, {NAME}!",
            f"Good to have you here, {NAME}!",
            f"What's up, {NAME}?",
            f"Hiya, {NAME}!",
            f"Hey there, {NAME}!"
        ]),
        "description": "Say hello to the assistant.",
    },
    "ration": {
        "triggers": [
            "rationing", "what are my rations?", "show me my rations",
            "how much food do I have?", "what do I have left to eat?",
            "check my rations", "display my rations", "how are my rations looking?",
            "what's in my ration pack?", "do I have any rations?", "view my current rations",
            "update my rations", "change my rations", "adjust my food supply",
            "add items to my rations", "remove food from my rations", "set my rations",
            "modify my ration plan", "log a new ration", "edit my food supplies",
            "alter my rations", "change what I'm eating", "record a new ration entry",
            "I need more food", "can you change my food?", "I want to see my supplies",
            "update the stuff I'm eating", "let's change my meals", "what food do I have?",
            "check food inventory", "food stock", "ration status", "food supplies",
            "current rations", "food tracker", "ration log", "food list", "ration details", "rations please",
            "sort out rations"
        ],
        "execute": lambda: update_rations(NAME),
        "description": "View your food rations.",
    },
    "recipes": {
        "triggers": [
            "get recipes", "show me recipes", "what recipes do you have?",
            "list recipes", "give me a recipe", "find a recipe", "suggest a recipe",
            "show me marinades", "list marinades", "what marinades do you have?",
            "get marinades", "give me a marinade", "find a marinade", "suggest a marinade",
            "show me sauces", "list sauces", "what sauces do you have?", "get sauces",
            "give me a sauce", "find a sauce", "suggest a sauce", "how do I cook",
            "what to cook", "what should I cook?", "any cooking ideas?",
            "suggest something to cook", "help me decide what to cook", "what can I make?",
            "give me cooking suggestions", "what's for dinner?", "what's for lunch?",
            "what's for breakfast?", "any meal ideas?", "suggest a meal",
            "what meals can I prepare?", "help me with meal planning",
            "what's a good recipe?", "show me meal options", "what can I prepare?",
            "give me a cooking idea", "help me with cooking", "suggest a dish",
            "what's a good dish to make?", "meal suggestions", "cooking help",
            "recipe ideas", "meal planning", "cooking inspiration", "dish ideas",
            "what's a quick recipe?", "easy recipes", "healthy recipes", "quick meals", "recipe"
        ],
        "execute": lambda: run_recipe_loop(NAME),
        "description": "Get cooking ideas and recipes.",
    },
    "exercise": {
        "triggers": [
            "start my workout", "show me today's workout", "exercise time",
            "let's work out", "give me my workout", "get workout plan", "workout plan",
            "begin my workout", "run workout", "show workout", "start training",
            "what's my workout?", "what should I train?", "open my workout routine",
            "start strength training", "strength session", "training time",
            "start gym routine", "exercise routine", "launch workout", "exercise plan",
            "initiate training", "workout now", "today's training", "training plan",
            "get lifting plan", "get my fitness plan", "what's my gym plan?", "open training"
        ],
        "execute": lambda: run_workout_loop(NAME),
        "description": "Start your workout or view your training plan.",
    },
    "health": {
        "triggers": [
            "health", "vitamins", "goals", "health update", "health report", "health check", "check my health", "health status", "track my health",
            "show health info", "health summary", "daily health check-in", "wellness report", "health dashboard", "get wellness summary",
            "show my supplements", "supplement list", "vitamin info", "what supplements am I taking?", "list my vitamins",
            "what vitamins do I take?", "daily vitamins", "what's my supplement stack?", "nutrition info", "supplement details",
            "weight progress", "weight update", "track my weight", "how's my weight?", "weight report", "check weight loss",
            "how much weight have I lost?", "am I making health progress?", "progress update", "weight tracking",
            "health notes", "show health notes", "any health notes?", "view health goals", "my health goals",
            "check physical health", "health insights", "update on my health", "how's my body doing?", "wellness data"

        ],
        "execute": lambda: run_health(NAME),
        "description": "Check your health data, supplements, and goals.",
    },
    "status": {
        "triggers": [
            "status", "generate status", "daily update", "show me a summary", "give me a rundown",
            "what's the update?", "report please", "system report", "how am I doing?", "how's everything?",
            "daily report", "give me my status", "show status", "status report", "overview", "status check",
            "summary", "update summary", "generate report", "daily log", "current state", "where am I at?",
            "progress report", "quick update", "update me", "where do I stand?", "give me an overview",
            "how's today looking?", "what's going on?", "show my progress", "check status", "brief me",
            "recap", "tell me my status", "any updates?", "summary report", "overall progress", "system update",
            "status rundown", "daily dashboard", "log update", "daily insights", "today's report", "what's my progress?",
            "fetch report", "overview please", "log status", "report status", "print status", "show everything",
            "how's my day?", "review my day", "where am I?", "summarise the day", "summarise everything",
            "what's going on with me?", "summarise it all", "current overview", "daily sync", "health + progress summary"
        ],
        "execute": lambda: generate_status(NAME),
        "description": "Get a summary of your health, progress, and status. This will be sent via your email.",
    },
    "clear": {
        "triggers": [
            "clear", "cls", "clear screen", "wipe screen", "erase screen", "clean screen",
            "reset screen", "refresh screen", "clear the console", "wipe the console",
            "erase the console", "clean the console", "reset the console", "refresh the console",
            "clear terminal", "wipe terminal", "erase terminal", "clean terminal",
            "reset terminal", "refresh terminal", "clear display", "wipe display",
            "erase display", "clean display", "reset display", "refresh display",
            "clear output", "wipe output", "erase output", "clean output", "reset output",
            "refresh output", "clear everything", "wipe everything", "erase everything",
            "clean everything", "reset everything", "refresh everything"
        ],
        "execute": lambda: (clear_console(), "Console cleared. " + random_ending(NAME))[-1],
        "description": "Clear the console screen.",
    },
    "help": {
        "description": "Show this help message.",
        "triggers": [
            "help", "what can you do?", "available commands", "show commands", "list commands",
            "how do I use this?", "how does this work?", "show help", "i need help",
            "command list", "show me help", "assist me", "need assistance", "what commands are there?"
        ],
        "execute": lambda: generate_help()
    },
    "default": {
        "triggers": [],
        "execute": lambda: random.choice([
            f"System error! Sorry, {NAME}, that's not available right now. Perhaps I can't help with something else?",
            f"Hmm... I'm not sure how to help with that, {NAME}. Is there anything else I can do?",
            f"Apologies, {NAME}. I didn't quite catch that. Could you try rephrasing?",
            f"Oops! I don't have the answer to that, {NAME}. Let me know if there's something else I can assist with.",
            f"I'm not sure about that, {NAME}. Maybe try asking in a different way?",
            f"Sorry, {NAME}. I couldn't process that. Is there something else you'd like help with?",
            f"Unfortunately, I don't understand that, {NAME}. Can I help with something else?",
            f"That doesn't seem to match anything I know, {NAME}. Try asking differently?",
            f"I'm sorry, {NAME}, but I can't help with that. Anything else?",
            f"Not sure what you mean, {NAME}. Let me know if there's something else."
        ])
    }
}


def generate_help(specific_command=None):
    if specific_command and specific_command in COMMANDS:
        desc = COMMANDS[specific_command]["description"]
        triggers = COMMANDS[specific_command]["triggers"]
        return f"{specific_command}: {desc}\nExamples: {', '.join(triggers[:5])}..."
    else:
        help_text = "Here are some things you can ask me to do:\n"
        for command, data in COMMANDS.items():
            if command != "default":
                help_text += f" - {command}: {data.get('description', 'No description')}\n"
        help_text += "\nType something like `help status` for more info about a specific command."
        return help_text


def init_commands(name, sid):
    global NAME, SID
    NAME = name
    SID = sid


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def get_best_command(user_input: str) -> tuple:
    user_input = user_input.strip().lower()

    if user_input.startswith("help "):
        cmd = user_input[5:].strip().lower()
        return "help", cmd

    if user_input in ["help", "commands", "show help"]:
        return "help", None

    best_match = "default"
    best_score = 0.0

    for command, data in COMMANDS.items():
        for phrase in data["triggers"]:
            score = similarity(user_input, phrase)
            if score > best_score:
                best_score = score
                best_match = command

    return (best_match if best_score > 0.6 else "default", None)


def execute_command(command_info):
    command, arg = command_info
    if command == "exit":
        return False, COMMANDS[command]["execute"]()
    elif command == "help":
        return True, generate_help(arg)
    else:
        return True, COMMANDS[command]["execute"]()
