import os
import json
import asyncio
import uuid
from datetime import date
from concurrent.futures import ThreadPoolExecutor

from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool

# IMPORTANT
from google.genai import types

from mcp_tools.file_reader import read_uploaded_file

session_service = InMemorySessionService()


async def create_deadline_agent_async():
    """
    Create ADK agent using local FunctionTool only.
    No MCP server required.
    """

    system_instruction = f"""
You are a Student Deadline Tracker Agent.

Today's date is: {date.today().isoformat()}.

If the user provides a file path,
use the read_uploaded_file tool.

Extract all deadlines.

For each event return:

1. event_name
2. event_type
3. deadline_date
4. raw_date_text

event_type must be exactly one of:

- Assignment
- Exam
- Scholarship
- Fee Payment
- Project
- Other

Convert dates to YYYY-MM-DD.

Resolve relative dates like:
- tomorrow
- next Monday
- next week

Output ONLY valid JSON.

Example:

[
  {{
    "event_name": "Physics Exam",
    "event_type": "Exam",
    "deadline_date": "2026-07-10",
    "raw_date_text": "July 10"
  }}
]
"""

    tools = [
        FunctionTool(read_uploaded_file)
    ]

    agent = Agent(
        name="deadline_tracker_agent",
        model="gemini-2.5-flash",
        instruction=system_instruction,
        tools=tools,
    )

    return agent


async def run_deadline_agent_async(message: str):

    agent = await create_deadline_agent_async()

    runner = Runner(
        app_name="student_deadline_tracker",
        agent=agent,
        session_service=session_service,
    )

    session_id = f"session_{uuid.uuid4().hex}"

    await session_service.create_session(
        app_name="student_deadline_tracker",
        user_id="student_user",
        session_id=session_id,
    )

    # FIX FOR ADK 2.3.0
    content = types.Content(
        role="user",
        parts=[
            types.Part(text=message)
        ]
    )

    events = runner.run(
        user_id="student_user",
        session_id=session_id,
        new_message=content,
    )

    final_text = ""

    for event in events:
        try:
            if event.is_final_response():
                if event.content:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            final_text += part.text
        except Exception:
            pass

    return final_text


def run_async_helper(coro):

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        with ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()

    return loop.run_until_complete(coro)


def analyze_deadlines(input_data: str, is_file_path=False):

    if is_file_path:

        file_content = read_uploaded_file(input_data)

        prompt = f"""
Extract all deadlines from this file content:

{file_content}
"""

    else:

        prompt = f"""
Extract all deadlines from this text:

{input_data}
"""

    raw_response = run_async_helper(
        run_deadline_agent_async(prompt)
    )

    cleaned = raw_response.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        cleaned = "\n".join(lines)

    try:
        return json.loads(cleaned)

    except Exception as e:

        print("JSON Parse Error:", e)
        print("Raw Response:")
        print(raw_response)

        return []