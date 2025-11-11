import os
import sys
from dotenv import load_dotenv
import openai

# Load .env from the current project directory (or parent if you run from elsewhere)
load_dotenv()  # looks for a .env file in cwd

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY not found in environment. Create a .env file with: OPENAI_API_KEY=your_key"
    )

openai.api_key = OPENAI_API_KEY

def get_chat_response(prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 300):
    """
    Call OpenAI Chat Completions API and return assistant content.
    """
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    # navigate response structure safely
    return resp.choices[0].message.get("content", "").strip()

def main():
    # accept prompt from CLI or ask interactively
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        try:
            prompt = input("Enter prompt for OpenAI: ").strip()
        except EOFError:
            print("No prompt provided.")
            return

    if not prompt:
        print("Prompt is empty.")
        return

    try:
        reply = get_chat_response(prompt)
        print("\n-- Assistant Reply --\n")
        print(reply)
    except Exception as e:
        print(f"API call failed: {e}")

if __name__ == "__main__":
    main()