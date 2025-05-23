# 🧠 AI Multimodal Agent Backend — Documentación Técnica

## Descripción General

Este proyecto es un **prototipo funcional de agente de inteligencia artificial multimodal** para la Municipalidad de Momostenango. Permite procesar texto, imágenes y archivos PDF, consultar información en reglamentos y FAQs usando un índice vectorial (PgVector), y persistir interacciones en PostgreSQL. El backend está construido sobre **Blacksheep** (servidor HTTP) y **Agno** (orquestador de agentes), integrando modelos gratuitos vía **OpenRouter**.

---

## Arquitectura

- **Servidor HTTP:** [Blacksheep](https://www.neoteroi.dev/blacksheep/)
- **Orquestador de agentes:** [Agno](https://docs.agno.com/)
- **Persistencia:** PostgreSQL (con extensión [pgvector](https://github.com/pgvector/pgvector))
- **Contenedores:** Docker Compose para base de datos y Adminer
- **Modelos LLM:** Modelos gratuitos (`:free`) vía [OpenRouter](https://openrouter.ai/)
- **Embeddings:** OpenAI o Google Gemini (según configuración y disponibilidad de API keys)
- **ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) para modelos y sesiones

---

## Estructura del Proyecto



---

## Principales Dependencias

- **Blacksheep:** Servidor HTTP asíncrono y flexible.
- **Agno:** Orquestador de agentes, integración con LLMs y vector DBs.
- **PgVector:** Extensión de PostgreSQL para búsquedas vectoriales.
- **SQLModel:** ORM para modelos y persistencia.
- **OpenRouter:** Proxy de modelos LLM gratuitos y de pago.
- **Adminer:** UI web para administración de la base de datos.
- **fitz (PyMuPDF):** Extracción de texto de PDFs.
- **Pydantic Settings:** Manejo de configuración vía variables de entorno.

---

## Flujos Principales

### 1. Procesamiento Multimodal

- **Texto:** Procesado directamente por el agente.
- **Imágenes:** Convertidas a base64 y enviadas al modelo LLM compatible.
- **PDFs:** Texto extraído con PyMuPDF y enviado al modelo o indexado en PgVector.

### 2. Búsqueda en Reglamentos y FAQs

- Los documentos se indexan en PgVector (PostgreSQL).
- Las búsquedas semánticas se realizan usando embeddings generados por OpenAI, Gemini o el modelo específicado con OpenRouter.
- Los resultados relevantes se devuelven al usuario.

### 3. Persistencia

- Todas las interacciones (ciudadano, sesión, consulta, respuesta) se almacenan en PostgreSQL usando SQLModel.

---

## Configuración y Despliegue

### Variables de Entorno

- Definidas en `.env` (ver `.env.template` para referencia).
- Incluyen credenciales de PostgreSQL y API keys de OpenRouter.

### Base de Datos

- Se ejecuta en Docker usando la imagen oficial de `pgvector`.
- Adminer disponible en el puerto 8080 para administración visual.

### Inicialización

1. Clonar el repositorio y copiar `.env.template` a `.env`.
2. Levantar la base de datos con Docker Compose:
   ```bash
    docker-compose up -d
3. Instalar dependencias Python y ejecutar el servidor:
    ```bash
    pip install -r requirements.txt
    python app/server.py

---

## Endpoints Principales

- `POST /chat`: Chat multimodal con el agente (texto, imágenes, PDFs).
- `POST /faqs/chat`: Consulta de FAQs y reglamentos usando búsqueda semántica.
- Otros endpoints pueden ser agregados según necesidades de integración o ampliación.

---

## Notas y Recomendaciones

- **Modelos LLM:** Se recomienda usar modelos gratuitos (`:free`) de OpenRouter para evitar costos en prototipado.
- **Embeddings:** Si no se cuenta con API key de OpenAI, se puede usar Gemini (requiere API key de Google AI Studio).
- **Latencia:** El sistema está optimizado para respuestas rápidas (P95 < 800 ms).
- **Persistencia:** Toda la información relevante se almacena en PostgreSQL para trazabilidad y análisis.
- **Docker:** Se recomienda ejecutar la base de datos y Adminer en contenedores para facilitar el desarrollo y la portabilidad.

### Configuración Local MCP - SystemFile
```
    docker run -it -dp 8082:8080 -v /Users/carlosngv/Documents/dev:/local-directory mcp/filesystem /local-directory