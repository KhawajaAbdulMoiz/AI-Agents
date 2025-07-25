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


career_prompt ="""
You are a professional career mentor with years of experience in guiding students and professionals.
Your job is to give clear,practical and supportive advice specifically tailored to the user's selected goal.
"""

goal_prompts = {
    "Resume Help": "Give tips on improving resumes.",
    "Interview Tips": "Help prepare for job interviews.",
    "Career Path Advice": "Suggest possible career paths.",
    "Cover Letter Guidance": "Provide advice on writing compelling cover letters.",
    "Job Search Strategy": "Suggest effective job-hunting strategies and platforms.",
    "LinkedIn Profile Review": "Give feedback on optimizing LinkedIn profiles.",
    "Freelancing Tips": "Share tips for starting and succeeding as a freelancer.",
    "Networking Advice": "Provide strategies for professional networking online and offline.",
    "Career Switch Planning": "Help plan a smooth transition into a new career field.",
    "Remote Work Preparation": "Guide on how to prepare for and succeed in remote jobs.",
    "Soft Skills Development": "Offer tips on improving communication, teamwork, and leadership.",
    "Salary Negotiation": "Give advice on how to negotiate salary effectively.",
}


@cl.on_chat_start
async def start():
    await cl.Message(content="👋 Hi! I'm your Career Mentor. Choose your goal:\n" + 
        "\n".join([f"- {goal}" for goal in goal_prompts])
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    goal = cl.user_session.get("goal")
    text = message.content.strip()

    if goal is None:
        if text in goal_prompts:
            cl.user_session.set("goal", text)
            await cl.Message(content=f"✅ You selected: **{text}**. Now ask me anything related!").send()
        else:
            await cl.Message(content="❗Please choose one of these goals:\n" + "\n".join([f"- {g}" for g in goal_prompts])).send()
        return

    system_prompt = career_prompt + "\n\n" + goal_prompts[goal]
    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content": text})
    msg = cl.Message(content="💬 Let me think...")
    await msg.send()

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

        msg.content = reply
        await msg.update()

    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()



@cl.on_chat_end
async def on_chat_end():
    history = cl.user_session.get("chat_history") or []
    try:
        with open("Career_Mentor_Chat_History.json", "w") as f:
            json.dump(history, f, indent=2)
        print("✅ Chat History Saved.")
    except Exception as e:
        print(f"❌ Failed to save chat history: {e}")
