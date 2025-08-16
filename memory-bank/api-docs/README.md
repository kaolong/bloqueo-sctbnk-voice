# API Documentation: Bloqueo de Tarjetas SCTBNK con Rasa Pro

## Descripción General
Documentación de las APIs y webhooks utilizados en el sistema de bloqueo de tarjetas de SCTBNK desarrollado con Rasa Pro, Twilio y Freshdesk.

## Arquitectura de APIs

### **Componentes de API**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cliente       │    │   Twilio        │    │   Rasa Pro      │
│   (Teléfono)    │◄──►│   (Voice API)   │◄──►│   (Webhook)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Base de       │    │   Freshdesk     │    │   Sistema de    │
│   Datos         │    │   API v2        │    │   Logging       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 1. Rasa Pro API

### **Base URL**
```
Development: http://localhost:5005
Production: https://your-rasa-server.com
```

### **Endpoints Principales**

#### **Webhook para Twilio**
```
POST /webhooks/twilio/webhook
```

**Descripción**: Endpoint que recibe llamadas de Twilio y las procesa con Rasa Pro.

**Headers Requeridos**:
```
Content-Type: application/x-www-form-urlencoded
```

**Parámetros de Entrada** (Twilio Form Data):
```json
{
  "From": "+1234567890",
  "To": "+0987654321",
  "SpeechResult": "necesito bloquear mi tarjeta",
  "CallSid": "CA1234567890abcdef",
  "CallStatus": "in-progress"
}
```

**Respuesta de Éxito** (TwiML):
```xml
<Response>
  <Say language="es-MX">¡Buenos días!, soy el asistente de Scotiabank, ¿en qué puedo ayudarte?</Say>
  <Gather input="speech" action="/webhooks/twilio/process" method="POST">
    <Say language="es-MX">Por favor, dime cómo puedo ayudarte</Say>
  </Gather>
</Response>
```

#### **API de Mensajes**
```
POST /webhooks/rest/webhook
```

**Descripción**: Endpoint REST para procesar mensajes de texto.

**Headers Requeridos**:
```
Content-Type: application/json
```

**Body de Entrada**:
```json
{
  "sender": "user123",
  "message": "necesito bloquear mi tarjeta"
}
```

**Respuesta de Éxito**:
```json
[
  {
    "recipient_id": "user123",
    "text": "Ok, te puedo ayudar con eso. Dime, ¿qué tarjeta es la que necesitas bloquear? Puedes darme los últimos 4 dígitos"
  }
]
```

#### **API de Predicciones**
```
POST /model/parse
```

**Descripción**: Endpoint para analizar texto y extraer intents y entidades.

**Headers Requeridos**:
```
Content-Type: application/json
```

**Body de Entrada**:
```json
{
  "text": "necesito bloquear mi tarjeta 1234"
}
```

**Respuesta de Éxito**:
```json
{
  "intent": {
    "name": "bloquear_tarjeta",
    "confidence": 0.9876
  },
  "entities": [
    {
      "entity": "digitos",
      "value": "1234",
      "start": 28,
      "end": 32,
      "confidence": 0.9999
    }
  ],
  "text": "necesito bloquear mi tarjeta 1234",
  "intent_ranking": [
    {
      "name": "bloquear_tarjeta",
      "confidence": 0.9876
    },
    {
      "name": "nlu_fallback",
      "confidence": 0.0124
    }
  ]
}
```

#### **API de Entrenamiento**
```
POST /model/train
```

**Descripción**: Endpoint para entrenar el modelo de NLU.

**Headers Requeridos**:
```
Content-Type: application/json
```

**Body de Entrada**:
```json
{
  "force": true,
  "save_to_default_model_directory": true
}
```

**Respuesta de Éxito**:
```json
{
  "model_file": "models/20240115-143022.tar.gz",
  "fingerprint": "2024-01-15T14:30:22.123456"
}
```

### **Códigos de Respuesta Rasa**
- `200` - Éxito
- `400` - Bad Request (datos inválidos)
- `500` - Error interno del servidor

