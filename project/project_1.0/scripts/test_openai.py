from dotenv import load_dotenv
import os
import sys
import traceback

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"OPENAI_API_KEY={'SET' if api_key else 'MISSING'}")
if not api_key:
    print("Missing OPENAI_API_KEY in environment. Cannot test OpenAI.")
    sys.exit(3)

try:
    import openai
except Exception as e:
    print("The `openai` package is not installed in this environment.")
    print("Install with: pip install openai")
    sys.exit(4)

openai.api_key = api_key

try:
    print("Sending a small ChatCompletion request...")
    # Prefer the new client API if available (openai>=1.0.0)
    OpenAIClient = getattr(openai, "OpenAI", None)
    if OpenAIClient is not None:
        client = OpenAIClient()
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Respond with a single word: pong"}],
            max_tokens=10,
            temperature=0.0,
        )
        # New API returns content in: resp.choices[0].message.content
        content = resp.choices[0].message.content.strip()
    else:
        # Fallback to older API
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Respond with a single word: pong"}],
            max_tokens=10,
            temperature=0.0,
        )
        content = resp["choices"][0]["message"]["content"].strip()

    print("Response:", content)
    print("OpenAI test: SUCCESS")
    sys.exit(0)
except Exception:
    print("OpenAI test: FAILED")
    traceback.print_exc()
    sys.exit(5)
