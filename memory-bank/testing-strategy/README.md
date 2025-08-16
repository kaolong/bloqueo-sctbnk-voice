# Testing Strategy: Bloqueo de Tarjetas SCTBNK con Rasa Pro

## Visión General
Estrategia integral de testing para asegurar la calidad, seguridad y confiabilidad del sistema de asistente virtual de bloqueo de tarjetas desarrollado con Rasa Pro, Twilio y Freshdesk.

## Objetivos de Testing
- **Calidad Conversacional**: Asegurar que el asistente entienda y responda correctamente
- **Integración de Sistemas**: Validar la comunicación entre Rasa, Twilio y Freshdesk
- **Seguridad Bancaria**: Verificar cumplimiento de estándares PCI DSS
- **Performance**: Validar respuesta en menos de 2 segundos por interacción
- **Usabilidad**: Validar experiencia del usuario en llamadas telefónicas
- **Compliance**: Asegurar cumplimiento de regulaciones bancarias

## Tipos de Testing

### 1. **Testing de Conversaciones (Rasa Pro)**
- **Objetivo**: Probar flujos conversacionales y entendimiento de intents
- **Cobertura Objetivo**: 95%+
- **Herramientas**: Rasa shell, Rasa test, Rasa interactive

#### **Testing de Intents**
```python
# tests/test_intents.py
import pytest
from rasa.nlu.model import Interpreter
from rasa.shared.nlu.training_data.training_data import TrainingData

class TestIntents:
    def setup_method(self):
        self.interpreter = Interpreter.load("models/")
    
    def test_bloquear_tarjeta_intent(self):
        # Test variaciones de "necesito bloquear mi tarjeta"
        test_cases = [
            "necesito bloquear mi tarjeta",
            "quiero bloquear mi tarjeta",
            "mi tarjeta fue robada",
            "perdí mi tarjeta",
            "necesito cancelar mi tarjeta"
        ]
        
        for text in test_cases:
            result = self.interpreter.parse(text)
            assert result["intent"]["name"] == "bloquear_tarjeta"
            assert result["intent"]["confidence"] > 0.8
    
    def test_confirmar_bloqueo_intent(self):
        # Test variaciones de confirmación
        test_cases = [
            "sí",
            "correcto",
            "perfecto",
            "adelante",
            "procede"
        ]
        
        for text in test_cases:
            result = self.interpreter.parse(text)
            assert result["intent"]["name"] == "confirmar_bloqueo"
            assert result["intent"]["confidence"] > 0.8
```

#### **Testing de Entidades**
```python
# tests/test_entities.py
def test_digitos_entity_extraction(self):
    # Test extracción de últimos 4 dígitos
    test_cases = [
        ("es la 1234", "1234"),
        ("son los 5678", "5678"),
        ("9012", "9012"),
        ("la tarjeta 3456", "3456")
    ]
    
    for text, expected_digits in test_cases:
        result = self.interpreter.parse(text)
        entities = result["entities"]
        
        assert len(entities) > 0
        assert entities[0]["entity"] == "digitos"
        assert entities[0]["value"] == expected_digits
        assert entities[0]["confidence"] > 0.9
```

#### **Testing de Flows**
```python
# tests/test_flows.py
from rasa.core.agent import Agent
from rasa.core.tracker_store import InMemoryTrackerStore

class TestFlows:
    def setup_method(self):
        self.agent = Agent.load("models/")
        self.tracker_store = InMemoryTrackerStore(domain=self.agent.domain)
    
    def test_bloqueo_tarjeta_flow(self):
        # Test flujo completo de bloqueo
        sender_id = "test_user_123"
        
        # Paso 1: Saludar
        response = self.agent.handle_text("hola", sender_id=sender_id)
        assert any("Buenos días" in msg["text"] or "Buenas tardes" in msg["text"] or "Buenas noches" in msg["text"] 
                  for msg in response)
        
        # Paso 2: Solicitar bloqueo
        response = self.agent.handle_text("necesito bloquear mi tarjeta", sender_id=sender_id)
        assert any("últimos 4 dígitos" in msg["text"] for msg in response)
        
        # Paso 3: Proporcionar dígitos
        response = self.agent.handle_text("es la 1234", sender_id=sender_id)
        assert any("generaré un ticket" in msg["text"] for msg in response)
        
        # Paso 4: Confirmar generación
        response = self.agent.handle_text("sí, procede", sender_id=sender_id)
        assert any("ticket número" in msg["text"] for msg in response)
```

