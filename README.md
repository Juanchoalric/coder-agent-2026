# Business Dashboard - Ventas 2026

Dashboard interactivo de ventas generado automáticamente a partir de archivos Excel, con un pipeline ETL en Python (pandas) y un frontend single-file en HTML/Tailwind/Chart.js/DataTables.

Diseño: estilo minimalista Apple, con **modo claro/oscuro** (toggle en el header).

## Cómo funciona

1. **Ingesta**: el ETL lee `Usuarios_Ventas_2026.xlsx` y `Ventas_Productos_2026.xlsx` en modo read-only.
2. **Transformación**: valida tipos de datos, cruza por `ID Transacción` (umbral de 90% de match - si cae por debajo, el build falla con alerta), agrega métricas y genera `payload.json` como auditoría intermedia.
3. **Render**: genera un único archivo `dashboard.html` con el JSON embebido y las librerías frontend **vendored e inline** (Tailwind, Chart.js, jQuery, DataTables) - no necesita internet para abrirse.
4. **Aprobación humana**: el dashboard no se publica sin un `approve` explícito, atado a un fingerprint SHA-256 del artefacto.

Cada ejecución queda auditada en `data_log.csv` (run_id, match_rate, hashes, aprobaciones).

## Requisitos

- Python 3.13+
- Chrome/Chromium (solo para los tests E2E del navegador)

## Setup

```bash
# 1. Crear el entorno virtual
python3 -m venv .venv

# 2. Instalar dependencias
.venv/bin/pip install -r requirements.txt
```

## Generar el dashboard

```bash
# Build completo: lee los Excels, valida, agrega y genera dashboard.html
.venv/bin/python -m etl build
```

El primer build descarga las librerías vendored (una sola vez, a `etl/vendor/`). Los builds siguientes son **100% offline**.

Abrí `dashboard.html` en cualquier navegador.

## Flujo con aprobación humana

```bash
# 1. Generar el dashboard
.venv/bin/python -m etl build

# 2. Revisar el resultado (dashboard.html) y aprobar
.venv/bin/python -m etl approve --approver "Tu Nombre"

# 3. Publicar localmente a un destino (ej. una carpeta compartida)
.venv/bin/python -m etl release --dest ./out
```

`release` verifica que el `dashboard.html` actual sea exactamente el que se aprobó (recalcula el SHA-256) y bloquea ante cualquier desajuste o aprobación faltante.

## Tests

```bash
# Suite completa: unit + integración + E2E (offline, KPIs, DataTable)
.venv/bin/python -m unittest discover -s tests
```

El test E2E usa Chrome headless (via `playwright`). Si no está disponible, esos tests se saltean con gracia; el resto de la suite sigue corriendo.

## Estructura

```
etl/                  Paquete ETL (ingest, validate, sanitize, aggregate, audit, render, vendor, CLI)
tests/                Suite de tests (unit, integración, E2E)
openspec/             Especificaciones SDD (specs baseline + cambios archivados)
PRODUCT.md            Contexto de producto (impeccable)
DESIGN.md             Sistema de diseño (impeccable)
*.xlsx                Datos fuente (read-only)
```

## Artefactos generados (gitignored)

| Archivo | Qué es |
|---|---|
| `dashboard.html` | Dashboard single-file final |
| `payload.json` | Payload JSON intermedio (revisable) |
| `data_log.csv` | Auditoría de ejecuciones y aprobaciones |
| `etl/vendor/` | Librerías frontend pineadas (descarga única) |

## Datos

El dataset actual cubre **Ene-May 2026** (año parcial): 100 transacciones, USD 274,285 en ventas, 1,035 unidades. El dashboard etiqueta el periodo explícitamente y no hace afirmaciones de comparación anual (YoY).
