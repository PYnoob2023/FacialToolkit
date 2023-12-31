import cv2
import tkinter as tk
from tkinter import filedialog
from deepface import DeepFace
from PIL import Image, ImageTk
from tkinter import ttk

class FaceRecognitionApp:
    def __init__(self, root):
        # 初始化Tkinter主窗口
        self.root = root
        self.root.title("人脸识别应用")

        # 设置Tkinter界面样式
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 创建用于显示图片的标签
        self.image_label = tk.Label(self.root)
        self.image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

        # 创建用于显示人脸识别结果的标签
        self.result_label = tk.Label(self.root, text="人脸识别结果:")
        self.result_label.grid(row=0, column=1, padx=10, pady=10, columnspan=3)

        # 创建身高输入相关的控件
        self.bmi_label = tk.Label(self.root, text="身高（cm）:")
        self.bmi_label.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        self.bmi_height_entry = tk.Entry(self.root)
        self.bmi_height_entry.grid(row=1, column=2, padx=10, pady=10)

        # 创建体重输入相关的控件
        self.bmi_weight_label = tk.Label(self.root, text="体重（kg）:")
        self.bmi_weight_label.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        self.bmi_weight_entry = tk.Entry(self.root)
        self.bmi_weight_entry.grid(row=2, column=2, padx=10, pady=10)

        # 创建计算BMI按钮
        self.calculate_button = ttk.Button(self.root, text="计算", command=self.calculate_bmi)
        self.calculate_button.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

        # 创建文本框用于显示BMI计算结果
        self.result_text = tk.Text(self.root, height=10, width=30, state="disabled")
        self.result_text.grid(row=4, column=1, columnspan=2, padx=10, pady=10)

        # 创建选择图片按钮
        self.select_button = ttk.Button(self.root, text="选择图片", command=self.select_image)
        self.select_button.grid(row=5, column=0, padx=10, pady=10, sticky="sw")

        # 创建退出程序按钮
        self.quit_button = ttk.Button(self.root, text="退出程序", command=self.root.destroy)
        self.quit_button.grid(row=5, column=2, padx=10, pady=10, sticky="se")

        # 初始化选定的图片路径
        self.selected_image = None

    def select_image(self):
        # 打开文件对话框，选择图片文件
        file_path = filedialog.askopenfilename(title="选择图片", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            # 显示选定的图片
            self.display_image(file_path)

    def display_image(self, file_path):
        # 读取图片并显示在界面上
        image = cv2.imread(file_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image.thumbnail((400, 400))
        tk_image = ImageTk.PhotoImage(image)

        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image
        self.selected_image = file_path

    def calculate_bmi(self):
        # 获取身高和体重输入值，计算BMI
        height_entry_value = self.bmi_height_entry.get()
        weight_entry_value = self.bmi_weight_entry.get()

        if height_entry_value and weight_entry_value:
            height = float(height_entry_value) / 100
            weight = float(weight_entry_value)

            bmi = weight / (height ** 2)
            bmi_result = f"BMI数值: {bmi:.2f}"
            bmi_category = self.calculate_bmi_category(bmi)
            result_text = f"BMI类型: {bmi_category}" if bmi_category else ""
        else:
            bmi_result = ""
            result_text = ""

        # 如果已选择图片，进行人脸识别
        if self.selected_image:
            rgb_image = cv2.imread(self.selected_image)
            rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
            result = DeepFace.analyze(rgb_image, actions=["age", "gender", "emotion", "race"], enforce_detection=False)

            # 显示人脸识别结果
            self.display_results(result, bmi_result, result_text)
        else:
            self.display_results(None, bmi_result, result_text)

    def calculate_bmi_category(self, bmi):
        # 根据BMI值判断BMI类型
        if bmi < 18.5:
            return "偏瘦"
        elif 18.5 <= bmi < 24.9:
            return "正常"
        elif 25 <= bmi < 29.9:
            return "过重"
        else:
            return "肥胖"

    def display_results(self, result, bmi_result, result_text):
        # 显示人脸识别和BMI计算结果
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)

        if bmi_result and result_text:
            self.result_text.insert(tk.END, f"{bmi_result}\n{result_text}\n")

        if result:
            for face in result:
                age = face["age"]
                gender_label = self.translate_gender(max(face["gender"], key=face["gender"].get))
                emotion = self.translate_emotion(max(face["emotion"], key=face["emotion"].get))
                race = self.translate_race(max(face["race"], key=face["race"].get))

                self.result_text.insert(tk.END, f"年龄: {age}\n")
                self.result_text.insert(tk.END, f"性别: {gender_label}\n")
                self.result_text.insert(tk.END, f"情绪: {emotion}\n")
                self.result_text.insert(tk.END, f"种族: {race}\n\n")

        self.result_text.config(state="disabled")

    def translate_gender(self, gender):
        # 将性别翻译为中文
        return {"Man": "男性", "Woman": "女性"}.get(gender, gender)

    def translate_emotion(self, emotion):
        # 将情绪翻译为中文
        return {"angry": "生气", "disgust": "厌恶", "fear": "害怕", "happy": "高兴", "sad": "伤心", "surprise": "惊讶", "neutral": "面无表情"}.get(emotion, emotion)

    def translate_race(self, race):
        # 将种族翻译为中文
        return {"asian": "亚洲人", "indian": "印度人", "black": "黑人", "white": "白人", "middle eastern": "中东人", "latino hispanic": "拉丁裔/西班牙裔"}.get(race, race)

    def animate_image(self, angle=0):
        # 旋转并显示图片
        if self.selected_image:
            image = Image.open(self.selected_image)
            image = image.rotate(angle)
            image.thumbnail((400, 400))
            tk_image = ImageTk.PhotoImage(image)

            self.image_label.config(image=tk_image)
            self.image_label.image = tk_image

            angle = (angle + 10) % 360
            self.root.after(100, lambda: self.animate_image(angle))

if __name__ == "__main__":
    # 创建Tkinter应用程序主窗口
    root = tk.Tk()
    # 创建人脸识别应用程序实例
    app = FaceRecognitionApp(root)
    # 启动图片旋转动画
    app.animate_image()
    # 运行Tkinter事件循环
    root.mainloop()
