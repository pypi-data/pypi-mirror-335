import argparse
import time
import json
import platform
from typing import Callable
from collections.abc import Callable

from computer_use_ootb_internal.computer_use_demo.executor.teachmode_executor import TeachmodeShowUIExecutor
from computer_use_ootb_internal.computer_use_demo.gui_agent.gui_parser.simple_parser.gui_capture import get_screenshot
from computer_use_ootb_internal.computer_use_demo.gui_agent.llm_utils.oai import encode_image
from computer_use_ootb_internal.computer_use_demo.gui_agent.gui_parser.simple_parser.icon_detection.icon_detection import get_screen_resize_factor
from computer_use_ootb_internal.computer_use_demo.tools.aws_request import send_request_to_server
from computer_use_ootb_internal.computer_use_demo.gui_agent.gui_parser.uia_tools.screenshot_service import get_screenshot_external_cmd


def simple_teachmode_sampling_loop(
    model: str,
    task: str,
    api_keys: dict = None,
    action_history: list[dict] = [],
    selected_screen: int = 0,
    user_id: str = None,
    trace_id: str = None,
    server_url: str = "http://localhost:5000/generate_action",
    output_callback: Callable[[str, str], None] = None,
    tool_output_callback: Callable[[str, str], None] = None,
    api_response_callback: Callable[[dict], None] = None,
):
    """
    Synchronous sampling loop for assistant/tool interactions in 'teach mode'.
    """
    if platform.system() != "Windows":
        raise ValueError("Teach mode is only supported on Windows.")

    executor = TeachmodeShowUIExecutor(
        output_callback=output_callback,
        tool_output_callback=tool_output_callback,
        selected_screen=selected_screen,
    )

    step_count = 0

    if model.startswith("teach-mode"):

        while True:
            
            print(f"step_count: {step_count}")

            # Pause briefly so we don't spam screenshots
            time.sleep(1)

            uia_meta, sc_path = get_screenshot_external_cmd(selected_screen=selected_screen)
            # print(f"uia_meta: {uia_meta}, sc_path: {sc_path}")

            payload = {
                "uia_data": uia_meta,
                "screenshot_path": sc_path,
                "query": task,
                "action_history": action_history,
                "mode": "teach",
                "user_id": user_id,
                "trace_id": trace_id,
                "scale_factor": get_screen_resize_factor(),
                "os_name": platform.system(),
                "llm_model": "gpt-4o",
                "api_keys": api_keys,
            }


            screenshot_base64 = encode_image(sc_path)
            yield f'<img src="data:image/png;base64,{screenshot_base64}">'

            # Send request to inference server
            infer_server_response = send_request_to_server(payload, server_url)

            # print(f"infer_server_response: {infer_server_response}")
            next_plan = infer_server_response["generated_plan"]
            next_plan_observation = "".join(next_plan["observation"])
            next_plan_action = "".join(next_plan["action"])
            next_action = infer_server_response["generated_action"]

            yield f"Model Observation:\n{next_plan_observation}\n{next_plan_action}"

            try:
                next_action = json.loads(infer_server_response["generated_action"]["content"])
            except Exception as e:
                print("Error parsing generated_action content:", e)
                continue

            if next_action.get("action") == "STOP":
                final_sc, final_sc_path = get_screenshot_external_cmd(selected_screen=selected_screen)
                break

            action_history.append(f"Performed Step [{step_count}]: Plan: {next_plan_action}, Action: {next_action};")

            for exec_message in executor({"role": "assistant", "content": next_action}, action_history):
                yield f"Executing:\n{exec_message}"

            step_count += 1

    else:
        raise ValueError("Invalid model selected.")


def output_callback(response: str, sender: str) -> None:
    """
    Callback for text-based output from the assistant.
    """
    pass  


def tool_output_callback(tool_result: str, sender: str) -> None:
    """
    Callback for tool (non-text) output from the assistant.
    """
    pass  


def api_response_callback(response: dict) -> None:
    """
    Callback for receiving API responses.
    """
    pass 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a synchronous sampling loop for assistant/tool interactions in teach-mode."
    )
    parser.add_argument(
        "--model",
        default="teach-mode-gpt-4o",
        help="The model to use for teach-mode (e.g., 'teach-mode-gpt-4o').",
    )
    parser.add_argument(
        "--task",
        # default="Help me to complete the extraction of the viewer data of Downald Trump's first video on youtube,\
        # fill in the excel sheet.",
        default="Click on the Google Chorme icon",
#         default="Help me to complete the extraction of the viewer data of DeepSeek's first video on youtube, \
# fill in the video name and the viewer data to excel sheet.",
        help="The task to be completed by the assistant (e.g., 'Complete some data extraction.').",
    )
    parser.add_argument(
        "--selected_screen",
        type=int,
        default=0,
        help="Index of the screen to capture (default=0).",
    )
    parser.add_argument(
        "--user_id",
        default="liziqi",
        help="User ID for the session (default='liziqi').",
    )
    parser.add_argument(
        "--trace_id",
        default="default_trace",
        help="Trace ID for the session (default='default_trace').",
    )
    parser.add_argument(
        "--api_key_file",
        default="api_key.json",
        help="Path to the JSON file containing API keys (default='api_key.json').",
    )

    args = parser.parse_args()

    # # Load API keys
    # with open(args.api_key_file, "r") as file:
    #     api_keys = json.load(file)
    api_keys = None

    print(f"Starting task: {args.task}")

    # Execute the sampling loop
    sampling_loop = simple_teachmode_sampling_loop(
        model=args.model,
        task=args.task,
        output_callback=output_callback,
        tool_output_callback=tool_output_callback,
        api_response_callback=api_response_callback,
        selected_screen=args.selected_screen,
        user_id=args.user_id,
        trace_id=args.trace_id,
        api_keys=api_keys,
    )

    # # Print each step result
    for step in sampling_loop:
        print(step)
        time.sleep(1)

    print(f"Task '{args.task}' completed. Thanks for using Teachmode-OOTB.")
