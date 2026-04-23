"""Entry point — interactive CLI for the PPT Translator Agent."""

from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# TODO (Step 0): Import `root_agent` from the agent module you will build.
# from ppt_translator.agent import root_agent

_APP = "ppt_translator"
_USER = "user"
_SESSION = "s1"


async def main() -> None:
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=_APP, user_id=_USER, session_id=_SESSION
    )

    # TODO (Step 0): Uncomment the line below once you have implemented root_agent.
    # runner = Runner(agent=root_agent, app_name=_APP, session_service=session_service)
    raise NotImplementedError("Uncomment the Runner line above after implementing root_agent.")

    print("=" * 60)
    print("  PPT Translator Agent  (Google ADK · Azure OpenAI)")
    print("=" * 60)
    print("Example: translate report.pptx to French")
    print("Type 'quit' or Ctrl-C to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Bye.")
            sys.exit(0)

        message = genai_types.Content(
            role="user", parts=[genai_types.Part(text=user_input)]
        )
        async for event in runner.run_async(
            user_id=_USER, session_id=_SESSION, new_message=message
        ):
            if event.is_final_response() and event.content:
                print(f"\nAgent: {event.content.parts[0].text}\n")


if __name__ == "__main__":
    asyncio.run(main())
