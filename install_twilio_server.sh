#!/bin/bash

# ========================================
# INSTALADOR DEL SERVIDOR TWILIO VOICE
# ========================================

echo "🚀 Instalando dependencias para el servidor Twilio Voice..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar si pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está instalado. Por favor instálalo primero."
    exit 1
fi

echo "✅ Python 3 y pip3 están disponibles"

# Crear entorno virtual (opcional)
read -p "¿Quieres crear un entorno virtual? (y/n): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "🔧 Creando entorno virtual..."
    python3 -m venv twilio_venv
    source twilio_venv/bin/activate
    echo "✅ Entorno virtual activado"
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip3 install -r twilio_requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencias instaladas correctamente"
else
    echo "❌ Error instalando dependencias"
    exit 1
fi

# Verificar instalación
echo "🔍 Verificando instalación..."
python3 -c "import flask, twilio, requests; print('✅ Todas las dependencias están disponibles')"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 ¡Instalación completada exitosamente!"
    echo ""
    echo "📋 Para ejecutar el servidor:"
    echo "   python3 twilio_voice_server.py"
    echo ""
    echo "📋 Para ejecutar en producción:"
    echo "   gunicorn -w 4 -b 0.0.0.0:5001 twilio_voice_server:app"
    echo ""
    echo "📋 Recuerda configurar las variables de entorno en twilio.env"
    echo ""
else
    echo "❌ Error verificando la instalación"
    exit 1
fi
