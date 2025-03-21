import os
import cv2
import numpy as np
import json
import time
import base64
import requests
from pathlib import Path
# import easyocr

def text_detection(img_path, ocr_mode="googleocr"):
    if ocr_mode == "googleocr":
        ocr = GoogleOCR()
    # elif ocr_mode == "easyocr":
    #     ocr = EasyOCR()
    img, result_json = ocr.detect_text(img_path)
    return result_json

# class EasyOCR:
#     def __init__(self, api_key=None):
#         self.reader = easyocr.Reader(['en', 'ch_sim'])

#     def detect_text(self, input_file, save_png=True, cache_folder=".cache/ocr"):
#         start = time.time()

#         # Prepare paths
#         if isinstance(input_file, str):
#             name = os.path.splitext(os.path.basename(input_file))[0]
#         else:
#             name = "temp_image"
#             Path(cache_folder).mkdir(parents=True, exist_ok=True)
#             input_file.save(os.path.join(cache_folder, f"{name}.png"))
#             input_file = os.path.join(cache_folder, f"{name}.png")

#         # Perform OCR
#         ocr_result = self._call_easyocr(input_file)
#         if not ocr_result:
#             return None, None

#         texts = self._convert_ocr_format(ocr_result)
#         texts = self._merge_texts(self._filter_noise(texts))
#         texts = self._merge_sentences(texts)

#         # Load image and visualize results
#         img = cv2.imread(input_file)
#         if save_png:
#             output_img_path = os.path.join(cache_folder, f"{name}-ocr.png")
#             img = self._visualize_texts(img, texts, write_path=output_img_path)

#         # Save results
#         output_json = self._save_results_json(
#             os.path.join(cache_folder, f"{name}-ocr.json"), texts, img.shape
#         )
#         print(
#             f"[Text Detection Completed in {time.time() - start:.3f} s] "
#             f"Input: {input_file}, Output: {os.path.join(cache_folder, f'{name}-ocr.json')}"
#         )

#         return img, output_json

#     def _call_easyocr(self, img_path):
#         results = self.reader.readtext(img_path)
#         return results

#     @staticmethod
#     def _convert_ocr_format(ocr_result):
#         texts = []
#         for i, result in enumerate(ocr_result):
#             bbox, content, confidence = result
#             location = {
#                 "left": min(point[0] for point in bbox),
#                 "top": min(point[1] for point in bbox),
#                 "right": max(point[0] for point in bbox),
#                 "bottom": max(point[1] for point in bbox),
#             }
#             texts.append(Text(i, content, location))
#         return texts

#     @staticmethod
#     def _filter_noise(texts):
#         return [
#             text
#             for text in texts
#             if len(text.content) > 1 or text.content.lower() in ".,!?$%:&+"
#         ]

#     @staticmethod
#     def _merge_texts(texts):
#         merged = True
#         while merged:
#             merged = False
#             temp_set = []
#             for text_a in texts:
#                 for text_b in temp_set:
#                     if text_a.is_intersected(text_b, bias=2):
#                         text_b.merge_text(text_a)
#                         merged = True
#                         break
#                 else:
#                     temp_set.append(text_a)
#             texts = temp_set
#         return texts

#     @staticmethod
#     def _merge_sentences(texts):
#         merged = True
#         while merged:
#             merged = False
#             temp_set = []
#             for text_a in texts:
#                 for text_b in temp_set:
#                     if text_a.is_on_same_line(text_b, bias_justify=4, bias_gap=6):
#                         text_b.merge_text(text_a)
#                         merged = True
#                         break
#                 else:
#                     temp_set.append(text_a)
#             texts = temp_set
#         return texts

#     @staticmethod
#     def _visualize_texts(img, texts, write_path=None):
#         for text in texts:
#             text.visualize_element(img, line=2)
#         if write_path:
#             cv2.imwrite(write_path, img)
#         return img

#     @staticmethod
#     def _save_results_json(file_path, texts, img_shape):
#         output = {"img_shape": [int(x) for x in img_shape], "texts": []}
#         for text in texts:
#             loc = text.location
#             output["texts"].append({
#                 "content": text.content, 
#                 "bbox": [
#                     int(loc["left"]), 
#                     int(loc["top"]), 
#                     int(loc["right"]), 
#                     int(loc["bottom"])
#                 ]
#             })
        
#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(output, f, indent=4, ensure_ascii=False)
#         return output



