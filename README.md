# 🏥 Sistema de Monitoramento Assistivo: Detecção de Quedas com IA

Este projeto consiste em um sistema inteligente de detecção de quedas em tempo real, desenvolvido para rodar em dispositivos de borda (*Edge Computing*) como o **NVIDIA Jetson Nano** ou em computadores convencionais. O sistema utiliza Visão Computacional e Inteligência Artificial para monitorar a postura humana e enviar alertas imediatos via Telegram.

## 🚀 Funcionalidades
- **Detecção de Esqueleto:** Utiliza o MediaPipe Pose para mapeamento de 33 pontos articulares do corpo humano.
- **Cálculo Cinemático Real:** Diferencia quedas reais de movimentos bruscos voluntários calculando a velocidade vertical em metros por segundo (m/s).
- **Alertas em Tempo Real:** Integração com Bot do Telegram para envio de notificações de emergência de forma instantânea.
- **Privacidade e Segurança:** Gerenciamento seguro de credenciais via variáveis de ambiente (`.env`).
- **Alta Resolução:** Suporte para captura de vídeo em Widescreen/Full HD (1080p).

## 📚 Base Científica
A lógica de detecção de anomalias é pautada na literatura biomecânica para evitar falsos positivos:
- **Limiar de Velocidade:** O sistema adota o limiar de **1.3 m/s** como indicador de impacto de queda, baseado no estudo de *Bourke, A. K., et al. (2007)* ("Evaluation of a threshold-based tri-axial accelerometer fall detection algorithm").
- **Diferenciação:** Movimentos diários, como sentar-se ou abaixar-se rapidamente, raramente excedem 0.8 m/s, permitindo ao algoritmo filtrar atividades normais.

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python
- **Visão Computacional:** OpenCV (`cv2`)
- **Inteligência Artificial:** Google MediaPipe (Pose Landmarker / v0.8.5 Legacy para Jetson)
- **Comunicação IoT:** Telegram Bot API (`requests`)
- **Segurança:** `python-dotenv`
- **Hardware Alvo:** NVIDIA Jetson Nano (Aceleração por GPU) & Computadores Pessoais.

## ⚙️ Configuração e Instalação

1. **Instalação das Dependências:**
   No terminal, instale as bibliotecas necessárias:
   ```bash
   python -m pip install opencv-python mediapipe python-dotenv requests
   ```

2. **Variáveis de Ambiente (Segurança):**
   Crie um arquivo chamado `.env` na raiz do projeto e insira as chaves do seu Bot do Telegram (nunca suba este arquivo para o GitHub):
   ```env
   TELEGRAM_TOKEN=seu_token_do_botfather_aqui
   TELEGRAM_CHAT_ID=seu_chat_id_aqui
   ```

## 🏃 Como Executar

Para rodar o simulador no ambiente de desenvolvimento (PC):
```bash
python teste_pc.py
```

Para rodar o sistema otimizado no ambiente de produção (NVIDIA Jetson Nano):
```bash
python3 detecao_quedas.py
```

## 📝 Sobre o Projeto
Projeto desenvolvido com foco em aplicações de TCC/Pesquisa Acadêmica voltadas para o monitoramento assistivo, segurança de idosos e visão computacional na área da saúde.