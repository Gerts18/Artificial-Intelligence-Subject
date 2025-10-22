import cv2
import mediapipe as mp
import numpy as np

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Variables para gestionar cuadrados
SIZE_SCALE = 3            # factor para transformar distancia en tamaño de lado (ajustable)

# Captura de video en tiempo real
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convertir a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Procesar la imagen con MediaPipe
    results = hands.process(frame_rgb)

    # Dibujar puntos de la mano y crear/dimensionar cuadrados
    if results.multi_hand_landmarks:
        h, w, _ = frame.shape
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Obtener posiciones de pulgar (4) e índice (8) en píxeles
            lm_thumb = hand_landmarks.landmark[4]
            lm_index = hand_landmarks.landmark[8]
            tx, ty = int(lm_thumb.x * w), int(lm_thumb.y * h)
            ix, iy = int(lm_index.x * w), int(lm_index.y * h)

            # Distancia en píxeles entre pulgar e índice
            dx, dy = tx - ix, ty - iy
            dist_px = int(np.hypot(dx, dy))

            # Punto medio (centro del cuadrado)
            cx, cy = int((tx + ix) / 2), int((ty + iy) / 2)

            # Dibujar pequeños marcadores en los dedos
            cv2.circle(frame, (tx, ty), 6, (0, 0, 255), -1)
            cv2.circle(frame, (ix, iy), 6, (0, 255, 0), -1)
            cv2.line(frame, (tx, ty), (ix, iy), (255, 0, 0), 2)

            # Generar cuadrado dinámicamente basado en la distancia
            size = max(10, int(dist_px * SIZE_SCALE))
            half = size // 2
            x1, y1 = max(0, cx - half), max(0, cy - half)
            x2, y2 = min(w - 1, cx + half), min(h - 1, cy + half)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
            cv2.putText(frame, f"{size}px", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2, cv2.LINE_AA)

    # Mostrar el video
    cv2.imshow("Reconocimiento de Letras", frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()