# only photo
import tkinter as tk
from PIL import Image, ImageTk
import winsound
import threading
import imutils
from threading import Thread
import concurrent.futures
import pyttsx3
import cv2
import numpy as np
import pytesseract
import requests
from urllib.request import urlopen

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

frame_counter = 0
warning_count = 0
frame_counter = 0
ROI = [(0, 0), (640, 480)]
def_cords = (1000, 1000)
def_word = ""
closeClicked=False
# IsEven=0
def run_ocr():
    #http://192.168.1.4:8080/video

    class VideoStream:

        # def __init__(self, src="http://192.168.1.4:8080/video"):
        def __init__(self, src=textbox.get()):
            if not("http://192.168" in src):
                 src=0
            #     def __init__(self, src=0):
            requests.get(src + "/control?var=framesize&val=6")
            img_resp = urlopen(src)
            imgnp = np.asarray(bytearray(img_resp.read()), dtype="uint8")
            img = cv2.imdecode(imgnp, -1)

            self.stopped = False
            self.frame = img
            self.clone = self.frame

        def start(self):
            """
            Creates a thread targeted at get(), which reads frames from CV2 VideoCapture

            :return: self
            """
            Thread(target=self.get, args=()).start()
            return self

        def get(self):

            """
            Continuously gets frames from CV2 VideoCapture and sets them as self.frame attribute
            """
            while not self.stopped:

                img_resp = urlopen(textbox.get())
                imgnp = np.asarray(bytearray(img_resp.read()), dtype="uint8")
                img = cv2.imdecode(imgnp, -1)
                #             img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                self.frame = img

                self.clone = self.frame
                if True:
                    img = self.frame.astype(float)
                    red = img[:, :, 2]
                    green = img[:, :, 1]
                    blue = img[:, :, 0]

                    sum_n = (red + green + blue) + 0.00000001

                    n_red = np.divide(red, sum_n) * (255.0)
                    n_red = n_red.astype(np.uint8)
                    blur = cv2.GaussianBlur(n_red, (5, 5), 0)
                    blur = blur.astype(np.uint8)

                    ret3, th3 = cv2.threshold(n_red, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    global closeClicked

                    if closeClicked == False:
                        drawcursor(self.frame, th3)

                    #                 cv2.imshow('Adaptive Threshold', self.frame)
                    # cv2.waitKey(1)

                    if closeClicked==True:
                        cv2.destroyAllWindows()
                        self.stopped = True
                        OCR.stopped = True
                        break

                else:
                    break

    class OCR:

        stopped = False

        # def _init_(self, exchange: VideoStream, language=None):
        def _init_(self):
            self.boxes = None
            self.exchange = None
            self.language = None
            self.width = None
            self.height = None
            self.X_cord = 0
            self.Y_cord = 0

        def start(self):
            """
            Creates a thread targeted at the ocr process
            :return: self
            """
            Thread(target=self.ocr).start()
            return self

        def set_exchange(self, video_stream):
            """
            Sets the self.exchange attribute with a reference to VideoStream class
            :param video_stream: VideoStream class
            """
            self.exchange = video_stream

        # ######################## Important #####################################3
        # I have edited this function to get the cropped frame as an argument from the draw cursor

        def ocr(self):

            """
            Creates a process where frames are continuously grabbed from the exchange and processed by pytesseract OCR.
            Output data from pytesseract is stored in the self.boxes attribute.
            """
            while not self.stopped:

                if self.exchange is not None:  # Defends against an undefined VideoStream reference
                    frame = self.exchange.frame

                    threshHold_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                    threshHold_frame = cv2.adaptiveThreshold(threshHold_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                             cv2.THRESH_BINARY,
                                                             83, 15)

                    global ROI
                    global frame_counter
                    frame_counter += 1
                    # self.frame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 13,2)

                    data1 = pytesseract.image_to_data(frame)
                    data2 = pytesseract.image_to_data(threshHold_frame)
                    data = [data1, data2]
                    word_details_pair = [[0, "", (0, 0), (0, 0)], [0, "", (0, 0), (0, 0)]]
                    for i in range(0, 2):

                        for z, a in enumerate(data[i].splitlines()):
                            if z != 0:
                                a = a.split()
                                if len(a) == 12:
                                    x, y = int(a[6]), int(a[7])
                                    w, h = int(a[8]), int(a[9])

                                    if self.X_cord >= x and self.X_cord <= x + w:
                                        if self.Y_cord >= y and self.Y_cord <= y + h:

                                            if float(a[10]) >= 75.0:
                                                word_details_pair[i] = [float(a[10]), a[11], (x, y), (w, h)]
                                                break

                    most_accurate_word = [0, "", (0, 0), (0, 0)]

                    if word_details_pair[0][0] != 0 or word_details_pair[1][0] != 0:

                        print("Ordinary Frame :", word_details_pair[0][0])
                        print("Adaptive THreshhold :", word_details_pair[1][0])

                        if word_details_pair[0][0] >= word_details_pair[1][0]:
                            most_accurate_word = word_details_pair[0]

                        else:
                            most_accurate_word = word_details_pair[1]

                        x, y = most_accurate_word[2]
                        w, h = most_accurate_word[3]
                        word = most_accurate_word[1]
                        word_cords = (x, y)

                        global def_cords
                        global def_word
                        if def_cords == word_cords or abs(def_cords[0] - word_cords[0]) <= 2 or abs(
                                def_cords[1] - word_cords[1]) <= 2 and word == def_word:

                            # print("Cords in if",def_cords)
                            # print("XY in if",word_cords)
                            continue
                        else:
                            # print("Cords in else",def_cords)
                            # print("XY in else",word_cords)
                            def_cords = word_cords
                            def_word = word
                            print(word)
                            word_label.config(text=word)
                            read_word(word)

                            #                             print(frame_counter)
                            half_height = int(h * 0.4)
                            #                                             half_height=3

                            p1 = (0, y - half_height)
                            p2 = (frame.shape[1], h + y + half_height)

                            if frame_counter > 25:
                                frame_counter = 0
                            if self.Y_cord >= p1[1] and self.Y_cord <= p2[1]:
                                ROI = [p1, p2]

        def set_dimensions(self, width, height):
            self.X_cord = width
            self.Y_cord = height

    def read_word(word):
        engine = pyttsx3.init()
        engine.say(word)
        engine.runAndWait()

    def drawcursor(img, image):
        # After The Thresholding
        cnts = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # collecting the heighest point in the contours
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key=cv2.contourArea)
        extTop = tuple(c[c[:, :, 1].argmin()][0])
        copiedFrame = img.copy();

        X, Y = extTop
        #     global def_cords
        #     def_cords = (X, Y)

        cv2.line(copiedFrame, (X, Y - 13), (X, Y + 13), (0, 0, 255), 1)
        cv2.line(copiedFrame, (X - 13, Y), (X + 13, Y), (0, 0, 255), 1)

        # global ocr1
        ocr1.set_dimensions(X, Y - 13)
        cv2.circle(copiedFrame, (X, Y - 13), 2, (0, 255, 0), -1)
        global ROI
        #       print(ROI)
        global warning_count
        if Y - 13 > ROI[0][1] and Y - 13 < ROI[1][1]:
            warning_count = 0


        elif Y - 13 < ROI[0][1] and warning_count < 2 and Y - 13 > 0:
            warning_count += 1
            duration = 300  # milliseconds
            freq = 300  # Hz
            winsound.Beep(freq, duration)
        elif Y - 20 > ROI[1][1] and warning_count < 2:
            warning_count += 1
            duration = 300  # milliseconds
            freq = 500  # Hz
            winsound.Beep(freq, duration)

            #     global Cur_Y
        #     Cur_Y=Y-20
        global IsEven
        IsEven+=1
        cv2.rectangle(copiedFrame, ROI[0], ROI[1], (0, 0, 255), 1)
        # if IsEven %2==0:
        open_camera(copiedFrame)

        # cv2.imshow("drawing_Frame", copiedFrame)


    v1 = VideoStream()
    ocr1 = OCR()
    ocr1.set_exchange(v1)
    ocr1.start()
    # ocr1.ocr(img)
    v1.start()

