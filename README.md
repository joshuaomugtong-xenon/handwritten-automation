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

#### Opening Images

1. Open an image:
   - Click **File** > **Open...** in the upper-right corner
   - Or use the keyboard shortcut `CTRL+O`
2. Choose an image to process
3. Select the template file to use for the ROI detection from the dropdown list
4. Click **Ok** to process the document image

#### Viewing Content

- To navigate the image:
  - Drag the mouse to move around the image
  - Use the mouse scroll to zoom in and out of the image
- Click any of the highlighted ROIs in the **Photo Viewer** on the left side to automatically scroll to it in the **Data View** tab
- Click the image in the **Data View** tab to highlight the corresponding ROI in the **Photo Viewer**
- Adjust the UI size by dragging the splitter in the middle

#### Editing and Saving Extracted Data

- Edit the fields in the **Data** tab for any corrections
- To save the extracted data:
  - Click **File** > **Save...** in the upper-right corner
  - Or use the keyboard shortcut `CTRL+S`
- The saved file will be in JSON format

### Template Editing

You can edit the template YAMLs in the **Template View** tab.

#### Adding New ROIs

1. To add a new ROI:
   - Right-click any empty location in the **Photo Viewer** and select **New**
   - This will create a new region box in the **Photo Viewer**
   - The new region will also appear in the **Template View** tab
2. Edit the new region in the **Template View** tab
   - Clicking the ROI on the **Photo Viewer** will highlight the region in the **Template View** tab
   - Clicking the **Click to View** button in the **Template View** tab will highlight the ROI in the **Photo Viewer**

#### Moving and Resizing ROIs

1. To move or resize a ROI in the **Photo Viewer**:
   - Right-click a ROI and select **Edit**
   - Or double-click a ROI
2. Drag the center of the ROI to move it around
3. Drag any of the eight directional handles to resize it
4. Exit editing mode by clicking outside the ROI

Note: Moving and resizing a ROI automatically updates the value of the **coordinates** in the corresponding region entry in the **Template View** in real time.

#### Copying and Pasting ROIs

1. To copy a ROI on the **Photo Viewer**:
   - Right-click a ROI and select **Copy**
   - Or left-click a ROI and press `CTRL+C`
2. To paste it:
   - Right-click on a blank space and select **Paste**
   - Or move the mouse to a blank space and press `CTRL+V`

Note: Pasting a ROI automatically creates a new blank entry in the **Template View**.

#### Deleting ROIs

1. To delete a ROI on the **Photo Viewer**:
   - Right-click on a ROI and select **Delete**
   - Or left-click on a ROI and press `Del`

Note: Deleting a ROI automatically deletes the corresponding entry in the **Template View**.

#### Saving the Template

1. To save the template:
   - Click **File** > **Save Template..** in the upper-right corner
   - Or use the keyboard shortcut `CTRL+SHIFT+S`
