import argparse
import time
import gradio as gr
import json
from fastapi import FastAPI, Request
import threading
from screeninfo import get_monitors
from computer_use_ootb_internal.computer_use_demo.tools.computer import get_screen_details
from computer_use_ootb_internal.run_teachmode_ootb_args import simple_teachmode_sampling_loop
from fastapi.responses import JSONResponse

app = FastAPI()

class SharedState:
    def __init__(self, args):
        self.args = args
        self.chatbot = None
        self.chat_input = None
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

shared_state = None

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

def process_input(user_input):
    shared_state.chatbot_messages.append(gr.ChatMessage(role="user", content=user_input))
    # shared_state.chatbot_messages.append(gr.ChatMessage(role="assistant", content=""))  # seperate msgs
    shared_state.task = user_input
    shared_state.args.task = user_input  # Add this line to update args.task as well
    yield shared_state.chatbot_messages

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
        # print(f"loop_msg: {loop_msg}")
        if loop_msg.startswith('<img'):
            shared_state.chatbot_messages.append(gr.ChatMessage(role="user", content=loop_msg))
            # shared_state.chatbot_messages.append(gr.ChatMessage(role="assistant", content=""))  # seperate msgs
        else:
            shared_state.chatbot_messages.append(gr.ChatMessage(role="assistant", content=loop_msg))
            # shared_state.chatbot_messages.append(gr.ChatMessage(role="user", content=""))  # seperate msgs

        time.sleep(2)
        yield shared_state.chatbot_messages

    complete_msg = f"Task '{shared_state.task}' completed. Thanks for using Teachmode-OOTB."
    shared_state.chatbot_messages.append(gr.ChatMessage(role="assistant", content=complete_msg))
    yield shared_state.chatbot_messages
    
def update_input():
    while True:
        time.sleep(1)
        if shared_state and shared_state.task_updated:
            if shared_state.chat_input is not None:
                shared_state.chat_input.value = shared_state.args.task
                shared_state.task_updated = False

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

    polling_thread = threading.Thread(target=update_input, daemon=True)
    polling_thread.start()

    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Teach Mode Beta")

        with gr.Accordion("Settings", open=True): 
            with gr.Row():
                with gr.Column():
                    model = gr.Dropdown(
                        label="Model",
                        choices=["teach-mode-beta"],
                        value="teach-mode-beta",
                        interactive=False,
                    )
                with gr.Column():
                    provider = gr.Dropdown(
                        label="API Provider",
                        choices=["openai"],
                        value="openai",
                        interactive=False,
                    )
                with gr.Column():
                    api_key = gr.Textbox(
                        label="API Key",
                        type="password",
                        value=shared_state.api_keys,
                        placeholder="No API key needed in beta",
                        interactive=False,
                    )
                with gr.Column():
                    screen_options, primary_index = get_screen_details()
                    screen_selector = gr.Dropdown(
                        label="Select Screen",
                        choices=screen_options,
                        value=args.selected_screen,
                        interactive=False,
                    )

        with gr.Row():
            with gr.Column(scale=8):
                chat_input = gr.Textbox(
                    value=args.task,
                    show_label=False,
                    container=False,
                    elem_id="chat_input"
                )
                shared_state.chat_input = chat_input
                
            with gr.Column(scale=1, min_width=50):
                submit_button = gr.Button(value="Send", variant="primary")

        chatbot = gr.Chatbot(
            label="Chatbot History",
            group_consecutive_messages=False,
            autoscroll=True,
            height=580,
            type="messages",
            elem_id="chatbot",
        )
        shared_state.chatbot = chatbot
        
        submit_button.click(fn=process_input, inputs=[chat_input], outputs=chatbot)

    app.add_route("/update_params", update_parameters, methods=["POST"])
    app = gr.mount_gradio_app(app, demo, path="/")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7888)

if __name__ == "__main__":
    main()
