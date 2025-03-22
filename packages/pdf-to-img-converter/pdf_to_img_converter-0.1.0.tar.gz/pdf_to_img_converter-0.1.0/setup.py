from setuptools import find_packages, setup

setup(
    name="pdf_to_img_converter",
    version="0.1.0",
    packages=find_packages(),
    author="Roberto Lima",
    author_email="robertolima.izphera@gmail.com",
    description="Uma biblioteca Python para converter arquivos PDF em imagens.", # noqa501
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/robertolima-dev/pdf_to_img_converter",
    install_requires=[
        "pdf2image",
        "requests",
        "Pillow"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "pdf-to-img=pdf_to_img_converter.cli:main",  # Opcional para CLI
        ],
    },
)
