import os,sys
import numpy as np
import pandas as pd

def make_Annotator(msidata_path=None,basedata=None,uplimit=1e-5,downlimit=-1e-5):
    database_path = r'C:\Users\jlp10\Desktop\朱颖\python代码\Database.xlsx' if basedata is None else basedata 
    msidata_path = r'C:\Users\jlp10\Desktop\朱颖\python代码\MSIdata.xlsx' if msidata_path is None else msidata_path

    data_base = pd.read_excel(database_path)
    msi_data = pd.read_excel(msidata_path)

    base_row, base_col = data_base.shape
    msi_row, msi_col = msi_data.shape

    Annotator = pd.DataFrame(np.zeros((msi_row,base_col-2),dtype=np.str_))
    # for i in range(msi_row):
    #     Annotator.iloc[i,0] = msi_data.iloc[i,0]
    Annotator.columns = np.r_[[msi_data.columns[0]],data_base.columns[4:].to_numpy(),['total']]
    Annotator[Annotator.columns[0]] = msi_data.iloc[:,0]

    def Annotator_ele(i,j):
        # index = np.nonzero((np.abs(data_base.iloc[:,i] - msi_data.iloc[j,0])/data_base.iloc[:,i]).to_numpy() < 10e-6)
        index = np.nonzero(
            ((data_base.iloc[:,i] - msi_data.iloc[j,0]/data_base.iloc[:,i]).to_numpy() < uplimit) &
            ((data_base.iloc[:,i] - msi_data.iloc[j,0]/data_base.iloc[:,i]).to_numpy() > downlimit))
        if len(index[0]):
            Annotator.iloc[j,i-3] = ';'.join([str(v) for v in data_base.iloc[index[0],0]])
    [Annotator_ele(i,j) for i in range(4,base_col) for j in range(msi_row)]

    # for i in range(4,base_col):
    #     for j in range(msi_row):
    #         str1 = ''
    #         str0 = ''
    #         for k in range(base_row):
    #             theor = float(data_base.iloc[k,i])
    #             mea = float(msi_data.iloc[j,0])
    #             if abs(theor-mea)/theor < 10*10e-6:
    #                 str1 = data_base.iloc[k,0]
    #                 str0 = ';'.join([str0,str1]) if str0 else str1
    #                 Annotator.iloc[j,i-3] = str0

    for i in range(msi_row):
        str2adduct = ''
        str3adduct = ''
        for j in range(1,base_col-3):
            if Annotator.iloc[i,j] != '':
                str2adduct = ';'.join([str(Annotator.iloc[i,j]),Annotator.columns[j]])
                str3adduct = '/'.join([str3adduct,str2adduct]) if str3adduct else str2adduct
                Annotator.iloc[i,base_col-3] = str3adduct
    
    return Annotator
