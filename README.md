# ECE-COE-199

This is the repo for our ECE COE 199 project.

## Setup Guide

This guide will help you set up the development environment for this project.

### Prerequisites

- Python

We recommend using `pyenv` to install and manage your Python version. If you haven't already installed `pyenv`, follow the installation instructions from [pyenv GitHub](https://github.com/pyenv/pyenv).

Once `pyenv` is installed, install the recommended Python version `3.12.2` by running the following command in your terminal:

```bash
pyenv install 3.12.2
```

### 1. Clone the repo

Clone the repository using the following command:

```bash
git clone https://github.com/ganpm/ECE-COE-199
```

Go into the directory.

```bash
cd ECE-COE-199
```

If you installed Python using `pyenv` run the following command:

```bash
pyenv local 3.12.2
```
This ensures the local python version used is 3.12.2. Verify that the correct python version is being used using the following command:

```bash
python --version
```

The version that is displayed should be `Python 3.12.2`.

### 2. Create and Activate Virtual Environment

In the same project directory, create a virtual enviroment using the following command:
```bash
python -m venv .venv
```
Activate the virtual enviroment using the following commands:

On Windows:
```bash
.venv\Scripts\activate
```
On macOS/Linux:
```bash
source .venv/bin/activate
```
If the virtual environment is activated, you should see a `(.venv)` in your terminal prompt.

### 3. Install Dependencies
Install the required packages while the virtual enviroment is activated:
```bash
pip install -r requirements.txt
```

## Usage Guide

Make sure that the virtual environment is activated before running any of the following commands

### main.py

This app allows you to select a photo of the document with fiducial markers and extracts its contents using the selected template. Templates are located in the `./templates` folder.

```bash
python main.py
```

Open a specific image using `File` > `Open...` or using the `CTRL + O` shortcut key. Choose an image to process and select the template file to use for the ROI detection in the drop down list and click `Ok` to process the document image.

Inspect the image using `Left-Click` to drag to move around the image and `Mouse Scroll Up` or `Mouse Scroll Down` to zoom in and out, respectively.

Adjust the UI size by dragging the splitter in the middle.

Edit the fields for any corrections and save the JSON file using `File` > `Save...` or using the `CTRL + S` shortcut key.

### query.py

This app looks for JSON files in the `./data` folder.

```bash
python query.py
```

Enter query in the search bar and the search results will be displayed on the left side. The app uses a simple search algorithm that matches any filenames and contents containing the search term.

Click on any of the search results to view the JSON file. The contents of the file will be displayed in table view on the right side.

Adjust the UI size by dragging the splitter in the middle.