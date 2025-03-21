import ast
import json
import asyncio
from typing import Any, Dict, cast, List, Union
from collections.abc import Callable
import uuid
from anthropic.types.beta import (
    BetaContentBlock,
    BetaContentBlockParam,
    BetaImageBlockParam,
    BetaMessage,
    BetaMessageParam,
    BetaTextBlockParam,
    BetaToolResultBlockParam,
)
from anthropic.types import TextBlock
from anthropic.types.beta import BetaMessage, BetaTextBlock, BetaToolUseBlock
from computer_use_ootb_internal.computer_use_demo.tools import BashTool, ComputerTool, EditTool, ToolCollection, ToolResult


class TeachmodeShowUIExecutor:
    def __init__(
        self, 
        output_callback: Callable[[BetaContentBlockParam], None], 
        tool_output_callback: Callable[[Any, str], None],
        selected_screen: int = 0
    ):
        self.output_callback = output_callback
        self.tool_output_callback = tool_output_callback
        self.selected_screen = selected_screen
        self.screen_bbox = self._get_screen_resolution()
        print("Screen BBox:", self.screen_bbox)
        
        self.tool_collection = ToolCollection(
            ComputerTool(selected_screen=selected_screen, is_scaling=False)
        )
        
        self.supported_action_type={
            # "showui_action": "anthropic_tool_action"
            "CLICK": 'key',  # TBD
            "INPUT": "key",
            "ENTER": "key",  # TBD
            "ESC": "key",
            "ESCAPE": "key",
            "PRESS":  "key",
            "KEY": "key",
            "HOTKEY": "key",
            "DRAG": "mouse_move",
            "SCROLL": "key",
            "DOUBLE_CLICK": "key",
        }

    def __call__(self, response: str, messages: list[BetaMessageParam]):
        # response is expected to be :
        # {'content': "{'action': 'CLICK', 'value': None, 'position': [0.83, 0.15]}, ...", 'role': 'assistant'}, 
        
        action_dict = self._format_actor_output(response)  # str -> dict
        
        actions = action_dict["content"]
        role = action_dict["role"]
        
        # Parse the actions from showui
        action_list = self._parse_showui_output(actions)
        print("Parsed Action List:", action_list)
        
        tool_result_content = None
        
        if action_list is not None and len(action_list) > 0:
                    
            for action in action_list:  # Execute the tool (adapting the code from anthropic_executor.py)
            
                tool_result_content: list[BetaToolResultBlockParam] = []
                
                # self.output_callback(f"{colorful_text_showui}:\n{action}", sender="bot")
                print("Converted Action:", action)
                
                sim_content_block = BetaToolUseBlock(id=f'toolu_{uuid.uuid4()}',
                                        input={'action': action["action"], 'text': action["text"], 'coordinate': action["coordinate"]},
                                        name='computer', type='tool_use')

                # Run the asynchronous tool execution in a synchronous context
                result = asyncio.run(self.tool_collection.run(
                    name=sim_content_block.name,
                    tool_input=cast(dict[str, Any], sim_content_block.input),
                ))
                
                tool_result_content.append(
                    _make_api_tool_result(result, sim_content_block.id)
                )
                print(f"[teachmode_executor] tool_result_content: {tool_result_content}")
                # tool_result_content =
                # [{'type': 'tool_result',
                #  'content': [{'type': 'text', 'text': 'Moved mouse to (1183, 1056)'}],
                #  'tool_use_id': 'toolu_e6d396c5-21b1-46bf-b41d-33b34863dc94',
                #  'is_error': False}]

                yield tool_result_content[0]['content'][0]['text']


        
        return tool_result_content[0]['content'][0]['text']
    
    
    def _format_actor_output(self, action_output: str|dict) -> Dict[str, Any]:
        if type(action_output) == dict:
            return action_output
        else:
            try:
                action_output.replace("'", "\"")
                action_dict = ast.literal_eval(action_output)
                return action_dict
            except Exception as e:
                print(f"Error parsing action output: {e}")
                return None
    

    def _parse_showui_output(self, output_text: str | dict) -> Union[List[Dict[str, Any]], None]:
        try:
            # refine key: value pairs, mapping to the Anthropic's format
            refined_output = []
            
            action_item = output_text
            
            print("[_parse_showui_output] Action Item:", action_item)
            
            # sometime showui returns lower case action names
            action_item["action"] = action_item["action"].upper()
            
            # if "coordinate" in action_item:
            #     action_item["position"] = action_item["coordinate"]
            # if "text" in action_item:
            #     action_item["value"] = action_item["text"]
            
            if action_item["action"] not in self.supported_action_type:
                raise ValueError(f"Action {action_item['action']} not supported. Check the output from ShowUI: {output_text}")
                # continue
            
            elif action_item["action"] == "CLICK":  # 1. click -> mouse_move + left_click
                x, y = action_item["position"]

                # action_item["position"] = (int(x * (self.screen_bbox[2] - self.screen_bbox[0])),
                #                             int(y * (self.screen_bbox[3] - self.screen_bbox[1])))
                action_item["position"] = (int(x), int(y))
                
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": tuple(action_item["position"])})
                refined_output.append({"action": "left_click", "text": None, "coordinate": None})
            
            elif action_item["action"] == "INPUT":  # 2. input -> type
                if "text" in action_item:
                    refined_output.append({"action": "type", "text": action_item["text"], "coordinate": None})
                elif "value" in action_item:
                    refined_output.append({"action": "type", "text": action_item["value"], "coordinate": None})
                else:
                    raise ValueError(f"Input action {action_item['action']} does not contain 'text' or 'value'.")
            
            elif action_item["action"] == "ENTER":  # 3. enter -> key, enter
                refined_output.append({"action": "key", "text": "Enter", "coordinate": None})
            
            elif action_item["action"] == "ESC" \
                or action_item["action"] == "ESCAPE" \
                or (action_item["action"] == "KEY" and action_item["value"] == "ESC"):  # 4. enter -> key, enter
                refined_output.append({"action": "key", "text": "Escape", "coordinate": None})
                
            elif action_item["action"] == "HOVER":  # 5. hover -> mouse_move
                x, y = action_item["position"]
                action_item["position"] = (int(x * (self.screen_bbox[2] - self.screen_bbox[0])),
                                        int(y * (self.screen_bbox[3] - self.screen_bbox[1])))
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": tuple(action_item["position"])})
                
            elif action_item["action"] == "SCROLL":  # 6. scroll -> key: pagedown
                if action_item["value"] == "up":
                    refined_output.append({"action": "key", "text": "pageup", "coordinate": None})
                elif action_item["value"] == "down":
                    refined_output.append({"action": "key", "text": "pagedown", "coordinate": None})
                else:
                    raise ValueError(f"Scroll direction {action_item['value']} not supported.")

            elif action_item["action"] == "PRESS":  # 7. press
                x, y = action_item["position"]
                action_item["position"] = (int(x * (self.screen_bbox[2] - self.screen_bbox[0])),
                                        int(y * (self.screen_bbox[3] - self.screen_bbox[1])))
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": tuple(action_item["position"])})
                refined_output.append({"action": "left_press", "text": None, "coordinate": None})

            elif action_item["action"] == "HOTKEY" or action_item["action"] == "KEY":  # 8. hotkey
                refined_output.append({"action": "key", "text": action_item["value"], "coordinate": None})

            elif action_item["action"] == "DRAG":  # 9. drag
                x1, y1 = action_item["value"]
                x2, y2 = action_item["position"]
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": (x1, y1)})
                refined_output.append({"action": "left_click_drag", "text": None, "coordinate": (x2, y2)})

            elif action_item["action"] == "DOUBLE_CLICK":  # 10. double click
                x, y = action_item["position"]
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": (x, y)})
                refined_output.append({"action": "double_click", "text": None, "coordinate": None})

            return refined_output

        except Exception as e:
            print(f"Error parsing output: {e}")
            import pdb; pdb.set_trace()
            return None
        

    def _get_screen_resolution(self):
        from screeninfo import get_monitors
        import platform
        if platform.system() == "Darwin":
            import Quartz  # uncomment this line if you are on macOS
        import subprocess
            
        # Detect platform
        system = platform.system()

        if system == "Windows":
            # Windows: Use screeninfo to get monitor details
            screens = get_monitors()

            # Sort screens by x position to arrange from left to right
            sorted_screens = sorted(screens, key=lambda s: s.x)

            if self.selected_screen < 0 or self.selected_screen >= len(screens):
                raise IndexError("Invalid screen index.")

            screen = sorted_screens[self.selected_screen]
            bbox = (screen.x, screen.y, screen.x + screen.width, screen.y + screen.height)

        elif system == "Darwin":  # macOS
            # macOS: Use Quartz to get monitor details
            max_displays = 32  # Maximum number of displays to handle
            active_displays = Quartz.CGGetActiveDisplayList(max_displays, None, None)[1]

            # Get the display bounds (resolution) for each active display
            screens = []
            for display_id in active_displays:
                bounds = Quartz.CGDisplayBounds(display_id)
                screens.append({
                    'id': display_id,
                    'x': int(bounds.origin.x),
                    'y': int(bounds.origin.y),
                    'width': int(bounds.size.width),
                    'height': int(bounds.size.height),
                    'is_primary': Quartz.CGDisplayIsMain(display_id)  # Check if this is the primary display
                })

            # Sort screens by x position to arrange from left to right
            sorted_screens = sorted(screens, key=lambda s: s['x'])

            if self.selected_screen < 0 or self.selected_screen >= len(screens):
                raise IndexError("Invalid screen index.")

            screen = sorted_screens[self.selected_screen]
            bbox = (screen['x'], screen['y'], screen['x'] + screen['width'], screen['y'] + screen['height'])

        else:  # Linux or other OS
            cmd = "xrandr | grep ' primary' | awk '{print $4}'"
            try:
                output = subprocess.check_output(cmd, shell=True).decode()
                resolution = output.strip().split()[0]
                width, height = map(int, resolution.split('x'))
                bbox = (0, 0, width, height)  # Assuming single primary screen for simplicity
            except subprocess.CalledProcessError:
                raise RuntimeError("Failed to get screen resolution on Linux.")
        
        return bbox



