import os
import pandas as pd
import numpy as np
from loguru import logger

class CompoundMatch(object):
    def __init__(self, df_source=None, df_target=None):
        self._df_source = df_source
        self._df_target = df_target
        self._df_output = pd.DataFrame()
        self._source_mz = 'm/z'
        self._source_intensity = 'Intensity'
        self._target_mz = 'Theoretical m/z'
        self._output_mz = 'measured m/z'
        self._output_rel_error = 'Relative Error(ppm)'
        self._output_intensity = 'Intensity'
        self._intensity_threshold = 1000
        self._mz_tolerance = 20e-6
        self._output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                      'userdata','output_mz.xlsx')

    def match(self):
        logger.info("source data shape: {}".format(self._df_source.shape))
        logger.info("target data shape: {}".format(self._df_target.shape))
        logger.info("intensity_threshold: {}".format(self._intensity_threshold))
        logger.info("mz tolerance: {} ppm".format(self._mz_tolerance*1e6))
        self._df_output = self._df_target.copy()
        self._df_output[self._output_mz] = self._df_target[self._target_mz].apply(self.find_once)
        self._df_output[self._output_rel_error] = (self._df_output[self._output_mz] - 
                self._df_output[self._target_mz]) / self._df_output[self._target_mz] * 1e6
        # self._df_output[self._output_intensity] = self._df_output[self._output_mz].apply(self.find_intensity)

    def find_once(self, theoretical_mz):
        """
        Find the closest m/z value in the source data to the theoretical m/z value in the target data.
        """
        mz_diff = np.abs((self._df_source[self._source_mz] - theoretical_mz)/theoretical_mz)
        if mz_diff.min() < self._mz_tolerance:
            if self._df_source.loc[mz_diff.idxmin(), self._source_intensity] > self._intensity_threshold:
                return self._df_source[self._source_mz].iloc[mz_diff.idxmin()]
        return np.nan
    
    def find_intensity(self, source_mz):
        """
        Find the intensity of the m/z value in the source data.
        """
        if pd.notna(source_mz):
            intensity = self._df_source.loc[np.where(self._df_source[self._source_mz] == source_mz), 
                                   self._source_intensity].values[0]
        else:
            intensity = np.nan
        logger.debug("source_mz: {}".format(source_mz))
        return intensity
    
    def output_process(self):
        """
        Save the output DataFrame to an Excel file.
        """
        os.makedirs(os.path.dirname(self._output_file), exist_ok=True)
        # 将 DataFrame 写入 Excel 文件
        self._df_output.to_excel(self._output_file, index=False)
        logger.info(f"Output successfully saved to {self._output_file}")


    @property
    def df_source(self):
        return self._df_source
    @df_source.setter
    def df_source(self, value):
        self._df_source = value
    @property
    def df_target(self):
        return self._df_target
    @df_target.setter
    def df_target(self, value):
        self._df_target = value
    @property
    def df_output(self):
        return self._df_output
    @df_output.setter
    def df_output(self, value):
        self._df_output = value
    @property
    def source_mz(self):
        return self._source_mz
    @source_mz.setter
    def source_mz(self, value):
        self._source_mz = value
    @property
    def source_intensity(self):
        return self._source_intensity
    @source_intensity.setter
    def source_intensity(self, value):
        self._source_intensity = value
    @property
    def target_mz(self):
        return self._target_mz
    @target_mz.setter
    def target_mz(self, value):
        self._target_mz = value
    @property
    def output_mz(self):
        return self._output_mz
    @output_mz.setter
    def output_mz(self, value):
        self._output_mz = value
    @property
    def output_intensity(self):
        return self._output_intensity
    @output_intensity.setter
    def output_intensity(self, value):
        self._output_intensity = value
    @property
    def intensity_threshold(self):
        return self._intensity_threshold
    @intensity_threshold.setter
    def intensity_threshold(self, value):
        self._intensity_threshold = value
    @property
    def mz_tolerance(self):
        return self._mz_tolerance
    @mz_tolerance.setter
    def mz_tolerance(self, value):
        self._mz_tolerance = value
    @property
    def output_file(self):
        return self._output_file
    @output_file.setter
    def output_file(self, value):
        self._output_file = value

