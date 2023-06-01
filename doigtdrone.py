import cv2
import mediapipe as mp
from djitellopy import Tello
from Salutleslou import linetrack
from face_utils import gui_window, wait_gui, tracking
import time

# Initialiser les détecteurs de mains de Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialiser la connexion au drone
drone = Tello()
drone.connect()
drone.streamon()
drone.takeoff()
drone.send_rc_control(0, 0, 30, 0)
time.sleep(5)
drone.send_rc_control(0, 0, 0, 0)

frames_with_five_fingers = 0

with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
    print("-------DOIGTDRONE-------")
    while True:
        # Récupérer l'image de la caméra du drone
        frame = drone.get_frame_read().frame
        frame = cv2.resize(frame, (360, 240))

        # Convertir l'image en noir et blanc pour le traitement
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Détecter les mains
        results = hands.process(image)

        # Dessiner les repères de la main sur l'image
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Vérifier si la main est ouverte ou fermée
                thumb_closed = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x < hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x
                index_finger_closed = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y
                middle_finger_closed = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y
                ring_finger_closed = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y
                pinky_finger_closed = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].y

                # Compter le nombre de doigts levés
                fingers_up = 4
                fingers_up += 1 if not thumb_closed else 0
                fingers_up -= 1 if not index_finger_closed else 0
                fingers_up -= 1 if not middle_finger_closed else 0
                fingers_up -= 1 if not ring_finger_closed else 0
                fingers_up -= 1 if not pinky_finger_closed else 0

                # Ajouter le texte indiquant le nombre de doigts levés
                font = cv2.FONT_HERSHEY_SIMPLEX
                bottomLeftCornerOfText = (10, 80)
                fontScale = 1
                fontColor = (255, 255, 255)
                lineType = 2
                cv2.putText(image, f'{fingers_up} doigt(s) leve(s)', bottomLeftCornerOfText, font, fontScale, fontColor, lineType)

                if fingers_up == 5:
                    # Incrémenter le compteur de frames avec 5 doigts levés
                    frames_with_five_fingers += 1

                    # Vérifier si le compteur de frames avec 5 doigts levés a atteint 3 secondes (90 frames à 30 FPS)
                    if frames_with_five_fingers == 40:
                        # Effectuer une flip
                        print("----ENTER MODE FLIP----")
                        drone.flip("r")

                        # Réinitialiser le compteur de frames avec 5 doigts levés
                        frames_with_five_fingers = 0

                elif fingers_up == 1:
                    # Incrémenter le compteur de frames avec 5 doigts levés
                    frames_with_five_fingers += 1

                    # Vérifier si le compteur de frames avec 5 doigts levés a atteint 3 secondes (90 frames à 30 FPS)
                    if frames_with_five_fingers == 40:
                        # Effectuer une flip
                        #subprocess.run(["python", "LineTrack.py"])
                        print("-----ENTER MODE LINE TRACKING-------")
                        drone.send_rc_control(0, 0, -30, 0)
                        time.sleep(5)
                        linetrack(drone)
                        print("-----salut-------")

                        # Réinitialiser le compteur de frames avec 5 doigts levés
                        frames_with_five_fingers = 0
                elif fingers_up == 3:
                    # Incrémenter le compteur de frames avec 5 doigts levés
                    frames_with_five_fingers += 1

                    # Vérifier si le compteur de frames avec 5 doigts levés a atteint 3 secondes (90 frames à 30 FPS)
                    if frames_with_five_fingers == 40:
                        # Effectuer une flip
                        # subprocess.run(["python", "LineTrack.py"])
                        print("-----ENTER MODE FACE TRACKING-------")
                        # lancer le GUI pour choisir qui suivre
                        gui_window()
                        # attendre que quelqu'un clic
                        wait_gui()
                        drone.send_rc_control(0, 0, 0, 0)
                        # lance la fonction de tracking du visage
                        tracking(drone)
                        cv2.destroyAllWindows()
                        drone.send_rc_control(0, 0, 0, 0)
                        print("-----salut-------")

                        # Réinitialiser le compteur de frames avec 5 doigts levés
                        frames_with_five_fingers = 0
                else:
                    # Réinitialiser le compteur de frames avec 5 doigts levés
                    frames_with_five_fingers = 0

        # Afficher l'image avec la webcam
        cv2.imshow('Webcam', image)
        cv2.waitKey(1)

# Fermer la fenêtre de la webcam et libérer la webcam
cv2
