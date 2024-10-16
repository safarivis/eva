import json
import re

# Set the path for the memory file
memory_file_path = r'D:\Projects\MyAssistant\eva_memories.json'

# Load memory from the file
def load_memory(file_path=memory_file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save memory to the file
def save_memory(memory, file_path=memory_file_path):
    with open(file_path, 'w') as file:
        json.dump(memory, file)

# Automatically update memory based on the user's input
def update_memory_based_on_input(user_input, file_path=memory_file_path):
    memory = load_memory(file_path)
    updated = False  # Track if memory was updated

    # Detect name input (e.g., "My name is Louis")
    name_match = re.search(r"my name is (\w+)", user_input, re.IGNORECASE)
    if name_match:
        memory["user_name"] = name_match.group(1)
        print(f"Got it! I'll remember your name is {memory['user_name']}.")
        updated = True  # Memory was updated

    # Detect preference input (e.g., "I like green")
    preference_match = re.search(r"i like (\w+)", user_input, re.IGNORECASE)
    if preference_match:
        memory["favorite_color"] = preference_match.group(1)
        print(f"Got it! I'll remember your favorite color is {memory['favorite_color']}.")
        updated = True  # Memory was updated

    # If memory was updated, save it to the file and notify the user
    if updated:
        save_memory(memory, file_path)
        print("Memory updated successfully.")

# Recall user data
def recall_user_data(key, file_path=memory_file_path):
    memory = load_memory(file_path)
    return memory.get(key, "I don't remember that yet!")

# Main conversation loop
def conversation():
    print("Hello! How can I help you today?")
    
    while True:
        user_input = input("You: ").lower()  # Convert to lowercase to make input case-insensitive

        # Automatically update memory based on the input
        update_memory_based_on_input(user_input)

        # Flexible check for name-related queries
        if "name" in user_input:
            user_name = recall_user_data("user_name")
            print(f"Your name is {user_name}.")

        # Flexible check for color-related queries
        if "color" in user_input or "favourite color" in user_input or "favorite color" in user_input:
            favorite_color = recall_user_data("favorite_color")
            print(f"Your favorite color is {favorite_color}.")

        # Break the loop when the user says "exit"
        if "exit" in user_input:
            print("Goodbye!")
            break

# Start the conversation
conversation()
