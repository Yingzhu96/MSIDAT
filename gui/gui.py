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
from msidat.annotator.make_annotator import Annotator

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
        self.annotator = Annotator()
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
        
        # Create molar mass calculator tab
        molar_mass_tab = MolarMassTab(self.mol_calculator)
        tab_widget.addTab(molar_mass_tab, "Molar Mass Calculator")
        
        # Create compound match tab
        compound_match_tab = CompoundMatchTab(self.compound_match)
        tab_widget.addTab(compound_match_tab, "Compound Match")
        
        # Create annotator tab
        annotator_tab = AnnotatorTab(self.annotator)
        tab_widget.addTab(annotator_tab, "Annotator")
        
        # Create log tab
        log_tab = LogTab()
        tab_widget.addTab(log_tab, "Log")
        
        layout.addWidget(tab_widget)

class LogTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setup_logger()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Log display area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Clear button
        clear_btn = QPushButton('Clear Log')
        clear_btn.clicked.connect(self.clear_log)
        layout.addWidget(clear_btn)
        
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
        
    def clear_log(self):
        """Clear the log display"""
        self.log_text.clear()

class CompoundMatchTab(QWidget):
    def __init__(self, compound_match):
        super().__init__()
        self.compound_match = compound_match
        self.initUI()
        
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
        
        # Statistics area
        stats_group = QGroupBox("Relative Error Statistics")
        stats_layout = QFormLayout()
        
        self.avg_error_label = QLabel('--')
        self.max_error_label = QLabel('--')
        self.min_error_label = QLabel('--')
        self.std_error_label = QLabel('--')
        
        stats_layout.addRow('Average Relative Error (ppm):', self.avg_error_label)
        stats_layout.addRow('Maximum Relative Error (ppm):', self.max_error_label)
        stats_layout.addRow('Minimum Relative Error (ppm):', self.min_error_label)
        stats_layout.addRow('Standard Deviation (ppm):', self.std_error_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Run button
        run_btn = QPushButton('Run Matching')
        run_btn.clicked.connect(self.run_match)
        layout.addWidget(run_btn)
        
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
            
            # Update statistics display
            self.avg_error_label.setText(f"{self.compound_match.avg_rel_error:.2f}")
            self.max_error_label.setText(f"{self.compound_match.max_rel_error:.2f}")
            self.min_error_label.setText(f"{self.compound_match.min_rel_error:.2f}")
            self.std_error_label.setText(f"{self.compound_match.std_rel_error:.2f}")
            
            # Save results
            logger.info("Saving results...")
            self.compound_match.output_process()
            
            # Log statistics
            logger.info("Matching completed!")
            logger.info(f"Average relative error: {self.compound_match.avg_rel_error:.2f} ppm")
            logger.info(f"Maximum relative error: {self.compound_match.max_rel_error:.2f} ppm")
            logger.info(f"Minimum relative error: {self.compound_match.min_rel_error:.2f} ppm")
            logger.info(f"Standard deviation: {self.compound_match.std_rel_error:.2f} ppm")
            
            # Show success message
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
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # 设置垂直间距
        
        # File selection and settings area
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout()
        settings_layout.setSpacing(15)  # 设置表单项间距
        
        # Elements mass file selection
        elements_layout = QHBoxLayout()
        self.elements_path = QLineEdit()
        default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'elements_mass.json')
        self.elements_path.setText(default_path)  # 设置默认值
        elements_btn = QPushButton('Browse...')
        elements_btn.setFixedWidth(100)
        elements_btn.clicked.connect(lambda: self.browse_file(self.elements_path))
        elements_layout.addWidget(self.elements_path)
        elements_layout.addWidget(elements_btn)
        settings_layout.addRow('Elements Mass File:', elements_layout)
        
        # Input file selection
        input_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        input_btn = QPushButton('Browse...')
        input_btn.setFixedWidth(100)  # 固定按钮宽度
        input_btn.clicked.connect(lambda: self.browse_file(self.input_path, self.update_input_columns))
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(input_btn)
        settings_layout.addRow('Input File:', input_layout)
        
        # Formula column selection
        self.column_combo = QComboBox()
        settings_layout.addRow('Formula Column:', self.column_combo)
        
        # Output file selection
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        output_btn = QPushButton('Browse...')
        output_btn.setFixedWidth(100)  # 固定按钮宽度
        output_btn.clicked.connect(lambda: self.browse_save_file(self.output_path))
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_btn)
        settings_layout.addRow('Output File:', output_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Run button area
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 添加弹性空间使按钮居中
        run_btn = QPushButton('Calculate Molecular Masses')
        # run_btn.setFixedWidth(400)  # 增加按钮宽度
        # run_btn.setFixedHeight(40)  # 增加按钮高度
        # run_btn.setStyleSheet("font-size: 12pt;")  # 设置字体大小
        run_btn.clicked.connect(self.run_calculation)
        button_layout.addWidget(run_btn)
        button_layout.addStretch()  # 添加弹性空间使按钮居中
        
        layout.addLayout(button_layout)
        layout.addStretch()  # 添加弹性空间将内容推到顶部
        
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
            elements_path = self.elements_path.text()
            formula_column = self.column_combo.currentText()
            
            if not all([input_path, output_path, elements_path, formula_column]):
                raise ValueError("Please select all required files and formula column")
                
            # Process file
            self.calculator.input_file = input_path
            self.calculator.output_file = output_path
            self.calculator.elements_mass_file = elements_path
            self.calculator.compounds_col = formula_column
            self.calculator.process_file()
            
            # Show success message
            QMessageBox.information(self, 'Success', 'Calculation completed. Results have been saved to the specified file.')
            
            # Open output directory
            os.startfile(os.path.dirname(output_path))
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            QMessageBox.critical(self, 'Error', f'Operation failed: {str(e)}')

class AnnotatorTab(QWidget):
    def __init__(self, annotator):
        super().__init__()
        self.annotator = annotator
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Compound Annotation Tool')
        self.setGeometry(100, 100, 1000, 800)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # File selection area
        file_group = QGroupBox("File Selection")
        file_layout = QFormLayout()
        
        # MSI data file selection
        self.msi_path = QLineEdit()
        msi_btn = QPushButton('Browse...')
        msi_btn.clicked.connect(lambda: self.browse_file(self.msi_path, self.update_msi_sheets))
        msi_layout = QHBoxLayout()
        msi_layout.addWidget(self.msi_path)
        msi_layout.addWidget(msi_btn)
        file_layout.addRow('MSI Data File:', msi_layout)
        
        # MSI sheet selection
        self.msi_sheet_combo = QComboBox()
        file_layout.addRow('MSI Sheet:', self.msi_sheet_combo)
        
        # Database file selection
        self.database_path = QLineEdit()
        database_btn = QPushButton('Browse...')
        database_btn.clicked.connect(lambda: self.browse_file(self.database_path, self.update_database_sheets))
        database_layout = QHBoxLayout()
        database_layout.addWidget(self.database_path)
        database_layout.addWidget(database_btn)
        file_layout.addRow('Database File:', database_layout)
        
        # Database sheet selection
        self.database_sheet_combo = QComboBox()
        file_layout.addRow('Database Sheet:', self.database_sheet_combo)
        
        # Output file selection
        self.output_path = QLineEdit()
        output_btn = QPushButton('Browse...')
        output_btn.clicked.connect(lambda: self.browse_save_file(self.output_path))
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_btn)
        file_layout.addRow('Output File:', output_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Parameters area
        param_group = QGroupBox("Parameters")
        param_layout = QFormLayout()
        
        self.up_limit_ppm = QDoubleSpinBox()
        self.up_limit_ppm.setRange(-1000, 1000)
        self.up_limit_ppm.setDecimals(2)
        self.up_limit_ppm.setValue(10)
        self.up_limit_ppm.setSingleStep(0.1)
        param_layout.addRow('Upper Limit (ppm):', self.up_limit_ppm)
        
        self.low_limit_ppm = QDoubleSpinBox()
        self.low_limit_ppm.setRange(-1000, 1000)
        self.low_limit_ppm.setDecimals(2)
        self.low_limit_ppm.setValue(-10)
        self.low_limit_ppm.setSingleStep(0.1)
        param_layout.addRow('Lower Limit (ppm):', self.low_limit_ppm)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # Run button
        run_btn = QPushButton('Run Annotation')
        run_btn.clicked.connect(self.run_annotation)
        layout.addWidget(run_btn)
        
    def update_msi_sheets(self):
        """Update MSI file sheet selection dropdown"""
        try:
            if self.msi_path.text():
                excel_file = pd.ExcelFile(self.msi_path.text())
                self.msi_sheet_combo.clear()
                self.msi_sheet_combo.addItems(excel_file.sheet_names)
                logger.info(f"Found {len(excel_file.sheet_names)} sheets in MSI file")
        except Exception as e:
            logger.error(f"Failed to update MSI sheets: {str(e)}")
            
    def update_database_sheets(self):
        """Update database file sheet selection dropdown"""
        try:
            if self.database_path.text():
                excel_file = pd.ExcelFile(self.database_path.text())
                self.database_sheet_combo.clear()
                self.database_sheet_combo.addItems(excel_file.sheet_names)
                logger.info(f"Found {len(excel_file.sheet_names)} sheets in database file")
        except Exception as e:
            logger.error(f"Failed to update database sheets: {str(e)}")
        
    def browse_file(self, line_edit, callback=None):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*.*)"
        )
        if file_name:
            line_edit.setText(file_name)
            if callback:
                callback()
            
    def browse_save_file(self, line_edit):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Excel Files (*.xlsx);;All Files (*.*)"
        )
        if file_name:
            if not file_name.endswith('.xlsx'):
                file_name += '.xlsx'
            line_edit.setText(file_name)
            
    def run_annotation(self):
        try:
            # Validate inputs
            if not self.msi_path.text() or not self.database_path.text() or not self.output_path.text():
                QMessageBox.warning(self, "Warning", "Please select all required files.")
                return
                
            # Update annotator parameters
            self.annotator.msidata_path = self.msi_path.text()
            self.annotator.database_path = self.database_path.text()
            self.annotator.output_path = self.output_path.text()
            self.annotator.up_limit_ppm = self.up_limit_ppm.value()
            self.annotator.low_limit_ppm = self.low_limit_ppm.value()
            
            # Set sheet selections
            self.annotator.msidata_sheet = self.msi_sheet_combo.currentIndex()
            self.annotator.database_sheet = self.database_sheet_combo.currentIndex()
            
            # Run annotation
            logger.info("Starting annotation process...")
            logger.info(f"Using MSI sheet: {self.msi_sheet_combo.currentText()}")
            logger.info(f"Using database sheet: {self.database_sheet_combo.currentText()}")
            logger.info(f"Using limits: {self.low_limit_ppm.value()} ppm to {self.up_limit_ppm.value()} ppm")
            result = self.annotator.make_annotator()
            logger.info("Annotation completed successfully!")
            logger.info(f"Results saved to: {self.output_path.text()}")
            
            QMessageBox.information(self, "Success", "Annotation completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during annotation: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 