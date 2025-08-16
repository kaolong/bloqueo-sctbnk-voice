# System Patterns: Bloqueo de Tarjetas SCTBNK con Rasa Pro

## Arquitectura del Sistema

### **Arquitectura General**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cliente       │    │   Twilio        │    │   Rasa Pro      │
│   (Teléfono)    │◄──►│   (Telefonía)   │◄──►│   (Chatbot)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Base de       │    │   Freshdesk     │    │   Sistema de    │
│   Datos         │    │   API           │    │   Logging       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Componentes Principales**

#### 1. **Rasa Pro 3.13.5 (Core del Sistema)**
- **Tecnología**: Rasa Pro con CALM (Conversational AI with Language Models)
- **Patrón**: Arquitectura moderna de Flows y Patterns
- **Funcionalidades**: 
  - **Flows para Lógica de Negocio**: Implementación escalable de tareas
  - **Patrones de Conversación Automáticos**: Manejo automático de cambios de tema, correcciones
  - **LLMs para Interacciones Contextuales**: Asistentes más robustos y fáciles de mantener
  - **Seguridad Integrada**: Resistente a alucinaciones, inyección de prompts y jailbreaking
  - **Control Total del Negocio**: Lógica de negocio siempre seguida correctamente
  - **Componentes Reutilizables**: Tareas descompuestas en piezas reutilizables

#### 2. **Twilio (Telefonía)**
- **Tecnología**: Twilio Voice API
- **Patrón**: Webhook-based communication
- **Funcionalidades**:
  - Recepción de llamadas entrantes
  - Text-to-Speech (TTS)
  - Manejo de eventos de llamada
  - Integración con Rasa via webhooks

#### 3. **Base de Datos**
- **Tecnología**: PostgreSQL o MongoDB
- **Patrón**: Repository pattern para consultas de tarjetas
- **Funcionalidades**:
  - Almacenamiento de información de tarjetas
  - Consulta por últimos 4 dígitos
  - Verificación de estado de tarjetas
  - Logging de transacciones

#### 4. **Freshdesk Integration**
- **Tecnología**: REST API
- **Patrón**: Service layer para creación de tickets
- **Funcionalidades**:
  - Creación automática de tickets
  - Asignación de prioridades
  - Inclusión de información del cliente
  - Tracking de estado del ticket

## Patrones de Diseño

### **Patrón Moderno de Flows y Patterns (CALM)**
```yaml
# flows.yml - Flujo principal de bloqueo usando la nueva arquitectura
flows:
  - name: bloqueo_tarjeta_flow
    description: "Flujo principal para bloqueo de tarjetas usando CALM"
    steps:
      - step: start
        action: action_saludo_contextual
        next:
          - condition: user_wants_to_block_card
            step: solicitar_digitos
          - condition: user_greeting
            step: greeting_response
      
      - step: solicitar_digitos
        action: action_solicitar_digitos
        next:
          - condition: user_provided_digits
            step: verificar_tarjeta
          - condition: user_confused
            step: clarify_digits_request
      
      - step: verificar_tarjeta
        action: action_verificar_tarjeta
        next:
          - condition: card_verified
            step: confirmar_bloqueo
          - condition: card_not_found
            step: card_not_found_response
      
      - step: confirmar_bloqueo
        action: action_confirmar_bloqueo
        next:
          - condition: user_confirmed
            step: generar_ticket
          - condition: user_declined
            step: decline_response
      
      - step: generar_ticket
        action: action_generar_ticket
        next:
          - condition: ticket_created
            step: confirmar_ticket
          - condition: ticket_failed
            step: fallback_to_human
      
      - step: confirmar_ticket
        action: action_confirmar_ticket
        next:
          - condition: conversation_complete
            step: despedida
      
      - step: despedida
        action: action_despedida_contextual
        next:
          - condition: end_conversation
            step: end
```

### **Patrón Moderno de LLM con CALM**
```yaml
# nlu.yml - Configuración moderna con CALM
nlu:
  - intent: user_wants_to_block_card
    examples: |
      - necesito bloquear mi tarjeta
      - quiero bloquear mi tarjeta
      - mi tarjeta fue robada
      - perdí mi tarjeta
      - necesito cancelar mi tarjeta
      - mi tarjeta está comprometida
      - quiero reportar mi tarjeta como perdida
      - bloquea mi tarjeta
      - cancela mi tarjeta
      - reporta mi tarjeta
    # CALM maneja automáticamente variaciones y contexto

  - intent: user_confirmation
    examples: |
      - sí
      - correcto
      - perfecto
      - adelante
      - procede
      - sí, procede
      - está bien
      - de acuerdo
    # CALM entiende confirmaciones en contexto
```

### **Patrón Moderno de Entity Extraction con CALM**
```yaml
# nlu.yml - Entidades con CALM para mejor extracción
nlu:
  - intent: user_provided_digits
    examples: |
      - es la [1234](digitos)
      - son los [5678](digitos)
      - [9012](digitos)
      - la tarjeta [3456](digitos)
      - [7890](digitos)
      - mi tarjeta termina en [1111](digitos)
      - los últimos cuatro son [2222](digitos)
    entities:
      - digitos:
          type: regex
          pattern: "\d{4}"
    # CALM mejora la extracción contextual de entidades
```

