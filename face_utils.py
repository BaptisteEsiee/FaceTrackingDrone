from ultralytics import YOLO
from djitellopy import Tello
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import time


def tracking(drone):
    w, h = 360, 240
    fbRange = [6200, 6800]
    pid = [0.2, 0.2, 0]
    pError = 0
    t = "1"
    r = "1"
    MODEL_PATH = "best.pt"
    CONF_THRESHOLD = 0.85
    WAIT_TIME = 500
    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(0)
    info = []  # initialize empty info list
    detection_flag = False
    liste: list = []
    temps_tourn = 0

    while True:

        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (360, 240))

        t = ""
        r = ""
        results = ""
        # Detect objects in the image
        results = model.predict(frame, show=True, conf=CONF_THRESHOLD)

        for result in results:  # iterate results
            boxes = result.boxes.cpu().numpy()  # get boxes on cpu in numpy
            for box in boxes:  # iterate boxes
                r = box.xyxy[0].astype(int)  # get corner points as int
                t = result.names[int(box.cls[0])]
                detection_flag = True
                liste.append(1)
            else:
                liste.append(0)

        if t == selected_pilot and detection_flag:
            myFaceListC = []
            myFaceListArea = []

            # Get the center coordinates of the box
            x_center = int((r[0] + r[2]) / 2)
            y_center = int((r[1] + r[3]) / 2)

            # Draw a circle at the center of the box
            cv2.circle(frame, (x_center, y_center), 5, (0, 0, 255), -1)

            myFaceListC.append([x_center, y_center])
            myFaceListArea.append(int((r[2] - r[0]) * (r[3] - r[1])))

            if len(myFaceListArea) != 0:
                i = myFaceListArea.index(max(myFaceListArea))
                info = [myFaceListC[i], myFaceListArea[i]]
            else:
                info = [[0, 0], 0]

            pError = track_face(info, w, pid, pError, drone, fbRange)
        else:
            if len(liste) > 10:
                new_list = liste[-10:]
                print(new_list)
                nb_count = new_list.count(1)
                if nb_count >= 1:
                    pass
            drone.send_rc_control(0, 0, 0, 15)
            time.sleep(0.2)
            temps_tourn = 1 + temps_tourn
            print(f"count: {temps_tourn}")
            if temps_tourn == 200:
                # drone.land()
                temps_tourn = 0
                break
            print("TURN")

        detection_flag = False
        # print(liste)
        if len(liste) > 100:
            liste.clear()


def track_face(info, w, pid, pError, drone, fbRange):
    area = info[1]
    x, y = info[0]
    fb = 0
    error = x - w // 2
    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -100, 100))
    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb = -20
    elif area < fbRange[0] and area != 0:
        fb = 20
    if x == 0:
        speed = 0
        error = 0
    drone.send_rc_control(0, fb, 0, speed)
    return error


def gui_window():
    # Initialize the GUI window
    root = tk.Tk()
    root.title("Choose Pilot")
    root.geometry("400x400")

    # Define the window title label
    title_label = tk.Label(root, text="Select a Target")
    title_label.config(font=("Arial", 20))
    title_label.pack(pady=20)

    # Define the frame to hold the buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    # Define the buttons with images
    romain_image = Image.open("romain.jpg").resize((100, 100))
    romain_photo = ImageTk.PhotoImage(romain_image)
    romain_button = tk.Button(button_frame, image=romain_photo, command=lambda: select_pilot("Romain", root))
    romain_button.grid(row=0, column=0, padx=20)

    simon_image = Image.open("simon.jpg").resize((100, 100))
    simon_photo = ImageTk.PhotoImage(simon_image)
    simon_button = tk.Button(button_frame, image=simon_photo, command=lambda: select_pilot("Simon", root))
    simon_button.grid(row=0, column=1, padx=20)

    baptiste_image = Image.open("baptiste.jpg").resize((100, 100))
    baptiste_photo = ImageTk.PhotoImage(baptiste_image)
    baptiste_button = tk.Button(button_frame, image=baptiste_photo, command=lambda: select_pilot("Baptiste", root))
    baptiste_button.grid(row=1, column=0, padx=20, pady=20)

    enzo_image = Image.open("enzo.jpg").resize((100, 100))
    enzo_photo = ImageTk.PhotoImage(enzo_image)
    enzo_button = tk.Button(button_frame, image=enzo_photo, command=lambda: select_pilot("Enzo", root))
    enzo_button.grid(row=1, column=1, padx=20, pady=20)

    # Start the GUI event loop
    root.mainloop()

    # Get the selected pilot name
    # print(selected_pilot(root=root))


# Define the function to be called when a button is clicked
def select_pilot(pilot_name, root):
    global selected_pilot
    selected_pilot = pilot_name
    print(selected_pilot)
    root.destroy()


def wait_gui():
    # Wait for the user to input the selected pilot before takeoff
    while True:
        try:
            selected_pilot
        except NameError:
            continue
        else:
            break


# Initialize the connection to the drone
# gui_window()
# wait_gui()
# drone = Tello()
# drone.connect()
# drone.streamon()
# # Takeoff the drone
# drone.takeoff()
# drone.send_rc_control(0, 0, 30, 0)
# time.sleep(5)
# drone.send_rc_control(0, 0, 0, 0)
# tracking(drone)
# # Release resources
# cv2.destroyAllWindows()
# drone.streamoff()
# drone.land()
# drone.disconnect()
