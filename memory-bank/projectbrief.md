# Project Brief: Bloqueo de Tarjetas SCTBNK con Rasa Pro

## Descripción del Proyecto
Sistema de asistente virtual inteligente desarrollado en Rasa Pro 3.13.5 que utiliza la nueva arquitectura de **Flows y Patterns** con **CALM (Conversational AI with Language Models)**. El asistente permite a los clientes de SCTBNK bloquear sus tarjetas de crédito/débito mediante llamadas telefónicas, utilizando LLMs para interacciones más contextuales y agentivas, mientras mantiene el control total del negocio y la seguridad.

## Objetivos Principales
- **Automatizar el proceso de bloqueo de tarjetas** mediante asistente virtual
- **Reducir la carga del call center** manejando solicitudes de bloqueo automáticamente
- **Mejorar la experiencia del cliente** con atención 24/7 para bloqueos urgentes
- **Integrar con sistemas existentes** (Freshdesk) para gestión de tickets
- **Cumplir con estándares de seguridad bancaria** en el proceso de verificación

## Contexto de Negocio
### **Problema que Resuelve**
- **Alta demanda de bloqueos**: Los clientes necesitan bloquear tarjetas por pérdida, robo o sospecha de fraude
- **Sobrecarga del call center**: Los ejecutivos están saturados con solicitudes de bloqueo simples
- **Tiempo de respuesta**: Los clientes esperan largas colas para solicitudes urgentes
- **Costo operativo**: Procesamiento manual de bloqueos incrementa costos operativos

### **Beneficios Esperados**
- **Reducción del 70%** en llamadas de bloqueo al call center
- **Tiempo de respuesta** de menos de 2 minutos para bloqueos
- **Disponibilidad 24/7** para solicitudes urgentes
- **Ahorro estimado** de $50,000 USD anuales en costos operativos

## Alcance del Proyecto
### **Funcionalidades Core**
- **Asistente virtual inteligente** desarrollado en Rasa Pro 3.13.5 con CALM
- **Arquitectura de Flows y Patterns** para lógica de negocio escalable
- **Integración con Twilio** para llamadas telefónicas
- **LLMs para interacciones contextuales** y agentivas
- **Consulta a base de datos** para verificar tarjetas del cliente
- **Integración con Freshdesk API** para generación automática de tickets
- **Sistema de verificación** por últimos 4 dígitos de tarjeta
- **Seguridad integrada** contra alucinaciones e inyección de prompts

### **Flujo de Conversación**
1. **Saludo contextual** según horario del día
2. **Entendimiento de intención** de bloqueo de tarjeta
3. **Verificación de identidad** mediante últimos 4 dígitos
4. **Confirmación del cliente** para proceder con el bloqueo
5. **Generación automática** de ticket en Freshdesk
6. **Confirmación y cierre** de la conversación

### **Integraciones Técnicas**
- **Rasa Pro 3.13.5**: Framework moderno con CALM y Flows/Patterns
- **Twilio**: Servicio de telefonía y comunicación
- **Freshdesk**: Sistema de tickets y soporte
- **Base de Datos**: Consulta de información de tarjetas
- **API REST**: Comunicación entre sistemas
- **LLMs**: Modelos de lenguaje para interacciones avanzadas

## Stakeholders
### **Primarios**
- **Clientes de SCTBNK**: Usuarios finales que solicitan bloqueo de tarjetas
- **Ejecutivos del Call Center**: Personal que maneja casos complejos
- **Equipo de Seguridad**: Responsables de políticas de bloqueo

### **Secundarios**
- **Equipo de IT**: Mantenimiento y soporte técnico del sistema
- **Gerencia de Operaciones**: Supervisión de eficiencia operativa
- **Compliance**: Verificación de cumplimiento regulatorio
- **Auditoría**: Monitoreo de transacciones y tickets

## Requisitos Regulatorios
### **Compliance Bancario**
- **Verificación de identidad**: Confirmación mediante últimos 4 dígitos de tarjeta
- **Registro de transacciones**: Log completo de todas las interacciones
- **Auditoría**: Trazabilidad de cada solicitud de bloqueo
- **Seguridad**: Cumplimiento de estándares PCI DSS para datos de tarjetas

### **Regulaciones Aplicables**
- **Ley de Protección al Consumidor**: Transparencia en el proceso
- **Regulaciones Fintech**: Cumplimiento de estándares de tecnología financiera
- **Políticas Internas SCTBNK**: Estándares de seguridad corporativos

## Métricas de Éxito (KPIs)
### **Operacionales**
- **Tasa de resolución automática**: >85% de bloqueos sin intervención humana
- **Tiempo promedio de conversación**: <2 minutos por bloqueo
- **Precisión de entendimiento**: >95% de intenciones correctamente identificadas
- **Disponibilidad del sistema**: 99.9% uptime

### **De Negocio**
- **Reducción de costos**: 70% menos llamadas al call center
- **Satisfacción del cliente**: >4.5/5 en encuestas post-llamada
- **Volumen de transacciones**: 1000+ bloqueos mensuales
- **ROI del proyecto**: Retorno positivo en 6 meses

## Timeline del Proyecto
### **Fase 1: Desarrollo Core ✅ COMPLETADA (2 semanas)**
- **Semana 1**: Configuración de Rasa Pro 3.13.5 y desarrollo de intents
- **Semana 2**: Integración con Twilio, base de datos y Freshdesk API

### **Fase 2: Testing y Optimización ✅ COMPLETADA (1 semana)**
- **Semana 3**: Testing de conversaciones, refinamiento de NLU y optimización de performance

### **Fase 3: Documentación y Repositorio ✅ COMPLETADA (1 semana)**
- **Semana 4**: Documentación completa, diagramas del flujo conversacional y repositorio en GitHub

### **Fase 4: Despliegue y Monitoreo 🚧 EN PROGRESO**
- **Semana 5**: Despliegue en ambiente de producción
- **Semana 6**: Monitoreo inicial y ajustes post-despliegue

## Estado del Proyecto
- **Fase**: Implementación Completada y Funcionando
- **Prioridad**: Alta (Reducción de costos operativos críticos)
- **Complejidad**: Media (Tecnologías maduras, integraciones estándar)
- **Riesgo**: Bajo (Sistema funcionando, dependencias controladas)

## Dependencias del Proyecto
### **Técnicas**
- **Acceso a API de Freshdesk** con credenciales apropiadas
- **Base de datos de tarjetas** con información actualizada
- **Cuenta de Twilio** configurada y funcional
- **Licencia de Rasa Pro** activa

### **Organizacionales**
- **Aprobación de Seguridad** para integración con sistemas bancarios
- **Aprobación de Compliance** para proceso automatizado
- **Recursos de desarrollo** con experiencia en Rasa y APIs
- **Aprobación de presupuesto** para licencias y servicios

## Criterios de Aceptación
- **Funcionalidad**: Asistente debe manejar 100% de los casos de bloqueo estándar
- **Performance**: Respuesta en menos de 2 segundos para cada interacción
- **Precisión**: >95% de entendimiento correcto de intenciones del cliente
- **Integración**: 100% de tickets generados correctamente en Freshdesk
- **Seguridad**: Cumplimiento de todos los estándares de seguridad bancaria
