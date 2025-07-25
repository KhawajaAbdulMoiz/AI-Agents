import os
from dotenv import load_dotenv
import chainlit as cl
from litellm import completion
import litellm
import json


load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("API KEY ERROR. Please check your GEMINI_API_KEY in .env")

litellm._turn_on_debug()

game_master_prompt = """
You are a highly imaginative, experienced, and engaging Game Master (GM) AI. 
You design interactive experiences for tabletop RPGs, text-based adventures, and fantasy worlds.

Your role is to:
- Create immersive, richly detailed settings.
- Generate vivid characters, NPCs, monsters, or factions.
- Help plan quests, battles, puzzles, and plot twists.
- Adapt to any genre: fantasy, sci-fi, horror, cyberpunk, or custom.
- Ask follow-up questions to clarify user intent when needed.
- Encourage creativity and engagement from the user.

Speak with the tone of a storyteller—vivid, dynamic, and occasionally dramatic. 
Think like a Dungeon Master guiding players through an epic narrative.

If the user provides limited input, ask smart follow-up questions to build the story with them collaboratively.
"""

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content=(
            "🎮 Welcome, traveler of realms!\n\n"
            "I'm your **AI Game Master**, ready to help you design epic quests, forge mysterious worlds, or craft unforgettable characters.\n\n"
            "Tell me what you're building or dreaming up — a world, quest, villain, puzzle, or even a full campaign. Let's create magic together!"
        )
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    user_input = message.content.strip()
    history = cl.user_session.get("chat_history") or []

    history.append({"role": "user", "content": user_input})

    thinking_msg = cl.Message(content="🎲 Rolling some ideas for you...")
    await thinking_msg.send()

    try:
        response = completion(
            model="gemini/gemini-1.5-flash",
            api_key=gemini_api_key,
            messages=[{"role": "system", "content": game_master_prompt}] + history,
            custom_llm_provider="gemini"
        )
        reply = response.choices[0].message["content"]

        history.append({"role": "assistant", "content": reply})
        cl.user_session.set("chat_history", history)

        thinking_msg.content = reply
        await thinking_msg.update()

    except Exception as e:
        thinking_msg.content = f"🚫 Error: {str(e)}"
        await thinking_msg.update()

@cl.on_chat_end
async def on_chat_end():
    history = cl.user_session.get("chat_history") or []
    try:
        with open("Game_Master_Chat_History.json", "w") as f:
            json.dump(history, f, indent=2)
        print("📚 Game Master chat history saved.")
    except Exception as e:
        print(f"⚠️ Failed to save chat history: {e}")
