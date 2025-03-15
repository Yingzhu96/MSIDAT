import os,sys
import numpy as np
import json
import re
from loguru import logger

elements_mass_file = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'database', 'elements_mass.json')

def MolMass(compounds_str):
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
    ele_mass = json.load(open(elements_mass_file, 'r'))['ele_mass']
    # 去除[]
    compounds_str = compounds_str.strip('[]')
    compounds_list = compounds_str.replace(',', ' ').replace(';', ' ').split(' ')
    logger.info('compound list: %s' %compounds_list)
    ele_list = []
    for compound in compounds_list:
        for item in compound_split(compound):
            ele_list.append(item)
    logger.info('element list: %s' %ele_list)
    molar_mass = 0
    for item in ele_list:
        _cnt = int(item[1]) if item[1] else 1
        # logger.info(item)
        if item[0] not in ele_mass.keys():
            raise ValueError('Invalid element: ' + item[0])
            return -1
        if 'e' in item[2]:
            molar_mass += ele_mass[item[2]] * _cnt
        else:
            if (item[2] == '+') | (item[2] == '-'):
                molar_mass += ele_mass[item[0]]
                molar_mass += ele_mass['e'+item[2]] * _cnt
            else:
                molar_mass += ele_mass[item[0]] * _cnt
    return molar_mass
    
def compound_split(compound_str):
    '''
    Objective: split a compound into its elements and their number
    Input: string
    return: list
    '''
    ele_mass = json.load(open(elements_mass_file,'r'))
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