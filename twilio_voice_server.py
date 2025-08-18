#!/usr/bin/env python3
"""
Servidor Flask para integración de Twilio Voice con Rasa Pro
Maneja llamadas entrantes y las convierte en texto para Rasa
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración
RASA_WEBHOOK_URL = os.getenv('RASA_WEBHOOK_URL', 'http://localhost:5005/webhooks/rest/webhook')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'TU_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'TU_AUTH_TOKEN')

# Configuración de Polly
POLLY_VOICE = os.getenv('POLLY_VOICE', 'Polly.Mia')
POLLY_LANGUAGE = os.getenv('POLLY_LANGUAGE', 'es-MX')
POLLY_SPEED = os.getenv('POLLY_SPEED', '1.0')

class TwilioVoiceHandler:
    """Maneja llamadas de voz de Twilio y las convierte para Rasa"""
    
    def __init__(self):
        self.session_data = {}
        # Cache para evitar saludos repetitivos por call_sid
        self.saludos_dados = set()
    
    def get_greeting_by_time(self) -> str:
        """Retorna saludo según la hora del día"""
        hour = datetime.now().hour
        
        if 6 <= hour < 12:
            return "¡Buenos días! Soy el asistente de Scotiabank. ¿En qué puedo ayudarte?"
        elif 12 <= hour < 19:
            return "¡Buenas tardes! Soy el asistente de Scotiabank. ¿En qué puedo ayudarte?"
        else:
            return "¡Buenas noches! Soy el asistente de Scotiabank. ¿En qué puedo ayudarte?"
    
    def get_voice_config(self) -> dict:
        """Retorna configuración de voz optimizada"""
        return {
            'voice': POLLY_VOICE,
            'language': POLLY_LANGUAGE,
            'speed': POLLY_SPEED
        }
    
    def handle_incoming_call(self, call_sid: str, from_number: str, to_number: str) -> str:
        """Maneja una llamada entrante"""
        logging.info(f"📞 Llamada entrante: {call_sid} desde  {from_number} a  {to_number}")
        
        # Crear respuesta TwiML
        response = VoiceResponse()
        
        # SALUDO INMEDIATO cuando se recibe la llamada
        greeting = self.get_greeting_by_time()
        voice_config = self.get_voice_config()
        
        # Configurar Gather para capturar voz del usuario
        gather = Gather(
            action=f"/webhook/twilio/speech?call_sid={call_sid}",
            input="speech",
            language="es-MX",
            method="POST",
            speech_timeout="auto"
        )
        
        # Decir el saludo inmediatamente
        gather.say(
            greeting,
            voice=voice_config['voice'],
            language=voice_config['language']
        )
        
        # Agregar Gather a la respuesta
        response.append(gather)
        
        # Fallback si no se captura voz
        response.redirect(f"/webhook/twilio/fallback?call_sid={call_sid}")
        
        return str(response)
    
    def handle_speech_input(self, call_sid: str, speech_input: str, confidence: float) -> str:
        """Maneja el input de voz del usuario"""
        logging.info(f"🎤 Input de voz recibido: {speech_input} (confianza: {confidence})")
        
        # Enviar a Rasa para procesamiento
        rasa_response = self.send_to_rasa(call_sid, speech_input)
        
        if not rasa_response:
            # Si Rasa no responde, usar fallback
            return self.handle_fallback(call_sid)
        
        # Crear respuesta TwiML
        response = VoiceResponse()
        
        # Configurar Gather para la siguiente interacción
        gather = Gather(
            action=f"/webhook/twilio/speech?call_sid={call_sid}",
            input="speech",
            language="es-MX",
            method="POST",
            speech_timeout="auto"
        )
        
        # Decir la respuesta de Rasa (sin saludo duplicado)
        voice_config = self.get_voice_config()
        gather.say(
            rasa_response,
            voice=voice_config['voice'],
            language=voice_config['language']
        )
        
        # Agregar Gather a la respuesta
        response.append(gather)
        
        # Fallback si no se captura voz
        response.redirect(f"/webhook/twilio/fallback?call_sid={call_sid}")
        
        return str(response)
    
    def send_to_rasa(self, call_sid: str, message: str) -> Optional[str]:
        """Envía mensaje a Rasa y obtiene respuesta"""
        try:
            # Asegurar que call_sid no sea None
            if not call_sid:
                call_sid = "unknown_call"
                logger.warning(f"⚠️ call_sid es None, usando valor por defecto: {call_sid}")
            
            payload = {
                "sender": call_sid,
                "message": message
            }
            
            logger.info(f"📤 Enviando a Rasa: {payload}")
            
            response = requests.post(
                RASA_WEBHOOK_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                rasa_data = response.json()
                if rasa_data:
                    # Si hay múltiples respuestas, combinarlas en una sola respuesta coherente
                    if len(rasa_data) > 1:
                        logger.info(f"📥 Rasa retornó {len(rasa_data)} respuestas")
                        for i, resp in enumerate(rasa_data):
                            logger.info(f"📥 Respuesta {i+1}: {resp.get('text', '')}")
                        
                        # Combinar todas las respuestas en una sola
                        combined_responses = []
                        for resp in rasa_data:
                            text = resp.get('text', '').strip()
                            if text and text not in combined_responses:
                                combined_responses.append(text)
                        
                        response_text = " ".join(combined_responses)
                        logger.info(f"📥 Respuesta combinada: {response_text}")
                        return response_text
                    
                    # Si solo hay una respuesta, usarla directamente
                    response_text = rasa_data[0].get('text', '')
                    logger.info(f"📥 Respuesta única: {response_text}")
                    return response_text
            
            logger.warning(f"⚠️ Rasa retornó status {response.status_code}: {response.text}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error enviando a Rasa: {e}")
            return None
    
    def handle_fallback(self, call_sid: str) -> str:
        """Maneja casos donde no hay input del usuario"""
        logger.info(f"🔄 Fallback para llamada: {call_sid}")
        
        response = VoiceResponse()
        response.say(
            "No recibí tu respuesta. Te voy a conectar con un ejecutivo.",
            voice=self.get_voice_config()['voice'],
            language=self.get_voice_config()['language']
        )
        response.dial('+1234567890')  # Número de fallback
        
        return str(response)
    
    def handle_call_status(self, call_sid: str, call_status: str, duration: str = None) -> str:
        """Maneja el status de las llamadas"""
        logger.info(f"📊 Status de llamada {call_sid}: {call_status}, duración: {duration}")
        
        if call_status == 'completed':
            logger.info(f"✅ Llamada {call_sid} completada exitosamente")
        elif call_status == 'failed':
            logger.error(f"❌ Llamada {call_sid} falló")
        elif call_status == 'busy':
            logger.warning(f"⏳ Llamada {call_sid} ocupada")
        
        return "OK"

# Instancia global del handler
voice_handler = TwilioVoiceHandler()

@app.route('/webhook/twilio/voice', methods=['POST'])
def incoming_call():
    """Endpoint para llamadas entrantes"""
    try:
        # Obtener datos de la llamada
        call_sid = request.form.get('CallSid')
        from_number = request.form.get('From')
        to_number = request.form.get('To')
        
        # Generar respuesta de TwiML
        twiml_response = voice_handler.handle_incoming_call(call_sid, from_number, to_number)
        
        return Response(twiml_response, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"❌ Error en incoming_call: {e}")
        return Response("Error", status=500)

@app.route('/webhook/twilio/speech', methods=['POST'])
def speech_webhook():
    """Webhook para procesar input de voz"""
    call_sid = request.args.get('call_sid')
    if not call_sid:
        call_sid = request.form.get('CallSid')
    
    if call_sid:
        logging.info(f"🔍 call_sid extraído: {call_sid}")
        logging.info(f"🔍 request.args: {dict(request.args)}")
        logging.info(f"🔍 request.form: {dict(request.form)}")
    
    speech_input = request.form.get('SpeechResult', '')
    confidence = float(request.form.get('Confidence', 0))
    
    if not speech_input:
        return "Error: No se recibió input de voz", 400
    
    # Procesar con el handler
    twiml_response = voice_handler.handle_speech_input(call_sid, speech_input, confidence)
    return Response(twiml_response, mimetype='text/xml')

@app.route('/webhook/twilio/fallback', methods=['POST'])
def fallback():
    """Endpoint para fallbacks"""
    try:
        # Obtener call_sid de los parámetros de query string (URL)
        call_sid = request.args.get('call_sid')
        
        # Si no está en query string, intentar del formulario
        if not call_sid:
            call_sid = request.form.get('call_sid')
        
        logger.info(f"🔍 call_sid en fallback: {call_sid}")
        
        # Generar respuesta de TwiML
        twiml_response = voice_handler.handle_fallback(call_sid)
        
        return Response(twiml_response, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"❌ Error en fallback: {e}")
        return Response("Error", status=500)

@app.route('/webhook/twilio/status', methods=['POST'])
def call_status():
    """Endpoint para status de llamadas"""
    try:
        call_sid = request.form.get('CallSid')
        call_status = request.form.get('CallStatus')
        duration = request.form.get('CallDuration')
        
        # Manejar status
        voice_handler.handle_call_status(call_sid, call_status, duration)
        
        return Response("OK", status=200)
        
    except Exception as e:
        logger.error(f"❌ Error en call_status: {e}")
        return Response("Error", status=500)

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servidor"""
    return {
        "status": "healthy",
        "service": "Twilio Voice Server",
        "timestamp": datetime.now().isoformat(),
        "rasa_webhook": RASA_WEBHOOK_URL
    }

@app.route('/', methods=['GET'])
def root():
    """Endpoint raíz con información del servidor"""
    return {
        "message": "Servidor de Twilio Voice para Rasa Pro",
        "endpoints": {
            "voice": "/webhook/twilio/voice",
            "speech": "/webhook/twilio/speech", 
            "fallback": "/webhook/twilio/fallback",
            "status": "/webhook/twilio/status",
            "health": "/health"
        },
        "usage": "Este servidor actúa como intermediario entre Twilio Voice y Rasa Pro"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Iniciando servidor Twilio Voice en puerto {port}")
    logger.info(f"🔗 Rasa webhook: {RASA_WEBHOOK_URL}")
    logger.info(f"🐛 Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug,
        threaded=True
    )
