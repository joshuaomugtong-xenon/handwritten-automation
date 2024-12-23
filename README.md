# ECE-COE-199

This is the repo for our ECE COE 199 project.

## Setup Guide

This guide will help you set up the development environment for this project.

### Prerequisites

- Python

We recommend using `pyenv` to install and manage your Python version. If you haven't already installed `pyenv`, follow the installation instructions from [pyenv GitHub](https://github.com/pyenv/pyenv).

Once `pyenv` is installed, install the recommended Python version (3.12.2) by running the following command in your terminal:

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

### 4. Run the main file

```bash
python main.py
```

## Usage Guide

Open a specific image using `File` > `Open` or using the `CTRL + O` shortcut key. Select the template file to use for the ROI detection in the drop down box and click `Ok`.