def close_every_thing():
    root.destroy()
    global closeClicked
    closeClicked=True
    exit(0)

def open_camera(img):
    # Convert image from one color space to other
    opencv_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)

    # Capture the latest frame and transform to image
    captured_image = Image.fromarray(opencv_image)

    # Convert captured image to photoimage
    photo_image = ImageTk.PhotoImage(image=captured_image)

    # Displaying photoimage in the label
    label_widget.photo_image = photo_image

    # Configure image in the label
    label_widget.configure(image=photo_image)
    # cv2.waitKey(10)
    # # Repeat the same process after every 10 seconds
    # label_widget.after(5, open_camera)


root=tk.Tk()
root.geometry("1024x800")
root.title("Finger Reader")
root.configure(bg="#DFF8EF")
root.bind('<Escape>', lambda e: root.quit())
img = Image.open("Finger_Reader_V3.jpg")
photo_tk = ImageTk.PhotoImage(img)

label_widget=tk.Label(root,image=photo_tk,bg="#fff")
label_widget.pack(side=tk.TOP,anchor=tk.CENTER,pady=10)

button = tk.Button(root, text="Close", font=("Arial", 20), bg="#91D2FF",command=close_every_thing)
button.pack(side=tk.LEFT, padx=80,anchor=tk.CENTER)

button=tk.Button(root,text="Run",width=5,font=("Arial", 20), bg="#91D2FF",command=run_ocr)
button.pack(side=tk.RIGHT,padx=80,anchor=tk.CENTER)

label=tk.Label(root,text="Camera Stream Link",font=("Arial",14),bg="#DFF8EF")
label.pack(padx=5,pady=5)

textbox=tk.Entry(root,width=30, font=("Arial",14))
textbox.pack()

word_label=tk.Label(root,width=20,height=2,text="Read Word",font=("Arial",14),bg="#fff")
word_label.pack(pady=20,anchor=tk.CENTER)

root.mainloop()
