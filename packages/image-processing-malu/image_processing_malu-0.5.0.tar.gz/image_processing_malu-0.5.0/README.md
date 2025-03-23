# image_processing_malu

## Funcionalidades

✔ **Histogram Matching** – Ajusta o histograma de uma imagem para corresponder ao de outra.  
✔ **Structural Similarity** – Mede a similaridade estrutural entre duas imagens.  
✔ **Resize Image** – Redimensiona uma imagem para um tamanho específico.  
✔ **Utils**:
   - Ler imagem (`read_image`)
   - Salvar imagem (`save_image`)
   - Exibir imagem (`plot_image`)
   - Exibir comparação de imagens (`plot_result`)
   - Exibir histograma de uma imagem (`plot_histogram`)

## Instalação

Use o gerenciador de pacotes [pip](https://pip.pypa.io/en/stable/) para instalar o `image_processing_malu`:

```bash
pip install image_processing_malu
```

## Uso
```bash
from image_processing_malu.processing import histogram_matching, structural_similarity, resize_image
from image_processing_malu.utils import read_image, save_image, plot_image, plot_result, plot_histogram
```

## Autor
Maria Luiza Romani
Código Fonte: Karina Kato