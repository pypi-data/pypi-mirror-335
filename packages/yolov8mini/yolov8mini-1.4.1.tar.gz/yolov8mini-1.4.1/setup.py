from setuptools import setup, find_packages

setup(
    name="yolov8mini",
    version="1.4.1",
    packages=find_packages(),
    install_requires=[
        "pytelegrambotapi",
        "opencv-python",
        "numpy",
        "pyautogui",
        "pillow"
    ],
    entry_points={
        "console_scripts": [
            "yolov8mini = yolov8mini.bot:run_bot"
        ]
    },
    author="Tintumon",
    author_email="",
    description="A Telegram bot for system monitoring and control.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/appuachu",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
