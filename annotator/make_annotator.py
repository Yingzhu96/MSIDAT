import os,sys
import numpy as np
import pandas as pd

class Annotator(object):
    def __init__(self,msidata_path=None,basedata_path=None,output_path=None,
                 database_sheet=0,msidata_sheet=0,up_limit_ppm=10,low_limit_ppm=-10):
        self.database_path = basedata_path
        self.msidata_path = msidata_path
        self.database_sheet = database_sheet
        self.msidata_sheet = msidata_sheet
        self.output_path = output_path
        self.up_limit_ppm = up_limit_ppm
        self.low_limit_ppm = low_limit_ppm
    
    def make_annotator(self):
        self.data_base = pd.read_excel(self.database_path,sheet_name=self.database_sheet)
        self.msi_data = pd.read_excel(self.msidata_path,sheet_name=self.msidata_sheet)

        base_row, base_col = self.data_base.shape
        msi_row, msi_col = self.msi_data.shape

        self.Annotator = pd.DataFrame(np.zeros((msi_row,base_col-2),dtype=np.str_))
        self.Annotator.columns = np.r_[[self.msi_data.columns[0]],self.data_base.columns[4:].to_numpy(),['total']]
        self.Annotator[self.Annotator.columns[0]] = self.msi_data.iloc[:,0]

        [self.Annotator_ele(i,j) for i in range(4,base_col) for j in range(msi_row)]

        for i in range(msi_row):
            str2adduct = ''
            str3adduct = ''
            for j in range(1,base_col-3):
                if self.Annotator.iloc[i,j] != '':
                    str2adduct = ';'.join([str(self.Annotator.iloc[i,j]),self.Annotator.columns[j]])
                    str3adduct = '/'.join([str3adduct,str2adduct]) if str3adduct else str2adduct
                    self.Annotator.iloc[i,base_col-3] = str3adduct

        self.Annotator.to_excel(self.output_path,index=False)
        return self.Annotator

    def Annotator_ele(self,i,j):
        index = np.nonzero(
            (((self.data_base.iloc[:,i] - self.msi_data.iloc[j,0])/self.data_base.iloc[:,i]).to_numpy() < self.up_limit_ppm/1e6) &
            (((self.data_base.iloc[:,i] - self.msi_data.iloc[j,0])/self.data_base.iloc[:,i]).to_numpy() > self.low_limit_ppm/1e6))
        if len(index[0]):
            self.Annotator.iloc[j,i-3] = ';'.join([str(v) for v in self.data_base.iloc[index[0],0]])

    @property
    def database_path(self):
        return self._database_path
    @database_path.setter
    def database_path(self, value):
        self._database_path = value
    
    @property
    def msidata_path(self): 
        return self._msidata_path
    @msidata_path.setter
    def msidata_path(self, value):
        self._msidata_path = value

    @property
    def up_limit_ppm(self):
        return self._up_limit_ppm
    @up_limit_ppm.setter
    def up_limit_ppm(self, value):
        self._up_limit_ppm = value

    @property
    def low_limit_ppm(self):
        return self._low_limit_ppm
    @low_limit_ppm.setter
    def low_limit_ppm(self, value):
        self._low_limit_ppm = value

    @property
    def output_path(self):
        return self._output_path
    @output_path.setter
    def output_path(self, value):
        self._output_path = value

    @property
    def database_sheet(self):
        return self._database_sheet
    @database_sheet.setter
    def database_sheet(self, value):
        self._database_sheet = value
    
    @property
    def msidata_sheet(self):
        return self._msidata_sheet
    @msidata_sheet.setter
    def msidata_sheet(self, value):
        self._msidata_sheet = value
        
