import pandas as pd
import numpy as np

RUTA_ARCHIVO = r'C:\Users\madam\PORTAFOLIO\predictive_maintenance_dataset.csv'
#------------------------------------------------------------------------------------------------------
#    MUESTREO Y RECONOCIMIENTO DE DATOS
#------------------------------------------------------------------------------------------------------
#  Carga del set de datos
df = pd.read_csv(RUTA_ARCHIVO, nrows = 20)

# 1. Ver nombres de columnas y tipos de datos iniciales
print("--- Estructura y Tipos de Datos (Muestra) ---")
print(df.dtypes)

#  Ver las primeras filas para entender el formato de los datos
print("\n--- Vista Previa de Datos ---")
print(df.head())

# Solo cargamos a memoria las columnas que nos interesan para el análisis de IDs
columnas_interes = ['date', 'device', 'failure']

df_identificadores = pd.read_csv(RUTA_ARCHIVO, usecols=columnas_interes, nrows = 20)

print("--- DataFrame optimizado (Solo columnas seleccionadas) ---")
print(df_identificadores.info())
print(df_identificadores)

#------------------------------------------------------------------------------------------------------
#    MUESTREO Y RECONOCIMIENTO DE DATOS
#------------------------------------------------------------------------------------------------------

# Cargamos archivo completo
df_clean = pd.read_csv(RUTA_ARCHIVO)

# Convertimos tipo de datos
df_clean['date'] = pd.to_datetime(df_clean['date'])

# Eliminamos redundancia
df_clean.drop(columns = ['metric8'], inplace =True)

#eliminar duplicados lógicos

df_clean = df_clean.sort_values(by=['date', 'device', 'failure'])
registros_antes = df_clean.shape[0]
df_clean.drop_duplicates(subset = ['date', 'device'], keep ='last', inplace=True)
registros_despues = df_clean.shape[0]

print(f"-> Conversión de fechas completada exitosamente.")
print(f"-> Columna 'metric8' eliminada para optimizar almacenamiento.")
print(f"-> Duplicados lógicos eliminados: Se removieron {registros_antes - registros_despues} filas.")

#------------------------------------------------------------------------------------------------------
#    INGENIERÍA DE CARACTERÍSTICAS (MÉTRICAS CLAVE PARA EL PORTAFOLIO)
#------------------------------------------------------------------------------------------------------
print("\n--- Calculando Métricas e Ingeniería de Características ---")

# Métrica 1: Días en operación (Lifespan) de cada dispositivo
# Restamos la fecha actual de cada registro menos la primera fecha en que apareció ese dispositivo específico
df_clean['device_lifespan_days'] = df_clean.groupby('device')['date'].transform(lambda x: (x - x.min()).dt.days)

print("-> Métrica 'device_lifespan_days' generada correctamente.")
print("\n--- RESUMEN DEL DATAFRAME LIMPIO Y LISTO PARA SQL ---")
print(df_clean.info())

#------------------------------------------------------------------------------------------------------
#    MODELADO RELACIONAL Y EXPORTACIÓN (PREPARACIÓN PARA SQL)
#------------------------------------------------------------------------------------------------------
print("\n--- Generando Modelo de Datos Relacional (Esquema Estrella) ---")

# 1. Crear Tabla Dimensión: dim_device
# Agrupamos por dispositivo para extraer su información única y estática
dim_device = df_clean.groupby('device').agg(
    fecha_alta=('date', 'min'),
    dias_totales_operacion=('device_lifespan_days', 'max'),
    fallo_historico=('failure', 'max') # Si falló al menos una vez, será 1
).reset_index()

# Renombramos columnas para estandarizar el diseño de base de datos
dim_device.rename(columns={'device': 'device_id'}, inplace=True)

# 2. Crear Tabla de Hechos: fact_device_metrics
# Seleccionamos las series de tiempo diarias de telemetría
columnas_fact = ['date', 'device', 'failure', 'metric1', 'metric2', 'metric3', 'metric4', 'metric5', 'metric6', 'metric7', 'metric9', 'device_lifespan_days']
fact_device_metrics = df_clean[columnas_fact].copy()
fact_device_metrics.rename(columns={'device': 'device_id'}, inplace=True)

print(f"-> Dimensión 'dim_device' creada con {dim_device.shape[0]} dispositivos únicos.")
print(f"-> Tabla de hechos 'fact_device_metrics' creada con {fact_device_metrics.shape[0]} registros cronológicos.")