### 2. **Testing de Integración con Twilio**
- **Objetivo**: Probar comunicación entre Twilio y Rasa Pro
- **Cobertura**: Webhooks, manejo de llamadas, TTS
- **Herramientas**: Twilio CLI, Twilio Studio testing, Webhook testing

#### **Testing de Webhooks**
```python
# tests/test_twilio_webhooks.py
import requests
import json
from unittest.mock import patch

class TestTwilioWebhooks:
    def test_twilio_webhook_reception(self):
        # Test recepción de webhook de Twilio
        webhook_url = "http://localhost:5005/webhooks/twilio/webhook"
        
        # Simular datos de Twilio
        twilio_data = {
            "From": "+1234567890",
            "To": "+0987654321",
            "SpeechResult": "necesito bloquear mi tarjeta",
            "CallSid": "CA1234567890abcdef",
            "CallStatus": "in-progress"
        }
        
        response = requests.post(webhook_url, data=twilio_data)
        
        assert response.status_code == 200
        assert "text/xml" in response.headers["Content-Type"]
        
        # Verificar que la respuesta contiene TwiML válido
        content = response.text
        assert "<Response>" in content
        assert "<Say>" in content
        assert "<Gather>" in content
    
    def test_twilio_tts_response(self):
        # Test que la respuesta TTS sea en español
        webhook_url = "http://localhost:5005/webhooks/twilio/webhook"
        
        twilio_data = {
            "From": "+1234567890",
            "To": "+0987654321",
            "SpeechResult": "hola",
            "CallSid": "CA1234567890abcdef"
        }
        
        response = requests.post(webhook_url, data=twilio_data)
        content = response.text
        
        # Verificar configuración de idioma
        assert 'language="es-MX"' in content
        assert "Scotiabank" in content
```

#### **Testing de Llamadas**
```python
# tests/test_twilio_calls.py
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

class TestTwilioCalls:
    def setup_method(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
    
    def test_call_creation(self):
        # Test creación de llamada
        try:
            call = self.client.calls.create(
                to="+1234567890",
                from_="+0987654321",
                url="https://your-rasa-server.com/webhooks/twilio/webhook",
                method="POST"
            )
            
            assert call.sid is not None
            assert call.status in ["queued", "ringing", "in-progress"]
            
        except TwilioException as e:
            pytest.fail(f"Error creating call: {e}")
    
    def test_call_status_retrieval(self):
        # Test obtención de estado de llamada
        call_sid = "CA1234567890abcdef"  # SID de llamada existente
        
        try:
            call = self.client.calls(call_sid).fetch()
            assert call.sid == call_sid
            assert hasattr(call, 'status')
            
        except TwilioException as e:
            pytest.fail(f"Error retrieving call: {e}")
```

### 3. **Testing de Integración con Freshdesk**
- **Objetivo**: Probar creación y gestión de tickets
- **Cobertura**: API endpoints, autenticación, campos personalizados
- **Herramientas**: Freshdesk sandbox, API testing tools

#### **Testing de Creación de Tickets**
```python
# tests/test_freshdesk_api.py
import requests
import base64
import os

class TestFreshdeskAPI:
    def setup_method(self):
        self.api_url = "https://pocsctbnk.freshdesk.com/api/v2"
        self.api_key = os.getenv("FRESHDESK_API_KEY")
        self.auth_header = base64.b64encode(f"{self.api_key}:X".encode()).decode()
    
    def test_ticket_creation(self):
        # Test creación de ticket
        headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json"
        }
        
        ticket_data = {
            "subject": "Test - Bloqueo de tarjeta",
            "description": "Ticket de prueba para testing",
            "email": "test@example.com",
            "priority": 1,
            "status": 2,
            "type": "Bloqueo de Tarjeta",
            "custom_fields": {
                "cf_tarjeta_ultimos_digitos": "9999",
                "cf_cliente_id": "TEST123",
                "cf_tipo_bloqueo": "testing"
            }
        }
        
        response = requests.post(
            f"{self.api_url}/tickets",
            json=ticket_data,
            headers=headers
        )
        
        assert response.status_code == 201
        
        ticket = response.json()
        assert ticket["subject"] == ticket_data["subject"]
        assert ticket["custom_fields"]["cf_tarjeta_ultimos_digitos"] == "9999"
        
        # Limpiar ticket de prueba
        self._delete_test_ticket(ticket["id"])
    
    def test_ticket_retrieval(self):
        # Test obtención de ticket
        headers = {
            "Authorization": f"Basic {self.auth_header}"
        }
        
        # Crear ticket temporal para testing
        ticket_id = self._create_test_ticket()
        
        try:
            response = requests.get(
                f"{self.api_url}/tickets/{ticket_id}",
                headers=headers
            )
            
            assert response.status_code == 200
            
            ticket = response.json()
            assert ticket["id"] == ticket_id
            assert ticket["type"] == "Bloqueo de Tarjeta"
            
        finally:
            self._delete_test_ticket(ticket_id)
    
    def _create_test_ticket(self):
        # Método helper para crear ticket de prueba
        headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json"
        }
        
        ticket_data = {
            "subject": "Test Ticket",
            "description": "Ticket temporal para testing",
            "email": "test@example.com",
            "priority": 3,
            "status": 2
        }
        
        response = requests.post(
            f"{self.api_url}/tickets",
            json=ticket_data,
            headers=headers
        )
        
        return response.json()["id"]
    
    def _delete_test_ticket(self, ticket_id):
        # Método helper para eliminar ticket de prueba
        headers = {
            "Authorization": f"Basic {self.auth_header}"
        }
        
        requests.delete(
            f"{self.api_url}/tickets/{ticket_id}",
            headers=headers
        )
```

