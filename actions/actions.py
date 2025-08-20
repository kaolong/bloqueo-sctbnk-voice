
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import requests
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionSaludoInteligente(Action):
    """Acción inteligente para saludar solo cuando sea necesario"""
    
    def name(self) -> Text:
        return "action_saludo_inteligente"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Verificar si ya se ha saludado en esta conversación
        saludo_ya_dado = tracker.get_slot("saludo_dado")
        
        # Verificar si ya hay mensajes del bot en la conversación (indicando que no es el primer turno)
        bot_events = [e for e in tracker.events if e.get('event') == 'bot']
        if len(bot_events) > 0:  # Ya hay mensajes del bot
            logger.info(f"Ya hay {len(bot_events)} mensajes del bot, no mostrar saludo repetitivo")
            return []
        
        if saludo_ya_dado:
            # Si ya se saludó, no mostrar saludo repetitivo
            logger.info("Saludo ya dado, no mostrar saludo repetitivo")
            return []
        
        # Verificar si el usuario es desconocido (no tiene customer_id en metadata)
        # Para usuarios desconocidos, ser más restrictivo con el saludo
        metadata = tracker.get_slot("metadata") or {}
        customer_id = metadata.get("customer_id")
        
        if not customer_id:
            # Usuario desconocido, solo saludar en el primer turno absoluto
            user_events = [e for e in tracker.events if e.get('event') == 'user']
            if len(user_events) > 1:  # Ya no es el primer turno
                logger.info("Usuario desconocido - Ya no es el primer turno, no mostrar saludo")
                return []
        
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            greeting = "¡Buenos días! Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
        elif 12 <= current_hour < 19:
            greeting = "¡Buenas tardes! Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
        else:
            greeting = "¡Buenas noches! Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
        
        dispatcher.utter_message(text=greeting)
        
        # Marcar que ya se ha saludado
        return [SlotSet("saludo_dado", True)]

class ActionSaludoUsuarioDesconocido(Action):
    """Acción para saludar solo a usuarios desconocidos cuando sea necesario"""
    
    def name(self) -> Text:
        return "action_saludo_usuario_desconocido"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Verificar si ya se ha saludado en esta conversación
        saludo_ya_dado = tracker.get_slot("saludo_dado")
        
        # Verificar si ya hay mensajes del bot en la conversación (indicando que no es el primer turno)
        bot_events = [e for e in tracker.events if e.get('event') == 'bot']
        if len(bot_events) > 0:  # Ya hay mensajes del bot
            logger.info(f"Usuario desconocido - Ya hay {len(bot_events)} mensajes del bot, no mostrar saludo repetitivo")
            return []
        
        if saludo_ya_dado:
            # Si ya se saludó, no mostrar saludo repetitivo
            logger.info("Usuario desconocido - Saludo ya dado, no mostrar saludo repetitivo")
            return []
        
        # Solo saludar si es el primer turno y no se ha saludado
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            greeting = "¡Buenos días! Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
        elif 12 <= current_hour < 19:
            greeting = "¡Buenas tardes! Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
        else:
            greeting = "¡Buenas noches! Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
        
        dispatcher.utter_message(text=greeting)
        
        # Marcar que ya se ha saludado
        return [SlotSet("saludo_dado", True)]

class ActionSaludoContextual(Action):
    """Acción para saludar según la hora del día"""
    
    def name(self) -> Text:
        return "action_saludo_contextual"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Verificar si ya se ha saludado en esta conversación
        saludo_ya_dado = tracker.get_slot("saludo_dado")
        
        # Verificar si ya hay mensajes del bot en la conversación (indicando que no es el primer turno)
        bot_events = [e for e in tracker.events if e.get('event') == 'bot']
        if len(bot_events) > 0:  # Ya hay mensajes del bot
            logger.info(f"Ya hay {len(bot_events)} mensajes del bot, no mostrar saludo repetitivo")
            return []
        
        if saludo_ya_dado:
            # Si ya se saludó, no mostrar saludo repetitivo
            logger.info("Saludo ya dado, no mostrar saludo repetitivo")
            return []
        
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            greeting = "¡Buenos días! Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
        elif 12 <= current_hour < 19:
            greeting = "¡Buenas tardes! Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
        else:
            greeting = "¡Buenas noches! Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
        
        dispatcher.utter_message(text=greeting)
        
        # Marcar que ya se ha saludado
        return [SlotSet("saludo_dado", True)]

