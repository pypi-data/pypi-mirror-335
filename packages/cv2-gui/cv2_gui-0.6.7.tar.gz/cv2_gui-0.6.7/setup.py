from setuptools import setup, find_packages

# Read the README.md file for the project description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cv2_gui",
    version="0.6.7",
    description="A library to create buttons using OpenCV (cv2)",
    long_description=long_description,  # Add the project description
    long_description_content_type="text/markdown",  # Specify content type for Markdown
    author="Tarun Shenoy",
    author_email="tgshenoy1@gmail.com",
    url="https://github.com/Crystalazer/cv2_gui",
    packages=find_packages(),
    install_requires=["opencv-contrib-python", "numpy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="MIT",
)
