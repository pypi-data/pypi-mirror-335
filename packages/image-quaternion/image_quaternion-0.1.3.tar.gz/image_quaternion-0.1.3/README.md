<!-- -*- coding: iso-8859-1 -*- -->

# Image Quaternion Library

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**Image Quaternion Library** es una librería de Python que permite trabajar con imágenes en formato de cuaterniones. Proporciona herramientas para convertir imágenes RGB a cuaterniones, aplicar contrastes, comparar histogramas y calcular métricas de calidad de imagen.

## Instalación

Puedes instalar la librería directamente desde PyPI usando `pip`:

```bash
pip install image-quaternion
```

## Uso

### Conversión de RGB a Cuaterniones

Convierte una imagen RGB a una representación en cuaterniones:

```python
import cv2
from image_quaternion import rgb_to_quaternion

# Cargar una imagen
image = cv2.imread('ruta/a/tu/imagen.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertir a RGB
image = image / 255.0  # Normalizar la imagen

# Convertir a cuaterniones
q_image = rgb_to_quaternion(image)
```

### Aplicar Contraste

Aplica un factor de contraste a una imagen en formato de cuaterniones:

```python
from image_quaternion import apply_contrast

# Aplicar un contraste de 1.5
q_contrast = apply_contrast(q_image, contrast=1.5)
```

### Convertir de Cuaterniones a RGB

Convierte una imagen en formato de cuaterniones de vuelta a RGB:

```python
from image_quaternion import quaternion_to_rgb

# Convertir a RGB
rgb_image = quaternion_to_rgb(q_contrast)
```

### Visualizar Canales de Color

Visualiza los canales de color de una imagen en formato de cuaterniones:

```python
from image_quaternion import plot_channels

# Mostrar los canales de color
plot_channels(q_contrast, title='Canales de Color con Contraste 1.5')
```

### Comparar Histogramas

Compara los histogramas de una imagen tradicional y una en cuaterniones:

```python
from image_quaternion import compare_histograms

# Comparar histogramas
compare_histograms(q_image, image)
```

### Calcular Métricas de Calidad

Calcula métricas de calidad entre dos imágenes (MSE, PSNR y Entropía):

```python
from image_quaternion import calculate_metrics

# Calcular métricas
mse, psnr, entropy = calculate_metrics(image, rgb_image)
print(f'MSE: {mse}, PSNR: {psnr}, Entropía: {entropy}')
```

## Ejemplo Completo

```python
import cv2
import numpy as np
from image_quaternion import (
    rgb_to_quaternion,
    apply_contrast,
    quaternion_to_rgb,
    plot_channels,
    compare_histograms,
    calculate_metrics
)

# Cargar una imagen
image = cv2.imread('ruta/a/tu/imagen.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertir a RGB
image = image / 255.0  # Normalizar la imagen

# Convertir a cuaterniones
q_image = rgb_to_quaternion(image)

# Aplicar un contraste de 1.5
q_contrast = apply_contrast(q_image, contrast=1.5)

# Convertir de vuelta a RGB
rgb_image = quaternion_to_rgb(q_contrast)

# Mostrar los canales de color
plot_channels(q_contrast, title='Canales de Color con Contraste 1.5')

# Comparar histogramas
compare_histograms(q_image, image)

# Calcular métricas de calidad
mse, psnr, entropy = calculate_metrics(image, rgb_image)
print(f'MSE: {mse}, PSNR: {psnr}, Entropía: {entropy}')
```

## Requisitos

- Python 3.6 o superior.
- Dependencias:
  - `numpy`
  - `matplotlib`
  - `opencv-python`

## Instalación de Dependencias

Puedes instalar las dependencias automáticamente al instalar la librería con `pip`. Si prefieres instalarlas manualmente:

```bash
pip install numpy matplotlib opencv-python
```

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