# 3. Exportación a archivos preparados para la carga en BD
# Los guardaremos como CSV limpios en tu misma carpeta para que sea fácil importarlos
dim_device.to_csv(r'C:\Users\madam\PORTAFOLIO\dim_device.csv', index=False)
fact_device_metrics.to_csv(r'C:\Users\madam\PORTAFOLIO\fact_device_metrics.csv', index=False)

print("\n=====================================================================")
print("¡PROCESO FINALIZADO! Archivos 'dim_device.csv' y 'fact_device_metrics.csv' guardados.")
print("=====================================================================")

#------------------------------------------------------------------------------------------------------
#    CARGA DE DATOS A SQL SERVER
#------------------------------------------------------------------------------------------------------

from sqlalchemy import create_engine
import urllib

print("\n--- INICIANDO CARGA A SQL SERVER ---")

# Configurar la cadena de conexión usando Windows Authentication
# OJO: Remplaza con el nombre exacto de tu servidor de la captura
server_name = r'DESKTOP-7LLKM1B\SQLEXPRESS'
database_name = 'MantenimientoPredictivo'

params = urllib.parse.quote_plus(
    f'Driver={{ODBC Driver 17 for SQL Server}};'
    f'Server={server_name};'
    f'Database={database_name};'
    f'Trusted_Connection=yes;'
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# Inyectar DataFrames directamente a SQL
try:
    print("Cargando dim_device...")
    dim_device.to_sql('dim_device', con=engine, if_exists='append', index=False)
    
    print("Cargando fact_device_metrics...")
    # Quitamos el fact_id porque SQL Server lo genera automáticamente (IDENTITY)
    fact_device_metrics.to_sql('fact_device_metrics', con=engine, if_exists='append', index=False)
    
    print("¡CARGA EXITOSA! Los datos ya están en SQL Server.")
except Exception as e:
    print(f"Error en la carga: {e}")
    
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de estilos visuales profesionales
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [10, 6]

# 1. Cargar la tabla de hechos que guardamos en disco
RUTA_FACT = r'C:\Users\madam\PORTAFOLIO\fact_device_metrics.csv'
df_fact = pd.read_csv(RUTA_FACT)
df_fact['date'] = pd.to_datetime(df_fact['date'])

print("\n--- Generando Gráficos de Python para el Portafolio ---")

# ==========================================
# GRÁFICO 1: Comportamiento previo al fallo (Métricas Críticas)
# ==========================================
plt.figure()
# Filtramos un dispositivo de ejemplo que sepamos que falló para ver su historia
dispositivo_ejemplo = 'S1F0RRB1' 
df_dispositivo = df_fact[df_fact['device_id'] == dispositivo_ejemplo].sort_values('date')

plt.plot(df_dispositivo['date'], df_dispositivo['metric2'], label='Valor Diario Metric2', marker='o', color='royalblue')
plt.plot(df_dispositivo['date'], df_dispositivo['device_lifespan_days'], label='Días de Operación', linestyle='--', color='orange')

plt.title(f'Análisis de Tendencia Pre-Falla: Dispositivo {dispositivo_ejemplo}', fontsize=14, fontweight='bold')
plt.xlabel('Fecha')
plt.ylabel('Escala de Métricas')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

# Guardamos el gráfico directo en tu carpeta para el README de GitHub
plt.savefig(r'C:\Users\madam\PORTAFOLIO\grafico_tendencia_falla.png', dpi=300)
print("-> Gráfico 'grafico_tendencia_falla.png' guardado exitosamente.")

# ==========================================
# GRÁFICO 2: Distribución del Ciclo de Vida de las Máquinas
# ==========================================
plt.figure()
sns.histplot(data=df_fact[df_fact['failure'] == 1], x='device_lifespan_days', bins=15, kde=True, color='crimson')
plt.title('Distribución de Días en Operación al Momento de la Falla', fontsize=14, fontweight='bold')
plt.xlabel('Días transcurridos hasta fallar')
plt.ylabel('Frecuencia / Cantidad de Dispositivos')
plt.tight_layout()

plt.savefig(r'C:\Users\madam\PORTAFOLIO\grafico_distribucion_vida.png', dpi=300)
print("-> Gráfico 'grafico_distribucion_vida.png' guardado exitosamente.")