### 4. **Testing de Base de Datos**
- **Objetivo**: Probar consultas y operaciones de base de datos
- **Cobertura**: Consultas de tarjetas, verificación de clientes
- **Herramientas**: TestContainers, pytest-postgresql

#### **Testing de Consultas de Tarjetas**
```python
# tests/test_database.py
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor

class TestDatabase:
    def setup_method(self):
        # Configurar conexión de prueba
        self.conn = psycopg2.connect(
            host="localhost",
            database="test_sctbnk_cards",
            user="test_user",
            password="test_password"
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        
        # Crear datos de prueba
        self._setup_test_data()
    
    def teardown_method(self):
        # Limpiar datos de prueba
        self._cleanup_test_data()
        self.cur.close()
        self.conn.close()
    
    def test_card_verification_by_digits(self):
        # Test verificación de tarjeta por últimos 4 dígitos
        test_digits = "1234"
        
        query = """
        SELECT c.*, cl.name as client_name
        FROM cards c
        JOIN clients cl ON c.client_id = cl.client_id
        WHERE c.last_four_digits = %s AND c.status = 'active'
        """
        
        self.cur.execute(query, (test_digits,))
        result = self.cur.fetchone()
        
        assert result is not None
        assert result["last_four_digits"] == test_digits
        assert result["status"] == "active"
        assert result["client_name"] == "Cliente Test"
    
    def test_client_verification(self):
        # Test verificación de cliente
        test_phone = "+1234567890"
        
        query = """
        SELECT client_id, name, status
        FROM clients
        WHERE phone = %s AND status = 'active'
        """
        
        self.cur.execute(query, (test_phone,))
        result = self.cur.fetchone()
        
        assert result is not None
        assert result["phone"] == test_phone
        assert result["status"] == "active"
    
    def _setup_test_data(self):
        # Insertar datos de prueba
        self.cur.execute("""
        INSERT INTO clients (client_id, name, phone, email, status)
        VALUES ('TEST123', 'Cliente Test', '+1234567890', 'test@example.com', 'active')
        """)
        
        self.cur.execute("""
        INSERT INTO cards (card_number, last_four_digits, card_type, client_id, status)
        VALUES ('1234567890123456', '1234', 'credit', 'TEST123', 'active')
        """)
        
        self.conn.commit()
    
    def _cleanup_test_data(self):
        # Limpiar datos de prueba
        self.cur.execute("DELETE FROM cards WHERE client_id = 'TEST123'")
        self.cur.execute("DELETE FROM clients WHERE client_id = 'TEST123'")
        self.conn.commit()
```

### 5. **Testing End-to-End**
- **Objetivo**: Probar flujo completo del sistema
- **Cobertura**: Llamada completa desde Twilio hasta Freshdesk
- **Herramientas**: Rasa test, Twilio Studio testing, Freshdesk sandbox

