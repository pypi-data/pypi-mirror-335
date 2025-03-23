import cv2
import numpy as np
from skimage.metrics import structural_similarity

def histogram_matching(source, reference):
    """Ajusta o histograma de uma imagem de acordo com uma imagem de referência."""
    source_hist = cv2.calcHist([source], [0], None, [256], [0, 256])
    reference_hist = cv2.calcHist([reference], [0], None, [256], [0, 256])

    cdf_source = np.cumsum(source_hist) / np.sum(source_hist)
    cdf_reference = np.cumsum(reference_hist) / np.sum(reference_hist)

    lookup_table = np.interp(cdf_source, cdf_reference, np.arange(256))
    matched_image = cv2.LUT(source, lookup_table.astype('uint8'))

    return matched_image

def structural_similarity(image1, image2):
    """Calcula a similaridade estrutural entre duas imagens."""
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    score, _ = structural_similarity(gray1, gray2, full=True)
    return score

def resize_image(image, width, height):
    """Redimensiona uma imagem para a largura e altura especificadas."""
    return cv2.resize(image, (width, height))
