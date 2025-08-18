# 🎤 Configuración del Servidor Twilio Voice para Rasa Pro

## 📋 Descripción

Este servidor Flask actúa como intermediario entre **Twilio Voice API** y nuestro **proyecto Rasa Pro** de bloqueo de tarjetas. Convierte llamadas de voz en texto para Rasa y respuestas de texto en voz para el usuario.

## 🏗️ Arquitectura

```
┌─────────────┐    ┌─────────────────────┐    ┌─────────────┐
│   Usuario   │───▶│  Twilio Voice API  │───▶│ Servidor   │
│   (Voz)     │    │                     │    │   Flask    │
└─────────────┘    └─────────────────────┘    └─────────────┘
                                                       │
                                                       ▼
                                               ┌─────────────┐
                                               │   Rasa Pro  │
                                               │ (Bloqueo    │
                                               │  Tarjetas)  │
                                               └─────────────┘
```

## 🚀 Instalación

### 1. Dependencias del Sistema
```bash
# Verificar Python 3.10+
python3 --version

# Verificar pip
pip3 --version
```

### 2. Instalación Automática
```bash
# Dar permisos de ejecución
chmod +x install_twilio_server.sh

# Ejecutar instalador
./install_twilio_server.sh
```

### 3. Instalación Manual
```bash
# Instalar dependencias
pip3 install -r twilio_requirements.txt

# Verificar instalación
python3 -c "import flask, twilio, requests; print('✅ OK')"
```

## ⚙️ Configuración

### 1. Variables de Entorno
Edita el archivo `twilio.env`:

```bash
# Puerto del servidor
PORT=5001

# URL de Rasa Pro
RASA_WEBHOOK_URL=http://localhost:5005/webhooks/rest/webhook

# Credenciales de Twilio (opcional)
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token

# Número de fallback
FALLBACK_PHONE_NUMBER=+1234567890
```

### 2. Configuración de Twilio Console

#### A. Configurar Número de Teléfono
1. Ve a [Twilio Console](https://console.twilio.com/)
2. Navega a **Phone Numbers** → **Manage** → **Active numbers**
3. Selecciona tu número
4. En **Voice Configuration**:
   - **Webhook**: `https://tu-dominio.com/webhook/twilio/voice`
   - **HTTP Method**: `POST`

#### B. Configurar Webhook URLs
```
Voice Webhook: https://tu-dominio.com/webhook/twilio/voice
Status Callback: https://tu-dominio.com/webhook/twilio/status
```

## 🏃‍♂️ Ejecución

### 1. Desarrollo Local
```bash
# Cargar variables de entorno
export $(cat twilio.env | xargs)

# Ejecutar servidor
python3 twilio_voice_server.py
```

### 2. Producción con Gunicorn
```bash
# Cargar variables de entorno
export $(cat twilio.env | xargs)

# Ejecutar con Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 twilio_voice_server:app
```

### 3. Con Docker (opcional)
```bash
# Construir imagen
docker build -t twilio-voice-server .

# Ejecutar contenedor
docker run -p 5001:5001 --env-file twilio.env twilio-voice-server
```

## 🔗 Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información del servidor |
| `/health` | GET | Estado de salud |
| `/webhook/twilio/voice` | POST | Llamadas entrantes |
| `/webhook/twilio/speech` | POST | Input de voz |
| `/webhook/twilio/fallback` | POST | Manejo de fallbacks |
| `/webhook/twilio/status` | POST | Status de llamadas |

## 📱 Flujo de Llamada

### 1. Llamada Entrante
```
Usuario llama → Twilio → /webhook/twilio/voice → Saludo contextual
```

### 2. Procesamiento de Voz
```
Usuario habla → Twilio STT → /webhook/twilio/speech → Rasa Pro
```

### 3. Respuesta del Bot
```
Rasa Pro → /webhook/twilio/speech → Twilio TTS → Usuario escucha
```

### 4. Fallback
```
Sin input → /webhook/twilio/fallback → Conectar con ejecutivo
```

## 🧪 Testing

### 1. Test Local con ngrok
```bash
# Instalar ngrok
brew install ngrok  # macOS
# o descargar desde https://ngrok.com/

# Exponer puerto local
ngrok http 5001

# Usar URL de ngrok en Twilio Console
# https://abc123.ngrok.io/webhook/twilio/voice
```

### 2. Test de Endpoints
```bash
# Health check
curl http://localhost:5001/health

# Información del servidor
curl http://localhost:5001/
```

### 3. Test de Webhook
```bash
# Simular llamada entrante
curl -X POST http://localhost:5001/webhook/twilio/voice \
  -d "CallSid=test123&From=+1234567890&To=+0987654321"
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Puerto en Uso
```bash
# Verificar puerto
lsof -i :5001

# Matar proceso
kill -9 <PID>
```

#### 2. Error de Conexión con Rasa
```bash
# Verificar que Rasa esté corriendo
curl http://localhost:5005/status

# Verificar webhook URL en twilio.env
```

#### 3. Error de TwiML
```bash
# Verificar logs del servidor
tail -f twilio_voice_server.log

# Verificar formato de respuesta XML
```

### Logs y Debugging
```bash
# Activar debug mode
export DEBUG=True

# Ver logs en tiempo real
tail -f /var/log/twilio_voice.log
```

## 📊 Monitoreo

### 1. Métricas del Servidor
- Llamadas entrantes
- Tiempo de respuesta
- Errores de conexión
- Uso de memoria/CPU

### 2. Logs Estructurados
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "call_sid": "CA1234567890",
  "event": "incoming_call",
  "from_number": "+1234567890",
  "to_number": "+0987654321"
}
```

## 🚀 Despliegue en Producción

### 1. Servidor Web (Nginx/Apache)
```nginx
# Nginx configuration
server {
    listen 80;
    server_name tu-dominio.com;
    
    location /webhook/twilio/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. SSL/TLS
```bash
# Certbot para Let's Encrypt
sudo certbot --nginx -d tu-dominio.com
```

### 3. Firewall
```bash
# Abrir puerto 80 y 443
sudo ufw allow 80
sudo ufw allow 443
```

## 📞 Soporte

### Contacto del Equipo
- **Desarrollador**: [Tu Nombre]
- **Email**: [tu-email@empresa.com]
- **Slack**: #canal-rasa-twilio

### Recursos Adicionales
- [Documentación de Twilio Voice](https://www.twilio.com/docs/voice)
- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de Rasa Pro](https://rasa.com/docs/pro/)

---

**⚠️ Nota**: Este servidor es independiente del proyecto principal de Rasa. Se puede ejecutar en paralelo o en un servidor separado según las necesidades de infraestructura.
