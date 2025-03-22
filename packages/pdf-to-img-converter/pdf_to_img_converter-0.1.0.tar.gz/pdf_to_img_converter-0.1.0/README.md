# 📚 **PDF to Image Converter**

🚀 **pdf_to_img_converter** é uma biblioteca Python para converter arquivos **PDF** em imagens **PNG**. Suporta entrada de **arquivos locais** e **URLs**, além de oferecer a opção de remover automaticamente as imagens geradas.

---

## ✨ **Funcionalidades**
- 📄 **Conversão de PDF para imagens**.
- 🌐 **Suporte a arquivos locais e URLs**.
- 🗑 **Função para excluir as imagens após o uso**.

---

## ⚡ **Instalação**

Instale o pacote diretamente do PyPI:

```bash
pip install pdf_to_img_converter
```

> **Requisitos:** `pdf2image`, `requests` e `Pillow` (instalados automaticamente).

---

## 💡 **Como Usar**

### 📄 **Converter um PDF local para imagens**
```python
from pdf_to_img_converter.converter import convert_pdf_to_image

image_paths = convert_pdf_to_image("documento.pdf")
print("Imagens geradas:", image_paths)

for img in image_paths:
    print(img)
```

### 🌐 **Converter um PDF a partir de uma URL**
```python
image_paths = convert_pdf_to_image("https://www.exemplo.com/arquivo.pdf")
print("Imagens geradas:", image_paths)

for img in image_paths:
    print(img)
```

### 🗑 **Excluir imagens geradas após o uso**
```python
from pdf_to_img_converter.converter import delete_images

delete_images(image_paths)
print("Imagens excluídas com sucesso!")
```

---

## 🧪 **Executando Testes**

Para rodar os testes unitários:
```bash
pytest tests/
```

---

## 🏗 **Estrutura do Projeto**

```
pdf_to_img_converter/
│
├── pdf_to_img_converter/       # 📦 Código da biblioteca
│   ├── __init__.py
│   ├── converter.py            # 🔥 Funções principais
│
├── tests/                      # 🧪 Testes unitários
│   ├── test_converter.py
│
├── test_files/
│
├── setup.py                    # ⚙️ Configuração do pacote
├── pyproject.toml              # 📦 Configuração moderna
├── README.md                   # 📚 Documentação do pacote
├── LICENSE                     # 📜 Licença MIT
└── MANIFEST.in                 # 📋 Inclusão de arquivos extras
```

---

## 📝 **Licença**

Distribuído sob a **Licença MIT**. Veja o arquivo [LICENSE](LICENSE) para mais informações.

---

## 👨‍💻 **Autor**

Desenvolvido por **[Roberto Lima](https://robertolima-developer.vercel.app/)** 🚀✨

---

## 💬 **Contato**

- 📧 **Email**: robertolima.izphera@gmail.com
- 💼 **LinkedIn**: [Roberto Lima](https://www.linkedin.com/in/roberto-lima-01/)
- 💼 **Website**: [Roberto Lima](https://robertolima-developer.vercel.app/)
- 💼 **Gravatar**: [Roberto Lima](https://gravatar.com/deliciouslyautomaticf57dc92af0)

---

## ⭐ **Gostou do projeto?**

Deixe uma ⭐ no repositório e compartilhe com a comunidade! 🚀✨