## 2. Twilio Voice API

### **Base URL**
```
https://api.twilio.com/2010-04-01/Accounts/{AccountSid}
```

### **Endpoints Principales**

#### **Crear Llamada**
```
POST /Calls.json
```

**Descripción**: Iniciar una llamada saliente.

**Headers Requeridos**:
```
Authorization: Basic {Base64(AccountSid:AuthToken)}
Content-Type: application/x-www-form-urlencoded
```

**Body de Entrada**:
```json
{
  "To": "+1234567890",
  "From": "+0987654321",
  "Url": "https://your-rasa-server.com/webhooks/twilio/webhook",
  "Method": "POST"
}
```

**Respuesta de Éxito**:
```json
{
  "sid": "CA1234567890abcdef",
  "date_created": "Mon, 15 Jan 2024 14:30:22 +0000",
  "date_updated": "Mon, 15 Jan 2024 14:30:22 +0000",
  "parent_call_sid": null,
  "duration": null,
  "status": "queued",
  "start_time": null,
  "end_time": null,
  "price": null,
  "price_unit": "USD",
  "direction": "outbound-api",
  "answered_by": null,
  "annotation": null,
  "api_version": "2010-04-01",
  "forwarded_from": null,
  "group_sid": null,
  "caller_name": null,
  "queue_time": "0",
  "uri": "/2010-04-01/Accounts/AC1234567890abcdef/Calls/CA1234567890abcdef.json"
}
```

#### **Obtener Información de Llamada**
```
GET /Calls/{CallSid}.json
```

**Descripción**: Obtener detalles de una llamada específica.

**Headers Requeridos**:
```
Authorization: Basic {Base64(AccountSid:AuthToken)}
```

**Respuesta de Éxito**:
```json
{
  "sid": "CA1234567890abcdef",
  "date_created": "Mon, 15 Jan 2024 14:30:22 +0000",
  "date_updated": "Mon, 15 Jan 2024 14:30:22 +0000",
  "parent_call_sid": null,
  "duration": "45",
  "status": "completed",
  "start_time": "Mon, 15 Jan 2024 14:30:25 +0000",
  "end_time": "Mon, 15 Jan 2024 14:31:10 +0000",
  "price": "-0.0075",
  "price_unit": "USD",
  "direction": "outbound-api",
  "answered_by": null,
  "annotation": null,
  "api_version": "2010-04-01",
  "forwarded_from": null,
  "group_sid": null,
  "caller_name": null,
  "queue_time": "0",
  "uri": "/2010-04-01/Accounts/AC1234567890abcdef/Calls/CA1234567890abcdef.json"
}
```

### **Webhook Events de Twilio**

#### **Evento: Llamada Entrante**
```json
{
  "CallSid": "CA1234567890abcdef",
  "AccountSid": "AC1234567890abcdef",
  "From": "+1234567890",
  "To": "+0987654321",
  "CallStatus": "ringing",
  "ApiVersion": "2010-04-01",
  "Direction": "inbound",
  "Called": "+0987654321",
  "Caller": "+1234567890"
}
```

#### **Evento: Llamada Contestada**
```json
{
  "CallSid": "CA1234567890abcdef",
  "AccountSid": "AC1234567890abcdef",
  "From": "+1234567890",
  "To": "+0987654321",
  "CallStatus": "in-progress",
  "ApiVersion": "2010-04-01",
  "Direction": "inbound",
  "Called": "+0987654321",
  "Caller": "+1234567890",
  "CallDuration": "0"
}
```

#### **Evento: Llamada Finalizada**
```json
{
  "CallSid": "CA1234567890abcdef",
  "AccountSid": "AC1234567890abcdef",
  "From": "+1234567890",
  "To": "+0987654321",
  "CallStatus": "completed",
  "ApiVersion": "2010-04-01",
  "Direction": "inbound",
  "Called": "+0987654321",
  "Caller": "+1234567890",
  "CallDuration": "45"
}
```

