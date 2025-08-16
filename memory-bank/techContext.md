# Tech Context: Bloqueo de Tarjetas SCTBNK con Rasa Pro

## Stack Tecnológico

### **Core del Sistema**
- **Framework**: Rasa Pro 3.13.5 con CALM
- **Lenguaje**: Python 3.10.12
- **Arquitectura**: Flows y Patterns modernos
- **LLM Engine**: CALM (Conversational AI with Language Models)
- **Conversation Management**: Flows escalables para lógica de negocio
- **Action Server**: Rasa Action Server para acciones personalizadas
- **Seguridad**: Resistente a alucinaciones e inyección de prompts

### **Telefonía y Comunicación**
- **Servicio**: Twilio Voice API
- **Funcionalidades**: 
  - Recepción de llamadas entrantes
  - Text-to-Speech (TTS) en español
  - Webhooks para integración con Rasa
  - Manejo de eventos de llamada
- **Integración**: Webhook-based communication

### **Base de Datos**
- **Primary**: PostgreSQL 15+ o MongoDB 6+
- **Patrón**: Repository pattern para consultas de tarjetas
- **Funcionalidades**:
  - Almacenamiento de información de tarjetas
  - Consulta por últimos 4 dígitos
  - Verificación de estado de tarjetas
  - Logging de transacciones

### **Sistema de Tickets**
- **Plataforma**: Freshdesk
- **Integración**: REST API v2
- **Funcionalidades**:
  - Creación automática de tickets
  - Asignación de prioridades
  - Inclusión de información del cliente
  - Tracking de estado del ticket

### **Infraestructura**
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes (opcional para producción)
- **CI/CD**: GitHub Actions o GitLab CI
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack o Winston + Papertrail

## Dependencias Principales

### **Rasa Pro Dependencies (con CALM)**
```yaml
# requirements.txt
rasa[pro]==3.13.5
rasa[full]==3.13.5
rasa[spacy]==3.13.5
spacy==3.7.0
python-dateutil==2.8.2
requests==2.31.0
twilio==8.10.0
psycopg2-binary==2.9.7
pymongo==4.5.0
python-dotenv==1.1.0
openai==1.3.0  # Para integración con LLMs
```

### **Dependencias de Desarrollo**
```yaml
# requirements-dev.txt
pytest==7.2.0
pytest-cov==4.0.0
black==22.12.0
flake8==6.0.0
mypy==1.0.0
pre-commit==2.20.0
```

### **Dependencias de Sistema**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.10 python3.10-dev python3.10-venv
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y redis-server

# macOS
brew install python@3.10
brew install postgresql
brew install redis
```

## Configuración del Entorno

### **Variables de Entorno**
```bash
# Rasa Configuration
RASA_VERSION=3.13.5
RASA_TOKEN=your_rasa_token
RASA_MODEL_PATH=./models

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WEBHOOK_URL=https://your-domain.com/webhooks/twilio/webhook

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/sctbnk_cards
MONGODB_URL=mongodb://localhost:27017/sctbnk_cards

# Freshdesk Configuration
FRESHDESK_API_URL=https://pocsctbnk.freshdesk.com/api/v2
FRESHDESK_API_KEY=your_api_key
FRESHDESK_DOMAIN=pocsctbnk

# Security Configuration
ENCRYPTION_KEY=your_32_character_encryption_key
JWT_SECRET=your_jwt_secret_key
RATE_LIMIT_PER_MINUTE=10

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/rasa.log
SENTRY_DSN=your_sentry_dsn
```

### **Docker Configuration**
```yaml
# docker-compose.yml
version: '3.8'
services:
  rasa:
    build: .
    ports:
      - "5005:5005"
      - "5055:5055"
    environment:
      - RASA_TOKEN=${RASA_TOKEN}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sctbnk_cards
      POSTGRES_USER: sctbnk_user
      POSTGRES_PASSWORD: sctbnk_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### **Dockerfile**
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models logs

# Expose ports
EXPOSE 5005 5055

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5005/health || exit 1

# Start Rasa
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--debug"]
```

## Configuración de Rasa Pro

### **Configuración Principal**
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
    learning_rate: 0.001
    hidden_layers_sizes:
      text: [256, 128]
      label: [256, 128]
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 100
    learning_rate: 0.001

policies:
  - name: MemoizationPolicy
  - name: RulePolicy
  - name: UnexpecTEDIntentPolicy
  - name: TEDPolicy
    max_history: 5
    epochs: 100
    learning_rate: 0.001
```

