from setuptools import setup, find_packages

setup(
    name="grass_sample_chatbot", 
    version="0.1", 
    packages=find_packages(),  
    install_requires=[
        "torch",
        "transformers",
        "gradio",
    ],
    package_data={  
        "grass_gis_chatbot_model": [
            "model.safetensors",
            "config.json",
            "tokenizer_config.json",
            "generation_config.json",
            "special_tokens_map.json",
            "spiece.model",
            "added_tokens.json",
        ],
    },
    classifiers=[  # Metadata to specify how your package should be classified
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    author="Sachintha Nadeeshan",
    author_email="snkodikara52@gmail.com",
    description="A sample chatbot for GRASS GIS based on T5-small model",
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
)
