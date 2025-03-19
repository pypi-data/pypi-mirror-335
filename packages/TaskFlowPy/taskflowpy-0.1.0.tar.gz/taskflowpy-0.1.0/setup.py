from setuptools import find_packages, setup

setup(
    name="TaskFlowPy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",  # Para suporte ao CLI
    ],
    author="Roberto Lima",
    author_email="robertolima.izphera@gmail.com",
    description="Um gerenciador de tarefas simples e eficiente para projetos Python, com suporte a JSON e SQLite.", # noqa501
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/robertolima-dev/TaskFlowPy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "taskflowpy=TaskFlowPy.cli:main",
        ],
    },
    python_requires='>=3.7',
)
