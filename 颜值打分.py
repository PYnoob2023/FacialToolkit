import cv2
import numpy as np
from tkinter import filedialog, Tk, Text, Label, Button, messagebox, PhotoImage
from PIL import Image, ImageTk, ImageEnhance
import dlib
from tkinter import ttk

class BeautyCalculator:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        self.weights = {
            "脸部长宽比": 1,
            "鼻子长宽比": 1,
            "嘴唇厚度": 1,
            "嘴唇曲率": 1,
            "眼睛大小": 1,
            "眼睛形状": 1
        }

    def map_score(self, score):
        return max(0, min(score, 100))

    def calculate_beauty_score(self, image_path):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)

        if not faces:
            return "图像中未检测到人脸。"

        face = faces[0]
        landmarks = self.predictor(gray, face)
        beauty_score, detailed_scores = self.calculate_improved_beauty_score(landmarks)

        return beauty_score, detailed_scores

    def calculate_improved_beauty_score(self, landmarks):
        beauty_score = 0
        detailed_scores = {}

        eye_size = (self.calculate_distance(landmarks.part(37), landmarks.part(40)) +
                    self.calculate_distance(landmarks.part(38), landmarks.part(41))) / 2

        total_weight = sum(self.weights.values())

        for item in self.weights.keys():
            score = self.calculate_item_score(item, landmarks, eye_size)
            beauty_score += score * (self.weights[item] / total_weight)
            detailed_scores[item] = score

        beauty_score = self.map_score(round(beauty_score))
        return beauty_score, detailed_scores

    def calculate_item_score(self, item, landmarks, eye_size):
        indices = {
            "脸部长宽比": [16, 0, 8, 27],
            "鼻子长宽比": [35, 31, 33, 27],
            "嘴唇厚度": [66, 62, 58, 54],
            "嘴唇曲率": [48, 54, 51],
            "眼睛大小": [37, 40, 38, 41],
            "眼睛形状": [36, 39, 42, 45]
        }

        if item == "脸部长宽比":
            face_width = self.calculate_distance(landmarks.part(indices[item][0]), landmarks.part(indices[item][1]))
            face_height = landmarks.part(indices[item][2]).y - landmarks.part(indices[item][3]).y
            face_ratio = face_width / face_height
            return self.map_score(round(100 * np.abs(1.6 - face_ratio) / 0.4))
        elif item == "鼻子长宽比":
            nose_width = self.calculate_distance(landmarks.part(indices[item][0]), landmarks.part(indices[item][1]))
            nose_length = landmarks.part(indices[item][2]).y - landmarks.part(indices[item][3]).y
            nose_ratio = nose_width / nose_length
            return self.map_score(round(100 * np.abs(0.5 - nose_ratio) / 0.2))
        elif item == "嘴唇厚度":
            lip_thickness = (landmarks.part(indices[item][0]).y - landmarks.part(indices[item][1]).y +
                             landmarks.part(indices[item][2]).y - landmarks.part(indices[item][3]).y) / 2
            return self.map_score(round(100 * lip_thickness / 10))
        elif item == "嘴唇曲率":
            lip_curvature = self.calculate_distance(landmarks.part(indices[item][0]), landmarks.part(indices[item][1])) / (
                        landmarks.part(indices[item][2]).x - landmarks.part(indices[item][0]).x)
            return self.map_score(round(100 * lip_curvature / 0.5))
        elif item == "眼睛大小":
            return self.map_score(round(100 * eye_size / 10))
        elif item == "眼睛形状":
            eye_shape = (self.calculate_distance(landmarks.part(indices[item][0]), landmarks.part(indices[item][1])) +
                          self.calculate_distance(landmarks.part(indices[item][2]), landmarks.part(indices[item][3]))) / (
                                     eye_size * 2)
            return self.map_score(round(100 * eye_shape / 0.5))
        else:
            return 0

    def calculate_distance(self, point1, point2):
        return np.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


class BeautyApp:
    def __init__(self, root, beauty_calculator):
        self.root = root
        self.root.title("颜值评分")
        self.beauty_calculator = beauty_calculator

        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 12))

        self.label = ttk.Label(root, text="选择一张照片进行颜值评分")
        self.label.pack(padx=10, pady=10)

        self.button = ttk.Button(root, text="选择照片", command=self.select_image)
        self.button.pack(pady=10)

        self.textbox = Text(root, state='disabled', height=10, width=40)
        self.textbox.pack(pady=10)

        self.image_label = ttk.Label(root)
        self.image_label.pack(pady=10)

        self.exit_button = ttk.Button(self.root, text="退出", command=self.exit_program)
        self.exit_button.pack(pady=10)

    def horizontal_scanline_effect(self, alpha):
        alpha += 0.1
        if alpha < 1.0:
            self.image_label.after(50, lambda: self.horizontal_scanline_effect(alpha))
        else:
            # After the scanline effect, calculate and display scores
            beauty_score, detailed_scores = self.beauty_calculator.calculate_beauty_score(self.current_image_path)
            self.show_scores(beauty_score, detailed_scores)

    def display_image(self, file_path):
        self.current_image_path = file_path

        image = Image.open(file_path)
        raw_width, raw_height = image.size
        ratio = raw_width / raw_height
        new_width = 300
        new_height = int(new_width / ratio)
        image = image.resize((new_width, new_height), Image.LANCZOS)

        photo = ImageTk.PhotoImage(image)

        self.image_label.config(image=photo)
        self.image_label.image = photo

        self.horizontal_scanline_effect(0.0)

    def select_image(self):
        file_path = filedialog.askopenfilename()
        self.display_image(file_path)

    def show_scores(self, beauty_score, detailed_scores):
        self.textbox.config(state='normal')
        self.textbox.delete(1.0, 'end')
        self.textbox.insert('end', f"颜值评分: {beauty_score}\n")
        self.textbox.insert('end', "详细分数:\n")
        for item, score in detailed_scores.items():
            self.textbox.insert('end', f"{item}: {score}\n")
        self.textbox.config(state='disabled')

    def exit_program(self):
        if messagebox.askokcancel("退出程序", "确定要退出程序吗？"):
            self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    beauty_calculator = BeautyCalculator()
    app = BeautyApp(root, beauty_calculator)
    root.mainloop()
