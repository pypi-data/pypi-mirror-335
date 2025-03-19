from setuptools import setup, find_packages
import io

# Read README with UTF-8 encoding
with io.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="monitorpeek",
    version="2.1.2",
    packages=find_packages(),
    install_requires=[
        'PyQt6>=6.4.0',
        'opencv-python>=4.7.0',
        'numpy>=1.24.0',
        'mss>=9.0.1',
        'pywin32>=305'
    ],
    package_data={
        'monitorpeek': ['final_icon.ico'],
    },
    author="John",
    author_email="zorat@abv.bg",
    description="A real-time secondary monitor preview tool with cursor tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zorat111/MonitorPeek",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Win32 (MS Windows)",
        "Topic :: Utilities",
    ],
    entry_points={
        'console_scripts': [
            'monitorpeek=monitorpeek.main:main',
        ],
    },
    python_requires='>=3.8',
) 