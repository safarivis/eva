import os
from dotenv import load_dotenv
import subprocess

# Load environment variables from the .env file
load_dotenv()

# Get the OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')

if api_key is None:
    print("Error: OPENAI_API_KEY environment variable not set.")
else:
    # Run Aider with GPT-3.5 Turbo
    subprocess.run(["python", "-m", "aider", "--model", "gpt-3.5-turbo"])