#### **Testing de Flujo Completo**
```python
# tests/test_e2e_flow.py
import pytest
from unittest.mock import patch, MagicMock
from rasa.core.agent import Agent

class TestEndToEndFlow:
    def setup_method(self):
        self.agent = Agent.load("models/")
        
        # Mock de servicios externos
        self.freshdesk_mock = MagicMock()
        self.database_mock = MagicMock()
    
    @patch('services.freshdesk_service.FreshdeskService')
    @patch('services.database_service.DatabaseService')
    def test_complete_blocking_flow(self, mock_db, mock_freshdesk):
        # Test flujo completo de bloqueo
        
        # Configurar mocks
        mock_db.return_value.verify_card.return_value = {
            "success": True,
            "data": {
                "card_id": "card_123",
                "last_four_digits": "1234",
                "client_id": "client_456"
            }
        }
        
        mock_freshdesk.return_value.create_ticket.return_value = {
            "id": 12345,
            "subject": "Bloqueo de tarjeta - Cliente client_456"
        }
        
        # Simular conversación completa
        sender_id = "test_user_e2e"
        
        # Paso 1: Saludo
        response1 = self.agent.handle_text("hola", sender_id=sender_id)
        assert any("Buenos días" in msg["text"] or "Buenas tardes" in msg["text"] or "Buenas noches" in msg["text"] 
                  for msg in response1)
        
        # Paso 2: Solicitar bloqueo
        response2 = self.agent.handle_text("necesito bloquear mi tarjeta", sender_id=sender_id)
        assert any("últimos 4 dígitos" in msg["text"] for msg in response2)
        
        # Paso 3: Proporcionar dígitos
        response3 = self.agent.handle_text("es la 1234", sender_id=sender_id)
        assert any("generaré un ticket" in msg["text"] for msg in response3)
        
        # Paso 4: Confirmar generación
        response4 = self.agent.handle_text("sí, procede", sender_id=sender_id)
        assert any("ticket número 12345" in msg["text"] for msg in response4)
        
        # Verificar que se llamó a los servicios
        mock_db.return_value.verify_card.assert_called_once_with("1234", sender_id)
        mock_freshdesk.return_value.create_ticket.assert_called_once()
```

### 6. **Testing de Performance**
- **Objetivo**: Validar tiempos de respuesta y escalabilidad
- **Cobertura**: Respuesta <2 segundos, 100+ llamadas concurrentes
- **Herramientas**: Artillery, k6, Rasa performance testing

#### **Testing de Performance de Rasa**
```python
# tests/test_performance.py
import time
import concurrent.futures
from rasa.core.agent import Agent

class TestPerformance:
    def setup_method(self):
        self.agent = Agent.load("models/")
    
    def test_response_time(self):
        # Test tiempo de respuesta individual
        start_time = time.time()
        
        response = self.agent.handle_text("necesito bloquear mi tarjeta", "user_perf")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response_time < 2.0, f"Response time {response_time}s exceeds 2s limit"
        assert len(response) > 0
    
    def test_concurrent_requests(self):
        # Test múltiples requests concurrentes
        test_messages = [
            "hola",
            "necesito bloquear mi tarjeta",
            "es la 1234",
            "sí, procede"
        ]
        
        def process_message(message):
            start_time = time.time()
            response = self.agent.handle_text(message, f"user_{hash(message)}")
            end_time = time.time()
            return end_time - start_time
        
        # Ejecutar 100 requests concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(process_message, msg) for msg in test_messages * 25]
            response_times = [future.result() for future in futures]
        
        # Verificar que todos los requests respondieron en menos de 2 segundos
        for response_time in response_times:
            assert response_time < 2.0, f"Response time {response_time}s exceeds 2s limit"
        
        # Verificar tiempo promedio
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 1.0, f"Average response time {avg_response_time}s exceeds 1s limit"
```

### 7. **Testing de Seguridad**
- **Objetivo**: Validar medidas de seguridad bancaria
- **Cobertura**: Verificación de identidad, logging, auditoría
- **Herramientas**: OWASP ZAP, Custom security tests