def _message_display_callback(messages):
    display_messages = []
    for msg in messages:
        try:
            if isinstance(msg, str):
                display_messages.append((msg, None))
            else:
                if isinstance(msg["content"][0], TextBlock):
                    display_messages.append((msg["content"][0].text, None))  # User message
                elif isinstance(msg["content"][0], BetaTextBlock):
                    display_messages.append((None, msg["content"][0].text))  # Bot message
                elif isinstance(msg["content"][0], BetaToolUseBlock):
                    display_messages.append((None, f"Tool Use: {msg['content'][0].name}\nInput: {msg['content'][0].input}"))  # Bot message
                elif isinstance(msg["content"][0], Dict) and msg["content"][0]["content"][-1]["type"] == "image":
                    display_messages.append((None, f'<img src="data:image/png;base64,{msg["content"][0]["content"][-1]["source"]["data"]}">'))  # Bot message
                else:
                    pass
        except Exception as e:
            print("[_message_display_callback] error", e)
            pass
    return display_messages


def _make_api_tool_result(
    result: ToolResult, tool_use_id: str
) -> BetaToolResultBlockParam:
    """Convert an agent ToolResult to an API ToolResultBlockParam."""
    tool_result_content: list[BetaTextBlockParam | BetaImageBlockParam] | str = []
    is_error = False
    if result.error:
        is_error = True
        tool_result_content = _maybe_prepend_system_tool_result(result, result.error)
    else:
        if result.output:
            tool_result_content.append(
                {
                    "type": "text",
                    "text": _maybe_prepend_system_tool_result(result, result.output),
                }
            )
        if result.base64_image:
            tool_result_content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": result.base64_image,
                    },
                }
            )
    return {
        "type": "tool_result",
        "content": tool_result_content,
        "tool_use_id": tool_use_id,
        "is_error": is_error,
    }


