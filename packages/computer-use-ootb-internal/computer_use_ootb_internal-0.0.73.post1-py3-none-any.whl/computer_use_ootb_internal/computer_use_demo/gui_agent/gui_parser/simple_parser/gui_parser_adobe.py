
from .text_detection import text_detection
from .utils import *
from .panel_recognition.llm_panel_recognize import recognize_panel
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from .icon_detection.icon_detection import IconDetector
import glob


class AdobeParser():
    name = "adobe_parser"

    def __init__(self, cache_folder=".cache/"):
        self.cache_folder = cache_folder
        self.task_id = get_current_time()
        self.action_type = ["click"]

    def __call__(
        self, meta_data, screenshot_path, window_name=None, scaleFactor=None
    ):
        self.window_name = window_name.lower()
        self.scaleFactor = scaleFactor
        ocr = text_detection(screenshot_path, save_png=False)
        highlight_ocr = self.detect_highlight_with_ocr(screenshot_path)

        self.parsed_gui = {window_name: []}
        for window_name, window_meta_data in meta_data.items():
            if not window_meta_data:
                continue

            if window_meta_data[0]["properties"]["friendly_class_name"] in [
                "MenuItem",
                "Edit",
                "Button",
            ]:
                self.parsed_gui[window_name] += self.parse_popup_window(
                    window_meta_data, window_name
                )
            else:
                self.parsed_gui[window_name] += self.parse_main_window(
                    window_meta_data, screenshot_path, ocr, highlight_ocr
                )
                self.parsed_gui[window_name] += self.parse_menu(window_meta_data)

        return self.parsed_gui

    @staticmethod
    def parse_menu(meta_data):
        menu_items = []
        for item in meta_data:
            if item["properties"]["friendly_class_name"] == "Menu":
                new_item = {
                    "name": item["properties"]["texts"][0],
                    "rectangle": item["properties"]["rectangle"],
                    "type": ["click"],
                    "elements": [
                        [
                            {
                                "name": child["properties"]["texts"][0],
                                "rectangle": child["properties"]["rectangle"],
                                "type": ["click"],
                            }
                            for child in item["children"]
                            if child["properties"]["texts"]
                        ]
                    ],
                }
                menu_items.append(new_item)
        return menu_items

    def parse_popup_window(self, meta_data, window_name):
        filtered_data = self.filter_data(meta_data)
        sorted_data_y = self.sort_data_by_y_coordinate(filtered_data)
        elements = self.organize_elements(sorted_data_y)

        for entry in elements:
            for item in entry:
                item["type"] = self.action_type

        panel_item = {
            "name": window_name,
            "rectangle": find_compact_bounding_box(elements),
            "elements": elements,
        }
        return [panel_item]

    def parse_main_window(self, window_meta_data, screenshot_path, ocr, highlight_ocr):
        screen_resolution = Image.open(screenshot_path).size
        params = [
            (ocr, highlight_ocr, raw_item, screenshot_path, screen_resolution)
            for raw_item in window_meta_data
            if raw_item["properties"]["friendly_class_name"] in ["Pane", "Dialog"]
        ]

        main_panel = self.run_parallel_tasks(self.parse_panel, params)
        return main_panel

    def parse_panel(
        self, ocr, highlight_ocr, raw_item, screenshot_path, screen_resolution
    ):
        panel_name = recognize_panel(
            ocr, highlight_ocr, raw_item, screen_resolution, self.window_name
        )
        raw_item["properties"]["rectangle"] = [
            max(0, value) for value in raw_item["properties"]["rectangle"]
        ]

        panel_item = {
            "name": panel_name,
            "rectangle": raw_item["properties"]["rectangle"],
            "type": self.action_type + ["doubleClick", "rightClick"],
        }

        temp = {
            "editing_control": self.get_text(panel_item, ocr, screenshot_path),
            "button": self.get_button(panel_item, screenshot_path, self.scaleFactor)
        }
        
        
        panel_item["elements"] = self.merge_elements(temp)
        return panel_item


    def get_button(self, panel_item, screenshot_path, scale_factor="1.0x"):
        # print("GXW",scale_factor)
        # crop the panel based on the rectangle
        # print("processing button fuck")
        print(panel_item["name"], panel_item["rectangle"])
        panel_img = crop_panel(panel_item["rectangle"], screenshot_path)
        # get the button
        # th = 0.90 if self.software_name == 'after effect' else 0.78

        th = 0.80 if self.software_name == "after effect" else 0.75
        if self.software_name in [
            "premiere",
            "after effect",
            "Premiere",
            "After Effect",
        ]:
            print("Screenshot:", screenshot_path)
            button_box = self.detect_button_adobe(
                panel_img,
                software_name=self.software_name,
                panel_name=panel_item["name"],
                threshold=th,
                scale_factor=scale_factor,
            )
            
        # restore the button coordinate to the whole screenshot
        button_box = restore_coordinate(button_box, panel_item["rectangle"])
        return button_box
    
    @staticmethod
    def load_icon_templates(icon_folder, software_name, panel_name, scale_factor="1.0x"):
        # 初始化空的路径列表
        if "Accessory" in panel_name:
            panel_name = "Accessory"
        # 初始化空的路径列表
        if panel_name:
            template_folder = f"{icon_folder}/{software_name}/{panel_name}"
        else:
            template_folder = f"{icon_folder}/{software_name}"

        print("GXW load_icon_templates:scale_factor", scale_factor)
        template_folder = f"{icon_folder}/{software_name}/{scale_factor}/{panel_name}"
        print("loading icon templates... from ", template_folder)

        icon_path = glob.glob(f"{template_folder}/**/*.png", recursive=True)
        print("found ", len(icon_path), " icons")

        icons = []
        for template_path in icon_path:
            # 读取模板图片
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            # 获取模板图片的名称
            # print(template_path)
            name = re.search(r"[^\\/]+(?=\.\w+$)", template_path).group(0)
            name = re.sub(r"^\d+_", "", name) + "_icon"
            # print(name)
            # 将模板图片的名称和图片加入到列表中
            icons.append({"name": name, "template": template, "path": template_path})
        return icons
    
    @staticmethod
    def preprocess_image(img, software_name):
        # 转换为灰度
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 二值化
        # _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
        if software_name in ["premiere", "after effect"]:
            threshold = 60
        elif software_name in ["adobe acrobat", "acrobat"]:
            threshold = 190
        elif software_name in ["word", "excel", "powerpoint"]:
            threshold = 190
        else:
            threshold = 130

        binary, saved_path = multivalue_image(
            img,
            mode="None",  # 或者您可以用其他任何字符串，这里不重要
            thresholds=[threshold],  # 一个单一的阈值
            interval_values=[0, 255],  # 两个区间值
            save=False,  # 是否保存图像
            cache_folder="./.cache",  # 缓存文件夹
        )
        return binary
    @staticmethod
    def divide_activated_area(image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Define the scope of blue
        lower_blue = np.array([105, 100, 100])
        upper_blue = np.array([130, 255, 255])
        # Creates a mask that sets parts within a specified color range to white and other parts to black
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        # Perform a bitwise AND operation on the original image and the mask to extract the blue part
        blue = cv2.bitwise_and(image, image, mask=mask)
        non_blue_part = cv2.bitwise_not(image, image, mask)
        return blue, non_blue_part
    
    
    def detect_button_adobe(
        self,
        image,
        software_name="premiere",
        panel_name=None,
        icon_folder="./cache",
        icon_type=None,
        threshold=0.75,
        scale_factor="1x",
    ):
        # image的格式 cv2.imread(image_path, cv2.IMREAD_COLOR)   最理想情况是1080p的图片否则质量不会太好
        # button_folder button 库位置
        # threshold 模版匹配的阈值， 越高越准确，但是button数目有时会变少

        # image_path = "extracted_img/frame9725.jpg"
        # image = cv2.imread(image_path, cv2.IMREAD_COLOR)

        # print("GXW detect_button_adobe:scale_factor",scale_factor)

        blue_image, non_blue_image = self.divide_activated_area(image)
        non_blue_image = self.preprocess_image(non_blue_image, software_name)
        if "Accessory" in software_name:
            panel_name = "Accessory"

        templates = self.load_icon_templates(
            icon_folder, software_name, panel_name, scale_factor
        )
        # print("templates", templates)
        all_boxes, all_scores, labels = [], [], []
        # count = 0
        for i, template in enumerate(templates):
            icon_name = template["name"]
            icon_template = template["template"]

            icon_template_blue, icon_template_non_blue = self.divide_activated_area(
                icon_template
            )
            icon_template_non_blue = self.preprocess_image(icon_template_non_blue, software_name)

            # find the best scale for the template at the first iteration
            if i == 0:
                best_scale_blue = 1
                if "activated" in icon_name:
                    best_scale_blue = self.get_best_matching_scale(
                        blue_image, icon_template_blue
                    )
                best_scale_non_blue = self.get_best_matching_scale(
                    non_blue_image, icon_template_non_blue
                )

            if "activated" in icon_name:
                matches_blue, scores_blue = self.multi_scale_template_matching(
                    blue_image,
                    icon_template_blue,
                    threshold=threshold,
                    scales=[best_scale_blue],
                )

                icon_width = icon_template_blue.shape[1]
                icon_height = icon_template_blue.shape[0]
                for match, score in zip(matches_blue, scores_blue):
                    (pt_x, pt_y), scale = match

                    end_x = int(pt_x + icon_width * scale)
                    end_y = int(pt_y + icon_height * scale)

                    # 保存所有的框到all_boxes
                    all_boxes.append([pt_x, pt_y, end_x, end_y])
                    all_scores.append(score)
                    labels.append(icon_name)

            if "activated" not in icon_name:
                matches_non_blue, scores_non_blue = self.multi_scale_template_matching(
                    non_blue_image,
                    icon_template_non_blue,
                    threshold=threshold,
                    scales=[best_scale_non_blue],
                )
                icon_width = icon_template_non_blue.shape[1]
                icon_height = icon_template_non_blue.shape[0]
                for match, score in zip(matches_non_blue, scores_non_blue):
                    (pt_x, pt_y), scale = match

                    end_x = int(pt_x + icon_width * scale)
                    end_y = int(pt_y + icon_height * scale)

                    # 保存所有的框到all_boxes
                    all_boxes.append([pt_x, pt_y, end_x, end_y])
                    all_scores.append(score)
                    labels.append(icon_name)

        # print(threshold, labels)
        # 应用NMS bbox 去重
        nms_boxes, pick = self.non_max_suppression(all_boxes, 0.15, all_scores)
        labels = [labels[i] for i in pick]

        button_items = []
        for ix, box in enumerate(nms_boxes):
            if "scroll bar" in labels[ix] or "effects submenu" in labels[ix]:
                item = {
                    "name": labels[ix],
                    "rectangle": list(box),
                }
            else:
                item = {
                    "name": labels[ix],
                    "rectangle": list(box),
                }
            button_items.append(item)

        # button_items = [{"name": labels[ix], "rectangle": list(box), 'type': ['moveTo', 'click']} for ix, box in enumerate(nms_boxes)]

        return button_items

    @staticmethod
    def get_best_matching_scale(image, template, threshold=0.8, scales=None):
        if scales is None:
            scales = [i / 10.0 for i in range(5, 2, 21)]

        all_matches = []
        max_score = -1
        best_scale = 1
        best_location = None
        for scale in scales:
            resized_template = cv2.resize(
                template, (int(template.shape[1] * scale), int(template.shape[0] * scale))
            )

            if (
                resized_template.shape[0] > image.shape[0]
                or resized_template.shape[1] > image.shape[1]
            ):
                continue

            result = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)

            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > max_score:
                max_score = max_val
                best_scale = scale
                best_location = max_loc

        return best_scale

    @staticmethod
    def multi_scale_template_matching(
        image, template, threshold=0.9, scales=[i / 10.0 for i in range(5, 2, 21)]
    ):
        all_matches = []
        all_score = []
        all_scale = 1
        for scale in scales:
            # resized_template = cv2.resize(template, (int(template.shape[1] * scale), int(template.shape[0] * scale)))

            resized_template = cv2.resize(
                template,
                (
                    int(template.shape[1] * scale * all_scale),
                    int(template.shape[0] * scale * all_scale),
                ),
            )
            image = cv2.resize(
                image, (int(image.shape[1] * all_scale), int(image.shape[0] * all_scale))
            )

            if (
                resized_template.shape[0] > image.shape[0]
                or resized_template.shape[1] > image.shape[1]
            ):
                continue

            result = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)

            # _, max_val, _, max_loc = cv2.minMaxLoc(result)

            locs = np.where(result >= threshold)
            for pt in zip(*locs[::-1]):  # Switch cols and rows
                all_matches.append((pt, scale))
                score_at_pt = result[pt[1], pt[0]]
                all_score.append(score_at_pt)

        return all_matches, all_score


    @staticmethod   
    def non_max_suppression(boxes, overlap_thresh, scores):
        boxes = np.array(boxes)

        if len(boxes) == 0:
            return [], []

        if boxes.dtype.kind == "i":
            boxes = boxes.astype("float")

        pick = []

        x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]

        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(scores)

        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)

            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])

            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)

            overlap = (w * h) / area[idxs[:last]]

            idxs = np.delete(
                idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0]))
            )

        return boxes[pick].astype("int"), pick


    @staticmethod
    def filter_data(meta_data):
        return [entry for entry in meta_data if entry["properties"]["texts"][0]]

    @staticmethod
    def sort_data_by_y_coordinate(data):
        return sorted(data, key=lambda entry: entry["properties"]["rectangle"][1])

    @staticmethod
    def sort_row_by_x_coordinate(row):
        return sorted(row, key=lambda element: element["properties"]["rectangle"][0])

    def organize_elements(self, sorted_data):
        elements = []
        current_row = []
        prev_y = None

        for entry in sorted_data:
            y = entry["properties"]["rectangle"][1]

            if prev_y is not None and abs(y - prev_y) > 10:
                elements.append(self.sort_row_by_x_coordinate(current_row))
                current_row = []

            element_name = self.construct_element_name(entry)
            current_row.append(
                {"name": element_name, "rectangle": entry["properties"]["rectangle"]}
            )
            prev_y = y

        if current_row:
            elements.append(self.sort_row_by_x_coordinate(current_row))

        return elements

    @staticmethod
    def construct_element_name(entry):
        if entry["properties"]["friendly_class_name"] in ["MenuItem", "Button"]:
            return entry["properties"]["texts"][0]
        else:
            return f"{entry['properties']['texts'][0]}|{entry['properties']['friendly_class_name']}"

    def run_parallel_tasks(self, func, param_list):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(func, *param) for param in param_list]
            return [future.result() for future in futures]

    @staticmethod
    def filter_data(meta_data):
        return [entry for entry in meta_data if entry["properties"]["texts"][0]]

    @staticmethod
    def sort_data_by_y_coordinate(data):
        return sorted(data, key=lambda entry: entry["properties"]["rectangle"][1])

    @staticmethod
    def sort_row_by_x_coordinate(row):
        return sorted(row, key=lambda element: element["properties"]["rectangle"][0])

    def organize_elements(self, sorted_data):
        elements = []
        current_row = []
        prev_y = None

        for entry in sorted_data:
            y = entry["properties"]["rectangle"][1]

            if prev_y is not None and abs(y - prev_y) > 10:
                elements.append(self.sort_row_by_x_coordinate(current_row))
                current_row = []

            element_name = self.construct_element_name(entry)
            current_row.append(
                {"name": element_name, "rectangle": entry["properties"]["rectangle"]}
            )
            prev_y = y

        if current_row:
            elements.append(self.sort_row_by_x_coordinate(current_row))

        return elements

    @staticmethod
    def construct_element_name(entry):
        if entry["properties"]["friendly_class_name"] in ["MenuItem", "Button"]:
            return entry["properties"]["texts"][0]
        else:
            return f"{entry['properties']['texts'][0]}|{entry['properties']['friendly_class_name']}"

    def run_parallel_tasks(self, func, param_list):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(func, *param) for param in param_list]
            return [future.result() for future in futures]
