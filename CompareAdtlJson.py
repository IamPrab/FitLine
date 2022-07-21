import csv
import genericpath

import xlsxwriter
import json
import numpy
import numpy as np
from numpy.polynomial.polynomial import polyfit
import os
import math
import os.path
from os import path
import xlwings as xw

if __name__ == '__main__':

    path = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_Z\\ADTL_Equations.adtl.json"

    with open(path) as data:
        d = json.load(data)
        data.close()

    workbook = xlsxwriter.Workbook("C:\\Users\\kaurp\\Downloads\\60Z01NEW_15500.xlsx")
    worksheet = workbook.add_worksheet()

    header = ['TP','TestName', 'Slope', 'Intercept', 'X_15500', 'X_13500']
    worksheet.write_row(0, 0, header)
    count = 1

    for equation  in d:
        testname= equation["SourceTestName"]
        intercept = float(equation["Intercept"])
        slope = float(equation["Slope"])

        YHigh = (slope*15500) + intercept
        YLow = (slope*13500) + intercept

        rowData = ['60Z',testname,slope,intercept,YHigh,YLow ]
        worksheet.write_row(count, 0, rowData)
        count = count + 1

    workbook.close()

