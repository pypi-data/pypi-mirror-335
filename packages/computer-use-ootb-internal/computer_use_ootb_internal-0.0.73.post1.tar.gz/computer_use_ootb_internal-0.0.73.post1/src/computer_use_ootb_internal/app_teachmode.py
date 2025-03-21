import argparse
import time
import json
import threading
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from screeninfo import get_monitors
from computer_use_ootb_internal.computer_use_demo.tools.computer import get_screen_details
from computer_use_ootb_internal.run_teachmode_ootb_args import simple_teachmode_sampling_loop

app = FastAPI()

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SharedState:
    def __init__(self, args):
        self.args = args
        self.task_updated = False
        self.chatbot_messages = []
        # Store all state-related data here
        self.model = args.model
        self.task = getattr(args, 'task', "")
        self.selected_screen = args.selected_screen
        self.user_id = args.user_id
        self.trace_id = args.trace_id
        self.api_keys = args.api_keys
        self.server_url = args.server_url
        self.message_queue = []
        self.is_processing = False
        self.should_stop = False
        self.is_paused = False

shared_state = None

@app.post("/update_params")
async def update_parameters(request: Request):
    data = await request.json()
    
    if 'task' not in data:
        return JSONResponse(
            content={"status": "error", "message": "Missing required field: task"},
            status_code=400
        )
        
    shared_state.args = argparse.Namespace(**data)
    shared_state.task_updated = True
    
    # Update shared state when parameters change
    shared_state.model = getattr(shared_state.args, 'model', "teach-mode-gpt-4o")
    shared_state.task = getattr(shared_state.args, 'task', "Create a claim on the SAP system, using Receipt.pdf as attachment.")
    shared_state.selected_screen = getattr(shared_state.args, 'selected_screen', 0)
    shared_state.user_id = getattr(shared_state.args, 'user_id', "a_test")
    shared_state.trace_id = getattr(shared_state.args, 'trace_id', "jess_4")
    shared_state.api_keys = getattr(shared_state.args, 'api_keys', "sk-proj-1234567890")
    shared_state.server_url = getattr(shared_state.args, 'server_url', "http://ec2-35-81-81-242.us-west-2.compute.amazonaws.com/generate_action")
    
    return JSONResponse(
        content={"status": "success", "message": "Parameters updated", "new_args": vars(shared_state.args)},
        status_code=200
    )

@app.post("/update_message")
async def update_message(request: Request):
    data = await request.json()
    
    if 'message' not in data:
        return JSONResponse(
            content={"status": "error", "message": "Missing required field: message"},
            status_code=400
        )
    
    message = data['message']
    shared_state.chatbot_messages.append({"role": "user", "content": message})
    shared_state.task = message
    shared_state.args.task = message
    
    # Start processing if not already running
    if not shared_state.is_processing:
        threading.Thread(target=process_input, daemon=True).start()
    
    return JSONResponse(
        content={"status": "success", "message": "Message received", "task": shared_state.task},
        status_code=200
    )

@app.get("/get_messages")
async def get_messages():
    # Return all messages in the queue and clear it
    messages = shared_state.message_queue.copy()
    shared_state.message_queue = []
    
    return JSONResponse(
        content={"status": "success", "messages": messages},
        status_code=200
    )

@app.get("/get_screens")
async def get_screens():
    screen_options, primary_index = get_screen_details()
    
    return JSONResponse(
        content={"status": "success", "screens": screen_options, "primary_index": primary_index},
        status_code=200
    )

@app.post("/stop_processing")
async def stop_processing():
    if shared_state.is_processing:
        shared_state.should_stop = True
        return JSONResponse(
            content={"status": "success", "message": "Processing will be stopped"},
            status_code=200
        )
    else:
        return JSONResponse(
            content={"status": "error", "message": "No active processing to stop"},
            status_code=400
        )

