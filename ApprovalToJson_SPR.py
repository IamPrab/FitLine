import json
import os
import argparse
import yaml
import pandas as pd


def ReadcsvData(csvAprrovalFile):

    excel_data = pd.read_excel(csvAprrovalFile)
    dict_data={}
    data = pd.DataFrame(excel_data, columns=['TestName', 'Flow', 'Slope', 'Intercept_0', 'Intercept','Selected Sigma',
                                             'Sigma Multiple','Calculated_Offset','Overide sigma Multiple value','RootMeanSquareError','Approval',
                                             'MultiCore/MainCore'])
    length = (len (data['TestName']))
    count = 0
    #print(length)
    while(count<length):
        if data['TestName'][count] not in dict_data:
            stuff = [ data['Flow'][count], float(data['Slope'][count]),float(data['Intercept_0'][count]),float(data['Intercept'][count]),float(data['Selected Sigma'][count]),
                      data['Sigma Multiple'][count], float(data['Calculated_Offset'][count]), float(data['RootMeanSquareError'][count]), data['Approval'][count],
                      data['MultiCore/MainCore'][count]]
            dict_data[data['TestName'][count]] = stuff
        else:
            print(data['TestName'][count])
            print(dict_data[data['TestName'][count]])
            print("double Equation ^^")
        count = count + 1
    # print(count)
    # print(len(dict_data))

    return dict_data

def ConvertDirectlyToString(dataApproval,sdList):

    for SourceTestName in dataApproval:
        Flow = dataApproval[SourceTestName][0]
        SlopeA = float(dataApproval[SourceTestName][1])
        Intercept0 = float(dataApproval[SourceTestName][2])
        InterceptA = float(dataApproval[SourceTestName][3])
        SelectedSigmaA = float(dataApproval[SourceTestName][4])
        Sigmaa = dataApproval[SourceTestName][5]
        CalculatedOffset = float(dataApproval[SourceTestName][6])
        RootMeanSquareErrorA = float(dataApproval[SourceTestName][7])
        Approval = dataApproval[SourceTestName][8]
        Core = dataApproval[SourceTestName][9]

        if Approval=="YES" and Core == "MainCore":

            testname= SourceTestName.split("::")[1]
            sdList = sdList + "('" + testname + "','VADTSTR," + str(SlopeA) +","+ str(InterceptA) +","+ str(SelectedSigmaA) + "," + str(Sigmaa) +"',VMINPREDSTR,0,0,0.02,0.01,0.03')" +"\n"

    return sdList





if __name__ == '__main__':

    csvAprrovalFile = "\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\ICD_8PCG_ICXDHCC\\8PCG_40B_R1\\ApprovalFile.xlsx"
    dataApproval= ReadcsvData(csvAprrovalFile)

    sdList= "SDList = (\n"

    finalSDList = ConvertDirectlyToString(dataApproval,sdList)
    finalSDList = finalSDList + "\n)"
    print(finalSDList)


