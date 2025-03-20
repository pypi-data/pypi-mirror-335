
from setuptools import setup,find_packages


setup(
    name="ElliShape",
    version="1.4.4",
    packages= find_packages(include=['ElliShape', 'ElliShape.*', 'functions', 'functions.*','segment_anything', 'segment_anything.*',]),
    python_requires=">=3.8",  # 指定 Python 版本要求
    # cmdclass={"install": CustomInstall},
    install_requires=[
        "opencv-python>=4.9.0.80",
        "matplotlib>=3.7.2",
        "pyqt5>=5.15.10",
        "segment-anything>=1.0",
        "torch>=2.2.2",
        "torchvision>=0.17.2",
        "scipy>=1.10.1",
        "openpyxl>=3.1.2",
        "numpy>=1.24.3",
        "pandas>=2.0.3",
        "pillow>=10.2.0",
        "PyQt5-sip>=12.13.0",
        "PySocks>=1.7.1",
        "urllib3>=2.1.0",
        "requests>=2.31.0",
        "tqdm>=4.66.5",
    ],
    entry_points={
        'console_scripts': [
            'ElliShape=ElliShape.ElliShape:main',
        ],
    },
)