@app.post("/toggle_pause")
async def toggle_pause():
    if not shared_state.is_processing:
        return JSONResponse(
            content={"status": "error", "message": "No active processing to pause/resume"},
            status_code=400
        )
    
    # Toggle the pause state
    shared_state.is_paused = not shared_state.is_paused
    current_state = shared_state.is_paused
    
    print(f"Toggled pause state to: {current_state}")
    
    status_message = "paused" if current_state else "resumed"
    
    # Add a message to the queue to inform the user
    if current_state:
        message = {"role": "assistant", "content": f"Task '{shared_state.task}' has been paused. Click Continue to resume."}
    else:
        message = {"role": "assistant", "content": f"Task '{shared_state.task}' has been resumed."}
    
    shared_state.chatbot_messages.append(message)
    shared_state.message_queue.append(message)
    
    return JSONResponse(
        content={
            "status": "success", 
            "message": f"Processing {status_message}",
            "is_paused": current_state
        },
        status_code=200
    )

@app.get("/status")
async def get_status():
    print(f"Status check - Processing: {shared_state.is_processing}, Paused: {shared_state.is_paused}")
    return JSONResponse(
        content={
            "status": "success",
            "is_processing": shared_state.is_processing,
            "is_paused": shared_state.is_paused
        },
        status_code=200
    )

def process_input():
    shared_state.is_processing = True
    shared_state.should_stop = False
    shared_state.is_paused = False
    
    print(f"start sampling loop: {shared_state.chatbot_messages}")
    print(f"shared_state.args before sampling loop: {shared_state.args}")

    # 0224 demo:
    if "excel" in shared_state.task.lower():
        shared_state.user_id = "a_test"
        shared_state.trace_id = "excel_sum"

    sampling_loop = simple_teachmode_sampling_loop(
        model=shared_state.model,
        task=shared_state.task,
        selected_screen=shared_state.selected_screen,
        user_id=shared_state.user_id,
        trace_id=shared_state.trace_id,
        api_keys=shared_state.api_keys,
        server_url=shared_state.server_url,
    )

    for loop_msg in sampling_loop:
        # Check if we should stop processing
        if shared_state.should_stop:
            print("Processing stopped by user")
            break
            
        # Check if paused and wait while paused
        if shared_state.is_paused:
            print(f"Processing paused at: {time.strftime('%H:%M:%S')}")
            # Wait in a loop while paused
            while shared_state.is_paused and not shared_state.should_stop:
                time.sleep(0.2)  # More responsive pause
            
            # If we received stop signal while paused
            if shared_state.should_stop:
                print("Processing stopped while paused")
                break
                
            print(f"Processing resumed at: {time.strftime('%H:%M:%S')}")
            
        if loop_msg.startswith('<img'):
            message = {"role": "user", "content": loop_msg}
            shared_state.chatbot_messages.append(message)
        else:
            message = {"role": "assistant", "content": loop_msg}
            shared_state.chatbot_messages.append(message)
            
        # Add message to the queue for frontend to fetch
        shared_state.message_queue.append(message)
        time.sleep(0.5)

    # Handle completion or interruption
    if shared_state.should_stop:
        stop_msg = f"Task '{shared_state.task}' was stopped by the user."
        final_message = {"role": "assistant", "content": stop_msg}
    else:
        complete_msg = f"Task '{shared_state.task}' completed. Thanks for using Teachmode-OOTB."
        final_message = {"role": "assistant", "content": complete_msg}
        
    shared_state.chatbot_messages.append(final_message)
    shared_state.message_queue.append(final_message)
    
    shared_state.is_processing = False
    shared_state.should_stop = False
    shared_state.is_paused = False
    print("Processing completed")

def main():
    global app, shared_state
    
    parser = argparse.ArgumentParser(
        description="Run a synchronous sampling loop for assistant/tool interactions in teach-mode."
    )
    parser.add_argument("--model", default="teach-mode-gpt-4o")
    parser.add_argument("--task", default="Create a claim on the SAP system, using Receipt.pdf as attachment.")
    parser.add_argument("--selected_screen", type=int, default=0)
    parser.add_argument("--user_id", default="18")
    parser.add_argument("--trace_id", default="96")
    parser.add_argument("--api_key_file", default="api_key.json")
    parser.add_argument("--api_keys", default="")
    parser.add_argument(
        "--server_url",
        default="http://ec2-35-81-81-242.us-west-2.compute.amazonaws.com/generate_action",
        help="Server URL for the session"
    )

    args = parser.parse_args()
    shared_state = SharedState(args)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7888)

if __name__ == "__main__":
    main()