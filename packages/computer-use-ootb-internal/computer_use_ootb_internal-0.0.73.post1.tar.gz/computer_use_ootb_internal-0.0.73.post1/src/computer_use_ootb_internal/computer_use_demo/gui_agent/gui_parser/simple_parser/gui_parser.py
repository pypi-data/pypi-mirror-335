import cv2
import numpy as np
import datetime
import requests
import importlib
# import textdistance
import glob
from PIL import Image
import ctypes
from .gui_parser_adobe import AdobeParser

from .text_detection import text_detection
from .icon_detection.icon_detection import detect_icons, IconDetector
from .utils import *

import os

from importlib import resources
import pathlib
import computer_use_ootb_internal

class GUIParser():
    name = "gui_parser"
    description = """
This tool can extract the information of screenshot.
Invoke command: gui_parser(query, visual[i])
:param query -> str, specific command. visual[i] -> image, the latest screenshot.
"""

    def __init__(self, cache_folder=".cache/", user_id=None, trace_id=None, scaleFactor="1.0x"):
        # Use pathlib for platform-independent path handling
        cache_path = pathlib.Path(cache_folder)
        cache_path.mkdir(exist_ok=True)
        ocr_cache_path = cache_path / "ocr"
        ocr_cache_path.mkdir(exist_ok=True)
        
        super(GUIParser, self).__init__()
        self.cache_folder = str(cache_path)
        print(f"Cache folder: {self.cache_folder}")
        
        self.task_id = get_current_time()
        self.parsers = {}
        self.temperature = 0
        self.gui_parser = None
        self.icon_template_threshold = 0.7
        try:
            ootb_path = os.getenv("OOTB_PATH")
            if ootb_path:
                self.ootb_database_path = pathlib.Path(ootb_path) / "ootbdatabase"
            else:
                # Fallback to package resources if env var not set
                with resources.path(__package__, "ootbdatabase") as db_path:
                    self.ootb_database_path = db_path
        except Exception as e:
            print(f"Error: {e}. OOTB_PATH is not set correctly.")
        self.user_id = user_id
        self.trace_id = trace_id
        self.scaleFactor = scaleFactor
        self.width = None 
        self.height = None

    def __call__(self, uia_data=None, screenshot_path=None, query=None, mode="uia", ocr_mode="googleocr"):
        screenshot_path = pathlib.Path(screenshot_path)
        if not screenshot_path.exists():
            raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")
            
        image = Image.open(screenshot_path)
        self.width, self.height = image.size

        if mode == "teach":
            if query and isinstance(query, list) and len(query) > 1:
                specific_icon_names = [item for item in query if self.is_image_path(item)]
                if specific_icon_names:
                    icon_template_folder = self.ootb_database_path / self.user_id / self.trace_id / "icons"
                    icon_template_folder.mkdir(parents=True, exist_ok=True)

                    print(f"icon_template_folder: {icon_template_folder}")
                    icon_detector = IconDetector(str(icon_template_folder))

                    detected_items = icon_detector(
                        screenshot_path=screenshot_path,
                        mode="teach",
                        threshold=self.icon_template_threshold, # TODO: setting on init
                        scale_factor=self.scaleFactor,
                        specific_icon_names=specific_icon_names,
                    )
                    
                    if detected_items:
                        icon_items = detected_items
            print("detected_icons:", icon_items)
            # 获取OCR文本结果
            ocr_elements = []
            if ocr and "texts" in ocr:
                for text_item in ocr["texts"]:
                    ocr_elements.append({
                        "name": text_item["content"],
                        "rectangle": text_item["bbox"],
                        "is_text": True
                    })
            
            # 合并所有元素
            all_elements = []
            all_elements.extend(icon_items)  # 添加图标元素
            all_elements.extend(ocr_elements)  # 添加文本元素
            
            # 创建主面板
            ocr_icon_parsed_gui = {
                "Screen": [{
                    "name": "Main Content",
                    "rectangle": [0, 0, self.width, self.height],
                    "elements": self.merge_elements({"combined_elements": all_elements})
                }]
            }
            
            # get uia parsed gui
            uia_parsed_gui = self.get_panel_uia(uia_data)
            self.postprocess_uia(uia_parsed_gui)
            
            # merge the code
            self.parsed_gui = self.merge_uia_and_teach_results(uia_parsed_gui, ocr_icon_parsed_gui)
            return self.parsed_gui
        
        # only use uia mode
        elif mode == "uia":
            # Parse the UI elements of the current window
            self.parsed_gui = {}
            self.exclude_class_name_list = []
            # if self.if_browser(window_name):
            #     self.exclude_class_name_list = [
            #         "Custom",
            #         "Menu",
            #         "Pane",
            #         "TabControl",
            #         "DataItem",
            #     ]
            # elif self.if_office(window_name):
            #     self.exclude_class_name_list = [
            #         "Custom",
            #         "Menu",
            #         "Pane",
            #         "Toolbar",
            #         "TabControl",
            #         "TreeItem",
            #         "DataItem",
            #         "Hyperlink",
            #     ]
            # else:
            #     self.exclude_class_name_list = []

            self.parsed_gui = self.get_panel_uia(uia_data)
            self.postprocess_uia(self.parsed_gui)

            return self.parsed_gui
        
        # OCR + full icon detection mode
        elif mode == "icon_ocr": 
            ocr = text_detection(screenshot_path)
            icon_template_folder = os.path.join(self.ootb_database_path, "ootbdatabase/teach_mode")
            icon_detector = IconDetector(icon_template_folder)
            icon_items = [
                icon_detector(
                    screenshot_path=screenshot_path,  mode="full_detect", threshold=0.6, scale_factor=self.scaleFactor
                )
            ]
            self.parsed_gui = self.postprocess_icon(
                "screen", icon_items, screenshot_path
            )
            for panel_item in self.parsed_gui["screen"]:
                temp = {}
                temp["editing_control"] = self.get_text(
                    panel_item, ocr, screenshot_path
                )

                panel_item["elements"] += self.merge_elements(temp)
                
        # OCR only mode
        else: 
            ocr = text_detection(screenshot_path)
            self.parsed_gui = self.postprocess_icon(
                "screen", [], screenshot_path
            )
            for panel_item in self.parsed_gui["screen"]:
                temp = {}
                temp["editing_control"] = self.get_text(
                    panel_item, ocr, screenshot_path
                )

                panel_item["elements"] += self.merge_elements(temp)
        
            
            return self.parsed_gui



    def if_browser(self, window_name):
        # check if ["Edge", "Chrome", "Firefox", "Safari", "Opera"] in window_name
        if any(browser in window_name for browser in ["Edge", "Chrome", "Firefox", "Safari", "Opera"]):
            return True
        return False
    
    def if_adobe(self, window_name):
        # check if ["Adobe Premiere Pro", "Adobe After Effect", "Adobe Acrobat"] in window_name
        if any(adobe in window_name for adobe in ["Adobe Premiere Pro", "Adobe After Effect", "Adobe Acrobat"]):
            return True
        return False

    def if_office(self, window_name):
        # check if ["Excel", "Word", "PowerPoint", "Outlook"] in window_name
        if any(office in window_name for office in ["Excel", "Word", "PowerPoint", "Outlook"]):
            return True
        return False
    
    @staticmethod
    def is_image_path(text):
        # Checking if the input text ends with typical image file extensions
        image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif")
        if text.endswith(image_extensions):
            return True
        else:
            return False

    @staticmethod
    def get_text(panel_item, ocr, screenshot_path):
        # Step1: Find all the texts in the panel
        panel_rect = panel_item["rectangle"]
        # 过滤出在panel区域内的文本
        panel_texts = []
        for item in ocr["texts"]:
            bbox = item["bbox"]
            # 检查文本是否在panel区域内
            if (bbox[0] >= panel_rect[0] and 
                bbox[1] >= panel_rect[1] and 
                bbox[2] <= panel_rect[2] and 
                bbox[3] <= panel_rect[3]):
                panel_texts.append(item)

        if not panel_texts:
            return []
            
        # obtain information about panel texts
        sorted_panel_texts = sorted(
            panel_texts, key=lambda x: (x["bbox"][1], x["bbox"][0])
        )
        
        # Step 2: Identify rows by grouping elements that are in approximately the same vertical position.
        editing_controls = []
        current_row = []
        if sorted_panel_texts:
            previous_y = sorted_panel_texts[0]["bbox"][1]

            for item in sorted_panel_texts:
                y1 = item["bbox"][1]
                # If the vertical position of the current item is significantly different from the previous one, start a new row.
                if abs(y1 - previous_y) > 15:
                    if current_row:  # 只有当current_row非空时才添加
                        editing_controls.append(current_row)
                    current_row = []

                current_row.append(
                    {
                        "name": item["content"],
                        "rectangle": item["bbox"],
                    }
                )
                previous_y = y1
                
            # Add the last row if not empty.
            if current_row:
                editing_controls.append(current_row)
                
        # Step 3: Sort elements within each row based on their horizontal position.
        for i, row in enumerate(editing_controls):
            editing_controls[i] = sorted(row, key=lambda x: x["rectangle"][0])
            
        return editing_controls
        
    def postprocess_icon(self, window_name, icon_items, screenshot_path):
        image = Image.open(screenshot_path)
        width, height = image.size
        result = {
            window_name: [
                {
                    "name": "Main Content",
                    "rectangle": [0, 0, width, height],
                    "elements": None
                }
            ]
        }
        return result

    @staticmethod
    def merge_elements(panel_item):
        # 检查是否为空
        if not panel_item or not any(panel_item.values()):
            return []
        
        # 收集所有元素
        all_elements = []
        for key, value in panel_item.items():
            if isinstance(value, list):
                all_elements.extend(value)
        
        if not all_elements:
            return []
        
        # 按Y轴分组,同一行的阈值为15像素
        y_sorted = sorted(all_elements, key=lambda x: (x["rectangle"][1] + x["rectangle"][3]) / 2)
        merged_control = []
        current_row = []
        previous_y = None
        
        for element in y_sorted:
            y_center = (element["rectangle"][1] + element["rectangle"][3]) / 2
            
            if previous_y is not None and abs(y_center - previous_y) > 15:
                if current_row:
                    # 对当前行按X轴排序
                    current_row.sort(key=lambda x: x["rectangle"][0])
                    merged_control.append(current_row)
                current_row = []
                
            current_row.append(element)
            previous_y = y_center
        
        # 添加最后一行
        if current_row:
            current_row.sort(key=lambda x: x["rectangle"][0])
            merged_control.append(current_row)
            
        # 对所有行按Y轴中心点排序
        merged_control.sort(
            key=lambda row: (row[0]["rectangle"][1] + row[0]["rectangle"][3]) / 2
        )
        
        return merged_control

    def postprocess_uia(self, metadata):
        # iterate each window
        for window_data in metadata.values():

            for element_data in window_data:
                # get all elements of current level
                elements = element_data.get("elements", [])

                # if the class name is TitleBar, regain the rectangle of the whole panel
                if element_data["class_name"] == "TitleBar" and len(elements) > 0:
                    left = min(e.get("rectangle", [0, 0, 0, 0])[0] for e in elements)
                    top = min(e.get("rectangle", [0, 0, 0, 0])[1] for e in elements)
                    right = max(e.get("rectangle", [0, 0, 0, 0])[2] for e in elements)
                    bottom = max(e.get("rectangle", [0, 0, 0, 0])[3] for e in elements)
                    element_data["rectangle"] = [left, top, right, bottom]
                # sort elements by x and y
                element_data["elements"] = sort_elements_by_xy(elements)

        return metadata
    
    def merge_uia_and_teach_results(self,uia_result, teach_result):
        def calculate_overlap(rect1, rect2):
            # 计算两个矩形的重叠面积
            x1 = max(rect1[0], rect2[0])
            y1 = max(rect1[1], rect2[1])
            x2 = min(rect1[2], rect2[2])
            y2 = min(rect1[3], rect2[3])
            
            if x1 >= x2 or y1 >= y2:
                return 0
                
            overlap_width = x2 - x1
            overlap_height = y2 - y1
            
            return overlap_width * overlap_height

        def is_significant_overlap(ocr_element, uia_element):
            ocr_rect = ocr_element["rectangle"]
            uia_rect = uia_element["rectangle"]
            
            overlap_area = calculate_overlap(ocr_rect, uia_rect)
            ocr_area = (ocr_rect[2] - ocr_rect[0]) * (ocr_rect[3] - ocr_rect[1])
            
            return overlap_area > 0.5 * ocr_area if ocr_area > 0 else False

        merged_result = uia_result.copy()

        all_ocr_elements = []
        # 遍历teach模式下的OCR文本元素
        for screen in teach_result.get("Screen", []):
            for elements_row in screen.get("elements", []):
                for element in elements_row:
                    if element["is_text"]:
                        should_add = True
                        # 检查是否与任何UIA元素有显著重叠
                        for window_name, panels in merged_result.items():
                            for panel in panels:
                                for elements_list in panel.get("elements", []):
                                    for uia_element in elements_list:
                                        if is_significant_overlap(element, uia_element):
                                            should_add = False
                                            break
                                    if not should_add:
                                        break
                                if not should_add:
                                    break
                            if not should_add:
                                break
                                
                        # 如果没有显著重叠，将OCR元素添加到最合适的面板中
                        if should_add:
                            # 找到最合适的面板（这里简单地添加到第一个面板）
                            all_ocr_elements.append(element)
                    else:
                        all_ocr_elements.append(element)
                        
        merged_result["OCR"] = [{
                    "name": "Main Content",
                    "rectangle": [0, 0, self.width, self.height],
                    "elements": [all_ocr_elements]
                }]
        return merged_result
    def get_panel_uia(self, control_info_list):
        # 定义文本到面板名称的映射
        text2panel_name = {
            "新建会话属性": "New session properties",
            "会话管理器": "Session manager",
            "任务栏": "Taskbar",
        }

        # 递归处理控件信息
        def recurse_controls(control_info, dialog_components, depth, software_name):
            children = control_info.get("children", [])
            if not children:
                return
            
            for child_control in children:
                child_properties = child_control.get("properties", {})
                child_friendly_class_name = child_properties.get("friendly_class_name", "")
                
                # 如果控件类型在排除列表中，跳过处理
                if child_friendly_class_name in self.exclude_class_name_list:
                    continue
                    
                # 获取控件名称
                child_texts = child_properties.get("texts", [])
                if not child_texts:
                    child_properties_name = ""
                elif isinstance(child_texts[0], list):
                    result = []
                    for item in child_texts:
                        if isinstance(item, list) and item and isinstance(item[0], str):
                            result.append("".join(item))
                        elif isinstance(item, str):
                            result.append(item)
                    child_properties_name = "".join(result)
                else:
                    child_properties_name = child_texts[0]
                
                # 特殊处理编辑框和组合框
                if child_friendly_class_name in ["Edit", "ComboBox"] and not child_properties_name:
                    child_properties_name = "Search Bar"
                
                # 判断是否需要处理该控件
                rectangle = child_properties.get("rectangle", [0, 0, 0, 0])
                automation_id = child_properties.get("automation_id", "")
                
                # 放宽控件过滤条件
                browser_list = ["Edge", "Chrome", "Firefox", "Opera", "Safari"]
                is_browser = False
                for browser in browser_list:
                    if browser in software_name:
                        is_browser = True
                        break
                should_process = (
                    # 任务栏特殊处理
                    (software_name == "Taskbar" and child_friendly_class_name in ["Button", "Static", "Image"]) or
                    # 浏览器特殊处理
                    (is_browser and child_friendly_class_name in ["Pane", "Button", "Edit", "Tab", "TabItem", "Document", "Group"]) or
                    # 常规控件处理
                    (not child_control.get("children", []) or  # 没有子控件的元素保留
                     automation_id or  # 有automation_id的控件保留
                     child_friendly_class_name not in self.exclude_class_name_list)  # 不在排除列表中的控件保留
                ) and (
                    # 基本条件检查
                    len(rectangle) == 4 and
                    not all(element == 0 for element in rectangle) and
                    (child_properties_name not in ["", '"'] or automation_id)  # 允许有automation_id的空名称控件
                )
                
                if should_process:
                    # 获取控件的矩形边界
                    left, top, right, bottom = rectangle
                    dialog_rect = dialog_components.get("rectangle", [0, 0, 0, 0])
                    if len(dialog_rect) != 4:
                        dialog_rect = [0, 0, 0, 0]
                    left_bound, top_bound, right_bound, bottom_bound = dialog_rect

                    # 根据软件名称进行特殊逻辑处理
                    if software_name not in ["Taskbar"] and not is_browser:  # 任务栏和浏览器不裁剪坐标
                        child_properties["rectangle"] = [
                            max(left, left_bound),
                            max(top, top_bound),
                            min(right, right_bound),
                            min(bottom, bottom_bound)
                        ]
                    else:
                        child_properties["rectangle"] = [left, top, right, bottom]
                    
                    # 检查矩形有效性
                    if (child_properties["rectangle"][0] < child_properties["rectangle"][2] 
                        and child_properties["rectangle"][1] < child_properties["rectangle"][3]):
                        
                        # 添加控件信息到对话框组件
                        element_info = {
                            "name": child_properties_name.replace("\u200b", ""),
                            "rectangle": child_properties["rectangle"],
                            "class_name": child_friendly_class_name,
                            "type": ["Click", "rightClick"],
                            "depth": f"{depth}-{dialog_components.get('count', 1)}"
                        }
                        
                        # 添加automation_id（如果存在）
                        if automation_id:
                            element_info["automation_id"] = automation_id
                            
                        dialog_components.setdefault("elements", []).append(element_info)
                        dialog_components["count"] = dialog_components.get("count", 1) + 1

                # 递归处理子控件
                recurse_controls(child_control, dialog_components, depth, software_name)

        dialog_components = {}

        # 遍历每个软件的控件信息
        for software_name, controls in control_info_list.items():
            if not controls:  # 跳过空的控件列表
                continue
                
            dialog_components[software_name] = []
            
            for control_info in controls:
                # 判断是否为需要处理的对话框类型
                control_properties = control_info.get("properties", {})
                friendly_class_name = control_properties.get("friendly_class_name", "")
                
                # 放宽面板类型的限制
                panel_types = ["Dialog", "Pane", "GroupBox", "TitleBar", "Menu", "Document", "ListBox", "AppBar", "Tab", "Group"]
                if (friendly_class_name in panel_types and control_info.get("children")):
                    
                    control_texts = control_properties.get("texts", [""])
                    control_name = control_texts[0] if control_texts else ""
                    automation_id = control_properties.get("automation_id", "")
                    
                    # 设置控件名称
                    if not control_name and automation_id:
                        control_name = automation_id  # 使用automation_id作为备选名称
                    elif not control_name:
                        if friendly_class_name == "TitleBar":
                            control_name = "Title Bar"
                        elif friendly_class_name == "Document":
                            control_name = "Main Content"
                        elif friendly_class_name == "Pane":
                            if software_name == "Taskbar":
                                control_name = "Taskbar"
                            elif "Edge" in software_name or "Chrome" in software_name or "Firefox" in software_name:
                                control_name = "Browser Content"
                            else:
                                control_name = "Navigation Bar" if software_name in ["web", "web video"] else "Main Content"
                    elif friendly_class_name == "Document" and software_name in ["web", "web video"]:
                        control_name = "Main Content"
                    
                    # 转换文本名称
                    control_name = text2panel_name.get(control_name, control_name)

                    # 初始化对话框组件并递归处理控件
                    panel_info = {
                        "name": control_name,
                        "rectangle": control_properties.get("rectangle", [0, 0, 0, 0]),
                        "class_name": friendly_class_name,
                        "depth": "1",
                        "elements": [],
                        "count": 1
                    }
                    
                    # 添加automation_id（如果存在）
                    if automation_id:
                        panel_info["automation_id"] = automation_id
                        
                    dialog_components[software_name].append(panel_info)
                    recurse_controls(control_info, dialog_components[software_name][-1], "1", software_name)
                    
        return dialog_components
    
