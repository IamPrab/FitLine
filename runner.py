import os



if __name__ == '__main__':
    files = os.listdir("\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_60Y\\AllData")

    for file in files:
        namefile= "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_60Y\\AllData\\"+file
        print(namefile)
        os.system("AxelData_Runner.py FitLine " + namefile + " \\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_60Y 8")
        os.system("AxelData_Runner.py DrawGraphs " + namefile +" \\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ADL_8PQK_ADL081\\8PQK_60Y 8")