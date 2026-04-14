import asyncio
import sys
import traceback
from livekit.agents import JobContext, WorkerOptions, cli
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def entrypoint(ctx: JobContext):
    print(f"--- [START] Job Received for Room: {ctx.room.name} ---")
    
    try:
        await ctx.connect()
        print("--- [SUCCESS] Agent is now in the room! ---")

        # Listen for participants
        @ctx.room.on("participant_connected")
        def on_participant_connected(participant):
            print(f"--- [EVENT] Participant joined: {participant.identity} ---")

        # Keep it alive and printing status
        count = 0
        while ctx.room.isconnected():
            await asyncio.sleep(5)
            count += 5
            print(f"--- [STILL ALIVE] Agent has been in the room for {count}s ---")

    except Exception as e:
        print(f"--- [ERROR] The agent crashed! ---")
        traceback.print_exc() # This will show the EXACT line that failed

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))