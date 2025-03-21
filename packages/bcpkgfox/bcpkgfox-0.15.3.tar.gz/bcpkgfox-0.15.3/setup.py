from setuptools import setup, find_packages

setup(
    name="bcpkgfox",
    version="0.15.3",
    author="Guilherme Neri",
    author_email="guilherme.neri@bcfox.com.br",
    description="Biblioteca BCFOX",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/robotsbcfox/PacotePythonBCFOX",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "bc-find-imports=bcpkgfox.cli:main",
            "bc_find_imports=bcpkgfox.cli:main",
            "bc_find_import=bcpkgfox.cli:main",
            "find_imports=bcpkgfox.cli:main",
            "find_import=bcpkgfox.cli:main",
            "bfi=bcpkgfox.cli:main",
            "fi=bcpkgfox.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        'setuptools',
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