### **Códigos de Respuesta Twilio**
- `200` - Éxito
- `400` - Bad Request
- `401` - No autorizado
- `404` - No encontrado
- `500` - Error interno del servidor

## 3. Freshdesk API v2

### **Base URL**
```
https://pocsctbnk.freshdesk.com/api/v2
```

### **Autenticación**
```
Authorization: Basic {Base64(API_Key:X)}
```

### **Endpoints Principales**

#### **Crear Ticket**
```
POST /tickets
```

**Descripción**: Crear un nuevo ticket de bloqueo de tarjeta.

**Headers Requeridos**:
```
Authorization: Basic {Base64(API_Key:X)}
Content-Type: application/json
```

**Body de Entrada**:
```json
{
  "subject": "Bloqueo de tarjeta - Cliente 12345",
  "description": "Solicitud de bloqueo para tarjeta terminada en 1234. Cliente solicitó bloqueo por pérdida de tarjeta.",
  "email": "cliente@email.com",
  "priority": 1,
  "status": 2,
  "type": "Bloqueo de Tarjeta",
  "tags": ["bloqueo", "tarjeta", "urgente"],
  "custom_fields": {
    "cf_tarjeta_ultimos_digitos": "1234",
    "cf_cliente_id": "12345",
    "cf_tipo_bloqueo": "pérdida"
  }
}
```

**Respuesta de Éxito**:
```json
{
  "id": 12345,
  "subject": "Bloqueo de tarjeta - Cliente 12345",
  "description": "Solicitud de bloqueo para tarjeta terminada en 1234. Cliente solicitó bloqueo por pérdida de tarjeta.",
  "email": "cliente@email.com",
  "priority": 1,
  "status": 2,
  "type": "Bloqueo de Tarjeta",
  "tags": ["bloqueo", "tarjeta", "urgente"],
  "created_at": "2024-01-15T14:30:22Z",
  "updated_at": "2024-01-15T14:30:22Z",
  "custom_fields": {
    "cf_tarjeta_ultimos_digitos": "1234",
    "cf_cliente_id": "12345",
    "cf_tipo_bloqueo": "pérdida"
  }
}
```

#### **Obtener Ticket**
```
GET /tickets/{ticket_id}
```

**Descripción**: Obtener información de un ticket específico.

**Headers Requeridos**:
```
Authorization: Basic {Base64(API_Key:X)}
```

**Respuesta de Éxito**:
```json
{
  "id": 12345,
  "subject": "Bloqueo de tarjeta - Cliente 12345",
  "description": "Solicitud de bloqueo para tarjeta terminada en 1234. Cliente solicitó bloqueo por pérdida de tarjeta.",
  "email": "cliente@email.com",
  "priority": 1,
  "status": 2,
  "type": "Bloqueo de Tarjeta",
  "tags": ["bloqueo", "tarjeta", "urgente"],
  "created_at": "2024-01-15T14:30:22Z",
  "updated_at": "2024-01-15T14:30:22Z",
  "due_by": "2024-01-16T14:30:22Z",
  "fr_due_by": "2024-01-16T02:30:22Z",
  "is_escalated": false,
  "custom_fields": {
    "cf_tarjeta_ultimos_digitos": "1234",
    "cf_cliente_id": "12345",
    "cf_tipo_bloqueo": "pérdida"
  }
}
```

#### **Actualizar Ticket**
```
PUT /tickets/{ticket_id}
```

**Descripción**: Actualizar el estado o información de un ticket.

**Headers Requeridos**:
```
Authorization: Basic {Base64(API_Key:X)}
Content-Type: application/json
```

**Body de Entrada**:
```json
{
  "status": 3,
  "priority": 2,
  "custom_fields": {
    "cf_tarjeta_bloqueada": true,
    "cf_fecha_bloqueo": "2024-01-15T14:35:00Z"
  }
}
```

