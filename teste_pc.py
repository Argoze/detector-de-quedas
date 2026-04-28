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

# --- SETUP INICIAL ---
model_path = 'pose_landmarker_lite.task'
if not os.path.exists(model_path):
    url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
    urllib.request.urlretrieve(url, model_path)

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.PoseLandmarkerOptions(base_options=base_options, running_mode=vision.RunningMode.IMAGE)
detector = vision.PoseLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

# --- RESOLUÇÃO FULL HD (1920x1080) ---
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Variáveis de controle
tempo_anterior = time.time()
nariz_y_anterior = 0.0
queda_confirmada = False
momento_da_queda = 0
notificacao_enviada = False 

ALTURA_CENARIO_METROS = 2.5 
LIMIAR_METROS_POR_SEGUNDO = 1.3 

# Mapeamento dos "ossos" para ligar os pontos
CONEXOES_CORPO = [(0,1), (1,2), (2,3), (3,7), (0,4), (4,5), (5,6), (6,8), (9,10), (11,12), (11,13), (13,15), (15,17), (15,19), (15,21), (17,19), (12,14), (14,16), (16,18), (16,20), (16,22), (18,20), (11,23), (12,24), (23,24), (23,25), (24,26), (25,27), (26,28), (27,29), (28,30), (29,31), (30,32), (27,31), (28,32)]

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
    detection_result = detector.detect(mp_image)
    tempo_atual = time.time()

    if detection_result.pose_landmarks:
        pessoa = detection_result.pose_landmarks[0]
        h, w, _ = frame.shape

        # ESQUELETO
        for conexao in CONEXOES_CORPO:
            p1, p2 = pessoa[conexao[0]], pessoa[conexao[1]]
            cv2.line(frame, (int(p1.x * w), int(p1.y * h)), (int(p2.x * w), int(p2.y * h)), (255, 255, 255), 2)
            
        for ponto in pessoa:
            cv2.circle(frame, (int(ponto.x * w), int(ponto.y * h)), 4, (0, 255, 0), -1)

        # Lógica de Queda
        nariz_y = pessoa[0].y       
        quadril_y = (pessoa[23].y + pessoa[24].y) / 2

        delta_y_metros = (nariz_y - nariz_y_anterior) * ALTURA_CENARIO_METROS
        delta_t = tempo_atual - tempo_anterior
        velocidade_ms = (delta_y_metros / delta_t) if delta_t > 0 else 0.0

        if nariz_y > quadril_y and velocidade_ms > LIMIAR_METROS_POR_SEGUNDO:
            if not queda_confirmada:
                queda_confirmada = True
                momento_da_queda = tempo_atual
                
                # MENSAGEM TELEGRAM
                if not notificacao_enviada:
                    print("⚠️ Queda detetada! Enviando notificação para o Telegram...")
                    enviar_notificacao(f"🚨 ALERTA: Queda detetada no sistema! Velocidade de impacto: {velocidade_ms:.2f} m/s")
                    notificacao_enviada = True

        nariz_y_anterior = nariz_y
        cv2.putText(frame, f"Vel Y: {velocidade_ms:.2f} m/s", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    tempo_anterior = tempo_atual

    if queda_confirmada:
        cv2.putText(frame, "ALERTA: QUEDA DETECTADA!", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        if tempo_atual - momento_da_queda > 5:
            queda_confirmada = False 
            notificacao_enviada = False 

    
    cv2.namedWindow('Monitoramento Assistivo - PC Full HD', cv2.WINDOW_NORMAL)
    cv2.imshow('Monitoramento Assistivo - PC Full HD', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()