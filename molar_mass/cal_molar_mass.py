import os,sys
import numpy as np
import pandas as pd
import json
import re
from loguru import logger

class MolarMassCalculator(object):
    def __init__(self, input_file=None, output_file=None, compounds_col='Formula', 
                 input_sheet=0, elements_mass_file=None, adduct_type_file=None):
        # self._elements_mass_file = os.path.join(
        #     os.path.dirname(os.path.dirname(__file__)), 'database', 'elements_mass.json')
        # self._adduct_type_file = os.path.join(
        #     os.path.dirname(os.path.dirname(__file__)), 'database', 'adduct_type.json')
        self._elements_mass_file = elements_mass_file
        self._ele_mass = {}
        if self._elements_mass_file:
            self.get_ele_mass()
        self._adduct_type_file = adduct_type_file
        self._input_file = input_file
        self._input_sheet = input_sheet
        self._output_file = output_file
        self._compounds_col = compounds_col

    def cal_molar_mass(self, compounds_str):
        '''
        Objective: To find the molecular mass of a given compounds
        Input: string
        Constraints:
            1. single compound should be in the form of C6H12O6
            2. compounds should be separated by space or comma or semicolon
            3. ions should be in the form of Fe2+ or Cl-
            4. electrons mass is considered in ions
        return: float
        '''
        # 去除[]
        if not self._ele_mass:
            raise ValueError('Elements mass not found. Please select a valid file.')
        compounds_str = compounds_str.strip('[]')
        compounds_list = compounds_str.replace(',', ' ').replace(';', ' ').split(' ')
        logger.debug('compound list: %s' %compounds_list)
        ele_list = []
        for compound in compounds_list:
            for item in self.compound_split(compound):
                ele_list.append(item)
        logger.debug('element list: %s' %ele_list)
        molar_mass = 0
        for item in ele_list:
            _cnt = int(item[1]) if item[1] else 1
            # logger.info(item)
            if item[0] not in self._ele_mass.keys():
                raise ValueError('Invalid element: ' + item[0])
                return -1
            if 'e' in item[2]:
                molar_mass += self._ele_mass[item[2]] * _cnt
            else:
                if (item[2] == '+') | (item[2] == '-'):
                    molar_mass += self._ele_mass[item[0]]
                    molar_mass += self._ele_mass['e'+item[2]] * _cnt
                else:
                    molar_mass += self._ele_mass[item[0]] * _cnt
        return molar_mass
    
    def compound_split(self, compound_str):
        '''
        Objective: split a compound into its elements and their number
        Input: string
        return: list
        '''
        # 识别()内容
        ele_group_pare = re.findall(r'\(([^()]+)\)(\d*)([+-]?)',compound_str) 
        # logger.info(ele_group_pare)
        # 去掉括号及其内的所有字符，以及括号外的数字
        compound_str_nopare = re.sub(r'\([^()]+\)(\d*[+-]?)','',compound_str)
        # logger.info(compound_str_nopare)
        ele_group_nopare = re.findall(r'([A-Z][a-z]?)(\d*)([+-]?)',compound_str_nopare)
        # logger.info(ele_group_nopare)
        ele_group = ele_group_nopare
        for item in ele_group_pare:
            ele_group_sub = re.findall(r'([A-Z][a-z]?)(\d*)([+-]?)',item[0])
            if (item[2] == '+') | (item[2] == '-'):
                [ele_group.append(v) for v in ele_group_sub]
                ele_group.append(['e'+item[2],item[1],item[2]])
            else:
                cnt_ = 1 if item[1] == '' else int(item[1])
                [[ele_group.append(v) for v in ele_group_sub] for i in range(cnt_)]
        # logger.info(ele_group)
        return ele_group

    def process_file(self, positive_list=None, negative_list=None, all=True):
        logger.info('Start processing file')
        df = pd.read_excel(self._input_file,engine='openpyxl',sheet_name=self._input_sheet)
        compounds_series = df.loc[:,self._compounds_col]
        result = np.array([self.cal_molar_mass(v) for v in compounds_series])
        index = df.shape[1]
        df.insert(index, 'Monoisotopic Molecular Weight', result)
        df.insert(index+1, 'ID', df.index + 1)
        df2 = df.copy()

        adduct_set = json.load(open(self._adduct_type_file, 'r', encoding='utf-8'))
        adduct_set_positive = adduct_set['positve']
        adduct_set_negative = adduct_set['negative']
        if all:
            positive_list = adduct_set_positive.keys()
            negative_list = adduct_set_negative.keys()

        logger.info(f"Positive list: {positive_list}")
        logger.info(f"Negative list: {negative_list}")

        for adduct, idx in zip(positive_list, range(index+2, index+2+len(positive_list))):
            df.insert(idx, '[%s]+' %adduct, result+adduct_set_positive[adduct])
        df.round(5)

        for adduct, idx in zip(negative_list, range(index+2, index+2+len(negative_list))):
            df2.insert(idx, '[%s]-' %adduct, result+adduct_set_negative[adduct])
        df2.round(5)


        # df.insert(4, '[M+H]+', result+1.0072766)
        # df.insert(5, '[M+Na]+', result+22.9892213)
        # df.insert(6, '[M+K]+', result+38.9631585)
        # df.insert(7, '[M+NH4]+', result+18.0338257)
        # df.insert(8, '[M+H-H2O]+', result+17.0032880)
        # df.insert(9, '[M]+', result-0.0005484)
        # df.round(5)

        # df2.insert(4, '[M-H]-', result-1.0072766)
        # df2.insert(5, '[M+Cl]-', result+34.9694011)
        # df2.insert(6, '[M-H-H2O]-', result-19.0178413)
        # df2.insert(7, '[M+CH3COO]-', result+59.0138527)
        # df2.insert(8, '[M+HCOO]-', result+44.9982026)
        # df2.round(5)

        with pd.ExcelWriter(self._output_file) as writer:
            if positive_list:
                df.to_excel(writer, sheet_name='positive',index=False)
            if negative_list:
                df2.to_excel(writer, sheet_name='negative',index=False)
        logger.info('Molar mass calculation completed, total %d rows processed' %len(df))
        logger.info('Output file: %s' %self._output_file)
        
    def get_ele_mass(self):
        if not os.path.exists(self._elements_mass_file):
            raise ValueError('Elements mass file not found. Please select a valid file.')
        else:
            try:    
                self._ele_mass = json.load(open(self._elements_mass_file, 'r', encoding='utf-8'))['ele_mass']
                logger.info(f"ele_mass: {self._ele_mass}")
            except Exception as e:
                raise ValueError('Elements mass file format is incorrect. Please select a valid file.')

    @property
    def elements_mass_file(self):
        return self._elements_mass_file
    @elements_mass_file.setter
    def elements_mass_file(self, value):
        self._elements_mass_file = value
        logger.info(f"elements_mass_file: {self._elements_mass_file}") 
        self.get_ele_mass()

    @property
    def adduct_type_file(self):
        return self._adduct_type_file
    @adduct_type_file.setter
    def adduct_type_file(self, value):
        self._adduct_type_file = value
    @property
    def input_file(self):
        return self._input_file
    @input_file.setter
    def input_file(self, value):
        self._input_file = value
    @property
    def output_file(self):
        return self._output_file
    @output_file.setter
    def output_file(self, value):
        self._output_file = value
    @property
    def compounds_col(self):
        return self._compounds_col
    @compounds_col.setter
    def compounds_col(self, value):
        self._compounds_col = value
    @property
    def input_sheet(self):
        return self._input_sheet
    @input_sheet.setter
    def input_sheet(self, value):
        self._input_sheet = value
        

