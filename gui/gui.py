import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QFileDialog, QSpinBox, QDoubleSpinBox, QMessageBox,
                           QTextEdit, QComboBox, QGroupBox, QFormLayout,
                           QTabWidget)
from PyQt5.QtCore import Qt
import pandas as pd
from loguru import logger

from msidat.match.compound_match import CompoundMatch
from msidat.molar_mass.cal_molar_mass import MolarMassCalculator

class QTextEditLogger:
    """Custom loguru handler to redirect logs to QTextEdit"""
    def __init__(self, widget):
        self.widget = widget

    def write(self, message):
        self.widget.append(message.strip())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.compound_match = CompoundMatch()
        self.mol_calculator = MolarMassCalculator()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Mass Spectrometry Data Analysis Tool')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and tab widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Create compound match tab
        compound_match_tab = CompoundMatchTab(self.compound_match)
        tab_widget.addTab(compound_match_tab, "Compound Match")
        
        # Create molar mass calculator tab
        molar_mass_tab = MolarMassTab(self.mol_calculator)
        tab_widget.addTab(molar_mass_tab, "Molar Mass Calculator")
        
        layout.addWidget(tab_widget)

class CompoundMatchTab(QWidget):
    def __init__(self, compound_match):
        super().__init__()
        self.compound_match = compound_match
        self.initUI()
        self.setup_logger()
        
    def setup_logger(self):
        """Setup loguru logger handlers"""
        # Remove default console output
        logger.remove()
        # Add custom GUI output handler
        logger.add(
            QTextEditLogger(self.log_text).write,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO"
        )
        # Keep file logging
        log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log', 'gui.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logger.add(
            log_file,
            rotation="1 day",
            retention="30 days",
            level="DEBUG"
        )
        
    def initUI(self):
        self.setWindowTitle('Compound Matching Tool')
        self.setGeometry(100, 100, 1000, 800)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # File selection area
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
        # Source file selection
        source_layout = QHBoxLayout()
        source_label = QLabel('Source File:')
        self.source_path = QLineEdit()
        source_btn = QPushButton('Browse...')
        source_btn.clicked.connect(lambda: self.browse_file(self.source_path, self.update_source_columns))
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_path)
        source_layout.addWidget(source_btn)
        file_layout.addLayout(source_layout)
        
        # Target file selection
        target_layout = QHBoxLayout()
        target_label = QLabel('Target File:')
        self.target_path = QLineEdit()
        target_btn = QPushButton('Browse...')
        target_btn.clicked.connect(lambda: self.browse_file(self.target_path, self.update_target_columns))
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_path)
        target_layout.addWidget(target_btn)
        file_layout.addLayout(target_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Column settings area
        columns_group = QGroupBox("Column Settings")
        columns_layout = QFormLayout()
        
        # Source data column selection
        self.source_mz_combo = QComboBox()
        self.source_intensity_combo = QComboBox()
        columns_layout.addRow("Source m/z Column:", self.source_mz_combo)
        columns_layout.addRow("Source Intensity Column:", self.source_intensity_combo)
        
        # Target data column selection
        self.target_mz_combo = QComboBox()
        columns_layout.addRow("Target m/z Column:", self.target_mz_combo)
        
        # Output column names
        self.output_mz = QLineEdit('measured m/z')
        self.output_rel_error = QLineEdit('Relative Error(ppm)')
        self.output_intensity = QLineEdit('Intensity')
        columns_layout.addRow("Output m/z Column:", self.output_mz)
        columns_layout.addRow("Output Relative Error Column:", self.output_rel_error)
        columns_layout.addRow("Output Intensity Column:", self.output_intensity)
        
        columns_group.setLayout(columns_layout)
        layout.addWidget(columns_group)
        
        # Parameter settings area
        params_group = QGroupBox("Parameter Settings")
        params_layout = QHBoxLayout()
        
        # Intensity threshold setting
        intensity_layout = QVBoxLayout()
        intensity_label = QLabel('Intensity Threshold:')
        self.intensity_spin = QSpinBox()
        self.intensity_spin.setRange(0, 1000000)
        self.intensity_spin.setValue(1000)
        intensity_layout.addWidget(intensity_label)
        intensity_layout.addWidget(self.intensity_spin)
        params_layout.addLayout(intensity_layout)
        
        # m/z tolerance setting
        tolerance_layout = QVBoxLayout()
        tolerance_label = QLabel('m/z Tolerance (ppm):')
        self.tolerance_spin = QDoubleSpinBox()
        self.tolerance_spin.setRange(0, 1000)
        self.tolerance_spin.setValue(20)
        tolerance_layout.addWidget(tolerance_label)
        tolerance_layout.addWidget(self.tolerance_spin)
        params_layout.addLayout(tolerance_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Output file setting
        output_group = QGroupBox("Output Settings")
        output_layout = QHBoxLayout()
        output_label = QLabel('Output File:')
        self.output_path = QLineEdit()
        output_btn = QPushButton('Browse...')
        output_btn.clicked.connect(lambda: self.browse_save_file(self.output_path))
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_btn)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Run button
        run_btn = QPushButton('Run Matching')
        run_btn.clicked.connect(self.run_match)
        layout.addWidget(run_btn)
        
        # Log display area
        log_group = QGroupBox("Running Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
    def update_source_columns(self):
        """Update source data column selection dropdowns"""
        try:
            df = pd.read_excel(self.source_path.text())
            self.source_mz_combo.clear()
            self.source_intensity_combo.clear()
            self.source_mz_combo.addItems(df.columns)
            self.source_intensity_combo.addItems(df.columns)
            
            # Try to auto-select default columns
            mz_index = df.columns.str.lower().str.contains('m/z').argmax()
            intensity_index = df.columns.str.lower().str.contains('intensity').argmax()
            self.source_mz_combo.setCurrentIndex(mz_index)
            self.source_intensity_combo.setCurrentIndex(intensity_index)
        except Exception as e:
            logger.error(f"Failed to update source columns: {str(e)}")
            
    def update_target_columns(self):
        """Update target data column selection dropdown"""
        try:
            df = pd.read_excel(self.target_path.text())
            self.target_mz_combo.clear()
            self.target_mz_combo.addItems(df.columns)
            
            # Try to auto-select default column
            mz_index = df.columns.str.lower().str.contains('m/z').argmax()
            self.target_mz_combo.setCurrentIndex(mz_index)
        except Exception as e:
            logger.error(f"Failed to update target columns: {str(e)}")
        
    def browse_file(self, line_edit, callback=None):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Select File', '', 'Excel Files (*.xlsx *.xls);;All Files (*)'
        )
        if file_name:
            line_edit.setText(file_name)
            if callback:
                callback()
            
    def browse_save_file(self, line_edit):
        file_name, _ = QFileDialog.getSaveFileName(
            self, 'Save File', '', 'Excel Files (*.xlsx);;All Files (*)'
        )
        if file_name:
            if not file_name.endswith('.xlsx'):
                file_name += '.xlsx'
            line_edit.setText(file_name)
            
    def log_message(self, message):
        """Log message using loguru"""
        logger.info(message)
        
    def run_match(self):
        try:
            # Check file paths
            source_path = self.source_path.text()
            target_path = self.target_path.text()
            output_path = self.output_path.text()
            
            if not all([source_path, target_path, output_path]):
                raise ValueError("Please select all required files")
                
            # Read data
            logger.info("Reading source file...")
            df_source = pd.read_excel(source_path)
            logger.info("Reading target file...")
            df_target = pd.read_excel(target_path)
            
            # Set parameters
            self.compound_match.df_source = df_source
            self.compound_match.df_target = df_target
            self.compound_match.source_mz = self.source_mz_combo.currentText()
            self.compound_match.source_intensity = self.source_intensity_combo.currentText()
            self.compound_match.target_mz = self.target_mz_combo.currentText()
            self.compound_match.output_mz = self.output_mz.text()
            self.compound_match.output_rel_error = self.output_rel_error.text()
            self.compound_match.output_intensity = self.output_intensity.text()
            self.compound_match.intensity_threshold = self.intensity_spin.value()
            self.compound_match.mz_tolerance = self.tolerance_spin.value() * 1e-6
            self.compound_match.output_file = output_path
            
            # Execute matching
            logger.info("Starting matching process...")
            self.compound_match.match()
            
            # Save results
            logger.info("Saving results...")
            self.compound_match.output_process()
            
            # Show success message
            logger.info("Matching completed!")
            QMessageBox.information(self, 'Success', 'Matching completed. Results have been saved to the specified file.')
            
            # Open output directory
            os.startfile(os.path.dirname(output_path))
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            QMessageBox.critical(self, 'Error', f'Operation failed: {str(e)}')

class MolarMassTab(QWidget):
    def __init__(self, calculator):
        super().__init__()
        self.calculator = calculator
        self.initUI()
        self.setup_logger()
        
    def setup_logger(self):
        """Setup logging configuration"""
        # Add custom GUI output handler
        logger.add(
            QTextEditLogger(self.log_text).write,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level="INFO"
        )
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # File selection area
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
        # Input file selection
        input_layout = QHBoxLayout()
        input_label = QLabel('Input File:')
        self.input_path = QLineEdit()
        input_btn = QPushButton('Browse...')
        input_btn.clicked.connect(lambda: self.browse_file(self.input_path, self.update_input_columns))
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(input_btn)
        file_layout.addLayout(input_layout)
        
        # Column selection
        column_layout = QHBoxLayout()
        column_label = QLabel('Formula Column:')
        self.column_combo = QComboBox()
        column_layout.addWidget(column_label)
        column_layout.addWidget(self.column_combo)
        file_layout.addLayout(column_layout)
        
        # Output file selection
        output_layout = QHBoxLayout()
        output_label = QLabel('Output File:')
        self.output_path = QLineEdit()
        output_btn = QPushButton('Browse...')
        output_btn.clicked.connect(lambda: self.browse_save_file(self.output_path))
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_btn)
        file_layout.addLayout(output_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Run button
        run_btn = QPushButton('Calculate Molecular Masses')
        run_btn.clicked.connect(self.run_calculation)
        layout.addWidget(run_btn)
        
        # Log display area
        log_group = QGroupBox("Running Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
    def update_input_columns(self):
        """Update input file column selection dropdown"""
        try:
            df = pd.read_excel(self.input_path.text())
            self.column_combo.clear()
            self.column_combo.addItems(df.columns)
            
            # Try to auto-select formula column
            formula_index = df.columns.str.lower().str.contains('formula').argmax()
            self.column_combo.setCurrentIndex(formula_index)
        except Exception as e:
            logger.error(f"Failed to update columns: {str(e)}")
            
    def browse_file(self, line_edit, callback=None):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Select File', '', 'Excel Files (*.xlsx *.xls);;All Files (*)'
        )
        if file_name:
            line_edit.setText(file_name)
            if callback:
                callback()
            
    def browse_save_file(self, line_edit):
        file_name, _ = QFileDialog.getSaveFileName(
            self, 'Save File', '', 'Excel Files (*.xlsx);;All Files (*)'
        )
        if file_name:
            if not file_name.endswith('.xlsx'):
                file_name += '.xlsx'
            line_edit.setText(file_name)
            
    def run_calculation(self):
        try:
            # Check file paths
            input_path = self.input_path.text()
            output_path = self.output_path.text()
            formula_column = self.column_combo.currentText()
            
            if not all([input_path, output_path, formula_column]):
                raise ValueError("Please select input/output files and formula column")
                
            # Process file
            self.calculator.input_file = input_path
            self.calculator.output_file = output_path
            self.calculator.compounds_col = formula_column
            self.calculator.process_file()
            
            # Show success message
            QMessageBox.information(self, 'Success', 'Calculation completed. Results have been saved to the specified file.')
            
            # Open output directory
            os.startfile(os.path.dirname(output_path))
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            QMessageBox.critical(self, 'Error', f'Operation failed: {str(e)}')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 