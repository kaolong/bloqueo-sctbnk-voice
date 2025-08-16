# CALM Architecture: Rasa Pro 3.13.5 con Flows y Patterns

## 🚀 Introducción a CALM

### **¿Qué es CALM?**
**CALM (Conversational AI with Language Models)** es la nueva arquitectura de Rasa Pro que permite construir asistentes conversacionales más robustos, contextuales y fáciles de mantener utilizando **Large Language Models (LLMs)**.

### **Características Principales**
- **Flows para Lógica de Negocio**: Implementación escalable de tareas
- **Patrones de Conversación Automáticos**: Manejo automático de cambios de tema, correcciones
- **LLMs para Interacciones Contextuales**: Asistentes más robustos y fáciles de crear
- **Seguridad Integrada**: Resistente a alucinaciones, inyección de prompts y jailbreaking
- **Control Total del Negocio**: Lógica de negocio siempre seguida correctamente
- **Componentes Reutilizables**: Tareas descompuestas en piezas reutilizables

## 🏗️ Arquitectura Moderna: Flows y Patterns

### **Flows (Flujos)**
Los Flows son la nueva forma de definir la lógica de negocio en Rasa Pro:

```yaml
# flows.yml
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

### **Patterns (Patrones)**
Los Patterns son componentes reutilizables que se pueden usar en múltiples Flows:

```yaml
# patterns.yml
patterns:
  - name: greeting_pattern
    description: "Patrón reutilizable para saludos"
    steps:
      - step: start
        action: action_saludo_contextual
        next:
          - condition: user_has_request
            step: handle_request
          - condition: user_just_greeting
            step: end_greeting
    
  - name: confirmation_pattern
    description: "Patrón reutilizable para confirmaciones"
    steps:
      - step: start
        action: action_ask_confirmation
        next:
          - condition: user_confirmed
            step: proceed_with_action
          - condition: user_declined
            step: handle_decline
          - condition: user_confused
            step: clarify_confirmation
```

## 🔧 Configuración de CALM

### **Configuración del Pipeline**
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

# Configuración para LLMs externos
llm_endpoints:
  openai:
    url: "https://api.openai.com/v1"
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-3.5-turbo"
```

## 🎯 Ventajas de CALM para SCTBNK

### **1. Lógica de Negocio Robusta**
- **Flows estructurados**: Cada paso del proceso de bloqueo está claramente definido
- **Condiciones explícitas**: Manejo claro de casos de éxito y error
- **Fallbacks automáticos**: Redirección automática a ejecutivos humanos cuando sea necesario

### **2. Seguridad Bancaria**
- **Resistente a alucinaciones**: CALM previene respuestas incorrectas del LLM
- **Protección contra inyección**: Seguridad integrada contra manipulación de prompts
- **Control total**: La lógica de negocio siempre se sigue correctamente

### **3. Escalabilidad**
- **Componentes reutilizables**: Patrones que se pueden usar en otros flujos
- **Mantenimiento fácil**: Cambios en un lugar se reflejan en todos los usos
- **Testing simplificado**: Cada Flow y Pattern se puede probar independientemente

### **4. Experiencia del Usuario**
- **Interacciones contextuales**: El LLM entiende mejor el contexto de la conversación
- **Manejo automático de variaciones**: Entiende diferentes formas de expresar la misma intención
- **Recuperación de errores**: Manejo inteligente de malentendidos

## 🔄 Migración desde Arquitectura Tradicional

### **Cambios Principales**

#### **Antes (Intent-based)**
```yaml
# domain.yml (antiguo)
intents:
  - saludar
  - bloquear_tarjeta
  - confirmar_bloqueo

stories:
  - story: bloqueo_tarjeta_story
    steps:
      - intent: saludar
      - action: action_saludo
      - intent: bloquear_tarjeta
      - action: action_solicitar_digitos
```

#### **Ahora (Flow-based con CALM)**
```yaml
# flows.yml (nuevo)
flows:
  - name: bloqueo_tarjeta_flow
    steps:
      - step: start
        action: action_saludo_contextual
        next:
          - condition: user_wants_to_block_card
            step: solicitar_digitos
```

### **Beneficios de la Migración**
- **Menos código**: Los Flows son más declarativos
- **Mejor mantenibilidad**: Lógica de negocio más clara
- **Testing más fácil**: Cada Flow se puede probar independientemente
- **Escalabilidad**: Fácil agregar nuevos flujos y patrones

## 🧪 Testing de Flows y Patterns

### **Testing de Flows Individuales**
```bash
# Test de un Flow específico
rasa test flows --flow bloqueo_tarjeta_flow

# Test de todos los Flows
rasa test flows

# Test interactivo de Flows
rasa interactive --flows
```

### **Testing de Patterns**
```bash
# Test de un Pattern específico
rasa test patterns --pattern greeting_pattern

# Test de todos los Patterns
rasa test patterns
```

### **Testing de Integración**
```bash
# Test completo del sistema
rasa test

# Test de conversaciones específicas
rasa test --stories test_stories.yml
```

## 🚀 Implementación en Producción

### **Consideraciones de Despliegue**
- **LLM Endpoints**: Configurar endpoints seguros para LLMs
- **Rate Limiting**: Controlar el uso de APIs de LLMs
- **Monitoring**: Monitorear el rendimiento de CALM
- **Fallbacks**: Asegurar fallbacks robustos

### **Configuración de Producción**
```yaml
# config.prod.yml
llm:
  - name: CALMClassifier
    model_name: "gpt-4"  # Modelo más robusto para producción
    temperature: 0.05     # Menor temperatura para respuestas más consistentes
    max_tokens: 200
    rate_limit: 100       # Requests por minuto
    fallback_model: "gpt-3.5-turbo"  # Fallback si gpt-4 falla
```

## 📊 Monitoreo y Métricas

### **Métricas de CALM**
- **Accuracy del LLM**: Precisión de las respuestas generadas
- **Tiempo de Respuesta**: Latencia de las APIs de LLMs
- **Uso de Tokens**: Consumo de tokens de LLMs
- **Fallbacks**: Frecuencia de uso de fallbacks

### **Alertas Recomendadas**
```yaml
# monitoring/alerts.yml
groups:
- name: calm-monitoring
  rules:
  - alert: HighLLMErrorRate
    expr: rate(calm_llm_errors_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High LLM error rate in CALM"
      description: "LLM error rate is {{ $value }}"

  - alert: HighLLMLatency
    expr: histogram_quantile(0.95, rate(calm_llm_duration_seconds_bucket[5m])) > 5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High LLM latency in CALM"
      description: "95th percentile LLM latency is {{ $value }}s"
```

## 🔮 Futuro y Evolución

### **Tendencias de CALM**
- **Modelos Locales**: Integración con modelos LLM locales para mayor privacidad
- **Fine-tuning**: Personalización de modelos para dominios específicos
- **Multi-modal**: Soporte para voz, texto e imágenes
- **Auto-learning**: Mejora automática basada en interacciones

### **Roadmap de SCTBNK**
- **Fase 1**: Implementación de Flows básicos para bloqueo de tarjetas
- **Fase 2**: Integración de Patterns reutilizables
- **Fase 3**: Optimización de CALM para casos de uso bancarios
- **Fase 4**: Expansión a otros servicios bancarios

---

**Referencia**: [Rasa Pro Documentation](https://rasa.com/docs/pro/intro/)  
**Última Actualización**: $(date)  
**Versión CALM**: Rasa Pro 3.13.5  
**Estado**: ✅ Arquitectura Moderna Documentada
