import asyncio
import json
import uuid
from dotenv import load_dotenv
from google.adk.agents import Agent

from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.genai import types

try:
    from .base_types import AgentCallRequest, AgentCallResponse, FunctionPayload
    from .prompt import ROOT_AGENT_INSTR
except ImportError:
    from base_types import AgentCallRequest, AgentCallResponse, FunctionPayload
    from prompt import ROOT_AGENT_INSTR

# Load environment variables from .env file
load_dotenv()


async def call_agent(req: AgentCallRequest) -> AgentCallResponse:
    """Executes one turn of the shopping agent with a query and full chat context."""
    try:
        MCP_SERVER = McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="http://localhost:8000/mcp",
            )
        )

        ROOT_AGENT = Agent(
            model="gemini-2.5-flash",
            name="root_agent",
            description="A shopping assistant agent",
            instruction=ROOT_AGENT_INSTR,
            tools=[
                MCP_SERVER,
            ],
        )


        APP_NAME = "shopping-agent"
        SESSION_SERVICE = InMemorySessionService()
        ARTIFACT_SERVICE = InMemoryArtifactService()

        RUNNER = Runner(
            app_name=APP_NAME,
            agent=ROOT_AGENT,
            artifact_service=ARTIFACT_SERVICE,
            session_service=SESSION_SERVICE,
        )

        user_id = req.session_id or f"semanticpay_user-{str(uuid.uuid4())}"
        session = await SESSION_SERVICE.create_session(
            state={}, app_name=APP_NAME, user_id=user_id
        )

        # Build full conversation context from chat history
        full_context = ""
        if req.chat_history:
            for msg in req.chat_history:
                role_label = "user" if msg["role"] == "user" else "agent"
                full_context += f"[{role_label}]: {msg['content']}\n"

        # Add current question
        full_context += f"[user]: {req.question}"

        query = full_context
        print("[user]: ", req.question)
        print("[full context being sent]: ", query)
        content = types.Content(role="user", parts=[types.Part(text=query)])

        events_async = RUNNER.run_async(
            session_id=session.id, user_id=user_id, new_message=content
        )

        full_response = ""
        func_payloads = [] 

        # Results Handling
        # print(events_async)
        async for event in events_async:
            # {'error': 'Function activities_agent is not found in the tools_dict.'}
            if not event.content or not event.content or not event.content.parts:
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

            for func_call in function_calls:
                print(
                    f"\n FUNC CALLS: [{author}]: {func_call.name}( {json.dumps(func_call.args)} )"
                )
            for func_resp in function_responses:
                if func_resp.response is None:
                    print("func response is empty...")
                    continue

                func_payload = json.loads(func_resp.response["result"].content[0].text)
                print(f" FUNC RESPONSE: [{author}]: {func_resp.name} -> {func_payload}")

                func_payloads.append(FunctionPayload(
                    name=func_resp.name or "UNKNOWN",
                    payload=func_payload,
                ))
                    
        print(f"\033[92m{full_response}\033[0m")
        return AgentCallResponse(
            answer=full_response,
            function_payloads=func_payloads,
        )
    finally:
        # Properly close the MCP connection to avoid async context issues
        await MCP_SERVER.close()


if __name__ == "__main__":
    asyncio.run(call_agent(AgentCallRequest(question="i'm looking for a bag")))
