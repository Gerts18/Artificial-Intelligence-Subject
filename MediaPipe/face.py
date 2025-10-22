"""
Que pinte ciertos puntos de la cara al detectar ciertas emociones en la cara. Enojo, Felicidad y Trsiteza.
Solo debe pintar los puntos de contorno de la cara.
"""
import cv2
import mediapipe as mp
import numpy as np

# Inicializar MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=2, 
                                  min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Inicializar dibujador de MediaPipe
mp_drawing = mp.solutions.drawing_utils
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(234, 255, 233))  # Verde

# Captura de video
cap = cv2.VideoCapture(0)

# Puntos clave de la boca (según MediaPipe Face Mesh)
# 61: esquina izquierda, 291: esquina derecha
# 13: labio superior (centro), 14: labio inferior (centro)
# 78: labio superior izquierdo, 308: labio superior derecho
# 87: labio inferior izquierdo, 317: labio inferior derecho
BOCA_PUNTOS = {
    'esquina_izq': 61,
    'esquina_der': 291,
    'labio_sup_centro': 13,
    'labio_inf_centro': 14,
    'labio_sup_izq': 78,
    'labio_sup_der': 308
}


def calcular_emocion(face_landmarks, h, w):
    """
    Detecta emoción basándose en la posición de los puntos de la boca
    """
    # Obtener coordenadas de puntos clave
    esquina_izq = face_landmarks.landmark[BOCA_PUNTOS['esquina_izq']]
    esquina_der = face_landmarks.landmark[BOCA_PUNTOS['esquina_der']]
    labio_sup_centro = face_landmarks.landmark[BOCA_PUNTOS['labio_sup_centro']]
    labio_inf_centro = face_landmarks.landmark[BOCA_PUNTOS['labio_inf_centro']]
    
    # Calcular el promedio de altura de las esquinas (en píxeles)
    altura_esquinas = ((esquina_izq.y + esquina_der.y) / 2) * h
    
    # Calcular el punto medio entre labios superior e inferior
    altura_centro_boca = ((labio_sup_centro.y + labio_inf_centro.y) / 2) * h
    
    # Calcular la curvatura: si esquinas están arriba del centro -> sonrisa
    # si esquinas están abajo del centro -> tristeza
    curvatura = altura_centro_boca - altura_esquinas
    
    # Calcular apertura de la boca (en píxeles)
    apertura = abs(labio_sup_centro.y - labio_inf_centro.y) * h
    
    # DEBUG: descomentar para ver valores
    # print(f"Curvatura: {curvatura:.2f}, Apertura: {apertura:.2f}")
    
    # Umbrales ajustados (en píxeles)
    if curvatura > 3:  # Esquinas más arriba que el centro -> sonrisa
        return "Felicidad ", curvatura
    elif curvatura < -1.5:  # Esquinas más abajo que el centro -> tristeza
        return "Tristeza ", curvatura
    else:
        return "Neutral ", curvatura

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Espejo para mayor naturalidad
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Dibujar solo los contornos en lugar de la teselación completa
            mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS, 
                                      drawing_spec, drawing_spec)
            
            # Detectar emoción
            h, w, _ = frame.shape
            emocion, curvatura_valor = calcular_emocion(face_landmarks, h, w)
            
            # Mostrar emoción en pantalla
            cv2.putText(frame, f"Emocion: {emocion}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Mostrar valor de curvatura para debug
            cv2.putText(frame, f"Curvatura: {curvatura_valor:.2f}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow('PuntosFacialesMediaPipe', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()