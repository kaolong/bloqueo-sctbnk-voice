# Product Context: Bloqueo de Tarjetas SCTBNK con Rasa Pro

## ¿Por qué existe este proyecto?

### **Problema que resuelve**
- **Sobrecarga del Call Center**: Los ejecutivos están saturados con solicitudes simples de bloqueo de tarjetas que podrían automatizarse
- **Tiempo de Espera**: Los clientes esperan largas colas para solicitudes urgentes de bloqueo por pérdida o robo
- **Costo Operativo**: Procesamiento manual de bloqueos incrementa significativamente los costos operativos del banco
- **Experiencia del Cliente**: Atención limitada a horarios de oficina para solicitudes que requieren respuesta inmediata
- **Seguridad**: Necesidad de respuesta rápida para prevenir fraudes en tarjetas perdidas o robadas

### **Contexto del Negocio**
- **SCTBNK** maneja miles de solicitudes de bloqueo mensuales que saturan el call center
- **Los bloqueos de tarjetas** son solicitudes urgentes que requieren respuesta inmediata
- **El costo promedio** de una llamada al call center es de $15-20 USD
- **La automatización** puede reducir costos operativos en un 70% anual
- **La satisfacción del cliente** mejora con respuesta inmediata 24/7

## ¿Cómo debe funcionar?

### **Flujo de Usuario Detallado**

#### **1. Inicio de Llamada**
- **Trigger**: Cliente llama al número de Twilio configurado
- **Saludo Contextual**: Asistente responde según horario del día
  - "¡Buenos días!" (6:00 AM - 11:59 AM)
  - "¡Buenas tardes!" (12:00 PM - 5:59 PM)
  - "¡Buenas noches!" (6:00 PM - 5:59 AM)
- **Presentación**: "Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"

#### **2. Entendimiento de Intención**
- **Cliente dice**: "necesito bloquear mi tarjeta"
- **Variaciones que debe entender**:
  - "quiero bloquear mi tarjeta"
  - "mi tarjeta fue robada"
  - "perdí mi tarjeta"
  - "necesito cancelar mi tarjeta"
  - "mi tarjeta está comprometida"
  - "quiero reportar mi tarjeta como perdida"

#### **3. Verificación de Identidad**
- **Asistente responde**: "Ok, te puedo ayudar con eso. Dime, ¿qué tarjeta es la que necesitas bloquear? Puedes darme los últimos 4 dígitos"
- **Consulta a BD**: Sistema busca en base de datos las tarjetas asociadas al cliente
- **Validación**: Confirma que los últimos 4 dígitos corresponden a una tarjeta válida

#### **4. Confirmación del Cliente**
- **Cliente confirma**: Menciona los últimos 4 dígitos
- **Variaciones de confirmación**:
  - "Sí, es la 1234"
  - "Correcto, 1234"
  - "Sí, procede"
  - "Perfecto, adelante"
  - "Sí, bloquéala"

#### **5. Generación de Ticket**
- **Asistente confirma**: "Ok, generaré un ticket para el bloqueo, ¿te parece?"
- **Cliente confirma**: Debe entender variaciones de confirmación
- **Llamada a API**: Sistema llama a Freshdesk API para crear ticket
- **Respuesta**: "Ok, se ha generado el ticket número X, por lo que en instantes un ejecutivo realizará el bloqueo"

#### **6. Cierre de Conversación**
- **Despedida contextual**: "Gracias por contactarte con nosotros, buenas tardes/días/noches"
- **Finalización**: Llamada se corta automáticamente

### **Funcionalidades Principales**

#### **Procesamiento de Lenguaje Natural (Rasa Pro 3.13.5)**
- **Entendimiento de intenciones**: Identificación precisa de solicitudes de bloqueo
- **Entidades extraídas**: Últimos 4 dígitos de tarjeta, tipo de tarjeta
- **Contexto conversacional**: Mantenimiento del estado de la conversación
- **Fallbacks inteligentes**: Manejo de casos donde no entiende la intención

