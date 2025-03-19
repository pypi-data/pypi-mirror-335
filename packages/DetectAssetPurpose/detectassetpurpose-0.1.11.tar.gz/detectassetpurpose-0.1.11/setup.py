from setuptools import setup, find_packages

setup(
    name="DetectAssetPurpose",
    version="0.1.11",
    description="Package provides detection of asset purpose using LLM identification: Brand Building or Conversion",
    author="Irina White",
    author_email="i.white@neuronsinc.com",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},    
    package_data={  # ✅ Include `config.yaml`
        "DetectAssetPurpose": ["config.yaml"]
    },
    install_requires=[],
    include_package_data=True,
)
