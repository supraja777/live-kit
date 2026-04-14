import asyncio
import sys
from livekit.agents import JobContext, WorkerOptions, cli, llm
from livekit.plugins import groq, silero, openai # Keeping OpenAI for TTS only
from dotenv import load_dotenv
load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def prewarm(proc):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    # Groq handles ChatContext similarly to OpenAI
    initial_ctx = llm.ChatContext().append(
        role="system",
        text="You are a helpful mock interview assistant. Focus on technical questions. Keep responses concise."
    )

    await ctx.connect()

    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        # Use Groq for ultra-fast Speech-to-Text
        stt=groq.STT(), 
        # Use Groq for ultra-fast LLM (Llama 3.3 70B is excellent for interviews)
        llm=groq.LLM(model="llama-3.3-70b-versatile"), 
        # You can use OpenAI TTS for better voice quality, or Groq's TTS for speed
        tts=openai.TTS(), 
        chat_ctx=initial_ctx,
    )

    agent.start(ctx.room)
    await agent.say("I'm ready to start the interview. What role are we practicing for today?")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))