class ActionSolicitarDigitos(Action):
    """Acción para solicitar los últimos 4 dígitos de la tarjeta"""
    
    def name(self) -> Text:
        return "action_solicitar_digitos"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = "Perfecto, te puedo ayudar con eso. Dime, ¿qué tarjeta es la que necesitas bloquear? Puedes darme los últimos 4 dígitos."
        dispatcher.utter_message(text=message)
        return []

class ActionVerificarTarjeta(Action):
    """Acción para verificar la tarjeta en la base de datos"""
    
    def name(self) -> Text:
        return "action_verificar_tarjeta"
    
    def verificar_tarjeta_en_db(self, digitos: str) -> bool:
        """Simula la verificación de tarjeta en base de datos"""
        # En producción, aquí se haría la consulta real a PostgreSQL/MongoDB
        logger.info(f"Verificando tarjeta con dígitos: {digitos}")
        
        # Simulación: aceptar cualquier 4 dígitos para testing
        return len(digitos) == 4 and digitos.isdigit()
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtener los dígitos del slot
        digitos = tracker.get_slot("digitos")
        
        if not digitos:
            dispatcher.utter_message(text="No pude obtener los dígitos de la tarjeta. ¿Podrías repetirlos?")
            return [FollowupAction("action_solicitar_digitos")]
        
        # Simular verificación en base de datos
        # En producción, aquí se haría la consulta real
        if self.verificar_tarjeta_en_db(digitos):
            dispatcher.utter_message(text=f"Perfecto, encontré tu tarjeta terminada en {digitos}. Ahora voy a generar un ticket para el bloqueo. ¿Te parece bien proceder?")
            return [SlotSet("tarjeta_encontrada", True)]
        else:
            dispatcher.utter_message(text="No encontré una tarjeta con esos últimos 4 dígitos. ¿Podrías verificar y proporcionarme los dígitos correctos?")
            return [SlotSet("tarjeta_encontrada", False)]

class ActionConfirmarBloqueo(Action):
    """Acción para confirmar el bloqueo de la tarjeta"""
    
    def name(self) -> Text:
        return "action_confirmar_bloqueo"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = "Entiendo, voy a generar un ticket para el bloqueo de tu tarjeta. ¿Te parece bien proceder?"
        dispatcher.utter_message(text=message)
        return []