#### **Integración con Sistemas**
- **Base de Datos**: Consulta de información de tarjetas del cliente
- **Freshdesk API**: Creación automática de tickets con información completa
- **Twilio**: Manejo de llamadas telefónicas y TTS (Text-to-Speech)
- **Logging**: Registro completo de todas las interacciones

#### **Sistema de Verificación**
- **Validación de tarjeta**: Confirmación de que los últimos 4 dígitos son válidos
- **Verificación de cliente**: Confirmación de que la tarjeta pertenece al cliente
- **Estado de tarjeta**: Verificación de que la tarjeta no esté ya bloqueada

### **Experiencia del Usuario**

#### **Simplicidad**
- **Conversación natural**: El asistente habla como un humano
- **Instrucciones claras**: Guía paso a paso al cliente
- **Confirmaciones**: Verifica cada acción antes de proceder
- **Manejo de errores**: Reconoce cuando no entiende y pide aclaración

#### **Eficiencia**
- **Tiempo total**: Conversación completa en menos de 2 minutos
- **Sin esperas**: Respuesta inmediata sin colas
- **Disponibilidad**: Acceso 24/7 para solicitudes urgentes
- **Resolución automática**: 85% de casos resueltos sin intervención humana

#### **Seguridad**
- **Verificación de identidad**: Confirmación mediante últimos 4 dígitos
- **Registro completo**: Trazabilidad de cada solicitud
- **Cumplimiento**: Adherencia a estándares bancarios de seguridad

## Casos de Uso

### **Caso Principal: Bloqueo por Pérdida**
1. **Cliente**: Llama al número de emergencia
2. **Asistente**: Saluda y pregunta cómo puede ayudar
3. **Cliente**: "Perdí mi tarjeta, necesito bloquearla"
4. **Asistente**: Solicita últimos 4 dígitos para verificación
5. **Cliente**: Proporciona los dígitos
6. **Asistente**: Confirma y genera ticket automáticamente
7. **Resultado**: Tarjeta bloqueada en minutos, no en horas

### **Caso Secundario: Bloqueo por Robo**
1. **Cliente**: Llama reportando robo de tarjeta
2. **Asistente**: Entiende la urgencia y acelera el proceso
3. **Cliente**: Confirma identidad con últimos 4 dígitos
4. **Asistente**: Genera ticket de alta prioridad
5. **Resultado**: Bloqueo inmediato para prevenir fraudes

### **Caso de Error: Tarjeta No Encontrada**
1. **Cliente**: Proporciona dígitos incorrectos
2. **Asistente**: Solicita verificación adicional
3. **Cliente**: Corrige la información
4. **Asistente**: Procede con el bloqueo
5. **Resultado**: Proceso exitoso con verificación adicional

## Escenarios de Fallback

### **No Entendimiento de Intención**
- **Asistente**: "No estoy seguro de entenderte. ¿Podrías decirme si necesitas bloquear una tarjeta o hay algo más en lo que pueda ayudarte?"
- **Cliente**: Repite la solicitud de manera más clara
- **Asistente**: Procede con el flujo normal

### **Tarjeta No Encontrada**
- **Asistente**: "No encuentro una tarjeta con esos últimos 4 dígitos. ¿Podrías verificar el número?"
- **Cliente**: Proporciona dígitos correctos
- **Asistente**: Continúa con el proceso

### **Error en API**
- **Asistente**: "Estoy experimentando dificultades técnicas. Te transferiré a un ejecutivo que podrá ayudarte inmediatamente."
- **Resultado**: Transferencia automática al call center humano

## Métricas de Éxito

### **Operacionales**
- **Tasa de resolución automática**: >85%
- **Tiempo promedio de conversación**: <2 minutos
- **Precisión de entendimiento**: >95%
- **Tasa de transferencia**: <15%

### **De Experiencia del Usuario**
- **Satisfacción del cliente**: >4.5/5
- **Tiempo de respuesta**: <2 segundos por interacción
- **Disponibilidad del sistema**: 99.9%
- **Tasa de abandono**: <5%
