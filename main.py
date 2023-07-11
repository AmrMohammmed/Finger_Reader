import tkinter as tk
from tkinter import *
import cv2
from PIL import Image, ImageTk


#http://192.168.1.4:8080/video
def close_func():
    img2 = ImageTk.PhotoImage(Image.open("photo3.jpeg"))
    label_widget.configure(image=img2)
    label_widget.image = img2

i=0
def open_camera():
    link = textbox.get()
    vid = cv2.VideoCapture(link)
    global word,i
    i+=1
    word_label.config(text=str(i))
    # Capture the video frame by frame
    _, frame = vid.read()

    # Convert image from one color space to other
    opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

    # Capture the latest frame and transform to image
    captured_image = Image.fromarray(opencv_image)

    # Convert captured image to photoimage
    photo_image = ImageTk.PhotoImage(image=captured_image)

    # Displaying photoimage in the label
    label_widget.photo_image = photo_image

    # Configure image in the label
    label_widget.configure(image=photo_image)

    # Repeat the same process after every 10 seconds
    label_widget.after(5, open_camera)


import cv2

# cap = cv2.VideoCapture("http://192.168.1.4:8080/video")
# while cap.isOpened():
#     ret, frame = cap.read()
#     if ret:
#
#         cv2.imshow('Frame', frame)
#
#         if  cv2.waitKey(1) == ord('q'):
#             break
#     else:
#         break
# cap.release()
# cv2.destroyAllWindows()


root=tk.Tk()
root.geometry("1024x800")
root.title("Finger Reader")
root.configure(bg="#DFF8EF")
root.bind('<Escape>', lambda e: root.quit())
img = Image.open("Finger_Reader_V3.jpg")
photo_tk = ImageTk.PhotoImage(img)

label_widget=tk.Label(root,image=photo_tk,bg="#fff")
label_widget.pack(side=tk.TOP,anchor=tk.CENTER,pady=10)

button_close = tk.Button(root, text="Close", font=("Arial", 20), bg="#91D2FF",command=close_func)
button_close.pack(side=tk.LEFT, padx=80,anchor=tk.CENTER)

button_run=tk.Button(root,text="Run",width=5,font=("Arial", 20), bg="#91D2FF",command=open_camera)
button_run.pack(side=tk.RIGHT,padx=80,anchor=tk.CENTER)

label=tk.Label(root,text="Camera Stream Link",font=("Arial",14),bg="#DFF8EF")
label.pack(padx=5,pady=5)

textbox=tk.Entry(root,width=30, font=("Arial",14))
textbox.pack()

word_label=tk.Label(root,width=20,height=2,text="Read Word",font=("Arial",14),bg="#fff")
word_label.pack(pady=20,anchor=tk.CENTER)


root.mainloop()
