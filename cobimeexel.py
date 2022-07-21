from pathlib import Path  # Standard Python Module
import time  # Standard Python Module

import xlsxwriter
import xlwings as xw  # pip install xlwings
import os


def combine_one_wb():
    excel_files = os.listdir("\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_60YLots\\AllApprovalsModuleWise")
    print(excel_files)
    combined_wb = xw.Book()

    for excel_file in excel_files:
        name = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_60YLots\\AllApprovalsModuleWise\\" + excel_file
        wb = xw.Book(name)
        for sheet in wb.sheets:
            sheet.copy(after=combined_wb.sheets[0])
        wb.close()

    combined_wb.sheets[0].delete()
    combined_wb.save(f'\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_60YLots\\ApprovalFile.xlsx')
    if len(combined_wb.app.books) == 1:
        combined_wb.app.quit()
    else:
        combined_wb.close()

def combine_to_ws():
    workbook = xlsxwriter.Workbook('\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_60YLots\\AllApprovalsModuleWise')
    workbook.close()
    wkb = xw.books.open('\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_60YLots\\ApprovalFile.xl')
    AllDataSheet = wkb.sheets.add(name = "AllData", after = "Orders")


if __name__ == '__main__':
    combine_one_wb()