**Respuesta de Éxito**:
```json
{
  "id": 12345,
  "subject": "Bloqueo de tarjeta - Cliente 12345",
  "status": 3,
  "priority": 2,
  "updated_at": "2024-01-15T14:35:00Z",
  "custom_fields": {
    "cf_tarjeta_ultimos_digitos": "1234",
    "cf_cliente_id": "12345",
    "cf_tipo_bloqueo": "pérdida",
    "cf_tarjeta_bloqueada": true,
    "cf_fecha_bloqueo": "2024-01-15T14:35:00Z"
  }
}
```

### **Códigos de Respuesta Freshdesk**
- `200` - Éxito
- `201` - Creado
- `400` - Bad Request
- `401` - No autorizado
- `403` - Prohibido
- `404` - No encontrado
- `429` - Rate limit excedido
- `500` - Error interno del servidor

## 4. Base de Datos API

### **Endpoint de Consulta de Tarjetas**
```
POST /api/cards/verify
```

**Descripción**: Verificar tarjeta por últimos 4 dígitos.

**Headers Requeridos**:
```
Content-Type: application/json
Authorization: Bearer {JWT_TOKEN}
```

**Body de Entrada**:
```json
{
  "last_four_digits": "1234",
  "client_phone": "+1234567890"
}
```

**Respuesta de Éxito**:
```json
{
  "success": true,
  "data": {
    "card_id": "card_123",
    "last_four_digits": "1234",
    "card_type": "credit",
    "client_id": "client_456",
    "status": "active",
    "expiry_date": "2026-12-31"
  },
  "message": "Tarjeta encontrada y verificada"
}
```

**Respuesta de Error**:
```json
{
  "success": false,
  "error": "Tarjeta no encontrada o inactiva",
  "code": "CARD_NOT_FOUND"
}
```

## 5. Webhooks y Eventos

### **Eventos de Rasa Pro**
- `user_message` - Mensaje recibido del usuario
- `bot_message` - Respuesta del bot
- `session_started` - Inicio de sesión
- `session_ended` - Fin de sesión
- `action_executed` - Acción ejecutada

### **Eventos de Twilio**
- `call.initiated` - Llamada iniciada
- `call.ringing` - Llamada sonando
- `call.answered` - Llamada contestada
- `call.completed` - Llamada finalizada
- `speech.recognition` - Reconocimiento de voz

### **Eventos de Freshdesk**
- `ticket.created` - Ticket creado
- `ticket.updated` - Ticket actualizado
- `ticket.closed` - Ticket cerrado
- `ticket.reopened` - Ticket reabierto

## 6. Rate Limiting y Cuotas

### **Rasa Pro**
- **Requests por minuto**: 1000 (configurable)
- **Concurrent sessions**: 100 (configurable)
- **Model training**: 1 por minuto

### **Twilio**
- **Calls por minuto**: Según plan (Pay-as-you-go: 1000)
- **API requests**: 1000 por minuto
- **Webhook delivery**: 3 reintentos automáticos

### **Freshdesk**
- **API requests**: 1000 por hora
- **Tickets por minuto**: 100
- **File uploads**: 10MB por archivo

## 7. Manejo de Errores

### **Errores Comunes y Soluciones**

#### **Rasa Pro**
```json
{
  "error": "Model not found",
  "solution": "Entrenar modelo con rasa train",
  "status_code": 500
}
```

#### **Twilio**
```json
{
  "error": "Invalid phone number",
  "solution": "Verificar formato del número (+1234567890)",
  "status_code": 400
}
```

#### **Freshdesk**
```json
{
  "error": "Rate limit exceeded",
  "solution": "Esperar 1 hora o implementar retry con backoff",
  "status_code": 429
}
```

## 8. Testing y Debugging

### **Herramientas de Testing**
- **Rasa**: `rasa shell`, `rasa test`, `rasa interactive`
- **Twilio**: Twilio CLI, Studio Flow testing
- **Freshdesk**: Sandbox environment, API testing tools

### **Logs y Monitoreo**
- **Rasa**: Logs en `logs/` directory
- **Twilio**: Logs en Twilio Console
- **Freshdesk**: Logs en Admin Panel
- **Sistema**: ELK Stack o Winston logging
