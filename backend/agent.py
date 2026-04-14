import asyncio
import sys
from livekit import rtc
from livekit.agents import JobContext, WorkerOptions, cli, llm
from livekit.plugins import deepgram, groq
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def entrypoint(ctx: JobContext):
    print(f"--- Agent starting for room: {ctx.room.name} ---")
    
    await ctx.connect()
    print("Agent joined. Preparing greeting...")

    # 1. Groq for text, OpenAI for voice
    # Ensure llama-3.1-8b-instant is used as it's currently active
    model = groq.LLM(model="llama-3.1-8b-instant")
    tts = deepgram.TTS(model="aura-athena-en")

    # 2. Setup audio track
    source = rtc.AudioSource(24000, 1)
    track = rtc.LocalAudioTrack.create_audio_track("agent-voice", source)
    options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE)
    await ctx.room.local_participant.publish_track(track, options)

    # 3. Handle the Stream and Speak
    try:
        chat_ctx = llm.ChatContext()
        chat_ctx.add_message(
            role="system",
            content=["You are a professional interviewer. Say 'Hi, how are you doing?' and nothing else."]
        )
        
        print("Requesting stream from Groq...")
        
        # chat() returns a stream immediately in this SDK version
        stream = model.chat(chat_ctx=chat_ctx)
        
        full_text = ""
        async for chunk in stream:
            # PROPER FIX: Modern LiveKit ChatChunk uses 'choices' as a list 
            # but Pydantic is failing on it. We'll use the .text or .delta.content safely.
            
            # Check for the most common flattened attributes first
            content = ""
            if hasattr(chunk, 'choices') and chunk.choices:
                content = chunk.choices[0].delta.content or ""
            elif hasattr(chunk, 'delta') and chunk.delta:
                content = chunk.delta.content or ""
            elif hasattr(chunk, 'text'):
                content = chunk.text or ""
            
            if content:
                full_text += content

        print(f"Final Text from Groq: {full_text}")

        # 4. Synthesize the collected text
        if full_text.strip():
            print(f"Synthesizing: {full_text}")
            async for audio_frame in tts.synthesize(text=full_text):
                await source.capture_frame(audio_frame.frame)

        print("Greeting finished.")

    except Exception as e:
        print(f"Error during execution: {e}")

    while ctx.room.isconnected():
        await asyncio.sleep(1)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))