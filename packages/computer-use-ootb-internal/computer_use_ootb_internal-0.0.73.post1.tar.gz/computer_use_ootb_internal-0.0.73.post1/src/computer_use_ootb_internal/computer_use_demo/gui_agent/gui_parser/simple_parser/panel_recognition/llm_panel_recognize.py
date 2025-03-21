from ....llm_utils.llm_utils import extract_data
from ....llm_utils.run_llm import run_llm


def recognize_panel(ocr, highlight_ocr, panel_metadata, screen_resolution, software):
    panel_recognition = PanelRecognitionLLM(software=software)
    panel_name = panel_recognition(
        ocr, highlight_ocr, panel_metadata, screen_resolution
    )
    return panel_name


class PanelRecognitionLLM:
    def __init__(self, llm="gpt-4o-mini", software="premiere"):
        self.llm = llm
        self.software = software

    # TODO: Maybe consider supporting more general inputs
    def __call__(
        self,
        ocr: dict,
        highlight_ocr: dict,
        raw_item: dict,
        screen_resolution: str,
    ):
        if raw_item["properties"]["friendly_class_name"] == "Dialog":
            panel_name = raw_item["properties"]["texts"][0]
        else:
            panel_name = self.recognize_panel_llm(
                ocr, highlight_ocr, raw_item, screen_resolution
            )
        # print(f"GGGGGGGGGGGG Panel name: {panel_name}")
        return panel_name.strip("\"' ")

    def recognize_panel_llm(self, ocr, highlight_ocr, raw_item, screen_resolution):
        ocr_in_panel = self.get_ocr_in_panel(ocr, raw_item["properties"]["rectangle"])

        highlight_ocr_in_panel = self.get_ocr_in_panel(
            highlight_ocr, raw_item["properties"]["rectangle"]
        )

        panel_name_candidates = self.get_panel_name_candidates("premiere")

        prompt = f"""These are the texts detected in a panel of Adobe Premiere. 

OCR:
{ocr_in_panel}
, where the following ocrs are highlighted:
{highlight_ocr_in_panel}

Panel coordinates:
{raw_item['properties']['rectangle']}

Screen Resolution:
{screen_resolution}

Possible Panel:
{panel_name_candidates}

Could you infer the name of the panel from the OCR results?

Tips for panel:
Navigation Bar: The bar at the top of the screen with different panel names, e.g., Learn, Effects.
Tools: If there is No Text in it, and panel cordinates indicates is a vertical strip. This is the Tools Panel.
Timeline: A line of timecode numbers (more than three) on the top of the panel, xx:xx:xx:xx, that represent the time in the video
Program Monitor: A title that says "Program: [Name of the video]", also has two timecodes
Audio Meters: A column of numbers representing decibel (dB) levels
Source Monitor: A title that says "Source: [Name of the source]", also has two timecodes
Reference Monitor: A title that says "Reference: [Name of the referenced item]", also has two timecodes
Output format:
# Generate a brief Reason Here
```json
"Name of the panel"
```
"""
        # print(f"========================\n{prompt}")
        response = run_llm(prompt, "gpt-4o-mini")
        panel_name = extract_data(response, "json")
        # print(f"========================\nPanel name: {panel_name}")
        return panel_name

    def get_ocr_in_panel(self, ocr_result, panel):
        """
        Check if OCR text bounding boxes are within the specified panel.

        Parameters:
        - ocr_result: dict, OCR results containing bounding boxes of detected text.
        - panel: list, coordinates of the panel in the format [x_min, y_min, x_max, y_max].

        Returns:
        - result: list of booleans, True if the text bbox is within the panel, False otherwise.
        """
        panel_x_min, panel_y_min, panel_x_max, panel_y_max = panel

        results = []

        for text_info in ocr_result["texts"]:
            bbox = text_info["bbox"]
            x_min, y_min, x_max, y_max = bbox

            # Check if the bounding box is completely within the panel
            if (
                x_min >= panel_x_min
                and y_min >= panel_y_min
                and x_max <= panel_x_max
                and y_max <= panel_y_max
            ):
                results.append(text_info)

        return results


    def get_panel_knowledge(self, name):
        panel_knowledge = {
            "premiere": """Navigation Bar: The bar at the top of the screen with different panel names, e.g., Learn, Effects.
Tools: If there is No Text in it, and panel cordinates indicates is a vertical strip. This is the Tools Panel.
Timeline: A line of timecode numbers (more than three) on the top of the panel, xx:xx:xx:xx, that represent the time in the video
Program Monitor: A title that says "Program: [Name of the video]", also has two timecodes
Audio Meters: A column of numbers representing decibel (dB) levels
Source Monitor: A title that says "Source: [Name of the source]", also has two timecodes
Reference Monitor: A title that says "Reference: [Name of the referenced item]", also has two timecodes""",
            "capcut": """
            """,
            "after_effects": """
            """,
        }
        return panel_knowledge.get(name, "")

    @staticmethod
    def get_panel_name_candidates(name):
        panel_name_candidates = {
            "premiere": [
                "Navigation Bar",
                "Audio Track Mixer",
                "Capture",
                "Edit To Tape",
                "Effect Controls",
                "Essential Graphics",
                "Essential Sound",
                "Events",
                "History",
                "Info",
                "Learn",
                "Libraries",
                "Lumetri Color",
                "Lumetri Scopes",
                "Markers",
                "Media Browser",
                "Metadata",
                "Production",
                "Program Monitor",
                "Projects",
                "Reference Monitor",
                "Source Monitor",
                "Timeline",
                "Tools",
                # "other panel",
                "Text",
            ],
            "after_effects": [
                "Composition",
                "Timeline",
                "Preview",
                "Effects & Presets",
                "Character",
                "Paragraph",
            ],
        }

        return panel_name_candidates.get(name, [])
