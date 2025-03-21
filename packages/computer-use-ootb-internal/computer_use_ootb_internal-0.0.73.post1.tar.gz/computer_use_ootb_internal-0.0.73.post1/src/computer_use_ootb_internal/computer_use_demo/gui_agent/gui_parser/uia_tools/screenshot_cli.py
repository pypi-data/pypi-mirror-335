
# screenshot_cli.py
import sys
import json

from pathlib import Path
# get root dir of ootb
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from computer_use_ootb_internal.computer_use_demo.gui_agent.gui_parser.simple_parser.gui_capture import GUICapture

def main():
    # 1) Parse command-line arguments
    if len(sys.argv) > 1:
        selected_screen = int(sys.argv[1])
    else:
        selected_screen = 0

    # 2) Perform the screenshot capture
    
    # **Important**: make sure nothing is printed to stdout in GUICapture.capture()
    gui = GUICapture(selected_screen=selected_screen)
    meta_data, screenshot_path = gui.capture()

    # 3) Print JSON to stdout
    output = {
        "meta_data": meta_data,
        "screenshot_path": screenshot_path
    }
    print(json.dumps(output))  # critical: print to stdout

if __name__ == "__main__":
    main()
