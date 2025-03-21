from setuptools import setup, find_packages

setup(
    name="bcpkgfox",
    version="0.15.17",
    author="Guilherme Neri",
    author_email="guilherme.neri@bcfox.com.br",
    description="Biblioteca BCFOX",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/robotsbcfox/PacotePythonBCFOX",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            *[f"{cmd}=bcpkgfox.cli:main" for cmd in [
                "bc-find-imports",
                "bc_find_imports",
                "bc_find_import",
                "find_imports",
                "find_import",
                "bfi",
                "fi",
            ]],
            *[f"{cmd}=bcpkgfox.exec_file:main" for cmd in [
                "bc_gerar_executavel",
                "gerar.executavel",
                "gerar-executavel",
                "gerarexecutavel",
                "gerar executavel",
                "gerar_executavel",
                "gerar_exec",
                "gerarexec",
                "gerar exec",
                "gerar.exec",
                "gerar-exec",
                "gen_exec",
                "genexe",
                "genexec",
                "gexec",
                "ge",
            ]],
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        'setuptools',
        'pyperclip',
        'selenium'
    ],
    extras_require={
        "full": [
            'undetected-chromedriver',
            'webdriver-manager',
            'opencv-python',
            'pygetwindow',
            'pyscreeze',
            'pyautogui',
            'requests',
            'pymupdf',
            'Pillow',
            'psutil'
        ],
    },
)

