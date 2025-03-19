from setuptools import setup, find_packages

setup(
    name="causara",
    version="1.8.0",
    author="causara UG",
    author_email="support@causara.com",
    description="This package provides several AI-features for building and working with Gurobi optimization models.\n"
                "The currently supported features are:\n"
                "   (1) Learning a Gurobi model from historical / synthetic data\n"
                "   (2) Converting a plain Python function into a Gurobi model\n"
                "   (3) Post-processing Gurobi results with Python functions\n"
                "   (4) AI-Interface for end-users of Gurobi models (e.g. no-code modifications using natural language)\n"
                "   (5) Finetuning a Gurobi Model on real-world data\n",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://www.causara.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*"],
    },
    license="Proprietary",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9, <3.13",
    install_requires=[
        "torch",
        "bcrypt",
        "numpy<2",
        "scipy",
        "gurobipy",
        "pandas",
        "openpyxl",
        "reportlab",
        "psutil",
        "sympy",
        "tqdm",
        "pywebview",
        "qtpy; sys_platform == 'linux'",
        "PyQt5; sys_platform == 'linux'",
        "PyQtWebEngine; sys_platform == 'linux'",
        # Use cefpython3 on platforms other than Linux and macOS (e.g. Windows)
        "cefpython3; sys_platform != 'linux' and sys_platform != 'darwin'",
        "rdkit",
        "matplotlib",
        "folium",
        "orjson",
        "pyyaml",
        "pywin32; sys_platform=='win32'"
    ],
)
