import random

# excuse categories
# "bug" – Excuses for why a bug exists.
# "deadline" – Excuses for missing deadlines.
# "PR" – Excuses for pull request delays.
# "meeting" – Excuses for missing or being late to meetings.
# "deployment" – Excuses for why a deployment failed.

EXCUSES = {
    "bug": [
        "It works on my machine.",
        "We just need to restart the server.",
        "It's probably an edge case we didn't consider.",
        "Must be a caching issue :(",
        "I didn't break it, it was like that before.",

    ],
    "deadline": [
        "We've underestimated the complexity of this project",
        "Testing took longer than expected.",
        "We had some last minute requirement changes.",
        "The deadline was an appoximation.",
        "The timeline was more of a suggestion."
    ],
    "PR": [
        "I was waiting for a review.",
        "I need to refactor before merging.",
        "It was a small change, so I didn't push it yet.",
        "I'm in a merge conflict... with my own code.",
    ],
    "meeting": [
        "I was on mute the whole time, whoops.",
        "My inertnet cut out.",
        "Sorry, time zones got confusing.",
        "There was a power outage in my building."

    ],
    "deployment": [
        "It worked in my branch...",
        "There was a merge conflict we havent caught yet.",
        "Looks like a version mismatch issue.",
    ],
    "meeting_resp": {
        "late_meeting": [
            "Apologies for missing the start of the meeting. I was caught in another meeting.",
            "I apologize for the delay, I forgot to feed my pet.",
        ],
        "technical": [
            "My webcam isn't working.",
            "My wifi is cutting out right now. Sorry.",
            "Sorry, I had my microphone configured incorrectly",
            "I apologize, I had my speakers configured incorrectly so I could not hear you.",
        ],
        "clarification": [
            "Can you repeat what you just said?",
            "Sorry, could you repeat the last thing you just said.",
            "I didn’t quite catch that last part, could you elaborate?"
        ],
        "availability" : [
            "I have another meeting at that time, can we reschedule?",
            "I have a conflict at that hour, would __ (hour) be okay for everyone?"
        ]
    }
}

def generate_excuse(category: str, resp_type: str = None) -> str:
    category = category.lower()

    if category in EXCUSES:
        data = EXCUSES[category]

        if isinstance(data, dict):  # If category has subcategories
            if resp_type:
                resp_type = resp_type.lower()
                if resp_type in data:
                    return random.choice(data[resp_type])
                return f"Invalid response type. Available types: {list(data.keys())}"
            return f"The category '{category}' has subcategories: {list(data.keys())}. Please specify one."

        return random.choice(data)  # Standard categories

    return "Invalid category. Use list_categories() to see all available categories."


def add_custom_excuse(category: str, excuse: str, resp_type: str = None):
    category = category.lower()

    if category in EXCUSES:
        if isinstance(EXCUSES[category], dict):  # If it's a nested category
            if resp_type and resp_type in EXCUSES[category]:
                EXCUSES[category][resp_type].append(excuse)
            elif resp_type:
                EXCUSES[category][resp_type] = [excuse]  # Create new subcategory
            else:
                return f"'{category}' has subcategories: {list(EXCUSES[category].keys())}. Please specify one."
        else:
            EXCUSES[category].append(excuse)
    else:
        EXCUSES[category] = [excuse]


def random_excuse() -> str:
    category = random.choice(list(EXCUSES.keys()))
    return generate_excuse(category)


def list_categories() -> list:
    categories = list(EXCUSES.keys()) 
    for category in categories.copy():
        if isinstance(EXCUSES[category], dict):
            internal_keys = [f"{category} -> {key}" for key in EXCUSES[category].keys()]
            categories.extend(internal_keys)
    return categories

def help():
    help_message = """
    EXCUSE GENERATOR FOR SOFTWARE ENGINEERS
    ---------------------------------------

    Commands:

    1. generate_excuse(category: str, resp_type: str = None) -> str
       - Generates a random excuse based on the specified category.
       - Categories: "bug", "deadline", "PR", "meeting", "deployment", "meeting_resp"
       - Some categories (like "meeting_resp") have subcategories.
       - Example: generate_excuse("bug")
       - Example: generate_excuse("meeting_resp", "technical")

    2. random_excuse() -> str
       - Returns a random excuse from any category.

    3. add_custom_excuse(category: str, excuse: str, resp_type: str = None)
       - Adds a new excuse to an existing category.
       - If the category has subcategories, specify resp_type.
       - Example: add_custom_excuse("meeting_resp", "Dog unplugged my router.", "technical")

    4. list_categories() -> list
       - Returns a list of available excuse categories and subcategories.

    5. help()
       - Displays this help message.

    """
    print(help_message)