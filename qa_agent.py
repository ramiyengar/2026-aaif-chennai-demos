from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/qa-webhook")
async def receive_a2a_handoff(request: Request):
    """
    Receives an A2A standard payload from agentgateway.
    """
    payload = await request.json()
    
    sender = payload.get("sender_agent_id")
    task = payload.get("task_description")
    code_diff = payload.get("artifacts", {}).get("diff")
    
    print(f"🔒 Received A2A Handoff from: {sender}")
    print(f"📋 Task: {task}")
    print(f"💻 Scanning Code...\n{code_diff}")
    
    # Simulate a QA process
    return {
        "status": "accepted",
        "a2a_response": "Code passes initial static analysis. Commencing integration tests."
    }
