import os
import random

import requests
from pdf2image import convert_from_path


def download_pdf(url, output_folder="downloads"):
    """Baixa um PDF de uma URL e salva localmente."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        filename = os.path.join(output_folder, "downloaded_pdf.pdf")
        with open(filename, "wb") as file:
            file.write(response.content)
        return filename
    else:
        raise ValueError("❌ Erro ao baixar o PDF.")

def convert_pdf_to_image(filename, dpi=300, output_folder="images"): # noqa501
    """Converte um PDF em imagens PNG."""
    try:
        # Se for uma URL, baixa o arquivo primeiro
        if filename.startswith("http"):
            filename = download_pdf(filename)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        pages = convert_from_path(filename, dpi=dpi)

        image_paths = []
        for i, page in enumerate(pages):
            image_path = os.path.join(output_folder, f"page_{i+1}_{random.randint(10, 99)}.png") # noqa501
            page.save(image_path, "PNG")
            image_paths.append(image_path)

        return image_paths
    except Exception as e:
        raise ValueError(f"❌ Erro ao converter PDF: {str(e)}")


def delete_images(image_paths):
    """Remove as imagens geradas após o uso."""
    for image_path in image_paths:
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"❌ Erro ao remover {image_path}: {e}")
        except Exception as e:
            print(f"❌ Erro ao remover {image_path}: {e}")
