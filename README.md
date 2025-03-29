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

If `pyqtdarktheme.setup_theme()` does not work, or `pyqtdarktheme` version is `0.1.7` instead of `2.1.0`, install it manually using the following command:

```
pip install pyqtdarktheme==2.1.0 --ignore-requires-python
```

Reference:
https://github.com/5yutan5/PyQtDarkTheme/issues/252

## Usage Guide

### Prerequisites

Make sure that the virtual environment is activated before running any of the following commands

### Getting Started

The application allows you to select a photo of a document with fiducial markers and extract its contents using the selected template. Templates are located in the `./templates` folder.

To launch the application:

```bash
python main.py
```

### Basic Operations

### Opening Files

- Open a specific image using `File > Open...` or the keyboard shortcut `CTRL + O`
- Choose an image to process
- Select the template file to use for the ROI detection from the dropdown list
- Click `Ok` to process the document image

### Viewing Content

- Click any of the highlighted ROIs in the `Photo Viewer` on the left side to automatically scroll to it in the `Data` tab
- Navigate the image:
  - `Left-Click` and drag to move around the image
  - `Mouse Scroll Up` to zoom in
  - `Mouse Scroll Down` to zoom out
- Adjust the UI size by dragging the splitter in the middle

### Editing and Saving

- Edit the fields in the `Data` tab for any corrections
- Save the data using `File > Save...` or the keyboard shortcut `CTRL + S`
- The saved file will be in JSON format

### Template Editing

### Adding ROIs

1. Right-click any empty location in the `Photo Viewer`
2. Choose `New`
3. The new region will appear in the `Template` tab
4. Assign a name for the region

### Modifying ROIs

- Select a ROI in the `Photo Viewer` and choose `Edit`
- Drag the center of the ROI to move it
- Drag any of the eight directional handles to resize it
- Exit editing mode by clicking outside the ROI

### Copying ROIs

- Right-click on a ROI and select `Copy`
- Right-click on a blank space in the `Photo Viewer` and click `Paste`
