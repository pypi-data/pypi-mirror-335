from setuptools import setup, find_packages

setup(
    name="adaptive_trend_analysis",
    version="0.1.2",
    description="A library for Gradient-Adaptive Smoothing (GAS) trend analysis.",
    author="Jherson Aguto",
    author_email="dalisayfernando4@gmail.com",
    url="https://github.com/yourusername/adaptive_trend_analysis",  # Update with your actual GitHub repo
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
