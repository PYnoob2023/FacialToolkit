import cv2
import face_recognition
from tkinter import filedialog, Tk, Label, Button, Canvas, StringVar, PhotoImage, ttk
import time

def detect_face(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) == 0:
        return None, None
    face_location = face_locations[0]
    face_encoding = face_recognition.face_encodings(image, [face_location])[0]
    return face_location, face_encoding

def compare_faces(face_encoding1, face_encoding2):
    distance = face_recognition.face_distance([face_encoding1], face_encoding2)[0]
    score = 100 - distance * 100
    return score

def choose_file():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="选择图片", filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    root.destroy()
    return file_path

def display_face(image_path, canvas):
    image = cv2.imread(image_path)
    face_location, face_encoding = detect_face(image)
    if face_location is None:
        return None, None
    top, right, bottom, left = face_location
    face_image = image[top:bottom, left:right]
    face_image = cv2.resize(face_image, (300, 300))
    face_image = PhotoImage(data=cv2.imencode('.png', face_image)[1].tobytes())
    canvas.create_image(0, 0, anchor='nw', image=face_image)
    return face_encoding, face_image

def animate_scan(canvas):
    scan_line = canvas.create_line(0, 0, 0, 300, fill="red", width=2)
    for i in range(0, 301, 10):
        canvas.coords(scan_line, i, 0, i, 300)
        root.update()
        time.sleep(0.03)
    canvas.delete(scan_line)

def compare():
    if face_encoding1 is not None and face_encoding2 is not None:
        # Add scanning animation for canvas1 and canvas2
        animate_scan(canvas1)
        animate_scan(canvas2)

        # Compare faces
        score = compare_faces(face_encoding1, face_encoding2)

        # Format the result according to the score
        if score > 80:
            result.set("相似度：{:.0f}%\n这是同一个人。".format(score))
        elif score > 60:
            result.set("相似度：{:.0f}%\n同一个人的可能性比较高。".format(score))
        else:
            result.set("相似度：{:.0f}%\n这不是同一个人。".format(score))
    else:
        result.set("请先选择两张图片.")

root = Tk()
root.title("人脸对比")
root.geometry("770x650")  # 设置界面大小

style = ttk.Style()
style.theme_use("clam")  # 选择ttk主题

label1 = Label(root, text="请选择左侧的图片：")
label2 = Label(root, text="请选择右侧的图片：")
label1.place(x=50, y=20)
label2.place(x=400, y=20)

button1 = ttk.Button(root, text="选择图片", command=lambda: choose_image(1))
button2 = ttk.Button(root, text="选择图片", command=lambda: choose_image(2))
button1.place(relx=0.25, rely=0.1, anchor='center')  # 向下移动
button2.place(relx=0.75, rely=0.1, anchor='center')  # 向下移动

canvas1 = Canvas(root, width=300, height=300)
canvas2 = Canvas(root, width=300, height=300)
canvas1.place(x=50, y=100)
canvas2.place(x=400, y=100)

button3 = ttk.Button(root, text="对比", command=compare)
button3.place(relx=0.5, rely=0.95, anchor='center')  # 放在底部

face_encoding1 = None
face_encoding2 = None
face_image1 = None
face_image2 = None

result = StringVar()
label3 = Label(root, textvariable=result, font=("Arial", 20))
label3.place(relx=0.5, rely=0.75, anchor='center')

def choose_image(n):
    global face_encoding1, face_encoding2, face_image1, face_image2
    image_path = choose_file()
    if image_path:
        if n == 1:
            face_encoding1, face_image1 = display_face(image_path, canvas1)
        elif n == 2:
            face_encoding2, face_image2 = display_face(image_path, canvas2)

root.mainloop()