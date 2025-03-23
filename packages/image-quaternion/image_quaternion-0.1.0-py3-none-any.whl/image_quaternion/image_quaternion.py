import numpy as np
import matplotlib.pyplot as plt
import cv2

def rgb_to_quaternion(image):
    """Convierte una imagen RGB a una representación en cuaterniones."""
    R, G, B = image[:, :, 0], image[:, :, 1], image[:, :, 2]
    Q = np.zeros((image.shape[0], image.shape[1], 4))
    Q[:, :, 1] = R  # Parte imaginaria i (rojo)
    Q[:, :, 2] = G  # Parte imaginaria j (verde)
    Q[:, :, 3] = B  # Parte imaginaria k (azul)
    return Q

def apply_contrast(q, contrast):
    """Aplica un contraste a la imagen en formato de cuaterniones."""
    q[:, :, 1:] = q[:, :, 1:] * contrast
    return q

def quaternion_to_rgb(q):
    """Convierte una imagen en formato de cuaterniones de vuelta a RGB."""
    R = q[:, :, 1]
    G = q[:, :, 2]
    B = q[:, :, 3]
    return np.stack([R, G, B], axis=-1)

def plot_channels(q, title):
    """Muestra los canales de color de la imagen en formato de cuaterniones."""
    fig, axes = plt.subplots(1, 4, figsize=(15, 5))
    axes[0].imshow(q[:, :, 0], cmap='gray')
    axes[0].set_title('Parte Real')
    axes[1].imshow(q[:, :, 1], cmap='Reds')
    axes[1].set_title('Rojo')
    axes[2].imshow(q[:, :, 2], cmap='Greens')
    axes[2].set_title('Verde')
    axes[3].imshow(q[:, :, 3], cmap='Blues')
    axes[3].set_title('Azul')
    plt.suptitle(title)
    plt.show()

def compare_histograms(q_image, image):
    """Compara los histogramas de una imagen tradicional y una en cuaterniones."""
    q_rgb = quaternion_to_rgb(q_image)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    colors = ['Red', 'Green', 'Blue']
    for i, color in enumerate(colors):
        hist_trad, _ = np.histogram(image[:, :, i].ravel(), bins=256, range=(0, 1))
        hist_quat, _ = np.histogram(q_rgb[:, :, i].ravel(), bins=256, range=(0, 1))
        diff = np.abs(hist_trad - hist_quat)
        diff_percentage = (np.sum(diff) / np.sum(hist_trad)) * 100
        
        axes[0, i].hist(image[:, :, i].ravel(), bins=256, color=color, alpha=0.5)
        axes[0, i].set_title(f'{color} Tradicional')
        axes[1, i].hist(q_rgb[:, :, i].ravel(), bins=256, color=color, alpha=0.5)
        axes[1, i].set_title(f'{color} Cuaterniones')
        
        axes[0, i].text(0.5, 0.9, f'Diff: {np.sum(diff):.2f} ({diff_percentage:.2f}%)', transform=axes[0, i].transAxes, fontsize=12, color='black')
        axes[1, i].text(0.5, 0.9, f'Diff: {np.sum(diff):.2f} ({diff_percentage:.2f}%)', transform=axes[1, i].transAxes, fontsize=12, color='black')
    plt.show()

def calculate_metrics(image1, image2):
    """Calcula métricas de comparación entre dos imágenes."""
    mse = np.mean((image1 - image2) ** 2)
    psnr = 10 * np.log10(1 / mse)
    entropy = -np.sum(image1 * np.log2(image1 + 1e-10))
    return mse, psnr, entropy

def compare_histograms_by_contrast(q_image, image, contrasts):
    """Compara histogramas de imágenes con diferentes contrastes."""
    q_rgb = quaternion_to_rgb(q_image)
    fig, axes = plt.subplots(len(contrasts), 3, figsize=(15, 5 * len(contrasts)))
    colors = ['Red', 'Green', 'Blue']
    for j, contrast in enumerate(contrasts):
        q_contrast = apply_contrast(q_image.copy(), contrast)
        q_rgb_contrast = quaternion_to_rgb(q_contrast)
        for i, color in enumerate(colors):
            hist_trad, _ = np.histogram(image[:, :, i].ravel(), bins=256, range=(0, 1))
            hist_quat, _ = np.histogram(q_rgb_contrast[:, :, i].ravel(), bins=256, range=(0, 1))
            diff = np.abs(hist_trad - hist_quat)
            diff_percentage = (np.sum(diff) / np.sum(hist_trad)) * 100
            
            axes[j, i].hist(image[:, :, i].ravel(), bins=256, color=color, alpha=0.5, label='Tradicional')
            axes[j, i].hist(q_rgb_contrast[:, :, i].ravel(), bins=256, color=color, alpha=0.5, label='Cuaterniones')
            axes[j, i].set_title(f'{color} - Contraste: {contrast}')
            axes[j, i].text(0.5, 0.9, f'Diff: {np.sum(diff):.2f} ({diff_percentage:.2f}%)', transform=axes[j, i].transAxes, fontsize=12, color='black')
            axes[j, i].legend()
    plt.show()