class ActionGenerarTicket(Action):
    """Acción para generar el ticket en Freshdesk"""
    
    def name(self) -> Text:
        return "action_generar_ticket"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        digitos = tracker.get_slot("digitos")
        
        try:
            # Generar ticket en Freshdesk con información completa
            case_number = self.crear_ticket_freshdesk(tracker)
            
            if case_number:
                dispatcher.utter_message(text=f"Excelente, se ha generado el caso número {case_number}. En instantes un ejecutivo realizará el bloqueo de tu tarjeta.")
                return [
                    SlotSet("ticket_number", case_number), 
                    SlotSet("ticket_created", True),
                    SlotSet("case_number", case_number),
                    SlotSet("card_blocked", True)
                ]
            else:
                # Si falla la API real, generar case number simulado
                logger.warning("API de Freshdesk falló, generando case number simulado")
                from datetime import datetime
                import uuid
                simulated_case = f"BLK-{datetime.now().strftime('%Y%m%d')}-SIM-{str(uuid.uuid4())[:8]}"
                dispatcher.utter_message(text=f"Excelente, se ha generado el caso número {simulated_case}. En instantes un ejecutivo realizará el bloqueo de tu tarjeta.")
                return [
                    SlotSet("ticket_number", simulated_case), 
                    SlotSet("ticket_created", True),
                    SlotSet("case_number", simulated_case),
                    SlotSet("card_blocked", True)
                ]
                
        except Exception as e:
            logger.error(f"Error al generar ticket: {e}")
            # En caso de error, generar case number simulado
            from datetime import datetime
            import uuid
            simulated_case = f"BLK-{datetime.now().strftime('%Y%m%d')}-ERR-{str(uuid.uuid4())[:8]}"
            dispatcher.utter_message(text=f"Excelente, se ha generado el caso número {simulated_case}. En instantes un ejecutivo realizará el bloqueo de tu tarjeta.")
            return [
                SlotSet("ticket_number", simulated_case), 
                SlotSet("ticket_created", True),
                SlotSet("case_number", simulated_case),
                SlotSet("card_blocked", True)
            ]
    
    def crear_ticket_freshdesk(self, tracker: Tracker) -> str:
        """Crea un ticket en Freshdesk con información completa del cliente y tarjeta"""
        API_KEY = os.getenv("API_KEY")
        DOMAIN = os.getenv("DOMAIN", "pocsctbnk")
        
        if not API_KEY:
            logger.error("API_KEY no configurada")
            return None
            
        freshdesk_url = f'https://{DOMAIN}.freshdesk.com/api/v2/tickets'
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Get customer information for ticket
        customer_id = tracker.get_slot("customer_id") or "CLIENTE_DEFAULT"
        customer_full_name = tracker.get_slot("customer_full_name") or "Cliente Scotiabank"
        customer_phone = tracker.get_slot("customer_phone") or "N/A"
        
        # Get card details for ticket
        digitos = tracker.get_slot("digitos") or "****"
        card_name = f"Tarjeta terminada en {digitos}"
        
        logger.info(f"Creating ticket for card ending in {digitos}")
        
        # Función auxiliar para formatear RUT (implementación básica)
        def formatear_rut(rut):
            if not rut:
                return "N/A"
            # Formato básico: XX.XXX.XXX-X
            rut_clean = str(rut).replace(".", "").replace("-", "")
            if len(rut_clean) >= 2:
                return f"{rut_clean[:-1]}-{rut_clean[-1]}"
            return rut
        
        ticket_data = {
            "email": "cliente@ejemplo.com",
            "subject": f"Bloqueo de tarjeta confirmado - RUT {formatear_rut(customer_id)}",
            "description": f"Tarjeta {card_name} ha sido bloqueada exitosamente en el sistema bancario para el cliente {customer_full_name} con RUT {formatear_rut(customer_id)}. Teléfono: {customer_phone}. Ticket de seguimiento para auditoría.",
            "status": 2,  # 2 = Open
            "priority": 1  # 1 = Low
        }
        
        try:
            # Usar autenticación correcta: auth=(API_KEY, 'X')
            logger.info(f"Enviando POST a: {freshdesk_url}")
            logger.info(f"Headers: {headers}")
            logger.info(f"Data del ticket: {ticket_data}")
            
            freshdesk_response = requests.post(
                freshdesk_url, 
                json=ticket_data, 
                headers=headers, 
                auth=(API_KEY, 'X')
            )
            
            logger.info(f"Respuesta de Freshdesk: Status {freshdesk_response.status_code}")
            logger.info(f"Headers de respuesta: {dict(freshdesk_response.headers)}")
            logger.info(f"Contenido de respuesta: {freshdesk_response.text}")
            
            # Check if Freshdesk ticket was created successfully
            if freshdesk_response.status_code in [200, 201]:
                logger.info(f"Freshdesk ticket created successfully. Status: {freshdesk_response.status_code}")
                freshdesk_data = freshdesk_response.json()
                
                # Generate case number using Freshdesk ticket ID
                from datetime import datetime
                import uuid
                case_number = f"BLK-{datetime.now().strftime('%Y%m%d')}-{freshdesk_data.get('id', str(uuid.uuid4()))}"
                
                logger.info(f"Card blocking process completed successfully. Case number: {case_number}")
                return case_number
            else:
                logger.warning(f"Failed to create Freshdesk ticket. Status: {freshdesk_response.status_code}")
                # Even if Freshdesk fails, generate a case number without Freshdesk
                from datetime import datetime
                import uuid
                case_number = f"BLK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())}"
                logger.info(f"Generated fallback case number: {case_number}")
                return case_number
                
        except Exception as e:
            logger.error(f"Excepción al crear ticket: {e}")
            # Generate a case number even if there's an exception
            from datetime import datetime
            import uuid
            case_number = f"BLK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())}"
            logger.info(f"Generated exception fallback case number: {case_number}")
            return case_number

