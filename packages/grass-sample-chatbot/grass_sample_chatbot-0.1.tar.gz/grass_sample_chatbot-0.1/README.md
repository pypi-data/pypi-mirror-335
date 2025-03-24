# grass_sample_chatbot

A chatbot designed to help users interact with GRASS GIS commands. This application leverages the T5-small model fine-tuned for GIS-related tasks and uses Gradio for a user-friendly interface.

## Features

- **GRASS GIS Command Generation**: The chatbot helps generate GRASS GIS commands based on user queries related to geographic analysis.
- **Model**: Uses a T5-small model, fine-tuned for GIS tasks like generating instructions.
- **Gradio Interface**: Provides a simple, interactive web interface to communicate with the chatbot.

## Installation Guide

##  Clone the Repository

Start by cloning the GitHub repository to your local machine:

```
git clone https://github.com/Sachin-NK/grass_sample_chatbot.git
cd grass_sample_chatbot
```
Create a Virtual Environment
  On Windows:
```
python -m venv grass_gis_chatbot_env
grass_gis_chatbot_env\Scripts\activate
```

  On macOS/Linux:
```
python3 -m venv grass_gis_chatbot_env
source grass_gis_chatbot_env/bin/activate
```

Install Required Dependencies
```
pip install -r requirements.txt
```

Start the Chatbot
```
python chatbot.py
```


