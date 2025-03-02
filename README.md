# Medicine Components & Comparison API

A command line application that allows users to enter a medicine name, identify its components, and retrieve detailed information on similar products. The tool helps users compare products based on their manufacturer, usage, side effects, active ingredients, and more.

## Features

* Medicine Lookup: Enter a medicine name to see its components and details.
* Similar Product Identification: Automatically identify similar products based on active ingredients and other key attributes.
* Comprehensive Comparison: Display detailed information including manufacturer, usage and indications, side effects, dosage forms, strength and composition, and additional components.
* User-Friendly CLI: Designed for easy navigation and quick access to relevant medicine information directly from the terminal.

## How it works?

* Input: The user provides the name of the medicine via the command line.
* Component Identification: The application identifies the active ingredients and other components in the medicine.
* Comparison: Based on the identified components, the tool searches for similar products and retrieves their details.
* Output: The results are presented in a clear and organized format, making it easy to compare the medicines.

## Usage

* You must store a valid Groq API Key as a secret to proceed with this example.
* Update the Key in .env file
* Install the dependencies
```bash
pip install requirements.txt
```
* run it on the command line with 
```bash
run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
OR 
```bash
python main.py
```

## Docs
* The API doc is available at http://localhost:8000/docs

## Approach

* Established a comprehensive Medicine Database
* Developed a knowledge graph to map relationships between medicines, manufacturers, and components
* Implemented information retrieval methods to identify similar medicines
* Optimized prompts to extract and complete details for each medicine in the list