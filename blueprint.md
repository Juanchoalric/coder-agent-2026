# Blueprint Arquitectónico: Célula Híbrida de Análisis y Visualización de Ventas

### 1. Definición Estratégica del Caso

* **Descripción del proceso:** Automatización del ciclo de reporte trimestral de ventas. El proceso abarca la ingesta de múltiples fuentes de datos estructurados (archivos Excel de transacciones e inventario), su consolidación, y la generación de un dashboard interactivo en HTML/JS.
* **Problema actual o ineficiencia identificada:** Analistas y Project Managers dedican horas de trabajo manual a la consolidación de tablas cruzadas (ej. buscar correspondencias de `ID_Producto`), limpieza de datos y configuración repetitiva de gráficos, lo que genera cuellos de botella operativos y propensión a errores en métricas clave.
* **Objetivo de automatización:** Desplegar un flujo donde un agente digital consolide los datos y programe el frontend analítico de forma autónoma, reduciendo el tiempo de generación del reporte de varias horas a minutos.
* **Justificación de por qué el enfoque híbrido es adecuado:** La automatización total es riesgosa en contextos financieros o de reporte a clientes. La célula híbrida permite que el agente realice el "trabajo pesado" (data wrangling con código y maquetación web), mientras el humano interviene exclusivamente en la validación de la lógica de negocio y la interpretación de los insights antes de la presentación final.

### 2. Marco Persona – Tarea – Contexto

* **Persona (Agente Analista/Desarrollador):**
* **Rol:** Data & Frontend Engineer Digital.
* **Capacidades técnicas:** Ejecución de scripts para manipulación de datos, generación de código estructurado en HTML, CSS (Tailwind) y JavaScript (Chart.js, DataTables).
* **Límites de actuación:** Operación en modo de "solo lectura" sobre los Excels originales. Incapacidad para publicar o exponer el dashboard a servidores públicos sin un *commit* o aprobación humana.
* **Nivel de autonomía:** Medio-Alto para la escritura de código y cruce de datos; nulo para la toma de decisiones estratégicas de negocio.


* **Tarea:**
* Extraer, limpiar y cruzar datos de `Ventas.xlsx` e `Inventario.xlsx` (ej. consolidar volumen de ventas por categoría y región).
* Generar un archivo HTML de un solo bloque que integre librerías visuales para renderizar la información procesada.


* **Contexto:**
* **Sistemas:** Entorno de ejecución local (ej. terminal en arquitecturas basadas en M1) utilizando entornos virtuales y gestores de paquetes como npm para posibles despliegues en frameworks más complejos (ej. Next.js) si el proyecto escala.
* **Restricciones:** Estricto formato de salida en los cálculos (ej. el agente debe retornar valores numéricos limpios y exactos, excluyendo identificadores de índice u outputs ruidosos como la columna `N` típica de DataFrames).
* **Riesgos:** Errores de tipado (DataTypes) al leer el Excel (ej. que lea precios como *strings*), lo que rompería las lógicas de JavaScript en el HTML resultante.



### 3. Diseño del Agentic Workflow

1. **Estado 1: Ingesta (Trigger).** El usuario deposita los Excels en el directorio de trabajo y ejecuta el *prompt* de inicio.
2. **Estado 2: Exploración de Datos (Agente).** El agente lee los esquemas de los Excels. Si detecta anomalías (ej. columnas faltantes), pasa al estado de *Corte*.
3. **Estado 3: Transformación (Agente).** Ejecución de scripts subyacentes para agrupar ventas por fecha y categoría.
4. **Estado 4: Generación de UI (Agente).** Redacción del código HTML/Tailwind e inyección del JSON de datos procesados dentro de la configuración de Chart.js.
5. **Punto de Iteración:** El sistema ejecuta un *linter* sobre el código generado. Si hay errores de sintaxis en el JS, el agente refactoriza automáticamente.
6. **Estado 5: Intervención Humana (Human-in-the-loop).** El dashboard se renderiza en un servidor local. El analista o Project Manager revisa la visualización.
7. **Transición Final:** Si el humano aprueba, el archivo queda listo para empaquetarse; si requiere cambios ("cambia este gráfico de barras a líneas"), el flujo regresa al Estado 4.

