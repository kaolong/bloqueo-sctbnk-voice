# Versiones del Entorno: Bloqueo de Tarjetas SCTBNK con Rasa Pro

## 📋 Versiones Exactas del Sistema

### **Rasa Pro**
- **Versión Principal**: 3.13.5
- **Versión Mínima Compatible**: 3.11.0rc1
- **Rasa SDK**: 3.13.0
- **Arquitectura**: CALM (Conversational AI with Language Models)
- **Características**: Flows y Patterns modernos
- **Estado**: ✅ Instalado y Funcionando

### **Python**
- **Versión**: 3.10.12
- **Estado**: ✅ Instalado y Funcionando
- **Compatibilidad**: Compatible con Rasa Pro 3.13.5

### **Dependencias Principales (con CALM)**
```yaml
# Versiones exactas del entorno
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

### **Dependencias de Testing**
```yaml
# Versiones para testing
pytest==7.4.0
pytest-cov==4.1.0
pytest-postgresql==4.1.1
pytest-mock==3.11.1
```

## 🔧 Configuración del Entorno

### **Variables de Entorno Requeridas**
```bash
# Rasa Configuration
RASA_VERSION=3.13.5
RASA_TOKEN=your_rasa_token
RASA_MODEL_PATH=./models

# Python Configuration
PYTHON_VERSION=3.10.12
PYTHON_PATH=/usr/bin/python3.10

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
```

### **Verificación de Versiones**
```bash
# Verificar Rasa Pro
rasa --version

# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar dependencias instaladas
pip list | grep -E "(rasa|spacy|twilio|psycopg2|pymongo)"
```

## 📦 Instalación y Setup

### **Requisitos del Sistema**
- **Sistema Operativo**: Ubuntu 20.04+, macOS 11+, Windows 10+
- **Python**: 3.10.12 (exacto)
- **RAM**: 4GB mínimo (8GB recomendado)
- **Almacenamiento**: 20GB SSD mínimo (50GB recomendado)

### **Comandos de Instalación**
```bash
# Crear entorno virtual
python3.10 -m venv rasa_env
source rasa_env/bin/activate  # Linux/macOS
# rasa_env\Scripts\activate  # Windows

# Actualizar pip
pip install --upgrade pip

# Instalar Rasa Pro con CALM
pip install rasa[pro]==3.13.5

# Instalar dependencias adicionales
pip install -r requirements.txt

# Verificar instalación
rasa --version
```

### **Verificación de Funcionamiento**
```bash
# Inicializar proyecto Rasa
rasa init

# Entrenar modelo
rasa train

# Probar conversación
rasa shell

# Verificar endpoints
rasa run --enable-api --cors "*"
```

## 🔄 Compatibilidad y Actualizaciones

### **Matriz de Compatibilidad**
| Componente | Versión Actual | Versión Mínima | Versión Máxima |
|------------|----------------|----------------|----------------|
| Rasa Pro   | 3.13.5        | 3.11.0rc1      | 3.13.x         |
| Python     | 3.10.12       | 3.10.0         | 3.10.x         |
| Spacy      | 3.7.0         | 3.6.0          | 3.7.x          |
| Twilio     | 8.10.0        | 7.0.0          | 8.x.x          |

### **Política de Actualizaciones**
- **Rasa Pro**: Solo actualizaciones de patch (3.13.x)
- **Python**: Mantener en 3.10.x hasta nueva versión LTS
- **Dependencias**: Actualizaciones de seguridad y compatibilidad
- **Testing**: Verificar compatibilidad antes de actualizar

### **Proceso de Actualización**
```bash
# 1. Crear backup del entorno actual
pip freeze > requirements_backup.txt

# 2. Verificar compatibilidad
rasa --version
python --version

# 3. Actualizar dependencias
pip install --upgrade -r requirements.txt

# 4. Verificar funcionamiento
rasa test
rasa shell

# 5. Rollback si es necesario
pip install -r requirements_backup.txt
```

## 🚨 Consideraciones Importantes

### **Restricciones de Versión**
- **NO actualizar** Rasa Pro más allá de 3.13.x sin testing exhaustivo
- **NO cambiar** Python de 3.10.x sin verificar compatibilidad
- **SÍ actualizar** dependencias de seguridad cuando sea necesario

### **Dependencias Críticas**
- **Rasa Pro 3.13.5**: Core del sistema, no cambiar
- **Python 3.10.12**: Runtime, mantener estable
- **Spacy 3.7.0**: NLU engine, verificar compatibilidad
- **Twilio 8.10.0**: API de telefonía, mantener actualizado

### **Testing Post-Instalación**
```bash
# Test completo del sistema
rasa test

# Test de intents
rasa test nlu

# Test de stories
rasa test core

# Test de integración
pytest tests/
```

## 📊 Monitoreo de Versiones

### **Métricas de Estabilidad**
- **Uptime**: 99.9% objetivo
- **Response Time**: <2 segundos por interacción
- **Error Rate**: <1% en producción
- **Model Accuracy**: >95% en intents

### **Alertas de Versión**
- **Versión Rasa**: Cambios no autorizados
- **Versión Python**: Cambios de runtime
- **Dependencias**: Vulnerabilidades de seguridad
- **Compatibilidad**: Conflictos entre versiones

---

**Última Verificación**: $(date)  
**Entorno**: Rasa Pro 3.13.5 + Python 3.10.12  
**Estado**: ✅ Configurado y Verificado
