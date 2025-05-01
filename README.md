# MSI Data Analysis Tool

MSI Data Analysis Tool is a graphical interface tool for Mass Spectrometry Imaging (MSI) data analysis. This tool provides molecular weight and m/z calculation, mass shift calibration, ion matching, and metabolite annotation functions to help researchers process and analyze MSI data more efficiently.

## Main Features

### 1. Database Construction
- Calculate precise molecular weights from molecular formulas
- Support multiple adduct type calculations
- Customizable element mass file
- Batch processing of multiple compounds

### 2. MS Shift Evaluation
- Evaluate mass spectrometry data accuracy
- Calculate relative errors (ppm)
- Provide detailed statistical information
- Support intensity threshold filtering

### 3. Annotation Function
- Match experimental data with database
- Support customizable error ranges
- Multi-sheet processing

## System Requirements

- Windows operating system
- Python 3.7 or higher
- Minimum 4GB RAM
- Minimum screen resolution: 1280 x 720

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/msidat.git
cd msidat
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the program:
```bash
python gui/gui.py
```

## Usage Guide

### Database Construction
1. Prepare an Excel file containing molecular formulas
2. Select element mass file and adduct type file
3. Choose the adduct types to calculate
4. Click "Construct Database" to start calculation

### MS Shift Evaluation
1. Select source data file and target data file
2. Set corresponding column names and parameters
3. Set intensity threshold and m/z tolerance
4. Click "Run Evaluation" to start assessment

### Annotation Function
1. Select MSI data file and database file
2. Choose corresponding worksheets
3. Set upper and lower error limits (ppm)
4. Click "Run Annotation" to start annotation

## Configuration File

The program supports global settings through a JSON format configuration file, including:
- Element mass file path
- Adduct type file path
- Input/output file paths
- Various parameter settings

## Notes

1. Ensure input files are in the correct format (Excel format)
2. Regular backup of important data is recommended
3. Ensure sufficient memory space for processing large datasets
