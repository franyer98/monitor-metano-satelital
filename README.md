# 🛰️ Monitor de Metano Satelital — Campo Rubiales

Dashboard que cruza **datos satelitales públicos y gratuitos de metano
atmosférico** (Sentinel-5P / TROPOMI, ESA-Copernicus) sobre el área de Campo
Rubiales, como señal complementaria a las inspecciones OGI en tierra.

## Por qué este proyecto es distinto

La mayoría de proyectos de portafolio con IA integran una API de LLM (chatbot,
extracción de texto). Este va por otro lado: **datos geoespaciales reales de
observación de la Tierra**, cruzados con contexto de dominio que solo alguien
que hace inspecciones OGI en campo sabría interpretar correctamente. No es
algo que "cualquier IA" pueda producir con un prompt — requiere acceso y
procesamiento real de datos satelitales.

Esto es, a pequeña escala, el mismo principio detrás de productos comerciales
como GHGSat o MethaneSAT: correlacionar detección remota (satélite) con
verificación en tierra.

## Arquitectura

```
Google Earth Engine (COPERNICUS/S5P/OFFL/L3_CH4)
        │  reducción espacial en servidores de Earth Engine
        ▼
FastAPI (/metano/serie) — caché en memoria de 6h
        ▼
Dashboard HTML + Chart.js — serie de tiempo de CH₄ regional
```

El dataset `COPERNICUS/S5P/OFFL/L3_CH4` se actualiza aproximadamente cada 2
días. Se calcula el promedio diario de metano sobre el bounding box de Campo
Rubiales (Puerto Gaitán, Meta) directamente en los servidores de Earth Engine
(no se descargan imágenes satelitales completas, solo el resultado agregado).

## Cómo obtener acceso a Google Earth Engine (gratuito)

Earth Engine es gratuito para uso no comercial/personal, pero requiere una
cuenta de servicio de Google Cloud. Pasos:

1. Regístrate en [Earth Engine](https://earthengine.google.com/signup) — puedes
   usar tu cuenta de Google personal.
2. Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/).
3. En ese proyecto, habilita la **Earth Engine API**
   (`console.cloud.google.com/apis/library/earthengine.googleapis.com`).
4. Crea una **cuenta de servicio** (`IAM & Admin → Service Accounts → Create`).
5. Genera una **clave JSON** para esa cuenta de servicio (`Keys → Add Key →
   JSON`) — se descarga un archivo `.json`.
6. En [code.earthengine.google.com/register](https://code.earthengine.google.com/register),
   registra el proyecto para uso de Earth Engine.
7. Copia el **contenido completo** del archivo `.json` descargado y pégalo
   como valor de la variable de entorno `EE_SERVICE_ACCOUNT_JSON` en Render.
8. Define también `EE_PROJECT_ID` con el ID del proyecto de Google Cloud.

## Roadmap (siguiente iteración)

- Cruzar la serie satelital con las fechas y ubicaciones de hallazgos reales
  de `reporte-emisiones-cpf` (histórico propio de inspecciones OGI), para ver
  si los picos regionales de metano coinciden con clusters donde se
  reportaron fugas — el verdadero valor diferencial del proyecto.
- Desagregar por sub-zonas del campo (CPF-1 vs CPF-2) en vez de un único
  promedio regional.
- Alertas automáticas (WhatsApp) cuando el promedio regional supere un umbral
  histórico.

## Stack

FastAPI · Google Earth Engine Python API · Chart.js · Docker · Render

---

⚠️ Este dashboard usa un **promedio regional** de metano atmosférico, no
mediciones puntuales por cluster ni verificación de fuente — un pico no
confirma una fuga específica en un punto exacto. Es una señal complementaria
a las inspecciones OGI en tierra, no un reemplazo.
