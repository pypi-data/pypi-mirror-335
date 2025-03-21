import cv2
import numpy as np
import os
import re
import glob
from PIL import Image
import ctypes


class IconDetector:
    def __init__(self, icon_folder="./template"):
        self.icon_folder = icon_folder
        print("ICON FOLDER:", self.icon_folder)
        
    def __call__(
        self,
        screenshot_path,
        mode="teach",
        threshold=0.70,
        scale_factor="1.0x",
        specific_icon_names:list=None,
    ):
        image = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        templates = self.load_icon_templates(
            self.icon_folder,
            scale_factor,
            specific_icon_names
        )
        # print("specific_icon_names: ", specific_icon_names)
        # print("templates: ", templates)
        all_boxes, all_scores, labels = [], [], []
        for template in templates:
            icon_name = template["name"].replace(".png", "")
            icon_template = template["template"]

            # print(icon_name)

            result = cv2.matchTemplate(image, icon_template, cv2.TM_CCOEFF_NORMED)

            locs = np.where(result >= threshold)
            icon_width, icon_height = icon_template.shape[1], icon_template.shape[0]

            for pt in zip(*locs[::-1]):
                pt_x, pt_y = pt
                end_x = pt_x + icon_width
                end_y = pt_y + icon_height
                all_boxes.append([pt_x, pt_y, end_x, end_y])
                all_scores.append(result[pt_y, pt_x])
                # if teach mode, only detect the current step icon
                if template.get("current_step_icon", False):
                    labels.append(f"{icon_name} (click here for reproducing the action)")
                ## if not teach mode, detect all the icons
                else:
                    labels.append(icon_name)
        
        nms_boxes, pick = self.non_max_suppression(all_boxes, 0.5, all_scores)
        labels = [labels[i] for i in pick]
        # print("labels: ", labels)
        # 对于box 中的每一个元素, 用python 普通的int类型表示
        nms_boxes = [[int(box[0]), int(box[1]), int(box[2]), int(box[3])] for box in nms_boxes]
        button_items = [
            {
                "name": labels[ix],
                "rectangle": list(box),
                "is_text": False,
                "current_step_icon": "click here for reproducing the action" in labels[ix]
            }
            for ix, box in enumerate(nms_boxes)

        ]
        # print("button_items: ", button_items)
        
        return button_items
    
    def non_max_suppression(self, boxes, overlap_thresh, scores):
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


    # Teach mode only one icon
    def load_icon_templates(self, icon_folder:str, scale_factor:str="1.0x", specific_icon_names:list=None):
        icons = []
        specific_icon_template_flag = False
        # 如果提供了specific_icon_names,先处理这些路径
        if specific_icon_names:
            specific_icon_template_flag = True
        #     for icon_path in specific_icon_names:
        #         full_path = os.path.join(icon_folder, icon_path)
        #         print("FULL PATH:", full_path)
        #         if os.path.exists(full_path):
        #             print(f"Found icon at: {full_path}")
        #             current_step_icons.add(os.path.normpath(full_path))
        
        # print("Current step icons:", current_step_icons)
        # 支持的图片格式
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        # print("icon_folder: ", icon_folder)
        # 使用os.walk遍历文件夹
        for root, dirs, files in os.walk(icon_folder):
            for dir in dirs:
                scale_match = re.match(r'(\d+\.?\d*)x', dir)
                if scale_match:
                    template_scale_factor = scale_match.group(1)
                else:
                    raise ValueError(f"Invalid scale factor: {os.path.join(icon_folder, dir)}")
                # print("root: ", root)
                # print("files: ", files)
                for root, dirs, files in os.walk(os.path.join(icon_folder, dir)):
                    for filename in files:
                        # print("filename: ", filename)
                        if any(filename.lower().endswith(ext) for ext in image_extensions):
                            template_path = os.path.join(root, filename)
                            try:
                                name = os.path.splitext(filename)[0]
                                name = re.sub(r"^\d+_", "", name) + "|icon"
                                
                                icon_info = {
                                    "name": name,
                                    "path": template_path,
                                    "scale_factor": float(template_scale_factor),
                                    "current_step_icon": False
                                }
                                if specific_icon_template_flag:
                                    # only load the specific icon
                                    # print("specific_icon_names: ", specific_icon_names)
                                    # print("os.path.normpath(template_path): ", filename)
                                    if filename in specific_icon_names:
                                        icon_info["current_step_icon"] = True
                                        icons.append(icon_info)
                                else:
                                    # load all the icons
                                    icons.append(icon_info)
                                
                            except Exception as e:
                                print(f"Error processing template {template_path}: {str(e)}")
                                continue

        # 处理缩放
        for icon in icons:
            try:
                scale_factor_value = float(scale_factor[:-1]) if scale_factor.endswith('x') else float(scale_factor)
                icon_scale_factor_value = float(icon["scale_factor"])
                factor = scale_factor_value / icon_scale_factor_value
                print("factor: ", factor)
                icon["template"] = self.resize_image(icon["path"], factor)
            except Exception as e:
                print(f"Error processing template {icon['name']}: {str(e)}")
                continue
                    

        # show all the icons in the template folder
        for icon in icons:
            print("icon: ", icon["name"], icon["path"], icon["scale_factor"], icon["current_step_icon"])
        
        print("Icons Template loaded: ", len(icons))
        return icons

    @staticmethod
    def resize_image(input_path, factor):
        # Open the image
        with Image.open(input_path) as img:
            # Calculate new size
            new_size = (int(img.width * factor), int(img.height * factor))
            # Resize the image
            resized_img = img.resize(new_size, Image.LANCZOS)
            # Convert to NumPy array
            resized_img = np.array(resized_img)
            ## important! convert the image to RGB
            resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
        return resized_img



import matplotlib.pyplot as plt


def draw_detected_icons(image_path, detections):
    # 读取图像
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 遍历每个检测到的图标
    for detection in detections:
        name = detection["name"]
        x1, y1, x2, y2 = detection["rectangle"]
        # 画矩形框
        cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
        # 在矩形框上方添加标签
        cv2.putText(
            image, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2
        )

    # 使用 Matplotlib 显示图像
    plt.imshow(image)
    plt.axis("off")
    plt.show()

    # 保存图像（如果需要）
    # cv2.imwrite("output_with_icons.png", image)


def detect_icons(icon_folder, image_path, threshold=0.75, scale_factor="1.0x", specific_icon_names=None):
    # 初始化图标检测器
    detector = IconDetector(icon_folder)
    
    # 检测图标
    detections = detector(
        screenshot_path=image_path,
        threshold=threshold,
        scale_factor=scale_factor,
        mode="teach",  # 确保使用正确的模式
        specific_icon_names=specific_icon_names,
    )
    
    return detections


def get_screen_resize_factor():
    scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    scaleFactor = str(scaleFactor) + "x"
    return scaleFactor

# 示例调用
if __name__ == "__main__":
    buttons = detect_icons(
        icon_folder=r"",
        image_path=r"",
        threshold=0.75,
        scale_factor="1.5x",
        specific_icon_names=[r"test\1.5x\macOS.png"]
    )
    draw_detected_icons(
        r"D:\develop\computer_use_ootb_internal-main\.cache\20241214_023408\screenshot-0.png", buttons
    )

