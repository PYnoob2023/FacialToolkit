import os
import subprocess
import psutil
import tkinter
from tkinter import ttk, Tk, Button, Label, messagebox
from PIL import Image, ImageTk
from ttkbootstrap import Style

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI程序")

        style = Style(theme='sandstone')
        self.root = style.master

        self.label = ttk.Label(root, text="欢迎使用面部分析、颜值打分和人脸对比程序", font=("微软雅黑", 16))
        self.label.pack(pady=10)

        #face_image = Image.open('face.JPG')
        #star_image = Image.open('star.jpg')
        #close_image = Image.open('close.jpg')

        self.button_face_analysis = ttk.Button(root, text="面部分析", command=self.open_face_analysis, width=20)
        self.button_face_analysis.pack(pady=10)

        self.button_beauty_scoring = ttk.Button(root, text="颜值打分", command=self.open_beauty_scoring, width=20)
        self.button_beauty_scoring.pack(pady=10)

        self.button_face_comparison = ttk.Button(root, text="人脸对比", command=self.open_face_comparison, width=20)
        self.button_face_comparison.pack(pady=10)

        self.button_exit = ttk.Button(root, text="退出", command=self.root.destroy, width=20)
        self.button_exit.pack(pady=10)

    def is_script_running(self, script_name):
        for process in psutil.process_iter(['pid', 'name']):
            if script_name.lower() in process.info['name'].lower():
                return True
        return False

    def open_face_analysis(self):
        if not self.is_script_running("面部分析.py"):
            self.open_file("面部分析.py")

    def open_beauty_scoring(self):
        if not self.is_script_running("颜值打分.py"):
            self.open_file("颜值打分.py")

    def open_face_comparison(self):
        if not self.is_script_running("相似度对比.py"):
            self.open_file("相似度对比.py")

    def open_file(self, filename):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if os.path.exists(file_path):
            subprocess.Popen(["python", file_path])
        else:
            print(f"Error: File '{filename}' not found.")

    def get_tkinter_image(self, pil_image):
        return ImageTk.PhotoImage(pil_image)

if __name__ == "__main__":
    root = Tk()
    app = MainApp(root)
    root.mainloop()
