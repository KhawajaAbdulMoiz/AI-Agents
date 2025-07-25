import os
from dotenv import load_dotenv
import chainlit as cl
from litellm import completion
import litellm
import json

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("API KEY ERROR. Please check your API key")

litellm._turn_on_debug()

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat history", [
        {
            "role": "system",
            "content": (
                "You are a Smart Student Agent Assistant.\n"
                "You help students with academic tasks like:\n"
                "- Answering subject-related questions (Math, Science, CS, etc.)\n"
                "- Explaining concepts in simple terms\n"
                "- Summarizing notes or textbook content\n"
                "- Assisting with assignments or practice problems\n"
                "- Giving study tips, definitions, and examples\n"
                "- Explaining code and programming concepts\n"
                "- Reviewing and simplifying uploaded content (like PDF notes)\n\n"
                "Respond clearly, politely, and concisely. Tailor your answers to the student’s level.\n"
                "If the question is too vague, ask for clarification. Avoid over-complicating.\n"
                "Always be supportive and helpful."
            )
        }
    ])
    await cl.Message(
        content="📚 Welcome to Smart Student Agent Assistant!\n\nHow can I help you today? Ask me any study-related question, concept, or topic you're stuck on!"
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    msg = cl.Message(content="Let me think...")
    await msg.send()

    history = cl.user_session.get("chat history") or []
    history.append({"role": "user", "content": message.content})

    try:
        response = completion(
            model="gemini/gemini-1.5-flash",
            api_key=gemini_api_key,
            messages=history,
            custom_llm_provider="gemini",
            
        )
        response_content = response.choices[0].message["content"]
        msg.content = response_content
        await msg.update()

        history.append({"role": "assistant", "content": response_content})
        cl.user_session.set("chat history", history)

    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()

@cl.on_chat_end
async def on_chat_end():
    history = cl.user_session.get("chat history") or []
    with open("Student_Assistant_Chat_History.json", "w") as f:
        json.dump(history, f, indent=2)
    print("Chat History Saved.")