### **Configuración de Dominio**
```yaml
# domain.yml
version: "3.1"

intents:
  - saludar
  - bloquear_tarjeta
  - confirmar_bloqueo
  - solicitar_digitos
  - proporcionar_digitos
  - verificar_tarjeta
  - confirmar_verificacion
  - generar_ticket
  - confirmar_generacion
  - confirmar_ticket
  - despedida
  - nlu_fallback

entities:
  - digitos
  - cliente_id

slots:
  digitos:
    type: text
    mappings:
    - type: from_entity
      entity: digitos
  cliente_id:
    type: text
    mappings:
    - type: from_entity
      entity: cliente_id

responses:
  utter_saludo:
    - text: "¡Buenos días!, soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
    - text: "¡Buenas tardes!, soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
    - text: "¡Buenas noches!, soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"

  utter_confirmar_bloqueo:
    - text: "Ok, te puedo ayudar con eso. Dime, ¿qué tarjeta es la que necesitas bloquear? Puedes darme los últimos 4 dígitos"

  utter_confirmar_ticket:
    - text: "Ok, generaré un ticket para el bloqueo, ¿te parece?"

  utter_despedida:
    - text: "Gracias por contactarte con nosotros, buenas tardes"
    - text: "Gracias por contactarte con nosotros, buenos días"
    - text: "Gracias por contactarte con nosotros, buenas noches"

actions:
  - action_saludo_contextual
  - action_confirmar_bloqueo
  - action_solicitar_digitos
  - action_verificar_tarjeta
  - action_generar_ticket
  - action_confirmar_ticket
  - action_despedida_contextual

session_config:
  session_expiration_time: 60
  carry_over_slots_to_new_session: true
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
    phone_number: "+1234567890"
```

## Configuración de Twilio

### **Webhook Configuration**
```python
# webhooks/twilio_webhook.py
from flask import Flask, request
from rasa.core.agent import Agent
from rasa.core.utils import EndpointConfig
import json

app = Flask(__name__)

# Load Rasa agent
agent = Agent.load("models/")

@app.route("/webhooks/twilio/webhook", methods=["POST"])
def twilio_webhook():
    # Get Twilio parameters
    from_number = request.form.get("From")
    to_number = request.form.get("To")
    speech_result = request.form.get("SpeechResult")
    
    # Process with Rasa
    response = agent.handle_text(speech_result, sender_id=from_number)
    
    # Return TwiML response
    twiml_response = f"""
    <Response>
        <Say language="es-MX">{response[0]['text']}</Say>
        <Gather input="speech" action="/webhooks/twilio/process" method="POST">
            <Say language="es-MX">Por favor, dime cómo puedo ayudarte</Say>
        </Gather>
    </Response>
    """
    
    return twiml_response, 200, {"Content-Type": "text/xml"}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

### **Twilio Studio Flow**
```json
{
  "description": "SCTBNK Card Blocking Flow",
  "states": [
    {
      "name": "Trigger",
      "type": "trigger",
      "transitions": [
        {
          "next": "rasa_webhook",
          "event": "incomingCall"
        }
      ]
    },
    {
      "name": "rasa_webhook",
      "type": "webhook",
      "transitions": [
        {
          "next": "end_call",
          "event": "callCompleted"
        }
      ],
      "properties": {
        "url": "https://your-rasa-server.com/webhooks/twilio/webhook",
        "method": "POST"
      }
    },
    {
      "name": "end_call",
      "type": "endCall",
      "properties": {}
    }
  ],
  "initial_state": "Trigger"
}
```

## Configuración de Base de Datos

### **PostgreSQL Schema**
```sql
-- Schema para tarjetas de SCTBNK
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    card_number VARCHAR(16) NOT NULL,
    last_four_digits VARCHAR(4) NOT NULL,
    card_type VARCHAR(20) NOT NULL,
    client_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blocking_requests (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(50) NOT NULL,
    card_id INTEGER REFERENCES cards(id),
    request_type VARCHAR(20) DEFAULT 'block',
    status VARCHAR(20) DEFAULT 'pending',
    freshdesk_ticket_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Índices para optimización
CREATE INDEX idx_cards_last_four ON cards(last_four_digits);
CREATE INDEX idx_cards_client_id ON cards(client_id);
CREATE INDEX idx_blocking_requests_status ON blocking_requests(status);
```

### **MongoDB Schema**
```javascript
// Colección de tarjetas
db.createCollection("cards", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["cardNumber", "lastFourDigits", "cardType", "clientId"],
      properties: {
        cardNumber: {
          bsonType: "string",
          pattern: "^[0-9]{16}$"
        },
        lastFourDigits: {
          bsonType: "string",
          pattern: "^[0-9]{4}$"
        },
        cardType: {
          enum: ["credit", "debit", "prepaid"]
        },
        clientId: {
          bsonType: "string"
        },
        status: {
          enum: ["active", "blocked", "expired", "cancelled"]
        }
      }
    }
  }
});

