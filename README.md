# Ernesto Lomar - Proyecto: Visualizador de Imágenes y Análisis 3D

Este proyecto consiste en una aplicación desarrollada en Python utilizando PyQt5 y matplotlib para la visualización de imágenes, así como para el análisis y representación en 3D de datos obtenidos a partir de estas imágenes.

## Características principales

- **Visualización de imágenes:** Permite cargar imágenes en formatos comunes como JPG, PNG, BMP y GIF, y proporciona una interfaz intuitiva para previsualizarlas.

- **Análisis de imágenes:** Facilita el análisis de las imágenes cargadas, permitiendo la aplicación de filtros, ajustes y extracción de datos.

- **Representación en 3D:** Utilizando los datos extraídos de las imágenes, genera representaciones tridimensionales para un análisis más detallado.

## Línea cronológica

- **v2.0.0:**
  - Se añadió la función goldstein_unwrap al procesamiento.
  - Se añadió la función phase_to_height al procesamiento.
  - Se añadió la función takeda_phase_unwrap al procesamiento.
  - Se remodelo la interfaz gráfica de una manera mas intuitiva.
  - Ahora se pueden insertar las imágenes sin importar el nombre que tengan.
  - Se puede arrastras la imagen a su cuadro correspondiente para una mejor practica.
  - Se agregaron nuevos parámetros modificables por el usuario.
  - Se modificó el orden del umbral.
  - Se añadió la visualización de mas gráficos como "gradient of the wrapped phase, Laplacian of the gradient, 2D unwrapped phase using Fourier transform"
- **v1.1.1:**
  - Se añadió un umbral que puede ser ajustado para un rango específico de la coordenada Z.
  - Se implementó un botón denominado "Exportar .txt" en la interfaz gráfica, el cual permite exportar las coordenadas X, Y, y Z.
  - Se solucionó un error que impedía la actualización de la variable 'self.figura_3d', lo cual provocaba la superposición de los números en la gráfica 3D.
- **v1.0.0:**
  - Primera versión estable del visualizador de imágenes y análisis 3D.

## Instalación

Para utilizar este proyecto, sigue estos pasos:

1. Clona este repositorio en tu máquina local:

    ```bash
    git clone https://github.com/ErnestoLomar/Unwrapped_phase.git
    ```

2. Instala las dependencias necesarias:

    ```bash
    pip install PyQt5 matplotlib imageio pillow
    ```

3. Ejecuta la aplicación:

    ```bash
    python main.py
    ```

## Uso

Una vez que la aplicación esté en funcionamiento, puedes realizar las siguientes acciones:

- **Cargar imágenes:** Utiliza el botón "Cargar Imágenes" para seleccionar las imágenes que deseas analizar.

- **Previsualización:** Haz doble clic en una imagen de la lista para obtener una previsualización antes de realizar cualquier análisis.

- **Análisis de imágenes:** Aplica filtros y ajustes a las imágenes según tus necesidades.

- **Representación en 3D:** Utiliza los datos extraídos de las imágenes para generar visualizaciones en tres dimensiones.

- **Exportar resultados:** Guarda tus resultados y visualizaciones en archivos de imagen o texto para su posterior análisis.

## Contribución

Si deseas contribuir a este proyecto, sigue estos pasos:

1. Haz un fork del repositorio.

2. Realiza tus modificaciones en una rama aparte.

3. Envía un pull request con tus cambios para su revisión.

## Créditos

Este proyecto fue desarrollado por [Ernesto Lomar](https://github.com/ErnestoLomar) y diseñado por Dra. Angeles Mtz. Rmz.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para obtener más información.