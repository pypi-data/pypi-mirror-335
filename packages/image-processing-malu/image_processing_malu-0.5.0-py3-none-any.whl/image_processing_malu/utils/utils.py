import cv2
import matplotlib.pyplot as plt

def read_image(path):
    """Lê uma imagem de um arquivo."""
    return cv2.imread(path, cv2.IMREAD_COLOR)

def save_image(path, image):
    """Salva uma imagem no arquivo especificado."""
    cv2.imwrite(path, image)

def plot_image(image, title="Image"):
    """Exibe uma imagem."""
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis("off")
    plt.show()

def plot_result(original, modified):
    """Exibe duas imagens lado a lado para comparação."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Original")
    axes[0].axis("off")
    
    axes[1].imshow(cv2.cvtColor(modified, cv2.COLOR_BGR2RGB))
    axes[1].set_title("Modificada")
    axes[1].axis("off")

    plt.show()

def plot_histogram(image):
    """Exibe o histograma de uma imagem."""
    plt.hist(image.ravel(), bins=256, range=[0, 256])
    plt.title("Histograma")
    plt.show()
