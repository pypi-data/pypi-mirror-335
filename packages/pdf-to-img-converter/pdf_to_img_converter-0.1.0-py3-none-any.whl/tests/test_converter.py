import os
import unittest

from pdf_to_img_converter.converter import convert_pdf_to_image, delete_images


class TestPDFToImageConverter(unittest.TestCase):
    """Testes para conversão de PDF para imagens e exclusão de arquivos gerados.""" # noqa501

    def setUp(self):
        """Configuração inicial antes dos testes."""
        self.test_pdf = "test_files/sample.pdf"  # Certifique-se de que há um PDF de teste no diretório # noqa501
        self.output_folder = "test_images"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def test_convert_pdf_to_image(self):
        """Testa se o PDF é convertido corretamente em imagens."""
        image_paths = convert_pdf_to_image(self.test_pdf, output_folder=self.output_folder) # noqa501
        self.assertGreater(len(image_paths), 0, "A conversão não gerou imagens.") # noqa501
        self.assertTrue(all(os.path.exists(img) for img in image_paths), "Nem todas as imagens foram criadas corretamente.") # noqa501

        # Limpar imagens após o teste
        delete_images(image_paths)

    def test_delete_images(self):
        """Testa se as imagens geradas são excluídas corretamente."""
        image_paths = convert_pdf_to_image(self.test_pdf, output_folder=self.output_folder) # noqa501
        delete_images(image_paths)
        self.assertFalse(any(os.path.exists(img) for img in image_paths), "Nem todas as imagens foram excluídas corretamente.") # noqa501

    def tearDown(self):
        """Remove a pasta de teste após a execução dos testes."""
        if os.path.exists(self.output_folder):
            for file in os.listdir(self.output_folder):
                os.remove(os.path.join(self.output_folder, file))
            os.rmdir(self.output_folder)


if __name__ == "__main__":
    unittest.main()
