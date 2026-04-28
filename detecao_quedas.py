import cv2
import time
import mediapipe as mp
import urllib.request
import os
import requests
from dotenv import load_dotenv # <-- Nova biblioteca importada

print("A carregar variáveis de ambiente...")
# Carrega as senhas ocultas do ficheiro .env
load_dotenv()

# --- CONFIGURAÇÕES DO TELEGRAM (Agora seguras!) ---
# Puxa os dados do ficheiro .env
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("❌ ERRO: Faltam as credenciais no ficheiro .env!")
    exit()

def enviar_notificacao(mensagem):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensagem}"
        requests.get(url, timeout=5)
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")

# --- 1. Inicialização da Câmera ---
cap = cv2.VideoCapture(0)

# Resolução Full HD (1920x1080)
# NOTA: Se o vídeo ficar lento (baixo FPS) no Jetson, mude para 1280 e 720.
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

if not cap.isOpened():
    print("❌ ERRO CRÍTICO: Nenhuma câmera detetada!")
    exit()

# --- 2. Inicialização da IA (Versão Otimizada Jetson Nano 0.8.5) ---
mp_pose = mp.solutions.pose
# model_complexity=1 garante que a GPU do Jetson aguente o tranco
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Variáveis da Máquina de Física
tempo_anterior = time.time()
nariz_y_anterior = 0.0
queda_confirmada = False
momento_da_queda = 0
notificacao_enviada = False

ALTURA_CENARIO_METROS = 2.5 
LIMIAR_METROS_POR_SEGUNDO = 1.3 

print("✅ Sistema 100% Operacional. Pressione 'q' na janela de vídeo para sair.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    tempo_atual = time.time()

    if results.pose_landmarks:
        # No Jetson, o desenho do esqueleto é automático com 1 linha!
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Posições (No Jetson usamos LEFT_HIP)
        nariz_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y
        quadril_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y

        # Cálculo de Física (m/s)
        delta_y_metros = (nariz_y - nariz_y_anterior) * ALTURA_CENARIO_METROS
        delta_t = tempo_atual - tempo_anterior
        
        if delta_t > 0:
            velocidade_ms = delta_y_metros / delta_t
        else:
            velocidade_ms = 0.0

        # Lógica de Queda Científica
        if nariz_y > quadril_y and velocidade_ms > LIMIAR_METROS_POR_SEGUNDO:
            if not queda_confirmada:
                queda_confirmada = True
                momento_da_queda = tempo_atual
                
                # Envio do Telegram pelo Jetson
                if not notificacao_enviada:
                    print("⚠️ Queda detetada! Enviando notificação para o Telegram...")
                    enviar_notificacao(f"🚨 ALERTA: Queda detetada pelo Jetson Nano! Velocidade de impacto: {velocidade_ms:.2f} m/s")
                    notificacao_enviada = True

        nariz_y_anterior = nariz_y
        
        # Interface de Dados
        cv2.putText(frame, f"Vel Y: {velocidade_ms:.2f} m/s", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    tempo_anterior = tempo_atual

    # Interface de Alerta Visual
    if queda_confirmada:
        cv2.putText(frame, "ALERTA: QUEDA DETECTADA!", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        if tempo_atual - momento_da_queda > 5:
            queda_confirmada = False 
            notificacao_enviada = False 

    # Interface Expansível
    cv2.namedWindow('Monitoramento Assistivo - Jetson', cv2.WINDOW_NORMAL)
    cv2.imshow('Monitoramento Assistivo - Jetson', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()