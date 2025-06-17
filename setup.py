"""Setup configuration for Virtual Pedalboard"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="virtual-pedalboard",
    version="1.0.0",
    author="Virtual Pedalboard Team",
    description="A real-time audio effects processing system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/virtual-pedalboard",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
        "Topic :: Multimedia :: Sound/Audio :: Audio Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "virtual-pedalboard=virtual_pedalboard.main:main",
        ],
    },
    include_package_data=True,
)
