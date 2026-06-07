import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS

# ==========================================
# DATOS DE BRIAN DIRECTOS DE TU COLA DE DATOS
# ==========================================
GROQ_API_KEY = "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"
TELEGRAM_TOKEN = "8919816601:AAG4ibrZIjeAmSMP8l6BU8KWDoU3JSMRMu4"
ID_PERMITIDO = 8299149065
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ID_PERMITIDO:
        return
    await update.message.reply_text("¡Hola Brian! Tu asistente ya está corriendo en Render sin bloqueos de red. ¿En qué te ayudo hoy?")

def consultar_groq(pregunta):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system", 
                "content": "Eres un asistente de hogar inteligente para Brian. Responde de forma clara, concisa y amigable en español."
            },
            {"role": "user", "content": pregunta}
        ]
    }
    try:
        respuesta = requests.post(url, json=payload, headers=headers)
        return respuesta.json()['choices'][0]['message']['content']
    except Exception as e:
        return "Tuve un pequeño problema al conectarme a mi cerebro en la nube."

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ID_PERMITIDO:
        return

    texto_usuario = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    comando = texto_usuario.lower()
    if "prende la pc" in comando or "encender la pc" in comando:
        await update.message.reply_text("🔧 Recibido. Enviando señal para encender tu PC de escritorio...")
        return
        
    if "apaga la tele" in comando or "apagar la tele" in comando:
        await update.message.reply_text("🔧 Entendido. Mandando señal para apagar la televisión...")
        return

    respuesta_ia = consultar_groq(texto_usuario)
    await update.message.reply_text(respuesta_ia)
    
    try:
        tts = gTTS(text=respuesta_ia, lang='es', slow=False)
        archivo_audio = "respuesta.mp3"
        tts.save(archivo_audio)
        
        with open(archivo_audio, 'rb') as audio:
            await context.bot.send_voice(chat_id=update.effective_chat.id, voice=audio)
            
        os.remove(archivo_audio)
    except Exception as e:
        print(f"Error al generar audio: {e}")

def main():
    # En Render usamos la conexión estándar directa porque la red sí funciona libremente
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    
    print("Bot iniciado exitosamente en plataforma limpia.")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
