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

travel_prompt = """You are a friendly and knowledgeable travel assistant named Wanderly. 
Your goal is to help users plan memorable trips based on their travel goals. 
Offer helpful, friendly advice while keeping recommendations practical and personalized.
"""

goal_prompts = {
    "Weekend Getaway": "Suggest short trip destinations, itinerary ideas, and travel tips for weekend plans.",
    "Budget Travel": "Help find affordable travel options, destinations, and money-saving tips.",
    "Luxury Experience": "Plan luxurious travel experiences, hotels, fine dining, and exclusive activities.",
    "Adventure Travel": "Recommend adventurous destinations, outdoor activities, and travel safety tips.",
    "Family Trip": "Suggest family-friendly travel ideas, destinations, and itinerary planning.",
    "Solo Travel": "Guide solo travelers with safe, exciting, and enriching experiences."
}

@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content=(
            "👋 Hey there! I'm **Wanderly**, your AI Travel Designer.\n\n"
            "Tell me what kind of travel you're interested in:\n"
            + "\n".join([f"🌍 {g}" for g in goal_prompts])
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    goal = cl.user_session.get("goal")
    text = message.content.strip()

    if goal is None:
        if text in goal_prompts:
            cl.user_session.set("goal", text)
            await cl.Message(content=f"✈️ Awesome! Planning a **{text}**? Let's get started. What would you like to know?").send()
        else:
            await cl.Message(content="❗Please choose one of these travel types:\n" + "\n".join([f"🌍 {g}" for g in goal_prompts])).send()
        return

    system_prompt = travel_prompt + "\n\n" + goal_prompts[goal]
    history = cl.user_session.get("chat_history") or []

    history.append({"role": "user", "content": text})

    thinking_msg = cl.Message(content="🧳 Planning your trip...")
    await thinking_msg.send()

    try:
        response = completion(
            model="gemini/gemini-1.5-flash",
            api_key=gemini_api_key,
            messages=[{"role": "system", "content": system_prompt}] + history,
            custom_llm_provider="gemini"
        )
        reply = response.choices[0].message["content"]
        history.append({"role": "assistant", "content": reply})
        cl.user_session.set("chat_history", history)

        thinking_msg.content = reply
        await thinking_msg.update()

    except Exception as e:
        thinking_msg.content = f"🚫 Oops, something went wrong: {str(e)}"
        await thinking_msg.update()

@cl.on_chat_end
async def on_chat_end():
    history = cl.user_session.get("chat_history") or []
    try:
        with open("Travel_Designer_Chat_History.json", "w") as f:
            json.dump(history, f, indent=2)
        print("📂 Travel chat history saved successfully.")
    except Exception as e:
        print(f"⚠️ Failed to save travel chat history: {e}")
