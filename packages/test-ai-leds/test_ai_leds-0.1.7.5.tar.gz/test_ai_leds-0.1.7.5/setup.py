from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as file:
        descricao_longa = file.read()

setup(
    name="test_ai_leds",
    version="0.1.7.5",
    author="LEDS",
    author_email="gabrieldpbrunetti@gmail.com",
    description="AI automated test generation",
    packages=find_packages(include=['testailib', 'testailib.*']),
    include_package_data=True,
    install_requires=[
        "crewai==0.86.0",
        "crewai_tools==0.17.0",
        "google_generativeai",
        "pyaml",
        "chardet"
    ],
    entry_points={
        "console_scripts": [
            "testai=testailib.main:main",  # Executável que chama a função main
        ]
    },
    long_description=descricao_longa,
    long_description_content_type="text/markdown"
)
