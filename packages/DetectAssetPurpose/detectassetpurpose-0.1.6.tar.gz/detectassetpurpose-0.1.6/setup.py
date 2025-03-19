from setuptools import setup, find_packages

setup(
    name="DetectAssetPurpose",
    version="0.1.6",
    description="Package provides detection of asset purpose using LLM identification: Brand Building or Conversion",
    author="Irina White",
    author_email="i.white@neuronsinc.com",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},    
    install_requires=[],
)
