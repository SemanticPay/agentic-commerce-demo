import asyncio
import json
from dotenv import load_dotenv
from google.adk.agents import Agent
from prompt import ROOT_AGENT_INSTR

from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.genai import types

# Load environment variables from .env file
load_dotenv()


async def async_main(question, chat_history=None, session_id=None):
    """Executes one turn of the shopping agent with a query and full chat context."""
    semanticpay_mcp = McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="http://localhost:8000/mcp",
        )
    )

    try:
        root_agent = Agent(
            model="gemini-2.5-flash",
            name="root_agent",
            description="A shopping assistant agent",
            instruction=ROOT_AGENT_INSTR,
            tools=[
                semanticpay_mcp,
            ],
            # before_agent_callback=_load_precreated_itinerary,
        )

        user_id = session_id or "homayoon"
        app_name = "shopping-agent"
        session_service = InMemorySessionService()
        artifacts_service = InMemoryArtifactService()
        session = await session_service.create_session(
            state={}, app_name=app_name, user_id=user_id
        )

        # Build full conversation context from chat history
        full_context = ""
        if chat_history:
            for msg in chat_history:
                role_label = "user" if msg["role"] == "user" else "agent"
                full_context += f"[{role_label}]: {msg['content']}\n"

        # Add current question
        full_context += f"[user]: {question}"

        query = full_context
        print("[user]: ", question)
        print("[full context being sent]: ", query)
        content = types.Content(role="user", parts=[types.Part(text=query)])

        runner = Runner(
            app_name=app_name,
            agent=root_agent,
            artifact_service=artifacts_service,
            session_service=session_service,
        )

        events_async = runner.run_async(
            session_id=session.id, user_id=user_id, new_message=content
        )

        full_response = ""

        # Results Handling
        # print(events_async)
        async for event in events_async:
            # {'error': 'Function activities_agent is not found in the tools_dict.'}
            if not event.content:
                continue

            # print(event)
            author = event.author
            # Uncomment this to see the full event payload
            # print(f"\n[{author}]: {json.dumps(event)}")

            function_calls = [
                e.function_call for e in event.content.parts if e.function_call
            ]
            function_responses = [
                e.function_response for e in event.content.parts if e.function_response
            ]

            if event.content.parts[0].text:
                text_response = event.content.parts[0].text
                print(f"\n[{author}]: {text_response}")
                full_response += text_response

            if function_calls:
                for function_call in function_calls:
                    print(
                        f"\n[{author}]: {function_call.name}( {json.dumps(function_call.args)} )"
                    )

            items = []
            elif function_responses:
                for function_response in function_responses:
                    function_name = function_response.name
                    # Detect different payloads and handle accordingly
                    application_payload = function_response.response

                    if function_name == "search_items":
                        items = application_payload
                        
                    print(
                        f"\n[{author}]: {function_name} responds -> {application_payload}"
                    )

        print(f"\033[92m{full_response}\033[0m")
        return full_response, items
    finally:
        # Properly close the MCP connection to avoid async context issues
        await semanticpay_mcp.close()


if __name__ == "__main__":
    asyncio.run(async_main(("Find me a machine learning course")))
