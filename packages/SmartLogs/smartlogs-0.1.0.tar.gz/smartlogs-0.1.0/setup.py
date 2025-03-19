from setuptools import find_packages, setup

setup(
    name="SmartLogs",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "colorama",  # Para cores no terminal
    ],
    author="Roberto Lima",
    author_email="robertolima.izphera@gmail.com",
    description="Um logger inteligente para projetos Python, com suporte a cores, arquivos e integrações com Slack/Telegram.", # noqa501
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/robertolima-dev/SmartLogs",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
