from setuptools import setup, find_packages

setup(
    name="TeamTrackerPro",
    version="1.2.1",  # Increment version number
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15",
        "PyQtWebEngine>=5.15",
        "markdown>=3.3",
        "qdarkstyle",
        "plotly",
        "beautifulsoup4"
    ],
    entry_points={
        "console_scripts": [
            "teamtrackerpro=teamtrackerpro.main:main"
        ]
    },
    author="Your Name",
    description="A team tracking and performance review application",
)