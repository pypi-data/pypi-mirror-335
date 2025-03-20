# StellarPolAnalyzer

**StellarPolAnalyzer** es una librería de Python diseñada para el análisis de imágenes polarimétricas en astronomía. Esta herramienta detecta automáticamente las estrellas en imágenes FITS, identifica las parejas de estrellas (correspondientes a las dos proyecciones polarimétricas de la misma fuente) y permite realizar análisis posteriores. La idea es que, mediante este paquete, cualquier usuario pueda instalarlo usando `pip install StellarPolAnalyzer` y utilizar los métodos para obtener la imagen con parejas, la lista de parejas y, posteriormente, aplicar nuevos métodos para calcular la polarimetría.

---

## Características

- **Detección de Estrellas:**  
  Utiliza `DAOStarFinder` para detectar estrellas en imágenes FITS, permitiendo ajustar parámetros como el FWHM y el multiplicador de umbral.
  
- **Identificación de Parejas de Estrellas:**  
  Emplea un algoritmo basado en `NearestNeighbors` para buscar vecinos dentro de un radio máximo y genera parejas candidatas, filtrándolas posteriormente por la moda de la distancia y el ángulo, con tolerancias ajustables.

- **Visualización de Resultados:**  
  Muestra la imagen con:
  - Puntos rojos que indican los centros de las estrellas.
  - Líneas que conectan las parejas identificadas.
  - Círculos diferenciados: azul para la estrella con menor valor en X (izquierda) y rojo para la que tiene mayor valor en X (derecha).
  - Una leyenda externa que indica:
    - Número total de estrellas detectadas.
    - Número de parejas finales.
    - Valor de la distancia dominante ± la tolerancia en distancia.
    - Valor del ángulo dominante ± la tolerancia en ángulo.

- **Interfaz Gráfica Interactiva (GUI):**  
  Con Tkinter se permite al usuario ajustar parámetros críticos:
  - *Detección de estrellas:* FWHM y Threshold.
  - *Parámetros de búsqueda:* tol_distance (px), tol_angle (°) y max_distance (px).  
  La GUI interactiva facilita la ejecución del pipeline sin necesidad de modificar el código.

- **Modularidad y Extensibilidad:**  
  El paquete se organiza en dos partes:
  - **API (Lógica):** Funciones de procesamiento y análisis (detección, emparejamiento, filtrado y visualización).
  - **Interfaz Gráfica:** Permite ejecutar el pipeline con parámetros ajustables.

- **Fácil Integración:**  
  La librería se puede instalar vía `pip install StellarPolAnalyzer` y utilizarla en proyectos de análisis de polarimetría, o como base para el desarrollo de aplicaciones más complejas (por ejemplo, para calcular parámetros de polarimetría completos a partir de 4 imágenes).

---

## Instalación

Puedes instalar **StellarPolAnalyzer** desde PyPI con el siguiente comando:

```bash
pip install StellarPolAnalyzer
