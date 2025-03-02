import os
from dotenv import load_dotenv
from mem0 import MemoryClient

# Load environment variables
load_dotenv()

def initialize_client():
    api_key = os.getenv("MEM0_API_KEY")
    if not api_key:
        raise ValueError("MEM0_API_KEY environment variable not set")
    return MemoryClient()

def add_memories(client):
    messages = [
        {"role": "user", "content": "Thinking of making a sandwich. What do you recommend?"},
        {"role": "assistant", "content": "How about adding some cheese for extra flavor?"},
        {"role": "user", "content": "Actually, I don't like cheese."},
        {"role": "assistant", "content": "I'll remember that you don't like cheese for future recommendations."}
    ]
    client.add(messages, user_id="alex")
    print("Memories added successfully!")

def retrieve_memories(client):
    query = "I'm craving some pizza. Any recommendations?"
    filters = {
        "AND": [
            {
                "user_id": "alex"
            }
        ]
    }
    results = client.search(query, version="v2", filters=filters)
    print("\nSearch Results:")
    print(results)

    print("\nAll Memories:")
    all_memories = client.get_all(version="v2", filters=filters, page=1, page_size=50)
    print(all_memories)

def main():
    try:
        client = initialize_client()
        add_memories(client)
        retrieve_memories(client)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