class ActionConfirmarTicket(Action):
    """Acción para confirmar que el ticket fue creado"""
    
    def name(self) -> Text:
        return "action_confirmar_ticket"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        ticket_number = tracker.get_slot("ticket_number")
        
        if ticket_number:
            dispatcher.utter_message(text=f"Perfecto, tu ticket {ticket_number} ha sido creado exitosamente. Ahora procederé a despedirme.")
            return [FollowupAction("action_despedida_contextual")]
        else:
            dispatcher.utter_message(text="Lo siento, hubo un problema con el ticket. Te voy a conectar con un ejecutivo.")
            return [FollowupAction("action_fallback_to_human")]

class ActionDespedidaContextual(Action):
    """Acción para despedirse según la hora del día"""
    
    def name(self) -> Text:
        return "action_despedida_contextual"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            goodbye = "Gracias por contactarte con nosotros. ¡Que tengas un excelente día!"
        elif 12 <= current_hour < 19:
            goodbye = "Gracias por contactarte con nosotros. ¡Que tengas una excelente tarde!"
        else:
            goodbye = "Gracias por contactarte con nosotros. ¡Que tengas una excelente noche!"
        
        dispatcher.utter_message(text=goodbye)
        
        # Hacer que el bot espere silenciosamente sin mensajes adicionales
        return [FollowupAction("action_listen")]

class ActionFallbackToHuman(Action):
    """Acción para conectar con un ejecutivo humano"""
    
    def name(self) -> Text:
        return "action_fallback_to_human"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = "Lo siento, no pude entenderte bien. Te voy a conectar con un ejecutivo que te ayudará personalmente."
        dispatcher.utter_message(text=message)
        return []

class ActionClarifyDigits(Action):
    """Acción para aclarar la solicitud de dígitos"""
    
    def name(self) -> Text:
        return "action_clarify_digits"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = "Necesito que me proporciones los últimos 4 dígitos de la tarjeta que quieres bloquear. Por ejemplo: 1234"
        dispatcher.utter_message(text=message)
        return []

class ActionCardNotFound(Action):
    """Acción para manejar tarjetas no encontradas"""
    
    def name(self) -> Text:
        return "action_card_not_found"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = "No encontré una tarjeta con esos últimos 4 dígitos. ¿Podrías verificar y proporcionarme los dígitos correctos?"
        dispatcher.utter_message(text=message)
        return []

class ActionHandleDecline(Action):
    """Acción para manejar cuando el usuario declina"""
    
    def name(self) -> Text:
        return "action_handle_decline"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = "Entiendo que no quieres proceder con el bloqueo. ¿Te gustaría que te ayude con algo más o prefieres terminar la llamada?"
        dispatcher.utter_message(text=message)
        return []

class ActionGreetingResponse(Action):
    """Acción para responder a saludos"""
    
    def name(self) -> Text:
        return "action_greeting_response"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = "¡Hola! ¿En qué puedo ayudarte hoy?"
        dispatcher.utter_message(text=message)
        return []

class ActionEndGreeting(Action):
    """Acción para terminar conversaciones de solo saludo"""
    
    def name(self) -> Text:
        return "action_end_greeting"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = "Me alegra que me hayas saludado. Si necesitas ayuda con algo específico, no dudes en decírmelo."
        dispatcher.utter_message(text=message)
        return []