### **Patrón Action Custom**
```python
# actions.py - Acciones personalizadas
class ActionSaludoContextual(Action):
    def name(self) -> Text:
        return "action_saludo_contextual"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtener hora actual
        hora_actual = datetime.now().hour
        
        if 6 <= hora_actual < 12:
            saludo = "¡Buenos días!"
        elif 12 <= hora_actual < 18:
            saludo = "¡Buenas tardes!"
        else:
            saludo = "¡Buenas noches!"
        
        mensaje = f"{saludo}, soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
        
        dispatcher.utter_message(text=mensaje)
        return []
```

### **Patrón API Integration**
```python
# actions.py - Integración con Freshdesk
class ActionGenerarTicket(Action):
    def name(self) -> Text:
        return "action_generar_ticket"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtener información del cliente
        digitos = tracker.get_slot("digitos")
        cliente_id = tracker.get_slot("cliente_id")
        
        # Crear ticket en Freshdesk
        ticket_data = {
            "subject": f"Bloqueo de tarjeta - Cliente {cliente_id}",
            "description": f"Solicitud de bloqueo para tarjeta terminada en {digitos}",
            "priority": 1,
            "status": 2,
            "type": "Bloqueo de Tarjeta"
        }
        
        try:
            response = requests.post(
                "https://pocsctbnk.freshdesk.com/api/v2/tickets",
                json=ticket_data,
                auth=("api_key", "X"),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                ticket = response.json()
                ticket_id = ticket["id"]
                
                dispatcher.utter_message(
                    text=f"Ok, se ha generado el ticket número {ticket_id}, "
                         f"por lo que en instantes un ejecutivo realizará el bloqueo."
                )
            else:
                raise Exception(f"Error al crear ticket: {response.status_code}")
                
        except Exception as e:
            dispatcher.utter_message(
                text="Estoy experimentando dificultades técnicas. "
                     "Te transferiré a un ejecutivo que podrá ayudarte inmediatamente."
            )
        
        return []
```

## Decisiones Técnicas

### **Arquitectura de Conversación**
- **Flows estructurados**: Uso de flows de Rasa para manejo de conversaciones
- **Patterns reutilizables**: Patrones comunes para saludos y confirmaciones
- **Fallbacks inteligentes**: Manejo de casos donde no entiende la intención
- **Contexto persistente**: Mantenimiento del estado de la conversación

### **Integración de Sistemas**
- **Webhooks de Twilio**: Comunicación bidireccional con Rasa
- **API REST de Freshdesk**: Creación automática de tickets
- **Base de datos**: Consulta rápida de información de tarjetas
- **Logging centralizado**: Registro de todas las interacciones

### **Manejo de Errores**
- **Fallbacks conversacionales**: Alternativas cuando no entiende
- **Transferencia automática**: Redirección al call center humano
- **Logging de errores**: Registro detallado para debugging
- **Retry automático**: Reintentos en caso de fallos temporales

## Relaciones entre Componentes

### **Flujo de Datos**
1. **Cliente llama** → Twilio recibe la llamada
2. **Twilio webhook** → Rasa Pro inicia conversación
3. **Rasa procesa** → Entiende intención del cliente
4. **Consulta BD** → Verifica información de tarjeta
5. **API Freshdesk** → Crea ticket automáticamente
6. **Respuesta** → Confirma al cliente y cierra llamada

### **Dependencias**
- **Rasa Pro** depende de Twilio para comunicación telefónica
- **Rasa Pro** depende de Base de Datos para verificación
- **Rasa Pro** depende de Freshdesk API para tickets
- **Sistema de Logging** depende de todos los componentes

### **Comunicación Asíncrona**
- **Webhooks**: Twilio → Rasa (llamadas entrantes)
- **API Calls**: Rasa → Freshdesk (creación de tickets)
- **Database Queries**: Rasa → Base de Datos (verificación)
- **Logging**: Todos los componentes → Sistema de logs

## Configuración de Rasa Pro

### **Archivos de Configuración**
```yaml
# config.yml
language: es
pipeline:
  - name: WhitespaceTokenizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 100

# Configuración CALM para LLMs
llm:
  - name: CALMClassifier
    model_name: "gpt-3.5-turbo"  # o modelo local
    temperature: 0.1
    max_tokens: 150
    # CALM maneja automáticamente el contexto y la seguridad
```

### **Configuración de Endpoints**
```yaml
# endpoints.yml
action_endpoint:
  url: "http://localhost:5055/webhook"

# Configuración para Twilio
webhooks:
  twilio:
    webhook_url: "https://your-rasa-server.com/webhooks/twilio/webhook"
    account_sid: "your_account_sid"
    auth_token: "your_auth_token"
```

## Patrones de Seguridad

### **Verificación de Identidad**
- **Últimos 4 dígitos**: Verificación mediante base de datos
- **Validación de tarjeta**: Confirmación de estado activo
- **Logging de intentos**: Registro de todas las verificaciones
- **Rate limiting**: Prevención de ataques de fuerza bruta

### **Protección de Datos**
- **Encriptación**: Datos sensibles encriptados
- **Acceso limitado**: Solo información necesaria expuesta
- **Auditoría**: Trazabilidad completa de todas las acciones
- **Compliance**: Cumplimiento de estándares bancarios