import matplotlib.pyplot as plt
import cv2
import matplotlib.font_manager as fm

def show_img_with_box_points(img, box, ax, color="red"):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor=color, facecolor=(0, 0, 0, 0), lw=0.4))

def extract_second_underscore_content(filename):
    parts = filename.split('_')
    if len(parts) > 1 and "@" in filename:
        return parts[1]
    return filename

def show_guiParserd(gui, img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.figure(dpi=500)
    plt.axis('off')
    plt.imshow(img)

    # 设置微软雅黑字体
    # font_path = "C:/Windows/Fonts/msyh.ttc"  # Windows系统上的微软雅黑字体路径
    # prop = fm.FontProperties(fname=font_path)
    item_cache = []
    for windows_name, panel_list in gui.items():
        print("windows_name: ", windows_name)
        print("panel_list: ", panel_list)
        for sequence in panel_list:
            # print("sequence: ", sequence)
            show_img_with_box_points(img, sequence["rectangle"], plt.gca(), color="green")
            if len(sequence["name"]) < 100:
                plt.text(sequence["rectangle"][0], sequence["rectangle"][1], sequence["name"], 
                        fontsize=4, color='green')
            for _, items in enumerate(sequence['elements']):
                item_cache.extend(items)
    for item in item_cache:
        try:
            if "rectangle" in item:
                if len(item["name"]) > 200:
                    continue
                box = item["rectangle"]
                if "current_step_icon" in item.keys() and item["current_step_icon"]:
                    show_img_with_box_points(img, box, plt.gca(),color="green")
                    plt.text(box[0], box[3]+25, "Current Step Icon", fontsize=3, color='green')
                else:
                    show_img_with_box_points(img, box, plt.gca(),color="blue")
                plt.text(box[0], box[1], extract_second_underscore_content(item["name"]), 
                        fontsize=2, color='red')
        except Exception as e:
            print(e)
    # plt.savefig('gui_parser5.png', bbox_inches='tight', pad_inches=0)
    plt.show()



def get_screen_info():
    try:
        scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        scaleFactor = str(scaleFactor) + "x"
    except Exception as e:
        print(e)
        scaleFactor = "1.0x"
    return scaleFactor
        
def parse_gui(user_id, trace_id, screenshot_path, user_scaleFactor="auto", uia_data=None, query=None, mode="uia", ocr_mode="googleocr"):
    # TODO: check mult-screens
    if user_scaleFactor == "auto":
        user_scaleFactor = get_screen_info()
    print("user_scaleFactor: ", user_scaleFactor)
    gui_parser = GUIParser(user_id=user_id, trace_id=trace_id, scaleFactor=user_scaleFactor)
    return gui_parser(uia_data=uia_data, screenshot_path=screenshot_path, query=query, mode=mode, ocr_mode=ocr_mode)

import json
import sys
if __name__ == "__main__":

    screenshot_path = r'D:\develop\computer_use_ootb_internal-main\.cache\20241222_041910\screenshot-0.png'
    meta_data = json.load(open("test_uia_data.json", "r"))
    gui_parser = GUIParser(user_id="test", trace_id="test", scaleFactor="1.0x")
    uia_gui = gui_parser.get_panel_uia(meta_data)
    uia_gui = gui_parser.postprocess_uia(uia_gui)
    with open("test_uia_gui.json", "w") as f:
        json.dump(uia_gui, f, indent=4)


