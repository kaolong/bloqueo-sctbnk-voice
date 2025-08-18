#!/usr/bin/env python3
"""
Script para configurar datos de prueba en la base de datos MariaDB
Permite probar la funcionalidad de identificación de clientes por número de teléfono
"""

import os
import pymysql
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_database_connection():
    """Crea una conexión a la base de datos MariaDB"""
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'mauro'),
            password=os.getenv('DB_PASSWORD', 'santiago01'),
            database=os.getenv('DB_NAME', 'bank'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def create_customers_table(connection):
    """Crea la tabla customers si no existe"""
    try:
        with connection.cursor() as cursor:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS `customers` (
                `id` VARCHAR(36) NOT NULL,
                `rut` VARCHAR(9) NOT NULL,
                `nombre` VARCHAR(64) NOT NULL,
                `nombre_completo` VARCHAR(128) NOT NULL,
                `telefono` VARCHAR(12) NOT NULL,
                `fecha_creacion` TIMESTAMP NOT NULL DEFAULT current_timestamp(),
                PRIMARY KEY (`id`),
                UNIQUE KEY `uk_telefono` (`telefono`),
                UNIQUE KEY `uk_rut` (`rut`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(create_table_sql)
            connection.commit()
            print("✅ Tabla customers creada/verificada exitosamente")
            return True
    except Exception as e:
        print(f"❌ Error creando tabla customers: {e}")
        return False

def insert_test_customers(connection):
    """Inserta clientes de prueba en la base de datos"""
    try:
        with connection.cursor() as cursor:
            # Datos de prueba - RUTs más cortos para ajustarse al campo VARCHAR(9)
            test_customers = [
                {
                    'id': str(uuid.uuid4()),
                    'rut': '12345678',
                    'nombre': 'Mauricio',
                    'nombre_completo': 'Mauricio Martínez González',
                    'telefono': '+56982221070'
                },
                {
                    'id': str(uuid.uuid4()),
                    'rut': '98765432',
                    'nombre': 'María',
                    'nombre_completo': 'María González Silva',
                    'telefono': '+56987654321'
                },
                {
                    'id': str(uuid.uuid4()),
                    'rut': '55556666',
                    'nombre': 'Carlos',
                    'nombre_completo': 'Carlos Silva Pérez',
                    'telefono': '+56955556666'
                }
            ]
            
            # Insertar cada cliente
            for customer in test_customers:
                insert_sql = """
                INSERT INTO customers (id, rut, nombre, nombre_completo, telefono, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                nombre = VALUES(nombre),
                nombre_completo = VALUES(nombre_completo),
                fecha_creacion = VALUES(fecha_creacion)
                """
                
                cursor.execute(insert_sql, (
                    customer['id'],
                    customer['rut'],
                    customer['nombre'],
                    customer['nombre_completo'],
                    customer['telefono'],
                    datetime.now()
                ))
                
                print(f"✅ Cliente insertado: {customer['nombre_completo']} - {customer['telefono']}")
            
            connection.commit()
            print(f"✅ {len(test_customers)} clientes de prueba insertados exitosamente")
            return True
            
    except Exception as e:
        print(f"❌ Error insertando clientes de prueba: {e}")
        return False

def list_customers(connection):
    """Lista todos los clientes en la base de datos"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM customers ORDER BY fecha_creacion DESC")
            customers = cursor.fetchall()
            
            if not customers:
                print("📭 No hay clientes en la base de datos")
                return
            
            print(f"\n📋 Clientes en la base de datos ({len(customers)}):")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            for customer in customers:
                print(f"🆔 ID: {customer['id']}")
                print(f"📱 Teléfono: {customer['telefono']}")
                print(f"👤 Nombre: {customer['nombre']}")
                print(f"📝 Nombre Completo: {customer['nombre_completo']}")
                print(f"🆔 RUT: {customer['rut']}")
                print(f"📅 Fecha Creación: {customer['fecha_creacion']}")
                print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                
    except Exception as e:
        print(f"❌ Error listando clientes: {e}")

def main():
    """Función principal"""
    print("🚀 Configurando datos de prueba para identificación de clientes")
    print("=" * 80)
    
    # Conectar a la base de datos
    connection = get_database_connection()
    if not connection:
        print("❌ No se pudo conectar a la base de datos. Verifica tu configuración en .env")
        return
    
    try:
        # Crear tabla si no existe
        if not create_customers_table(connection):
            return
        
        # Insertar clientes de prueba
        if not insert_test_customers(connection):
            return
        
        # Listar clientes para verificación
        list_customers(connection)
        
        print("\n🎯 Configuración completada exitosamente!")
        print("💡 Ahora puedes probar la identificación de clientes con:")
        print("   ./test_conversation.sh +56982221070  # Cliente Mauricio")
        print("   ./test_conversation.sh +56987654321  # Cliente María")
        print("   ./test_conversation.sh +56955556666  # Cliente Carlos")
        print("   ./test_conversation.sh +56912345678  # Cliente no encontrado")
        
    finally:
        connection.close()
        print("\n🔌 Conexión a la base de datos cerrada")

if __name__ == "__main__":
    main()
