import sys
import os
from pathlib import Path
import json
# 设置模块搜索路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QFileDialog, QSpinBox, QDoubleSpinBox, QMessageBox,
                           QTextEdit, QComboBox, QGroupBox, QFormLayout,
                           QTabWidget,QListWidget,QListWidgetItem)
from PyQt5.QtCore import Qt
import pandas as pd
from PyQt5.QtGui import QIcon

# 导入自定义模块
from msidat.match.compound_match import CompoundMatch
from msidat.molar_mass.cal_molar_mass import MolarMassCalculator
from msidat.annotator.make_annotator import Annotator

# 初始化logger
from loguru import logger
import sys

class QTextEditLogger:
    """Custom loguru handler to redirect logs to QTextEdit"""
    def __init__(self, widget):
        self.widget = widget

    def write(self, message):
        # if self.widget and self.widget.isVisible():
        self.widget.append(message.strip())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.compound_match = CompoundMatch()
        self.mol_calculator = MolarMassCalculator()
        self.annotator = Annotator()
        
        # 设置应用程序图标
        if getattr(sys, 'frozen', False):
            # 在打包环境中
            icon_path = os.path.join(os.path.dirname(sys.executable), 'app_icon.ico')
        else:
            # 在开发环境中
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'app_icon.ico')
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            QApplication.instance().setWindowIcon(QIcon(icon_path))
        
        self.setup_style()
        self.initUI()
        
    def setup_style(self):
        """Set global application style"""
        app = QApplication.instance()
        
        # 设置全局字体
        font = app.font()
        font.setFamily("Microsoft YaHei")  # 使用微软雅黑字体
        font.setPointSize(11)  # 设置全局字体大小为11pt
        app.setFont(font)
        
        # 设置全局样式表
        app.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #7aa7e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6b96d1;
            }
            QPushButton:pressed {
                background-color: #5c85c0;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #7aa7e2;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox:focus {
                border: 1px solid #7aa7e2;
            }
            QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 20px;
                min-width: 200px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background-color: #e6e6e6;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: white;
            }
            QLabel {
                color: #333333;
            }
        """)
        
    def initUI(self):
        self.setWindowTitle('MSI Data Analysis Tool v1.1.1')
        self.setGeometry(100, 100, 1600, 1200)  # 增加窗口尺寸
        
        # Create central widget and tab widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)  # 增加布局间距

        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #C2C7CB;
                padding: 10px;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                padding: 8px 20px;
                min-width: 200px;
            }
        """)
        
        # Create molar mass calculator tab
        self.molar_mass_tab = MolarMassTab(self.mol_calculator)
        tab_widget.addTab(self.molar_mass_tab, "Database construction")
        
        # Create compound match tab
        self.compound_match_tab = CompoundMatchTab(self.compound_match)
        tab_widget.addTab(self.compound_match_tab, "MS shift evaluation")
        
        # Create annotator tab
        self.annotator_tab = AnnotatorTab(self.annotator)
        tab_widget.addTab(self.annotator_tab, "Annotation")
        
        # Create log tab
        self.log_tab = LogTab()
        tab_widget.addTab(self.log_tab, "Log")
        
        layout.addWidget(tab_widget)

        # config file selection
        config_file_layout = QHBoxLayout()
        # 添加标签
        config_label = QLabel('Global Config File (Optional):')
        # config_label.setFixedWidth(350)  # 设置标签的固定宽度
        config_file_layout.addWidget(config_label)

        self.config_file = QLineEdit()
        self.config_file.setMinimumHeight(35)
        config_btn = QPushButton('Browse...')
        config_btn.setMinimumSize(120, 35)
        config_btn.clicked.connect(lambda: self.browse_file(self.config_file, self.update_config))
        config_file_layout.addWidget(self.config_file)
        config_file_layout.addWidget(config_btn)
        layout.addLayout(config_file_layout)
        
        # Add developer info at the bottom
        info_label = QLabel("Developed by 朱颖 & 贾历平 | 2025.4.12")
        info_label.setStyleSheet("""
            QLabel {
                color: #666666;
                padding: 5px;
                font-size: 10pt;
            }
        """)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
    
    def browse_file(self, line_edit, callback=None):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Open File', '', 'Excel Files (*.xlsx *.xls *.json);;All Files (*)'
        )
        if file_name:
            line_edit.setText(file_name)
            if callback:
                callback()

    def update_config(self):
        if not os.path.exists(self.config_file.text()):
            QMessageBox.warning(self, "Warning", "Config file not found. Please select a valid file.")
            return
        else:
            logger.info(f"config from {self.config_file.text()} ...")
            self.config_dict = json.load(open(self.config_file.text(), 'r', encoding='utf-8'))
            if 'MolarMassCalculator' in self.config_dict.keys():
                temp_dict = self.config_dict['MolarMassCalculator']
                if 'Elements Mass File' in temp_dict.keys():
                    self.molar_mass_tab.elements_path.setText(os.path.abspath(temp_dict['Elements Mass File']))
                    logger.info(f"set elements mass file to {os.path.abspath(temp_dict['Elements Mass File'])}")
                if 'Adduct Type File' in temp_dict.keys():
                    self.molar_mass_tab.adduct_path.setText(os.path.abspath(temp_dict['Adduct Type File']))
                    logger.info(f"set adduct type file to {os.path.abspath(temp_dict['Adduct Type File'])}")
                    self.molar_mass_tab.update_adduct_type()
                if 'Input File' in temp_dict.keys():
                    self.molar_mass_tab.input_path.setText(os.path.abspath(temp_dict['Input File']))
                    logger.info(f"set input file to {os.path.abspath(temp_dict['Input File'])}")
                    self.molar_mass_tab.update_input_columns()
                if 'Output File' in temp_dict.keys():
                    self.molar_mass_tab.output_path.setText(os.path.abspath(temp_dict['Output File']))
                    logger.info(f"set output file to {os.path.abspath(temp_dict['Output File'])}")
            if 'CompoundMatch' in self.config_dict.keys():
                temp_dict = self.config_dict['CompoundMatch']
                if 'Source File' in temp_dict.keys():
                    self.compound_match_tab.source_path.setText(os.path.abspath(temp_dict['Source File']))
                    logger.info(f"set source file to {os.path.abspath(temp_dict['Source File'])}")
                    self.compound_match_tab.update_source_columns()
                if 'Target File' in temp_dict.keys():
                    self.compound_match_tab.target_path.setText(os.path.abspath(temp_dict['Target File']))
                    logger.info(f"set target file to {os.path.abspath(temp_dict['Target File'])}")
                    self.compound_match_tab.update_target_columns()
                if 'Output File' in temp_dict.keys():
                    self.compound_match_tab.output_path.setText(os.path.abspath(temp_dict['Output File']))
                    logger.info(f"set output file to {os.path.abspath(temp_dict['Output File'])}")
                if 'Output m/z Column' in temp_dict.keys():
                    self.compound_match_tab.output_mz.setText(temp_dict['Output m/z Column'])
                    logger.info(f"set output m/z column to {temp_dict['Output m/z Column']}")
                if 'Output Relative Error Column' in temp_dict.keys():
                    self.compound_match_tab.output_rel_error.setText(temp_dict['Output Relative Error Column'])
                    logger.info(f"set output relative error column to {temp_dict['Output Relative Error Column']}")
                if 'Output Intensity Column' in temp_dict.keys():
                    self.compound_match_tab.output_intensity.setText(temp_dict['Output Intensity Column'])
                    logger.info(f"set output intensity column to {temp_dict['Output Intensity Column']}")
                if 'Intensity Threshold' in temp_dict.keys():
                    self.compound_match_tab.intensity_spin.setValue(temp_dict['Intensity Threshold'])
                    logger.info(f"set intensity threshold to {temp_dict['Intensity Threshold']}")
                if 'm/z Tolerance (ppm)' in temp_dict.keys():
                    self.compound_match_tab.tolerance_spin.setValue(temp_dict['m/z Tolerance (ppm)'])
                    logger.info(f"set m/z tolerance to {temp_dict['m/z Tolerance (ppm)']}")
                    
            if 'Annotator' in self.config_dict.keys():
                temp_dict = self.config_dict['Annotator']
                if 'MSI Data File' in temp_dict.keys():
                    self.annotator_tab.msi_path.setText(os.path.abspath(temp_dict['MSI Data File']))
                    logger.info(f"set msi data file to {os.path.abspath(temp_dict['MSI Data File'])}")
                    self.annotator_tab.update_msi_sheets()
                if 'Database File' in temp_dict.keys():
                    self.annotator_tab.database_path.setText(os.path.abspath(temp_dict['Database File']))
                    logger.info(f"set database file to {os.path.abspath(temp_dict['Database File'])}")
                    self.annotator_tab.update_database_sheets()
                if 'Output File' in temp_dict.keys():
                    self.annotator_tab.output_path.setText(os.path.abspath(temp_dict['Output File']))
                    logger.info(f"set output file to {os.path.abspath(temp_dict['Output File'])}")
                if 'Up Limit (ppm)' in temp_dict.keys():
                    self.annotator_tab.up_limit_ppm.setValue(temp_dict['Up Limit (ppm)'])
                    logger.info(f"set up limit to {temp_dict['Up Limit (ppm)']}")
                if 'Low Limit (ppm)' in temp_dict.keys():
                    self.annotator_tab.low_limit_ppm.setValue(temp_dict['Low Limit (ppm)'])
                    logger.info(f"set low limit to {temp_dict['Low Limit (ppm)']}")
class LogTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setup_logger()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Log display area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                font-size: 12pt;
                padding: 10px;
            }
        """)
        layout.addWidget(self.log_text)
        
        # Clear button
        clear_btn = QPushButton('Clear Log')
        clear_btn.setMinimumSize(200, 40)
        clear_btn.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                padding: 10px;
            }
        """)
        clear_btn.clicked.connect(self.clear_log)
        layout.addWidget(clear_btn)
        
    def setup_logger(self):
        """Setup loguru logger handlers for GUI"""
        try:
            # 移除所有已存在的处理器
            logger.configure(handlers=[], extra={})
            
            # 添加默认的控制台输出（仅在开发环境中）
            if getattr(sys, 'frozen', False):
                # 在打包环境中不添加控制台输出
                pass
            else:
                logger.add(sys.stderr, level="INFO")
                logger.info("GUI logger reset successfully")
                
        except Exception as e:
            print(f"GUI logger reset failed: {str(e)}")
        try:
            # 添加GUI输出处理器
            gui_handler_id = logger.add(
                QTextEditLogger(self.log_text).write,
                format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
                level="INFO"
            )
            
            # 添加文件日志
            try:
                if getattr(sys, 'frozen', False):
                    # 在打包环境中使用相对于exe的路径
                    base_path = os.path.dirname(sys.executable)
                else:
                    # 在开发环境中使用相对于脚本的路径
                    base_path = os.path.dirname(os.path.dirname(__file__))
                
                log_dir = os.path.join(base_path, 'log')
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, 'gui.log')
                
                file_handler_id = logger.add(
                    log_file,
                    rotation="1 day",
                    retention="30 days",
                    level="DEBUG",
                    encoding="utf-8"
                )
                
                logger.info("日志系统初始化成功")
                
            except Exception as e:
                logger.error(f"文件日志初始化失败: {str(e)}")
                
        except Exception as e:
            print(f"GUI日志系统初始化失败: {str(e)}")
            
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
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # File selection area (full width)
        file_group = QGroupBox("File Selection")
        file_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                padding-top: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        file_layout = QFormLayout()
        file_layout.setSpacing(20)
        file_layout.setContentsMargins(15, 15, 15, 15)
        
        # Source file selection
        source_layout = QHBoxLayout()
        self.source_path = QLineEdit()
        self.source_path.setMinimumHeight(35)
        source_btn = QPushButton('Browse...')
        source_btn.setMinimumSize(120, 35)
        source_btn.clicked.connect(lambda: self.browse_file(self.source_path, self.update_source_columns))
        source_layout.addWidget(self.source_path)
        source_layout.addWidget(source_btn)
        file_layout.addRow('Source File:', source_layout)
        
        # Target file selection
        target_layout = QHBoxLayout()
        self.target_path = QLineEdit()
        self.target_path.setMinimumHeight(35)
        target_btn = QPushButton('Browse...')
        target_btn.setMinimumSize(120, 35)
        target_btn.clicked.connect(lambda: self.browse_file(self.target_path, self.update_target_columns))
        target_layout.addWidget(self.target_path)
        target_layout.addWidget(target_btn)
        file_layout.addRow('Target File:', target_layout)
        
        # Output file selection
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setMinimumHeight(35)
        output_btn = QPushButton('Browse...')
        output_btn.setMinimumSize(120, 35)
        output_btn.clicked.connect(lambda: self.browse_save_file(self.output_path))
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_btn)
        file_layout.addRow('Output File:', output_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Create two-column layout for the rest
        two_column_widget = QWidget()
        two_column_layout = QHBoxLayout(two_column_widget)
        two_column_layout.setSpacing(20)
        
        # Left column (5.5)
        left_column = QVBoxLayout()
        left_column.setSpacing(15)
        
        # Column settings area
        columns_group = QGroupBox("Column Settings")
        columns_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                padding-top: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        columns_layout = QFormLayout()
        columns_layout.setSpacing(20)
        columns_layout.setContentsMargins(15, 15, 15, 15)
        
        # Source data column selection
        self.source_mz_combo = QComboBox()
        self.source_mz_combo.setMinimumHeight(35)
        self.source_intensity_combo = QComboBox()
        self.source_intensity_combo.setMinimumHeight(35)
        columns_layout.addRow("Source m/z Column:", self.source_mz_combo)
        columns_layout.addRow("Source Intensity Column:", self.source_intensity_combo)
        
        # Target data column selection
        self.target_mz_combo = QComboBox()
        self.target_mz_combo.setMinimumHeight(35)
        columns_layout.addRow("Target m/z Column:", self.target_mz_combo)
        
        # Output column names
        self.output_mz = QLineEdit('measured m/z')
        self.output_mz.setMinimumHeight(35)
        self.output_rel_error = QLineEdit('Relative Error(ppm)')
        self.output_rel_error.setMinimumHeight(35)
        self.output_intensity = QLineEdit('Intensity')
        self.output_intensity.setMinimumHeight(35)
        columns_layout.addRow("Output m/z Column:", self.output_mz)
        columns_layout.addRow("Output Relative Error Column:", self.output_rel_error)
        columns_layout.addRow("Output Intensity Column:", self.output_intensity)
        
        columns_group.setLayout(columns_layout)
        left_column.addWidget(columns_group)
        
        # Parameter settings area
        params_group = QGroupBox("Parameter Settings")
        params_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                padding-top: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        params_layout = QFormLayout()
        params_layout.setSpacing(20)
        params_layout.setContentsMargins(15, 15, 15, 15)
        
        # Intensity threshold setting
        self.intensity_spin = QSpinBox()
        self.intensity_spin.setMinimumHeight(35)
        self.intensity_spin.setRange(0, 1000000)
        self.intensity_spin.setValue(1000)
        params_layout.addRow('Intensity Threshold:', self.intensity_spin)
        
        # m/z tolerance setting
        self.tolerance_spin = QDoubleSpinBox()
        self.tolerance_spin.setMinimumHeight(35)
        self.tolerance_spin.setRange(0, 1000)
        self.tolerance_spin.setValue(20)
        params_layout.addRow('m/z Tolerance (ppm):', self.tolerance_spin)
        
        params_group.setLayout(params_layout)
        left_column.addWidget(params_group)
        
        # Add left column to two-column layout with stretch factor 55
        two_column_layout.addLayout(left_column, 55)
        
        # Right column (4.5)
        right_column = QVBoxLayout()
        right_column.setSpacing(15)
        
        # Statistics area
        stats_group = QGroupBox("Relative Error Statistics")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                padding-top: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        stats_layout = QFormLayout()
        stats_layout.setSpacing(20)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        
        self.avg_error_label = QLabel('--')
        self.avg_error_label.setMinimumHeight(35)
        self.max_error_label = QLabel('--')
        self.max_error_label.setMinimumHeight(35)
        self.min_error_label = QLabel('--')
        self.min_error_label.setMinimumHeight(35)
        self.std_error_label = QLabel('--')
        self.std_error_label.setMinimumHeight(35)
        
        stats_layout.addRow('Average Relative Error (ppm):', self.avg_error_label)
        stats_layout.addRow('Maximum Relative Error (ppm):', self.max_error_label)
        stats_layout.addRow('Minimum Relative Error (ppm):', self.min_error_label)
        stats_layout.addRow('Standard Deviation (ppm):', self.std_error_label)
        
        stats_group.setLayout(stats_layout)
        right_column.addWidget(stats_group)
        right_column.addStretch()
        
        # Add right column to two-column layout with stretch factor 45
        two_column_layout.addLayout(right_column, 45)
        
        # Add two-column widget to main layout
        layout.addWidget(two_column_widget)
        
        # Run button
        run_btn = QPushButton('Run Evaluation')
        run_btn.setMinimumSize(300, 50)
        run_btn.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                padding: 10px;
            }
        """)
        run_btn.clicked.connect(self.run_match)
        layout.addWidget(run_btn)
        
    def update_source_columns(self):
        """Update source data column selection dropdowns"""
        try:
            df = pd.read_excel(self.source_path.text(),engine='openpyxl')
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
            df = pd.read_excel(self.target_path.text(),engine='openpyxl')
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
            self, 'Save File', '', 'Excel Files (*.xlsx *.xls);;All Files (*)'
        )
        if file_name:
            if not file_name.endswith('.xlsx') and not file_name.endswith('.xls'):
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
            df_source = pd.read_excel(source_path,engine='openpyxl')
            logger.info("Reading target file...")
            df_target = pd.read_excel(target_path,engine='openpyxl')
            
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
            
            # Log statistics
            logger.info("Matching completed!")
            logger.info(f"Average relative error: {self.compound_match.avg_rel_error:.2f} ppm")
            logger.info(f"Maximum relative error: {self.compound_match.max_rel_error:.2f} ppm")
            logger.info(f"Minimum relative error: {self.compound_match.min_rel_error:.2f} ppm")
            logger.info(f"Standard deviation: {self.compound_match.std_rel_error:.2f} ppm")
            
            # Save results
            logger.info("Saving results...")
            self.compound_match.output_process()
            
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
        layout.setSpacing(15)  # 增加垂直间距
        
        # File selection and settings area
        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                padding-top: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        settings_layout = QFormLayout()
        settings_layout.setSpacing(20)  # 增加表单项间距
        settings_layout.setContentsMargins(15, 15, 15, 15)  # 增加边距

        # Input file selection
        input_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setMinimumHeight(35)
        input_btn = QPushButton('Browse...')
        input_btn.setMinimumSize(120, 35)
        input_btn.clicked.connect(lambda: self.browse_file(self.input_path, self.update_input_columns))
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(input_btn)
        settings_layout.addRow('Input File:', input_layout)
        
        # Formula column selection
        self.column_combo = QComboBox()
        self.column_combo.setMinimumHeight(35)
        settings_layout.addRow('Formula Column:', self.column_combo)
        
        # Output file selection
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setMinimumHeight(35)
        output_btn = QPushButton('Browse...')
        output_btn.setMinimumSize(120, 35)
        output_btn.clicked.connect(lambda: self.browse_save_file(self.output_path))
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_btn)
        settings_layout.addRow('Output File:', output_layout)
        # Elements mass file selection
        elements_layout = QHBoxLayout()
        self.elements_path = QLineEdit()
        self.elements_path.setMinimumHeight(35)  # 增加输入框高度
        # default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'elements_mass.json')
        # self.elements_path.setText(default_path)
        elements_btn = QPushButton('Browse...')
        elements_btn.setMinimumSize(120, 35)  # 增加按钮尺寸
        elements_btn.clicked.connect(lambda: self.browse_file(self.elements_path))
        elements_layout.addWidget(self.elements_path)
        elements_layout.addWidget(elements_btn)
        settings_layout.addRow('Elements Mass File:', elements_layout)

        # adduct type file selection
        adduct_file_layout = QHBoxLayout()
        self.adduct_path = QLineEdit()
        self.adduct_path.setMinimumHeight(35)
        # default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'adduct_type.json')
        # self.adduct_path.setText(default_path)
        adduct_btn = QPushButton('Browse...')
        adduct_btn.setMinimumSize(120, 35)
        adduct_btn.clicked.connect(lambda: self.browse_file(self.adduct_path, self.update_adduct_type))
        adduct_file_layout.addWidget(self.adduct_path)
        adduct_file_layout.addWidget(adduct_btn)
        settings_layout.addRow('Adduct Type File:', adduct_file_layout)

        # adduct type selection
        adduct_layout = QHBoxLayout()
        adduct_layout.setSpacing(20)  # 设置水平间距

        # 创建正离子选择区域
        positive_group = QGroupBox("Positive Adduct")
        positive_layout = QVBoxLayout()
        self.positive_list = QListWidget()
        self.positive_list.setMinimumHeight(35)
        self.positive_list.setSelectionMode(QListWidget.MultiSelection)
        positive_layout.addWidget(self.positive_list)
        positive_group.setLayout(positive_layout)
        adduct_layout.addWidget(positive_group)

        # 创建负离子选择区域
        negative_group = QGroupBox("Negative Adduct")
        negative_layout = QVBoxLayout()
        self.negative_list = QListWidget()
        self.negative_list.setMinimumHeight(35)
        self.negative_list.setSelectionMode(QListWidget.MultiSelection)
        negative_layout.addWidget(self.negative_list)
        negative_group.setLayout(negative_layout)
        adduct_layout.addWidget(negative_group)

        if os.path.exists(self.adduct_path.text()):
            self.update_adduct_type()

        # 将布局添加到主布局中
        settings_layout.addRow(adduct_layout)  # 确保 layout 是主布局
        

        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Run button area
        run_btn = QPushButton('Construct Database')
        run_btn.setMinimumHeight(50)  # 只设置高度
        run_btn.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                padding: 10px;
            }
        """)
        run_btn.clicked.connect(self.run_calculation)
        layout.addWidget(run_btn)
        layout.addStretch()

    def update_adduct_type(self):
        """Update adduct type selection dropdown"""
        self.calculator.adduct_type_file = self.adduct_path.text()
        if not os.path.exists(self.calculator.adduct_type_file):
            # 弹窗警告
            QMessageBox.warning(self, "Warning", "Adduct type file not found. Please select a valid file.")
            return
        else:
            adduct_type_df = json.load(open(self.calculator.adduct_type_file, 'r', encoding='utf-8'))
            if ('positve' in adduct_type_df) and ('negative' in adduct_type_df):
                self.positive_list.clear()
                self.positive_list.addItems(adduct_type_df['positve'].keys())
                for index in range(self.positive_list.count()):
                    self.positive_list.item(index).setSelected(True)    
                self.negative_list.clear()
                self.negative_list.addItems(adduct_type_df['negative'].keys())
                for index in range(self.negative_list.count()):
                    self.negative_list.item(index).setSelected(True)
            else:
                QMessageBox.warning(self, "Warning", "Adduct type file format is incorrect. Please select a valid file with 'positve' and 'negative' keys.")
                return

    def update_input_columns(self):
        """Update input file column selection dropdown"""
        try:
            df = pd.read_excel(self.input_path.text(),engine='openpyxl')
            self.column_combo.clear()
            self.column_combo.addItems(df.columns)
            
            # Try to auto-select formula column
            formula_index = df.columns.str.lower().str.contains('formula').argmax()
            self.column_combo.setCurrentIndex(formula_index)
        except Exception as e:
            logger.error(f"Failed to update columns: {str(e)}")
            
    def browse_file(self, line_edit, callback=None):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Select File', '', 'Excel Files (*.xlsx *.xls *.json);;All Files (*)'
        )
        if file_name:
            line_edit.setText(file_name)
            if callback:
                callback()
            
    def browse_save_file(self, line_edit):
        file_name, _ = QFileDialog.getSaveFileName(
            self, 'Save File', '', 'Excel Files (*.xlsx *.xls);;All Files (*)'
        )
        if file_name:
            if not file_name.endswith('.xlsx') and not file_name.endswith('.xls'):
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
            positive_selected_text = [self.positive_list.item(i).text() for i in range(self.positive_list.count()) if self.positive_list.item(i).isSelected()]
            negative_selected_text = [self.negative_list.item(i).text() for i in range(self.negative_list.count()) if self.negative_list.item(i).isSelected()]
            self.calculator.process_file(positive_list=positive_selected_text, negative_list=negative_selected_text, all=False)
            
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
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # File selection area
        file_group = QGroupBox("File Selection")
        file_layout = QFormLayout()
        file_layout.setSpacing(20)
        file_layout.setContentsMargins(15, 15, 15, 15)
        
        # MSI data file selection
        msi_layout = QHBoxLayout()
        self.msi_path = QLineEdit()
        self.msi_path.setMinimumHeight(35)
        msi_btn = QPushButton('Browse...')
        msi_btn.setMinimumSize(120, 35)
        msi_btn.clicked.connect(lambda: self.browse_file(self.msi_path, self.update_msi_sheets))
        msi_layout.addWidget(self.msi_path)
        msi_layout.addWidget(msi_btn)
        file_layout.addRow('MSI Data File:', msi_layout)
        
        # MSI sheet selection
        self.msi_sheet_combo = QComboBox()
        self.msi_sheet_combo.setMinimumHeight(35)
        file_layout.addRow('MSI Sheet:', self.msi_sheet_combo)
        
        # Database file selection
        database_layout = QHBoxLayout()
        self.database_path = QLineEdit()
        self.database_path.setMinimumHeight(35)
        database_btn = QPushButton('Browse...')
        database_btn.setMinimumSize(120, 35)
        database_btn.clicked.connect(lambda: self.browse_file(self.database_path, self.update_database_sheets))
        database_layout.addWidget(self.database_path)
        database_layout.addWidget(database_btn)
        file_layout.addRow('Database File:', database_layout)
        
        # Database sheet selection
        self.database_sheet_combo = QComboBox()
        self.database_sheet_combo.setMinimumHeight(35)
        file_layout.addRow('Database Sheet:', self.database_sheet_combo)
        
        # Output file selection
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setMinimumHeight(35)
        output_btn = QPushButton('Browse...')
        output_btn.setMinimumSize(120, 35)
        output_btn.clicked.connect(lambda: self.browse_save_file(self.output_path))
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(output_btn)
        file_layout.addRow('Output File:', output_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Parameters area
        param_group = QGroupBox("Parameters")
        param_layout = QFormLayout()
        param_layout.setSpacing(20)
        param_layout.setContentsMargins(15, 15, 15, 15)
        
        self.up_limit_ppm = QDoubleSpinBox()
        self.up_limit_ppm.setMinimumHeight(35)
        self.up_limit_ppm.setRange(-1000, 1000)
        self.up_limit_ppm.setDecimals(2)
        self.up_limit_ppm.setValue(10)
        self.up_limit_ppm.setSingleStep(0.1)
        param_layout.addRow('Upper Limit (ppm):', self.up_limit_ppm)
        
        self.low_limit_ppm = QDoubleSpinBox()
        self.low_limit_ppm.setMinimumHeight(35)
        self.low_limit_ppm.setRange(-1000, 1000)
        self.low_limit_ppm.setDecimals(2)
        self.low_limit_ppm.setValue(-10)
        self.low_limit_ppm.setSingleStep(0.1)
        param_layout.addRow('Lower Limit (ppm):', self.low_limit_ppm)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # Add spacing between parameter group and run button
        spacer = QWidget()
        spacer.setFixedHeight(20)
        layout.addWidget(spacer)
        
        # Run button
        run_btn = QPushButton('Run Annotation')
        run_btn.setMinimumSize(300, 50)
        run_btn.setStyleSheet("""
            QPushButton {
                font-size: 12pt;
                padding: 10px;
            }
        """)
        run_btn.clicked.connect(self.run_annotation)
        layout.addWidget(run_btn)
        
        # Add spacing at the bottom
        layout.addStretch(1)
        
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
            "Excel Files (*.xlsx *.xls);;All Files (*.*)"
        )
        if file_name:
            if not file_name.endswith('.xlsx') and not file_name.endswith('.xls'):
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

if __name__ == '__main__':
    main() 