class GoogleOCR:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")

    def detect_text(self, input_file, save_png=True, cache_folder=".cache/ocr"):
        start = time.time()

        # Prepare paths
        if isinstance(input_file, str):
            name = os.path.splitext(os.path.basename(input_file))[0]
        else:
            name = "temp_image"
            Path(cache_folder).mkdir(parents=True, exist_ok=True)
            input_file.save(os.path.join(cache_folder, f"{name}.png"))
            input_file = os.path.join(cache_folder, f"{name}.png")

        # Perform OCR
        ocr_result = self._call_google_ocr(input_file)
        if not ocr_result:
            return None, None

        texts = self._convert_ocr_format(ocr_result)
        texts = self._merge_texts(self._filter_noise(texts))
        texts = self._merge_sentences(texts)

        # Load image and visualize results
        img = cv2.imread(input_file)
        if save_png:
            output_img_path = os.path.join(cache_folder, f"{name}-ocr.png")
            img = self._visualize_texts(img, texts, write_path=output_img_path)

        # Save results
        output_json = self._save_results_json(
            os.path.join(cache_folder, f"{name}-ocr.json"), texts, img.shape
        )
        print(
            f"[Text Detection Completed in {time.time() - start:.3f} s] "
            f"Input: {input_file}, Output: {os.path.join(cache_folder, f'{name}-ocr.json')}"
        )

        return img, output_json

    def _call_google_ocr(self, img_path):
        with open(img_path, "rb") as image_file:
            content = image_file.read()
            encoded_image = base64.b64encode(content).decode("utf-8")

        request_data = {
            "requests": [
                {
                    "image": {"content": encoded_image},
                    "features": [{"type": "TEXT_DETECTION"}],
                }
            ]
        }

        response = requests.post(
            f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(request_data),
        )

        if response.status_code == 200:
            results = response.json()
            annotations = results.get("responses", [{}])[0].get("textAnnotations", [])
            return annotations[1:] if annotations else None
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    @staticmethod
    def _convert_ocr_format(ocr_result):
        texts = []
        for i, result in enumerate(ocr_result):
            try:
                vertices = result["boundingPoly"]["vertices"]
                content = result["description"]
                location = {
                    "left": min(v.get("x", 0) for v in vertices),
                    "top": min(v.get("y", 0) for v in vertices),
                    "right": max(v.get("x", 0) for v in vertices),
                    "bottom": max(v.get("y", 0) for v in vertices),
                }
                texts.append(Text(i, content, location))
            except KeyError:
                continue
        return texts

    @staticmethod
    def _filter_noise(texts):
        return [
            text
            for text in texts
            if len(text.content) > 1 or text.content.lower() in ".,!?$%:&+"
        ]

    @staticmethod
    def _merge_texts(texts):
        merged = True
        while merged:
            merged = False
            temp_set = []
            for text_a in texts:
                for text_b in temp_set:
                    if text_a.is_intersected(text_b, bias=2):
                        text_b.merge_text(text_a)
                        merged = True
                        break
                else:
                    temp_set.append(text_a)
            texts = temp_set
        return texts

    @staticmethod
    def _merge_sentences(texts):
        merged = True
        while merged:
            merged = False
            temp_set = []
            for text_a in texts:
                for text_b in temp_set:
                    if text_a.is_on_same_line(text_b, bias_justify=4, bias_gap=6):
                        text_b.merge_text(text_a)
                        merged = True
                        break
                else:
                    temp_set.append(text_a)
            texts = temp_set
        return texts

    @staticmethod
    def _visualize_texts(img, texts, write_path=None):
        for text in texts:
            text.visualize_element(img, line=2)
        if write_path:
            cv2.imwrite(write_path, img)
        return img

    @staticmethod
    def _save_results_json(file_path, texts, img_shape):
        output = {"img_shape": [int(x) for x in img_shape], "texts": []}
        for text in texts:
            loc = text.location
            output["texts"].append({
                "content": text.content, 
                "bbox": [
                    int(loc["left"]), 
                    int(loc["top"]), 
                    int(loc["right"]), 
                    int(loc["bottom"])
                ]
            })
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
        return output


class Text:
    def __init__(self, id, content, location):
        self.id = id
        self.content = content
        self.location = location

    def is_on_same_line(self, other, bias_gap, bias_justify):
        # 检查是否在同一水平线上
        if abs(self.location["top"] - other.location["top"]) >= bias_justify:
            return False
            
        # 计算两个文本框之间的水平距离
        if self.location["left"] < other.location["left"]:
            horizontal_gap = other.location["left"] - self.location["right"]
        else:
            horizontal_gap = self.location["left"] - other.location["right"]
            
        # 只有当水平间距小于阈值时才合并
        return horizontal_gap <= bias_gap

    def is_intersected(self, other, bias):
        l_a, l_b = self.location, other.location
        return (
            max(l_a["left"], l_b["left"]) + bias
            < min(l_a["right"], l_b["right"])
            and max(l_a["top"], l_b["top"]) + bias
            < min(l_a["bottom"], l_b["bottom"])
        )

    def merge_text(self, other):
        loc = self.location
        other_loc = other.location
        self.location = {
            "left": min(loc["left"], other_loc["left"]),
            "top": min(loc["top"], other_loc["top"]),
            "right": max(loc["right"], other_loc["right"]),
            "bottom": max(loc["bottom"], other_loc["bottom"]),
        }
        self.content += " " + other.content

    def visualize_element(self, img, color=(0, 0, 255), line=1):
        loc = self.location
        try:
            left = int(loc["left"]) if loc["left"] is not None else 0
            top = int(loc["top"]) if loc["top"] is not None else 0
            right = int(loc["right"]) if loc["right"] is not None else 0
            bottom = int(loc["bottom"]) if loc["bottom"] is not None else 0
            
            if left >= 0 and top >= 0 and right > left and bottom > top:
                cv2.rectangle(
                    img, (left, top), (right, bottom), color, line
                )
        except (ValueError, TypeError) as e:
            print(f"Warning: Invalid coordinates in text visualization: {loc}")
            return img


# Example usage
if __name__ == "__main__":
    ocr = text_detection(r"D:\develop\computer_use_ootb_internal-main\.cache\20241214_023408\screenshot-0.png")
    print(ocr)