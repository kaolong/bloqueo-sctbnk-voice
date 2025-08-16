# 🏦 Bloqueo SCTBNK Voice - Asistente Virtual Rasa Pro

## 📋 Descripción del Proyecto

Sistema de asistente virtual inteligente desarrollado con **Rasa Pro 3.13.5** para el bloqueo de tarjetas de crédito/débito de Scotiabank. El bot utiliza la arquitectura **CALM (Conversational AI with Language Models)** con Flows y Patterns para gestionar conversaciones de voz a través de Twilio.

## 🎯 Funcionalidades Principales

- **Saludo contextual** según la hora del día
- **Reconocimiento de intención** de bloqueo de tarjetas
- **Validación de dígitos** de tarjeta (últimos 4 dígitos)
- **Confirmación de usuario** con múltiples variaciones de respuesta
- **Generación automática de tickets** en Freshdesk
- **Case numbers profesionales** con formato BLK-YYYYMMDD-ID
- **Despedida contextual** según la hora

## 🏗️ Arquitectura Técnica

### **Stack Tecnológico**
- **Rasa Pro**: 3.13.5 (CALM Architecture)
- **Python**: 3.10.12
- **Rasa SDK**: 3.13.0
- **Twilio Voice API**: Integración para llamadas telefónicas
- **Freshdesk API v2**: Sistema de tickets
- **PostgreSQL/MongoDB**: Base de datos (preparado para integración)

### **Arquitectura CALM**
- **Flows**: Gestión de flujos conversacionales
- **Patterns**: Patrones de diálogo reutilizables
- **FlowPolicy**: Política principal para gestión de flujos
- **RulePolicy**: Reglas para activación de flujos

## 🚀 Instalación y Configuración

### **Prerrequisitos**
```bash
# Python 3.10.12
pyenv install 3.10.12
pyenv local 3.10.12

# Rasa Pro
pip install rasa[pro]==3.13.5
pip install rasa-sdk==3.13.0
```

### **Configuración del Entorno**
```bash
# Clonar repositorio
git clone https://github.com/kaolong/bloqueo-sctbnk-voice.git
cd bloqueo-sctbnk-voice

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Freshdesk
```

### **Variables de Entorno**
```bash
# .env
API_KEY=tu_api_key_freshdesk
DOMAIN=tu_dominio_freshdesk
```

## 🎮 Uso del Sistema

### **1. Entrenar el Modelo**
```bash
rasa train
```

### **2. Ejecutar Action Server**
```bash
rasa run actions --port 5055 --debug
```

### **3. Ejecutar Rasa Shell**
```bash
rasa shell --port 5005
```

### **4. Flujo de Conversación**
```
Usuario: "quiero bloquear mi tarjeta"
Bot: "¡Buenas tardes! Soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"

Usuario: "3333"
Bot: "Perfecto, encontré tu tarjeta terminada en 3333. ¿Te parece bien proceder?"

Usuario: "claro!"
Bot: "Excelente, se ha generado el caso número BLK-20250815-12. En instantes un ejecutivo realizará el bloqueo de tu tarjeta."

Bot: "Gracias por contactarte con nosotros. ¡Que tengas una excelente tarde!"
```

## 📁 Estructura del Proyecto

```
bloqueo-sctbnk-voice/
├── actions/
│   └── actions.py          # Acciones personalizadas
├── data/
│   ├── flows.yml           # Flujos conversacionales CALM
│   ├── nlu.yml            # Datos de entrenamiento NLU
│   └── rules.yml          # Reglas de activación
├── domain/
│   └── shared.yml         # Configuración del dominio
├── models/                # Modelos entrenados
├── memory-bank/           # Documentación del proyecto
├── config.yml             # Configuración de Rasa
├── endpoints.yml          # Configuración de endpoints
├── requirements.txt       # Dependencias Python
└── .env                   # Variables de entorno
```

## 🔧 Configuración de Componentes

### **Pipeline NLU**
- **WhitespaceTokenizer**: Tokenización básica
- **RegexFeaturizer**: Características regex
- **LexicalSyntacticFeaturizer**: Características léxico-sintácticas
- **CountVectorsFeaturizer**: Vectores de características
- **DIETClassifier**: Clasificador de intents y entidades
- **CALMClassifier**: Clasificador CALM para Rasa Pro

### **Políticas**
- **FlowPolicy**: Gestión principal de flujos
- **RulePolicy**: Reglas de activación
- **IntentlessPolicy**: Política para intents no reconocidos

## 🌐 Integraciones

### **Freshdesk API**
- **URL**: `https://{DOMAIN}.freshdesk.com/api/v2/tickets`
- **Autenticación**: HTTP Basic Auth
- **Payload**: Información completa del cliente y tarjeta
- **Case Numbers**: Formato profesional BLK-YYYYMMDD-ID

### **Twilio Voice** (Preparado)
- **Webhook**: Configurado para recibir llamadas
- **TTS**: Conversión de texto a voz
- **STT**: Conversión de voz a texto

## 📊 Estado del Proyecto

### **✅ Completado (100%)**
- Setup del proyecto Rasa Pro
- Desarrollo de conversaciones
- Integración con Freshdesk
- Flujos conversacionales CALM
- Reconocimiento de confirmaciones
- Generación de tickets automática

### **🚧 En Progreso (80%)**
- Integración con Twilio Voice
- Integración con base de datos
- Testing completo del sistema

### **📋 Próximos Pasos**
- Testing end-to-end
- Optimización de rendimiento
- Documentación de API
- Despliegue en producción

## 🐛 Solución de Problemas

### **Problemas Resueltos**
1. **Confirmaciones no reconocidas** → SOLUCIONADO con anotaciones de entidades
2. **Slot no se llenaba** → SOLUCIONADO con mapping correcto
3. **Flujo interrumpido** → SOLUCIONADO con estructura CALM
4. **Mensaje final innecesario** → SOLUCIONADO con action personalizada

### **Logs y Debugging**
```bash
# Action Server con debug
rasa run actions --port 5055 --debug

# Rasa Shell con debug
rasa shell --port 5005 --debug
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Equipo

- **Desarrollador**: Mauricio Martínez
- **Empresa**: Scotiabank
- **Proyecto**: POC de Asistente Virtual para Bloqueo de Tarjetas

## 📞 Contacto

- **GitHub**: [@kaolong](https://github.com/kaolong)
- **Proyecto**: [bloqueo-sctbnk-voice](https://github.com/kaolong/bloqueo-sctbnk-voice)

---

**¡Gracias por usar Bloqueo SCTBNK Voice!** 🎉