// Índices
db.cards.createIndex({ "lastFourDigits": 1 });
db.cards.createIndex({ "clientId": 1 });
db.cards.createIndex({ "status": 1 });
```

## Configuración de Freshdesk

### **API Configuration**
```python
# services/freshdesk_service.py
import requests
from typing import Dict, Any
import os

class FreshdeskService:
    def __init__(self):
        self.api_url = os.getenv("FRESHDESK_API_URL")
        self.api_key = os.getenv("FRESHDESK_API_KEY")
        self.domain = os.getenv("FRESHDESK_DOMAIN")
        
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear ticket en Freshdesk"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.api_key}"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/tickets",
                json=ticket_data,
                headers=headers,
                auth=(self.api_key, "X")
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                raise Exception(f"Error creating ticket: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Failed to create ticket: {str(e)}")
    
    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Obtener información de un ticket"""
        
        headers = {
            "Authorization": f"Basic {self.api_key}"
        }
        
        try:
            response = requests.get(
                f"{self.api_url}/tickets/{ticket_id}",
                headers=headers,
                auth=(self.api_key, "X")
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Error getting ticket: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Failed to get ticket: {str(e)}")
```

## Scripts de Desarrollo

### **Scripts de Package.json**
```json
{
  "scripts": {
    "rasa:train": "rasa train",
    "rasa:run": "rasa run --enable-api --cors '*' --debug",
    "rasa:shell": "rasa shell",
    "rasa:test": "rasa test",
    "rasa:interactive": "rasa interactive",
    "rasa:data": "rasa data validate",
    "rasa:visualize": "rasa visualize",
    "docker:build": "docker build -t sctbnk-rasa .",
    "docker:run": "docker-compose up -d",
    "docker:stop": "docker-compose down",
    "docker:logs": "docker-compose logs -f rasa"
  }
}
```

### **Scripts de Python**
```python
# scripts/setup.py
#!/usr/bin/env python3
"""
Script de configuración inicial para SCTBNK Rasa Pro
"""

import os
import subprocess
import sys

def run_command(command):
    """Ejecutar comando del sistema"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando: {command}")
        print(f"Error: {e.stderr}")
        return None

def setup_environment():
    """Configurar entorno de desarrollo"""
    print("🚀 Configurando entorno de desarrollo para SCTBNK Rasa Pro...")
    
    # Crear directorios necesarios
    directories = ["models", "logs", "data", "actions"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Directorio creado: {directory}")
    
    # Instalar dependencias
    print("📦 Instalando dependencias...")
    run_command("pip install -r requirements.txt")
    
    # Entrenar modelo inicial
    print("🧠 Entrenando modelo inicial...")
    run_command("rasa train")
    
    print("✅ Configuración completada!")

if __name__ == "__main__":
    setup_environment()
```

## Restricciones Técnicas

### **Compatibilidad**
- **Python**: 3.10.12 (versión exacta instalada)
- **Rasa Pro**: 3.13.5 (versión exacta instalada)
- **PostgreSQL**: 15+ o MongoDB 6+
- **Twilio**: API v2010-04-01 o superior

### **Limitaciones**
- **Tiempo de respuesta**: <2 segundos por interacción
- **Concurrent calls**: Máximo 100 llamadas simultáneas
- **Model training**: Tiempo máximo de entrenamiento 30 minutos
- **API rate limits**: Freshdesk: 1000 requests/hour, Twilio: según plan

### **Requisitos de Sistema**
- **RAM mínima**: 4GB (8GB recomendado)
- **CPU**: 2 cores (4 cores recomendado)
- **Almacenamiento**: 20GB SSD (50GB recomendado)
- **Red**: 100Mbps (1Gbps recomendado)
- **Sistema Operativo**: Ubuntu 20.04+, macOS 11+, Windows 10+