def _maybe_prepend_system_tool_result(result: ToolResult, result_text: str):
    if result.system:
        result_text = f"<system>{result.system}</system>\n{result_text}"
    return result_text



# Testing main function
if __name__ == "__main__":
    def output_callback(content_block):
        # print("Output Callback:", content_block)
        pass

    def tool_output_callback(result, action):
        print("[showui_executor] Tool Output Callback:", result, action)
        pass

    # Instantiate the executor
    executor = ShowUIExecutor(
        output_callback=output_callback,
        tool_output_callback=tool_output_callback,
        selected_screen=0
    )

    # test inputs
    response_content = "{'content': \"{'action': 'CLICK', 'value': None, 'position': [0.49, 0.18]}\", 'role': 'assistant'}"
    # response_content = {'content': "{'action': 'CLICK', 'value': None, 'position': [0.49, 0.39]}", 'role': 'assistant'}
    # response_content = "{'content': \"{'action': 'CLICK', 'value': None, 'position': [0.49, 0.42]}, {'action': 'INPUT', 'value': 'weather for New York city', 'position': [0.49, 0.42]}, {'action': 'ENTER', 'value': None, 'position': None}\", 'role': 'assistant'}"

    # Initialize messages
    messages = []

    # Call the executor
    print("Testing ShowUIExecutor with response content:", response_content)
    for message, tool_result_content in executor(response_content, messages):
        print("Message:", message)
        print("Tool Result Content:", tool_result_content)

    # Display final messages
    print("\nFinal messages:")
    for msg in messages:
        print(msg)
