import asyncio
from a2a.client import create_client
from a2a.types import SendMessageRequest, Role
from a2a.helpers import new_text_message

async def run_client():
    # Initialize the client targeting the agent's exposed interface using the factory function
    client = await create_client("http://localhost:8000")
    
    print("Initiating A2A task delegation...")
    
    # 1. Structure the message properly using the SDK's helper utility
    # Use Role.ROLE_USER or Role.USER depending on your specific A2A version
    message_payload = new_text_message(
        "Analyze the economic impact of open standard protocols.",
        role=Role.ROLE_USER
    )

    # 2. Wrap it directly inside a SendMessageRequest object
    request_payload = SendMessageRequest(message=message_payload)

    # 3. Dispatch the wrapped request to the remote agent and stream the response
    task_id = None
    async for event in client.send_message(request_payload):
        # We only need the first event that contains the task metadata to start polling
        if hasattr(event, 'task') and event.task:
            task_id = event.task.id
            break
            
    if not task_id:
        print("Error: Could not retrieve a Task ID from the server.")
        return

    print(f"Task successfully registered on remote server. ID: {task_id}")
    
    # Poll the server until the task state machine reaches an immutable terminal state
    while True:
        task_status = await client.get_task(task_id)
        current_state = task_status.state
        
        print(f"Current Task State: {current_state}")
        
        # Terminate the polling loop if the state is COMPLETED, FAILED, CANCELED, or REJECTED
        if current_state in ["completed", "failed", "canceled", "rejected"]:
            break
            
        # Implement backoff to prevent overwhelming the server
        await asyncio.sleep(1.0)
    
    # Upon completion, extract and parse the generated artifacts
    if task_status.state == "completed":
        print("\nTask execution successful. Retrieving artifacts:")
        for artifact in task_status.artifacts:
            for part in artifact.parts:
                if hasattr(part, 'root') and hasattr(part.root, 'text'):
                    print(f"Output: {part.root.text}")
                else:
                    print(f"Output: {part.text}")

if __name__ == "__main__":
    asyncio.run(run_client())
