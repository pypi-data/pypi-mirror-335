import argparse
import time
import json
import threading

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit

from screeninfo import get_monitors
from computer_use_ootb_internal.computer_use_demo.tools.computer import get_screen_details
from computer_use_ootb_internal.run_teachmode_ootb_args import simple_teachmode_sampling_loop

###############################################################################
#                                Shared State
###############################################################################
class SharedState:
    def __init__(self):
        self.args = None  # Will hold argparse-like namespace
        self.messages = []  # If you want to store a global chat or last session

shared_state = SharedState()

###############################################################################
#                       Flask + SocketIO Application Setup
###############################################################################
app = Flask(__name__)
app.config["SECRET_KEY"] = "some-secret-key"  # In production, change this
socketio = SocketIO(app, cors_allowed_origins="*")

###############################################################################
#                            Utility Functions
###############################################################################
def setup_default_args():
    """
    Creates argparse-like defaults. 
    You can also parse real CLI args if you wish.
    """
    parser = argparse.ArgumentParser(description="Teachmode SocketIO Server.")
    parser.add_argument("--model", default="teach-mode-gpt-4o")
    parser.add_argument("--task", default="Help me complete data extraction on YouTube video.")
    parser.add_argument("--selected_screen", type=int, default=0)
    parser.add_argument("--user_id", default="liziqi")
    parser.add_argument("--trace_id", default="default_trace")
    parser.add_argument("--api_key_file", default="api_key.json")
    parser.add_argument("--api_keys", default="")
    parser.add_argument(
        "--server_url",
        default="http://ec2-35-81-81-242.us-west-2.compute.amazonaws.com/generate_action",
        help="Server URL for the session (local='http://localhost:5000/generate_action', \
              aws='http://ec2-35-81-81-242.us-west-2.compute.amazonaws.com/generate_action').",
    )

    # If you really want to parse sys.argv, do parser.parse_args().
    # But you can also return the defaults for this example:
    return parser.parse_args([])

def apply_args_to_state(args):
    """
    Helper that prints or logs relevant arguments and stores them in shared_state.
    """
    print("[apply_args_to_state] Applying arguments:", args)
    shared_state.args = args

def run_teachmode_task(user_input):
    """
    Calls simple_teachmode_sampling_loop and emits partial responses over SocketIO.
    """
    # 1) Log or store user input
    print(f"[run_teachmode_task] Received user_input: {user_input}")
    # Optionally store or reset message history for this session
    shared_state.messages = [{"role": "user", "content": user_input}]

    # 2) Grab arguments from shared_state
    args = shared_state.args
    if not args:
        print("[run_teachmode_task] No arguments in shared_state, applying defaults.")
        args = setup_default_args()
        apply_args_to_state(args)

    # 3) Run the sampling loop
    print(f"[run_teachmode_task] Starting the sampling loop with task: {args.task}")
    sampling_loop = simple_teachmode_sampling_loop(
        model=args.model,
        task=args.task,
        selected_screen=args.selected_screen,
        user_id=args.user_id,
        trace_id=args.trace_id,
        api_keys=args.api_keys,
        server_url=args.server_url
    )

    # 4) Send partial responses
    for loop_msg in sampling_loop:
        print(f"[run_teachmode_task] Emitting partial response: {loop_msg}")
        # You can store it in shared_state messages
        shared_state.messages.append({"role": "assistant", "content": loop_msg})
        # Emit immediately so the client sees partial responses
        emit("partial_response", {"role": "assistant", "content": loop_msg})
        time.sleep(1)  # Optional delay to simulate real-time streaming

    # 5) Done event
    print("[run_teachmode_task] Completed all messages.")
    emit("done", {"messages": shared_state.messages, "status": "completed"})

###############################################################################
#                           HTTP Endpoint: update_params
###############################################################################
@app.route("/update_params", methods=["POST"])
def update_parameters():
    """
    HTTP endpoint that allows updating the parameters (like Gradio's /update_params).
    Expects JSON body with fields matching the argparse Namespace (model, task, etc.)
    """
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No JSON provided."}), 400

    # Build an argparse.Namespace from the JSON keys
    # Fallback to the existing arguments if some keys are missing
    old_args = shared_state.args or setup_default_args()
    new_args_dict = {**vars(old_args), **data}  # Merge old with new
    new_args = argparse.Namespace(**new_args_dict)
    apply_args_to_state(new_args)

    return jsonify({
        "status": "success",
        "message": "Parameters updated",
        "new_args": vars(new_args)
    })

###############################################################################
#                           HTTP Endpoint: get_messages
###############################################################################
@app.route("/get_messages", methods=["GET"])
def get_messages():
    """
    Example new function: returns the current chat messages in shared_state.
    """
    return jsonify(shared_state.messages)

###############################################################################
#                           HTTP Endpoint: clear_messages
###############################################################################
@app.route("/clear_messages", methods=["POST"])
def clear_messages():
    """
    Example new function: clears the stored chat messages in shared_state.
    """
    shared_state.messages = []
    return jsonify({"status": "success", "message": "Chat history cleared."})

###############################################################################
#                        SocketIO Event: run_teachmode
###############################################################################
@socketio.on("run_teachmode")
def handle_run_teachmode(data):
    """
    Websocket event that starts the teachmode sampling loop.
    `data` can include e.g. {"user_input": "..."}.
    """
    user_input = data.get("user_input", "Hello, let's start!")
    run_teachmode_task(user_input)

###############################################################################
#                        SocketIO Event: connect
###############################################################################
@socketio.on("connect")
def on_connect():
    print("[SocketIO] Client connected.")

@socketio.on("disconnect")
def on_disconnect():
    print("[SocketIO] Client disconnected.")

###############################################################################
#                                   Main
###############################################################################
def main():
    # Pre-populate shared_state with default arguments
    args = setup_default_args()
    apply_args_to_state(args)

    # Optional: Preload screen info if needed
    screens = get_monitors()
    print("Detected screens:", screens)
    screen_names, primary_index = get_screen_details()
    print("Screen names:", screen_names, "Default selected index:", primary_index)

    # Run the Flask-SocketIO app
    # eventlet is the default async_mode if installed, but we specify it explicitly.
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)

if __name__ == "__main__":
    main()
