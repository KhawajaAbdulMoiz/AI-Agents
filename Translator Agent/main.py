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
    "You are a smart and friendly translation assistant. "
    "When a user gives you a sentence and the target language, simply translate it clearly and accurately. "
    "You dont need to ask questions—just translate right away based on the instruction. "
    "If the user says: 'Translate this into French: Hello, how are you?' — you respond with the French translation.\n\n"
    "If something is unclear, like no target language is given, then ask politely. "
    "Otherwise, just focus on giving quick and fluent translations."
)
        }
    ])
    await cl.Message(content="Welcome to Translator Agent. Please tell me what you want to translate and into which language.").send()

@cl.on_message
async def on_message(message: cl.Message):
    msg = cl.Message(content="Translating...")
    await msg.send()

    history = cl.user_session.get("chat history") or []
    history.append({"role": "user", "content": message.content})

    try:
        response = completion(
    model="gemini/gemini-1.5-flash",
    api_key=gemini_api_key,
    messages=history,
    custom_llm_provider="gemini"
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
    with open("Translation_chat_history.json", "w") as f:
        json.dump(history, f, indent=2)
    print("Chat History Saved.")


