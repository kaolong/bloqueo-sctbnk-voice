#!/usr/bin/env python3
"""
Script para debuggear el servidor Twilio y la identificación de clientes
"""

import os
import pymysql
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def debug_customer_lookup():
    """Debug de la búsqueda de clientes"""
    print("🔍 Debug de búsqueda de clientes...")
    
    # Simular exactamente lo que hace el servidor
    phone_number = "+56982221070"
    
    # Configuración de base de datos
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'mauro'),
        'password': os.getenv('DB_PASSWORD', 'santiago01'),
        'database': os.getenv('DB_NAME', 'bank'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    print(f"📱 Número de teléfono: {phone_number}")
    print(f"📊 Configuración BD: {db_config['host']}:{db_config['database']}")
    
    try:
        # Conectar a la base de datos
        connection = pymysql.connect(**db_config)
        print("✅ Conexión exitosa a la base de datos")
        
        with connection.cursor() as cursor:
            # Normalizar el número de teléfono (remover + si existe)
            normalized_phone = phone_number.replace('+', '') if phone_number else ''
            print(f"🔍 Teléfono normalizado: {normalized_phone}")
            
            # Buscar cliente por número de teléfono (con y sin +)
            sql = """
            SELECT id, rut, nombre, nombre_completo, telefono, fecha_creacion
            FROM customers 
            WHERE telefono = %s OR telefono = %s
            """
            
            print(f"🔍 SQL: {sql}")
            print(f"🔍 Parámetros: {phone_number}, {normalized_phone}")
            
            # Probar tanto con el número original como con el normalizado
            cursor.execute(sql, (phone_number, normalized_phone))
            customer = cursor.fetchone()
            
            if customer:
                print(f"✅ Cliente encontrado: {customer['nombre_completo']} (ID: {customer['id']})")
                print(f"📱 Teléfono en BD: {customer['telefono']}, Buscado: {phone_number}")
                
                # Simular la generación del saludo
                from datetime import datetime
                current_hour = datetime.now().hour
                
                if 5 <= current_hour < 12:
                    greeting = "¡Buenos días!"
                elif 12 <= current_hour < 19:
                    greeting = "¡Buenas tardes!"
                else:
                    greeting = "¡Buenas noches!"
                
                personalized_greeting = f"{greeting} {customer['nombre']}, soy el asistente de Scotiabank, ¿en qué puedo ayudarte?"
                print(f"🎯 Saludo generado: {personalized_greeting}")
                
            else:
                print(f"❌ Cliente no encontrado")
                
                # Ver qué hay en la tabla
                cursor.execute("SELECT telefono FROM customers LIMIT 5")
                phones = cursor.fetchall()
                print(f"📱 Teléfonos en la tabla: {[p['telefono'] for p in phones]}")
        
        connection.close()
        print("\n🔌 Conexión cerrada")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_customer_lookup()
