# Barcelona Bike Station Tracker

Aplicación web interactiva desarrollada en Python y con ayuda de Streamlit que permite a los usuarios encontrar la estación de Bicing (bicicletas públicas de Barcelona) más cercana con disponibilidad en tiempo real.

## Características Principales

- **Datos en Tiempo Real:** Se conecta directamente a la API oficial de Bicing (GBFS) para mostrar el estado actual de todas las estaciones de la ciudad.
- **Filtrado por Tipos:** Permite a los usuarios buscar específicamente bicicletas mecánicas (FIT/ICONIC) o eléctricas (BOOST/EFIT).
- **Cálculo de Rutas Integrado:** Utiliza la API de *Open Source Routing Machine (OSRM)* para dibujar en el mapa la ruta exacta desde la ubicación indicada hasta la estación más cercana.
- **Múltiples Medios de Transporte:** Calcula el tiempo estimado de llegada y la ruta dependiendo de si vas andando, en bicicleta o en coche.
- **Alertas por Disponibilidad:** El sistema avisa al usuario de forma dinámica si la estación de destino se está quedando sin bicicletas (3 o menos disponibles).

## Tecnologías Utilizadas

- **Frontend/Backend:** [Streamlit](https://streamlit.io/)
- **Procesamiento de Datos:** [Pandas](https://pandas.pydata.org/)
- **Mapas y Visualización:** [Folium](https://python-visualization.github.io/folium/)
- **Geolocalización:** [Geopy](https://geopy.readthedocs.io/)
- **APIs Externas:** OSRM (OpenStreetMap) y GBFS Bicing Barcelona.

## Instalación del Entorno

Para configurar el entorno de desarrollo, puedes hacerlo utilizando Conda o el gestor de paquetes estándar de Python (pip). 

Antes de instalar nada, clona el repositorio y entra en la carpeta del proyecto:
```bash
git clone https://github.com/eguijim/bike-tracker.git
cd bike-tracker
```
### Opción A: Usar Conda Environment
Si decides utilizar Anaconda o Miniconda, puedes recreaer el entorno exacto usado en el repositorio usando el archivo *environment.yml*.

*Nota: Este entorno fue exportado desde un equipo con Windows, por lo que podría generar conflictos de dependencias en macOS o Linux. Si es tu caso, te recomiendo utilizar la opción B, usando el archivo requirements.txt*

1. Crea el entorno:
```bash
conda env create -f environment.yml
```
2. Activa el entorno:
```bash
conda activate biketracker_streamlit
```

### Opción B: Usando Pip y Virtualenv de Python
Si en vez de Anaconda prefieres usar un entorno virtual estándar de Python, necesitarás el archivo llamado *requirements.txt*.

1. Crea y activa el entorno virtual:
   
    * **Windows**:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
    * **macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

## Ejecución de la Aplicación
Una vez hayas activado el entorno, ya puedes iniciar y utilizar la aplicación con Streamlit usando el siguiente comando:
```bash
streamlit run app.py
```
*Nota: La aplicación se abrirá automáticamente en tu navegador en http://localhost:8501.*
