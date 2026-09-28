import asyncio
from fastapi import FastAPI, APIRouter
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers.default_request_handler import LegacyRequestHandler
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater, InMemoryTaskStore
from a2a.types import TaskState, Part, AgentCard, AgentProvider, AgentCapabilities, AgentSkill, AgentInterface
from a2a.helpers import new_text_message, new_task_from_user_message
from a2a.server.routes import (
    create_agent_card_routes,
    create_jsonrpc_routes,
    create_rest_routes,
)

# 1. Define the cryptographic/metadata contract (Agent Card)
local_agent_card = AgentCard(
    name="Local Intelligence Agent",
    description="An autonomous agent executing reasoning tasks via local LLM infrastructure.",
    version="1.0.0",
    provider=AgentProvider(organization="Local Labs", url="http://localhost:8000"),
    capabilities=AgentCapabilities(streaming=True, push_notifications=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[
        AgentSkill(
            id="local_reasoning",
            name="General Reasoning",
            description="Analyzes input text and generates structured insights.",
            tags=["analysis", "local", "reasoning"]
        )
    ],
    supported_interfaces=[
        AgentInterface(
            protocol_binding="JSONRPC",
            protocol_version="0.3",
            url="http://localhost:8000/a2a/"
        ),
        AgentInterface(
            url="http://localhost:8000/a2a/",
            protocol_binding="JSONRPC",
            protocol_version="1.0"
        )
    ]
)

# 2. Implement the A2A Executor Bridge
class LocalAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Manages the A2A task lifecycle, transitioning states and dispatching artifacts.
        """
        query = context.get_user_input()
        
        task = context.current_task or new_task_from_user_message(context.message)
        await event_queue.enqueue_event(task)
        
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        
        await updater.update_status(
            TaskState.working,
            new_text_message("Agent is analyzing the request locally...", task.context_id, task.id)
        )
        
        await asyncio.sleep(2.0)
        simulated_llm_response = f"Processed insight regarding: '{query}'"
        
        artifact_part = Part(text=simulated_llm_response)
        await updater.add_artifact([artifact_part], name="analysis_result")
        
        await updater.complete()

    async def cancel(self, *args, **kwargs) -> None:
        """
        Handles task cancellation requests from the orchestrator.
        """
        pass

# 3. Expose the Agent via HTTP endpoint
app = FastAPI()

# Instantiate your custom executor
executor = LocalAgentExecutor()
# Create a router for the Agent Card (mounted at root)
card_router = APIRouter()
card_router.routes.extend(create_agent_card_routes(agent_card=local_agent_card))
app.include_router(card_router)

# Wrap your executor in the standard Request Handler
# Wrap your executor in the legacy handler
#request_handler = LegacyRequestHandler(executor)
# Initialize a local store to track task states
task_store = InMemoryTaskStore()

# Wrap your executor, task store, and agent card in the Legacy Handler
request_handler = LegacyRequestHandler(
    agent_executor=executor,
    task_store=task_store,
    agent_card=local_agent_card
)

# Create a separate router for the execution endpoints (mounted with /a2a prefix)
a2a_router = APIRouter(prefix="/a2a")

# Pass the request_handler and explicitly define the rpc_url (e.g., "/")
a2a_router.routes.extend(create_jsonrpc_routes(request_handler, rpc_url="/a2a/"))
a2a_router.routes.extend(create_rest_routes(request_handler))

app.include_router(a2a_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