#### **Testing de Seguridad**
```python
# tests/test_security.py
import pytest
from unittest.mock import patch

class TestSecurity:
    def test_identity_verification(self):
        # Test verificación de identidad mediante últimos 4 dígitos
        test_cases = [
            ("1234", True),   # Dígitos válidos
            ("9999", False),  # Dígitos inválidos
            ("abcd", False),  # Caracteres no numéricos
            ("123", False),   # Menos de 4 dígitos
            ("12345", False)  # Más de 4 dígitos
        ]
        
        for digits, expected_valid in test_cases:
            # Simular verificación en base de datos
            is_valid = self._verify_card_digits(digits)
            assert is_valid == expected_valid
    
    def test_sensitive_data_logging(self):
        # Test que no se registren datos sensibles
        test_message = "mi tarjeta es 1234567890123456"
        
        # Simular logging
        log_entry = self._log_message(test_message)
        
        # Verificar que no se registre el número completo de tarjeta
        assert "1234567890123456" not in log_entry
        assert "1234567890123456" not in str(log_entry)
        
        # Verificar que solo se registren los últimos 4 dígitos
        assert "3456" in log_entry
    
    def _verify_card_digits(self, digits):
        # Simulación de verificación
        if len(digits) != 4 or not digits.isdigit():
            return False
        
        # Simular consulta a base de datos
        valid_digits = ["1234", "5678", "9012"]
        return digits in valid_digits
    
    def _log_message(self, message):
        # Simulación de logging
        # En implementación real, esto iría al sistema de logging
        return {
            "timestamp": "2024-01-15T14:30:22Z",
            "message": message.replace("1234567890123456", "****3456"),
            "level": "INFO"
        }
```

## Estrategia de Implementación

### **Fase 1: Testing Foundation (Semana 1-2)**
- [ ] Configurar entorno de testing
- [ ] Implementar tests unitarios de intents
- [ ] Configurar tests de entidades
- [ ] Establecer tests de flujos básicos

### **Fase 2: Integration Testing (Semana 3-4)**
- [ ] Tests de integración con Twilio
- [ ] Tests de integración con Freshdesk
- [ ] Tests de base de datos
- [ ] Tests de webhooks

### **Fase 3: E2E y Performance (Semana 5-6)**
- [ ] Tests end-to-end completos
- [ ] Tests de performance
- [ ] Tests de seguridad
- [ ] Tests de fallbacks

### **Fase 4: Continuous Testing (Semana 7+)**
- [ ] Automatización completa
- [ ] CI/CD pipeline
- [ ] Monitoreo de calidad
- [ ] Optimización continua

## Configuración de Testing

### **Requirements de Testing**
```txt
# requirements-test.txt
pytest==7.4.0
pytest-cov==4.1.0
pytest-postgresql==4.1.1
pytest-mock==3.11.1
requests==2.31.0
twilio==8.10.0
psycopg2-binary==2.9.7
```

### **Configuración de pytest**
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90
```

### **Configuración de Base de Datos de Testing**
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  test-db:
    image: postgres:15
    environment:
      POSTGRES_DB: test_sctbnk_cards
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5433:5432"
    volumes:
      - ./tests/test_data.sql:/docker-entrypoint-initdb.d/test_data.sql
```

## Criterios de Aceptación

### **Cobertura de Código**
- **Unit Tests**: 95%+
- **Integration Tests**: 90%+
- **E2E Tests**: Casos críticos cubiertos

### **Performance**
- **Response Time**: <2 segundos (95th percentile)
- **Concurrent Calls**: 100+ llamadas simultáneas
- **Error Rate**: <1%

### **Seguridad**
- **Verificación de Identidad**: 100% de tarjetas verificadas
- **Logging Seguro**: 0% de datos sensibles expuestos
- **Compliance**: Cumplimiento de estándares bancarios

### **Calidad Conversacional**
- **Intent Recognition**: >95% de precisión
- **Entity Extraction**: >90% de precisión
- **Flow Completion**: >90% de conversaciones exitosas

## Monitoreo y Reportes

### **Métricas de Testing**
- **Test Execution Time**: Tiempo total de ejecución
- **Pass/Fail Rate**: Porcentaje de tests exitosos
- **Coverage Trends**: Evolución de cobertura
- **Performance Metrics**: Métricas de rendimiento

### **Reportes Automatizados**
- **Daily Reports**: Resumen diario de tests
- **Coverage Reports**: Reportes de cobertura
- **Performance Reports**: Métricas de rendimiento
- **Security Reports**: Vulnerabilidades encontradas

### **Alertas**
- **Test Failures**: Notificaciones inmediatas
- **Coverage Drops**: Alertas de cobertura
- **Performance Degradation**: Alertas de rendimiento
- **Security Issues**: Alertas de seguridad

## Mejora Continua

### **Retrospectivas de Testing**
- **Semanales**: Revisión de métricas y problemas
- **Mensuales**: Análisis de tendencias y mejoras
- **Trimestrales**: Evaluación de estrategia completa

### **Optimización**
- **Test Execution**: Reducir tiempo de ejecución
- **Coverage**: Aumentar cobertura efectiva
- **Maintenance**: Reducir mantenimiento de tests
- **Reliability**: Aumentar confiabilidad de tests
