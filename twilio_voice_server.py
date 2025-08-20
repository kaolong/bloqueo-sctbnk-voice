#!/usr/bin/env python3
"""
Servidor Flask para integración de Twilio Voice con Rasa Pro
Maneja llamadas entrantes y las convierte en texto para Rasa
"""

import os
import logging
import requests
from datetime import datetime
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather, Say, Redirect, Dial
import pymysql
from dotenv import load_dotenv
from typing import Optional
import re

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Consola
        logging.FileHandler('/tmp/twilio_voice_server.log')  # Archivo
    ]
)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)

class TwilioVoiceHandler:
    """Maneja llamadas de voz de Twilio y las convierte para Rasa"""
    
    def __init__(self):
        """Inicializa el manejador de voz de Twilio"""
        self.rasa_webhook_url = os.getenv('RASA_WEBHOOK_URL', 'http://localhost:5005/webhooks/rest/webhook')
        self.fallback_phone = os.getenv('FALLBACK_PHONE_NUMBER', '+56982221070')
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Configuración de base de datos
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'mauro'),
            'password': os.getenv('DB_PASSWORD', 'santiago01'),
            'database': os.getenv('DB_NAME', 'bank'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        
        # Cache para evitar saludos duplicados por conversación
        self.saludos_por_conversacion = {}
        
        # Cache global para evitar saludos duplicados en toda la sesión
        self.saludos_globales = set()
        
        # Cache para mantener números de teléfono por call_sid
        self.phone_numbers_by_call = {}
    
    def get_database_connection(self):
        """Crea una conexión a la base de datos MariaDB"""
        try:
            connection = pymysql.connect(**self.db_config)
            return connection
        except Exception as e:
            logger.error(f"❌ Error conectando a la base de datos: {e}")
            return None
    
    def get_customer_by_phone(self, phone_number: str):
        """Busca información del cliente por número de teléfono en la base de datos"""
        try:
            connection = self.get_database_connection()
            if not connection:
                return None
            
            with connection.cursor() as cursor:
                # Normalización robusta del teléfono
                raw_phone = (phone_number or '').strip()
                digits_only = re.sub(r"\D", "", raw_phone)
                candidates = []
                if raw_phone:
                    candidates.append(raw_phone)
                if digits_only:
                    candidates.append(digits_only)
                    candidates.append(f"+{digits_only}")
                # Quitar duplicados preservando orden
                seen = set()
                norm_candidates = []
                for c in candidates:
                    if c and c not in seen:
                        seen.add(c)
                        norm_candidates.append(c)
                
                # Construir consulta con múltiples candidatos
                conditions = " OR ".join(["telefono = %s" for _ in norm_candidates])
                sql = f"""
                SELECT id, rut, nombre, nombre_completo, telefono, fecha_creacion
                FROM customers
                WHERE {conditions}
                LIMIT 1
                """
                cursor.execute(sql, tuple(norm_candidates))
                customer = cursor.fetchone()
                
                logger.info(f"📱 Candidatos de búsqueda: {norm_candidates}")
                
                if customer:
                    logger.info(f"👤 Cliente encontrado: {customer['nombre_completo']} (ID: {customer['id']})")
                    logger.info(f"📱 Teléfono en BD: {customer['telefono']}, Buscado: {raw_phone}")
                    return customer
                else:
                    logger.info(f"❌ No se encontró cliente con teléfono: {raw_phone} (digits: {digits_only})")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error consultando cliente por teléfono: {e}")
            return None
        finally:
            if connection:
                connection.close()
    
    def get_greeting_by_time(self):
        """Retorna un saludo basado en la hora del día"""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            return "¡Buenos días!"
        elif 12 <= current_hour < 19:
            return "¡Buenas tardes!"
        else:
            return "¡Buenas noches!"
    
    def get_voice_config(self):
        """Retorna la configuración de voz desde variables de entorno"""
        return {
            'voice': os.getenv('POLLY_VOICE', 'Polly.Mia'),
            'language': os.getenv('POLLY_LANGUAGE', 'es-MX'),
            'speed': os.getenv('POLLY_SPEED', '1.0')
        }
    
    def handle_incoming_call(self, call_sid: str, from_number: str, to_number: str) -> str:
        """Maneja una llamada entrante"""
        # Normalizar números de entrada (trims)
        if from_number:
            from_number = from_number.strip()
        if to_number:
            to_number = to_number.strip()
        
        logger.info(f"📞 Llamada entrante: {call_sid} desde {from_number} a {to_number}")
        
        # Guardar número de teléfono en cache para uso posterior
        self.phone_numbers_by_call[call_sid] = from_number
        
        # Buscar cliente en base de datos
        customer = self.get_customer_by_phone(from_number)
        
        if customer:
            logger.info(f"🎯 Cliente identificado: {customer['nombre_completo']}")
        else:
            logger.info(f"👤 Cliente no identificado para teléfono: {from_number}")
        
        # Crear respuesta TwiML
        response = VoiceResponse()
        
        # SALUDO INMEDIATO cuando se recibe la llamada
        greeting = self.get_greeting_by_time()
        voice_config = self.get_voice_config()
        
        # Personalizar saludo si se conoce al cliente
        if customer:
            personalized_greeting = f"{greeting} {customer['nombre']}, soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
            logger.info(f"🎯 Saludo personalizado para cliente: {customer['nombre_completo']}")
            logger.info(f"🎯 Saludo generado: {personalized_greeting}")
        else:
            personalized_greeting = f"{greeting} Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
            logger.info(f"👤 Cliente no identificado, usando saludo genérico")
            logger.info(f"👤 Saludo generado: {personalized_greeting}")
        
        # Configurar Gather para capturar voz del usuario
        gather = Gather(
            action=f"/webhook/twilio/speech?call_sid={call_sid}",
            input="speech",
            language="es-MX",
            method="POST",
            speech_timeout="auto"
        )
        
        # Decir el saludo personalizado
        gather.say(
            personalized_greeting,
            voice=voice_config['voice'],
            language=voice_config['language']
        )
        
        # Marcar que ya se dio saludo en esta conversación
        self.saludos_por_conversacion[call_sid] = True
        logger.info(f"🎯 Saludo inicial marcado en cache para {call_sid}")
        
        response.append(gather)
        
        # Redirigir a fallback si no hay input
        response.redirect(f"/webhook/twilio/fallback?call_sid={call_sid}")
        
        return str(response)
    
    def handle_speech_input(self, call_sid: str, speech_input: str, confidence: float, from_number: str = None) -> str:
        """Maneja el input de voz del usuario"""
        logger.info(f"🎤 Input de voz recibido: {speech_input} (confianza: {confidence})")
        
        # Buscar cliente por número de teléfono del cache
        customer = None
        from_number = self.phone_numbers_by_call.get(call_sid)
        if from_number:
            customer = self.get_customer_by_phone(from_number)
            if customer:
                logger.info(f"👤 Procesando para Cliente: {customer['nombre_completo']}")
            else:
                logger.info(f"👤 Cliente no encontrado para teléfono: {from_number}")
        else:
            logger.warning("⚠️ No se encontró número de teléfono en cache para call_sid: {call_sid}")
        
        # Enviar a Rasa para procesamiento
        rasa_response = self.send_to_rasa(call_sid, speech_input, customer)
        
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
        
        # Decir la respuesta de Rasa
        voice_config = self.get_voice_config()
        gather.say(
            rasa_response,
            voice=voice_config['voice'],
            language=voice_config['language']
        )
        
        response.append(gather)
        
        # Redirigir a fallback si no hay input
        response.redirect(f"/webhook/twilio/fallback?call_sid={call_sid}")
        
        return str(response)
    
    def limpiar_cache_saludos(self, call_sid: str):
        """Limpia el cache de saludos para una conversación específica"""
        if call_sid in self.saludos_por_conversacion:
            del self.saludos_por_conversacion[call_sid]
            logger.info(f"🧹 Cache de saludos limpiado para conversación: {call_sid}")
    
    def limpiar_cache_conversacion(self, call_sid: str):
        """Limpia todos los caches relacionados con una conversación específica"""
        # Limpiar cache de saludos
        if call_sid in self.saludos_por_conversacion:
            del self.saludos_por_conversacion[call_sid]
            logger.info(f"🧹 Cache de saludos limpiado para conversación: {call_sid}")
        
        # Limpiar cache de números de teléfono
        if call_sid in self.phone_numbers_by_call:
            del self.phone_numbers_by_call[call_sid]
            logger.info(f"🧹 Cache de números de teléfono limpiado para conversación: {call_sid}")
    
    def send_to_rasa(self, call_sid: str, message: str, customer: dict = None) -> str:
        """Envía mensaje a Rasa y retorna la respuesta procesada"""
        try:
            rasa_data = {
                'sender': call_sid,
                'message': message
            }
            
            if customer:
                rasa_data['metadata'] = {
                    'customer_id': customer['id'],
                    'customer_name': customer['nombre'],
                    'customer_full_name': customer['nombre_completo'],
                    'customer_rut': customer['rut'],
                    'customer_phone': customer['telefono']
                }
                logger.info(f"📤 Enviando a Rasa con datos del cliente: {customer['nombre_completo']}")
            else:
                logger.info(f"📤 Enviando a Rasa: {rasa_data}")
            
            response = requests.post(self.rasa_webhook_url, json=rasa_data)
            response.raise_for_status()
            
            rasa_responses = response.json()
            logger.info(f"📥 Rasa retornó {len(rasa_responses)} respuestas")
            
            if not rasa_responses:
                logger.warning("⚠️ Rasa no retornó respuestas")
                return "Lo siento, no pude procesar tu solicitud. Te voy a conectar con un ejecutivo."
            
            # Procesar y filtrar respuestas para evitar saludos duplicados
            filtered_responses = []
            
            # Verificar si ya se dio un saludo en esta conversación
            saludo_ya_dado = self.saludos_por_conversacion.get(call_sid, False)
            logger.info(f"🎯 Estado del cache de saludos para {call_sid}: {'Ya se dio saludo' if saludo_ya_dado else 'No se ha dado saludo'}")
            logger.info(f"🎯 Cache completo: {self.saludos_por_conversacion}")
            
            # Lógica inteligente para filtrar saludos duplicados
            saludo_incluido = False
            
            for i, resp in enumerate(rasa_responses):
                text = resp.get('text', '')
                logger.info(f"📥 Respuesta {i+1}: {text}")
                
                # Detectar si es un saludo
                es_saludo = any(palabra in text.lower() for palabra in ['buenos días', 'buenas tardes', 'buenas noches', 'soy el asistente'])
                logger.info(f"🎯 ¿Es saludo? {es_saludo} - ¿Ya se dio saludo? {saludo_ya_dado} - ¿Saludo incluido? {saludo_incluido}")
                
                if es_saludo:
                    # Para TODOS los usuarios (conocidos y desconocidos), filtrar saludos después del primero
                    if saludo_ya_dado:
                        # Ya se dio saludo en esta conversación, filtrarlo
                        logger.info(f"🚫 Filtrando saludo repetitivo para {'usuario conocido' if customer else 'usuario desconocido'}: {text}")
                        continue
                    else:
                        # Primer saludo de la conversación, incluirlo
                        saludo_incluido = True
                        self.saludos_por_conversacion[call_sid] = True
                        logger.info(f"🎯 Primer saludo de la conversación incluido para {'usuario conocido' if customer else 'usuario desconocido'}: {text}")
                        filtered_responses.append(text)
                else:
                    # No es saludo, incluir siempre
                    filtered_responses.append(text)
            
            # Combinar respuestas filtradas
            if filtered_responses:
                combined_response = " ".join(filtered_responses)
                logger.info(f"📥 Respuesta combinada (filtrada): {combined_response}")
                return combined_response
            else:
                # Si todas las respuestas fueron filtradas, usar la primera original
                first_response = rasa_responses[0].get('text', '')
                logger.info(f"📥 Usando primera respuesta (filtrado falló): {first_response}")
                return first_response
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error enviando a Rasa: {e}")
            return "Lo siento, hay un problema técnico. Te voy a conectar con un ejecutivo."
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return "Lo siento, ocurrió un error inesperado. Te voy a conectar con un ejecutivo."
    
    def handle_fallback(self, call_sid: str) -> str:
        """Maneja casos donde no hay input del usuario"""
        logger.info(f"🔄 Fallback para llamada: {call_sid}")
        
        response = VoiceResponse()
        voice_config = self.get_voice_config()
        
        # Mensaje de fallback
        response.say(
            "No pude entender tu respuesta. Por favor, intenta de nuevo o espera a que un ejecutivo te atienda.",
            voice=voice_config['voice'],
            language=voice_config['language']
        )
        
        # Redirigir a un ejecutivo o terminar la llamada
        response.redirect(f"/webhook/twilio/fallback?call_sid={call_sid}")
        
        return str(response)
    
    def handle_call_status(self, call_sid: str, call_status: str, duration: str = None) -> str:
        """Maneja el status de las llamadas"""
        logger.info(f"📊 Status de llamada {call_sid}: {call_status}, duración: {duration}")
        
        if call_status == 'completed':
            logger.info(f"✅ Llamada {call_sid} completada exitosamente")
            # Limpiar cache cuando termine la llamada
            self.limpiar_cache_conversacion(call_sid)
        elif call_status == 'failed':
            logger.error(f"❌ Llamada {call_sid} falló")
            # Limpiar cache si falló
            self.limpiar_cache_conversacion(call_sid)
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
        customer_id = request.args.get('customer_id') # Obtener customer_id de query parameters
        
        # Normalizar entradas del webhook
        if from_number:
            from_number = from_number.strip()
        if to_number:
            to_number = to_number.strip()
        
        # 🆕 LOGGING DETALLADO PARA DEBUG
        logger.info(f"🔍 Webhook recibido:")
        logger.info(f"   📞 Call SID: {call_sid}")
        logger.info(f"   📱 From: {from_number}")
        logger.info(f"   📞 To: {to_number}")
        logger.info(f"   🆔 Customer ID: {customer_id}")
        logger.info(f"   📝 Form data: {dict(request.form)}")
        logger.info(f"   🔗 Args: {dict(request.args)}")
        
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
    
    customer_id = request.args.get('customer_id') # Obtener customer_id de query parameters
    
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
        
        customer_id = request.args.get('customer_id') # Obtener customer_id de query parameters
        
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
        "rasa_webhook": voice_handler.rasa_webhook_url
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
    logger.info(f"🔗 Rasa webhook: {voice_handler.rasa_webhook_url}")
    logger.info(f"🐛 Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug,
        threaded=True
    )