### 4. Selección y Justificación Tecnológica

* **Procesamiento de Datos: Python + Pandas/NumPy.** Se elige por su absoluta precisión matemática y capacidad para manejar broadcasting. Los LLM puros suelen alucinar en operaciones aritméticas complejas; delegar la consolidación a Pandas garantiza exactitud.
* **Generador de Código (LLM): Modelos multimodales avanzados (ej. deepseek-v4-flash).** Elegidos por su superioridad en la comprensión de contextos largos y su capacidad para escribir código de frontend (HTML/JS/CSS) altamente funcional y responsivo sin necesidad de múltiples iteraciones.
* **Frontend Stack: HTML Vanilla / CDN (Tailwind, Chart.js).** Se elige por portabilidad. Permite generar un único archivo que cualquier *stakeholder* puede abrir en su navegador, reduciendo la fricción respecto a soluciones más pesadas, aunque fácilmente migrable a componentes de React/Next.js en el futuro.

### 5. Guardrails y Control de Riesgo

* **Validaciones automáticas:**
* *Type checking* previo: Verificar que las columnas de "Total (USD)" no contengan valores nulos (NaN) o texto.
* *Sanitization:* Limpiar caracteres especiales de las columnas antes de inyectarlas en el código JavaScript para evitar errores de renderizado.


* **Límites de autonomía:** El agente opera en un entorno local aislado (sandbox). No tiene acceso a internet para subir datos a APIs de terceros ajenas a las librerías CDN especificadas.
* **Protocolos de escalamiento:** Si el agente falla en el cruce de datos (por ejemplo, si los IDs de transacción de los dos Excels no coinciden en un 90%), se detiene el procesamiento y se levanta una alerta detallando la discrepancia al usuario.
* **Auditoría:** Cada ejecución guarda un archivo temporal (ej. `data_log.csv`) con el paso intermedio de los datos procesados antes de incrustarlos en el HTML, para facilitar la revisión del consultor.

### 6. KPIs Operativos y Métricas

* **Latencia esperada:** < 60 segundos desde la carga de los Excels hasta la generación del archivo HTML.
* **Tasa de éxito objetivo:** 95% de *first-pass yield* (el HTML se renderiza sin errores en la consola del navegador en el primer intento).
* **Costo por tarea:** Reducción del costo operativo de analista en un 80% (medido en horas-hombre por reporte trimestral).
* **Ratio de intervención humana:** El humano solo debe invertir el 10% del tiempo total del ciclo (enfocado en QA y ajustes de formato) frente al 100% del modelo anterior.
* **Acciones correctivas:** Si la tasa de éxito cae por debajo del 80% (debido a actualizaciones de librerías o cambios en el formato del Excel), se detiene la ejecución autónoma y se refactoriza el *prompt* base del agente para endurecer la validación de entrada.

### 7. Roadmap de Implementación

* **Fase 1: Diagnóstico.** Mapeo exacto de las columnas que el equipo de proyectos utiliza habitualmente y definición de la paleta de colores corporativa para el dashboard.
* **Fase 2: Diseño y Arquitectura.** Creación del repositorio y configuración del entorno local. Establecimiento de los scripts de Python para ETL.
* **Fase 3: Desarrollo.** Integración del LLM para automatizar la inyección de datos transformados en el *template* dinámico de HTML y Chart.js.
* **Fase 4: Piloto.** Pruebas en *shadow mode* con un equipo reducido de analistas procesando Excels de meses anteriores para comparar la precisión del output generado por el agente vs. el dashboard histórico.
* **Fase 5: Despliegue Controlado y Gestión del Cambio.** Capacitar a los analistas sobre cómo "hablar" con el agente para pedir modificaciones al dashboard (ej. cambiar filtros) en lugar de hacerlo manualmente. Mitigar el riesgo de rechazo demostrando que el agente asume el trabajo tedioso, elevando al humano a un rol de auditor de negocio.