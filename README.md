# mantenimiento-predictivo-pipeline
Pipeline ETL en Python para procesamiento de telemetría industrial, almacenamiento relacional en SQL Server y analítica interactiva en Power BI.

```plaintext
PORTAFOLIO/
├── data/
│   ├── fact_device_metrics.csv
│   ├── dim_device.csv
|   └── predictive_maintenance_dataset.csv (Dataset crudo)
├── python/
│   └── Proyecto_predictive_maintenance.py
├── sql/
│   └── QUERY_ANALISIS.sql
├── dashboard/
│   └── Dashboard_Mantenimiento_Predictivo.pbix
├── images/
│   ├── portada_dashboard.png
│   ├── grafico_tendencia_falla.png
│   └── grafico_distribucion_vida.png
└── README.md
```

# Pipeline de Mantenimiento Predictivo: ETL, SQL Analytics y Dashboard de Control

Este proyecto implementa un pipeline de datos de extremo a extremo (End-to-End) para el monitoreo de salud de dispositivos industriales. El objetivo es identificar patrones de fallas mecánicas a través del análisis de telemetría, permitiendo a los equipos de mantenimiento tomar decisiones proactivas antes de que ocurra una avería.

## 📐 Arquitectura de la Solución
El flujo de los datos sigue la siguiente estructura:
**Datos Crudos (CSV)** ➡️ **Limpieza y ETL (Python & Pandas)** ➡️ **Modelado Relacional (SQL Server)** ➡️ **Dashboard Interactivo (Power BI)**

---

## 📁 Estructura del Repositorio
*   `data/`: Datasets origen en formato CSV.
*   `python/`: Scripts de extracción, limpieza y generación de analítica visual estática.
*   `sql/`: Queries de creación de tablas y análisis avanzado de promedios móviles.
*   `dashboard/`: Archivo fuente `.pbix` de Power BI.
*   `images/`: Capturas y recursos gráficos utilizados en esta documentación.

---

## 🛠️ Fase 1: ETL & Limpieza de Datos (Python)
Utilizando Python y la librería `pandas`, se procesó un dataset de telemetría de dispositivos con más de 100,000 registros para:
1.  **Manejo de nulos y tipos de datos:** Corrección de formatos de fecha y casteo de variables binarias (`failure`).
2.  **Ingeniería de Características (Feature Engineering):** Creación de la métrica `device_lifespan_days` para calcular los días acumulados de operación de cada dispositivo antes de fallar.
3.  **Capa Semántica:** Separación del set de datos en un modelo relacional de **Tabla de Hechos** (`fact_device_metrics`) y **Tabla de Dimensión** (`dim_device`).

---

## 🗄️ Fase 2: Modelado de Datos y SQL Analytics
Los datos fueron cargados en un motor relacional **SQL Server**. Para optimizar las alertas preventivas en la planta, se implementó un **Promedio Móvil de 3 días** sobre la métrica de ruido (`metric2`) utilizando funciones de ventana analíticas:

```sql
SELECT 
    date,
    device_id,
    metric2 AS valor_diario,
    AVG(metric2) OVER(
        PARTITION BY device_id
        ORDER BY date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS promedio_movil_3_dias
FROM fact_device_metrics
WHERE device_id = 'S1F0RRB1';
```
---

### Gráfico de Tendencia de Fallas (Generado en Python)
Este análisis nos permitió comprobar que métricas como `metric2` experimentan picos exponenciales de ruido justo antes de registrarse una falla.

![Análisis de Tendencia](images/grafico_tendencia_falla.png)

---

## 📊 Fase 3: Dashboard Ejecutivo (Power BI)
Se diseñó un cuadro de mando interactivo orientado a los gerentes de planta para el monitoreo de KPIs en tiempo real:

![Portada Dashboard Power BI](images/portada_dashboard.png)

### Principales Hallazgos del Negocio (Insights):
*   **Volumen de Monitoreo:** Se analizó un parque total de **1,169 dispositivos únicos**, registrando históricamente un total de **106 fallas críticas**.
*   **Patrón de Comportamiento:** Al promediar los datos de telemetría, se descubrió que los sensores de ruido actúan como indicadores tempranos de falla, permitiendo un margen de acción preventiva de 1 a 2 días antes de la ruptura total del dispositivo.

---
