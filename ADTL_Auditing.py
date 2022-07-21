import re
from typing import NamedTuple
import os.path
import json


class Escape_Results:
    Lot: str
    Wafer: str
    X: int
    Y: int
    Module_Name: str
    Test_Name: str
    Bin: int
    Delta: float
    Status: str
    ADTL_String: str
    escapeType: str


class EquationStatistics:
    ModuleName: str
    TestName: str
    EquationName: str
    Count: int
    Count_escape: int
    Count_notTested: int


class Results:
    tpID: str
    ModuleName: str
    Status: str
    TFM_Count: int
    LFM_Count: int
    HFM_Count: int
    Unknown_Count: int
    TFM_Kill_Count: int
    LFM_Kill_Count: int
    HFM_Kill_Count: int
    Unknown_Kill_Count: int
    TFM_Escape_Count: int
    LFM_Escape_Count: int
    HFM_Escape_Count: int
    Unknown_Escape_Count: int
    TFM_Not_Tested: int
    HFM_Not_Tested: int
    LFM_Not_Tested: int
    Unknown_Not_Tested: int


class Dye(NamedTuple):  # Unit Datastructures to store cells from database
    lot: str
    wafer: int
    bin: int
    X: int
    Y: int
    testname: str
    resultstring: str
    modulename: str
    status: str
    fmcategory: str
    delta: int
    offset: int
    testStatus: str


tp_id = "nill"


def post_testname(testname):  # extract information from testname
    result = []
    step_0 = testname.split('::')

    modulename = step_0[0]

    result.append(modulename)
    if len(step_0) >= 2:
        status = "KILL"  # Default
        fmcategory = "unk"
        s = step_0[1]
        if s.find("_EDC") > 0:  # Need to test
            status = "EDC"  # Check if you have both what category would that be?
        elif s.find("_E_") > 0:
            status = "EDC"

        if s.find("LFM") > 0:
            fmcategory = "LFM"
        elif s.find("TFM") > 0:
            fmcategory = "TFM"
        elif s.find("HFM") > 0:
            fmcategory = "HFM"

        result.append(status)
        result.append(fmcategory)
    else:
        result.append(testname)
        result.append("unk")
        result.append("unk")
    # print(result)
    return result


def post_resultstring(name):  #
    values = name.split('|')
    delta = 0
    offset = 0  # default# VMIN_OFFSET_004 VMIN_EDC??, UNDEFINED??
    flag = False
    tested_status = "ADTL_FAIL_NOT_BINNED"
    if len(values) == 8 and name.find('NA') < 0:
        flag = True
        not_set = -100000
        X = not_set
        Y = not_set
        if float(values[0]) > 100:
            X = float(values[0])
        elif float(values[1]) > 100:
            X = float(values[1])

        if (0 < float(values[0]) < 2) or (float(values[0]) < -500):
            Y = float(values[0])
        elif (0 < float(values[1]) < 2) or (float(values[1]) < -500):
            Y = float(values[1])

        if X == not_set or Y == not_set:
            flag = False

        intercept = float(values[2])
        slope = float(values[3])
        # print(values[7])
        if "SIGMA" in values[7]:
            if re.findall(r'\d+', values[7]):
                num = re.findall(r'\d+', values[7])
                offset = float(num[0])
        elif "OP" in values[7]:
            if re.findall(r'\d+', values[7]):
                num = re.findall(r'\d+', values[7])
                offset = float(num[0]) / 2
            # print(offset/0.02)
        elif "VMIN" in values[7]:
            if re.findall(r'\d+', values[7]):
                num = re.findall(r'\d+', values[7])
                offset = float(num[0]) * 5
        elif "0." in values[7]:
            if re.findall(r'\d+', values[7]):
                num = re.findall(r'\d+', values[7])
                offset = float(num[0]) / 2

        if "NOT_TESTED" in values[6]:
            flag = True
            tested_status = "NOT_TESTED"

        delta = round(((slope * X) + intercept - Y) / 0.02)

    elif len(values) == 6 and name.find('NA') < 0:
        flag = True
        not_set = -100000
        X = not_set
        Y = not_set
        if float(values[0]) > 100:
            X = float(values[0])
        elif float(values[1]) > 100:
            X = float(values[1])

        if (0 < float(values[0]) < 2) or (float(values[0]) < -500):
            Y = float(values[0])
        elif (0 < float(values[1]) < 2) or (float(values[1]) < -500):
            Y = float(values[1])

        if X == not_set or Y == not_set:
            flag = False

        intercept = float(values[4])
        slope = float(values[3])

        if "NOT_TESTED" in values[5]:
            flag = True
            tested_status = "NOT_TESTED"
        delta = round(((slope * X) + intercept - Y) / 0.02)

    del_off = [delta, offset, flag, tested_status]
    return del_off


def map_dyes(dye_single, blocks):  # blocks with modulenames

    key = dye_single.modulename + "%" + dye_single.status + "%" + dye_single.fmcategory
    if key in blocks:
        blocks[key].append(dye_single)
    else:
        blocks[key] = [dye_single]

    return blocks


def read_data(file):
    with open(file) as data:
        d = json.load(data)
        data.close()

        blocks = {}
        listOfGlobals = globals()
        listOfGlobals['tp_id'] = d['TestProgramName']
        for i in d['Data']:
            r = post_testname(i['test'])

            del_off = post_resultstring(i['result'])
            Dye_single = Dye(i['Lot'], i['Wafer_ID'], int(i['IB']), i['X'], i['Y'], i['test'],
                             i['result'], r[0], r[1], r[2], del_off[0], del_off[1], del_off[3])
            if (del_off[2] == True and Dye_single.modulename != "TPI_SIU" and Dye_single.modulename != "TPI_VCC"):
                blocks = map_dyes(Dye_single, blocks)
    # print (len(blocks))
    return blocks


def equationStats(blocks):
    eqstat = {}
    eqstat_escapes = {}
    eqstat_NotTested = {}

    for key in blocks:
        for dye in blocks[key]:
            singledye = dye.testname
            name = singledye.split(':')

            modulename = name[0]
            testname = name[2]
            equationname = name[3]

            newKey = modulename + '%' + testname + '%' + equationname
            if newKey in eqstat:
                eqstat[newKey] = eqstat[newKey] + 1
            else:
                eqstat[newKey] = 1
            if (dye.delta < 0 or dye.testStatus == "NOT_TESTED"):
                if (dye.delta < 0 and dye.bin < 3):
                    if newKey in eqstat_escapes:
                        eqstat_escapes[newKey] = eqstat_escapes[newKey] + 1
                    else:
                        eqstat_escapes[newKey] = 1
                elif dye.testStatus == "NOT_TESTED":
                    if newKey in eqstat_NotTested:
                        eqstat_NotTested[newKey] = eqstat_NotTested[newKey] + 1
                    else:
                        eqstat_NotTested[newKey] = 1

    # print(eqstat)
    # print(eqstat_escapes)
    # print(eqstat_NotTested)

    return [eqstat, eqstat_escapes, eqstat_NotTested]


def resultEquationStat(eqstat, eqstat_escapes, eqstat_NotTested, file):
    for key in eqstat:
        name = key.split("%")
        eqstat1 = EquationStatistics()

        eqstat1.ModuleName = name[0]
        eqstat1.TestName = name[1]
        eqstat1.EquationName = name[2]
        eqstat1.Count = eqstat[key]

        if key not in eqstat_escapes:
            eqstat1.Count_escape = 0
        else:
            eqstat1.Count_escape = eqstat_escapes[key]

        if key not in eqstat_NotTested:
            eqstat1.Count_notTested = 0
        else:
            eqstat1.Count_notTested = eqstat_NotTested[key]

        json_string = json.dumps(eqstat1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        file.write(json_string)
        file.write(',')


def cout_FmModuleStatus(fmCat):
    a = {}
    for key in fmCat:
        for dye in fmCat[key]:
            key1 = dye.status + "%" + dye.testname + "%" + dye.modulename + "%" + dye.fmcategory
            if key1 in fmCat:
                a[key1] = a[key1] + 1
            else:
                a[key1] = 1

    fm_module_cat = {}
    for key in a:
        step_0 = key.split("%")
        status = step_0[0]
        module = step_0[2]
        fmcategory = step_0[3]

        key1 = module + "%" + status + "%" + fmcategory

        if key1 in fm_module_cat:
            fm_module_cat[key1] = fm_module_cat[key1] + 1
        else:
            fm_module_cat[key1] = 1

    return fm_module_cat


def count_escapes(fmCat):
    escape = {}
    for key in fmCat:
        escape[key] = 0
        for dye in fmCat[key]:
            if dye.delta < 0:
                escape[key] = escape[key] + 1
    return escape


def red_alert(fmCat, file):
    escapeFlag = False
    reds = {}
    Not_tested = {}
    for key in fmCat:
        reds[key] = 0
        Not_tested[key] = 0
        for dye in fmCat[key]:
            if (dye.delta < 0 or dye.testStatus == "NOT_TESTED"):
                if (dye.delta < 0 and dye.bin < 3):
                    escapeFlag = True
                    reds[key] = reds[key] + 1
                    escapes1 = Escape_Results()
                    escapes1.Lot = dye.lot
                    escapes1.Wafer = dye.wafer
                    escapes1.X = dye.X
                    escapes1.Y = dye.Y
                    escapes1.Module_Name = dye.modulename
                    escapes1.Test_Name = dye.testname
                    escapes1.Bin = dye.bin
                    escapes1.Delta = dye.delta
                    escapes1.Status = dye.status
                    escapes1.ADTL_String = dye.resultstring
                    escapes1.escapeType = dye.testStatus

                    json_string = json.dumps(escapes1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
                    file.write(json_string)
                    file.write(',')

                elif dye.testStatus == "NOT_TESTED":
                    Not_tested[key] = Not_tested[key] + 1

    if escapeFlag == False:
        escapes1 = Escape_Results()
        escapes1.Lot = 'Null'
        escapes1.Wafer = 'Null'
        escapes1.X = 'Null'
        escapes1.Y = 'Null'
        escapes1.Module_Name = 'Null'
        escapes1.Test_Name = 'Null'
        escapes1.Bin = 'Null'
        escapes1.Delta = 'Null'
        escapes1.Status = 'Null'
        escapes1.ADTL_String = 'Null'
        escapes1.escapeType = 'Null'

        json_string = json.dumps(escapes1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        file.write(json_string)
        file.write(',')

    # print(reds)
    return [reds, Not_tested]


def result_file2(file, fm_module_cat, escapes, reds, Not_tested):
    LFM_count = {}
    TFM_count = {}
    HFM_count = {}
    Unk_count = {}
    LFM_Kill_count = {}
    TFM_Kill_count = {}
    HFM_Kill_count = {}
    Unk_Kill_count = {}
    LFM_Escape_count = {}
    TFM_Escape_count = {}
    HFM_Escape_count = {}
    Unk_Escape_count = {}
    TFM_Not_Tested = {}
    LFM_Not_Tested = {}
    HFM_Not_Tested = {}
    Unk_Not_Tested = {}

    for key in fm_module_cat:
        name = key.split('%')
        module_name = name[0]
        status = name[1]
        key1 = module_name + "%" + status

        LFM_count[key1] = 0
        TFM_count[key1] = 0
        HFM_count[key1] = 0
        Unk_count[key1] = 0

        LFM_Kill_count[key1] = 0
        TFM_Kill_count[key1] = 0
        HFM_Kill_count[key1] = 0
        Unk_Kill_count[key1] = 0

        LFM_Escape_count[key1] = 0
        TFM_Escape_count[key1] = 0
        HFM_Escape_count[key1] = 0
        Unk_Escape_count[key1] = 0

        TFM_Not_Tested[key1] = 0
        LFM_Not_Tested[key1] = 0
        HFM_Not_Tested[key1] = 0
        Unk_Not_Tested[key1] = 0

    for key in fm_module_cat:
        name = key.split('%')
        module_name = name[0]
        status = name[1]
        category = name[2]
        key1 = module_name + "%" + status

        if category == 'LFM':
            LFM_count[key1] = fm_module_cat[key]
            LFM_Kill_count[key1] = escapes[key]
            LFM_Escape_count[key1] = reds[key]
            LFM_Not_Tested[key1] = Not_tested[key]
        elif category == 'TFM':
            TFM_count[key1] = fm_module_cat[key]
            TFM_Kill_count[key1] = escapes[key]
            TFM_Escape_count[key1] = reds[key]
            TFM_Not_Tested[key1] = Not_tested[key]
        elif category == 'HFM':
            HFM_count[key1] = fm_module_cat[key]
            HFM_Kill_count[key1] = escapes[key]
            HFM_Escape_count[key1] = reds[key]
            HFM_Not_Tested[key1] = Not_tested[key]
        elif category == 'unk':
            Unk_count[key1] = fm_module_cat[key]
            Unk_Kill_count[key1] = escapes[key]
            Unk_Escape_count[key1] = reds[key]
            Unk_Not_Tested[key1] = Not_tested[key]

    for key in LFM_count:
        name = key.split('%')
        result1 = Results()
        result1.ModuleName = name[0]
        result1.Status = name[1]
        result1.tpID = tp_id

        result1.LFM_Count = LFM_count[key]
        result1.TFM_Count = TFM_count[key]
        result1.HFM_Count = HFM_count[key]
        result1.Unknown_Count = Unk_count[key]

        result1.LFM_Kill_Count = LFM_Kill_count[key]
        result1.TFM_Kill_Count = TFM_Kill_count[key]
        result1.HFM_Kill_Count = HFM_Kill_count[key]
        result1.Unknown_Kill_Count = Unk_Kill_count[key]

        result1.LFM_Escape_Count = LFM_Escape_count[key]
        result1.TFM_Escape_Count = TFM_Escape_count[key]
        result1.HFM_Escape_Count = HFM_Escape_count[key]
        result1.Unknown_Escape_Count = Unk_Escape_count[key]

        result1.LFM_Not_Tested = LFM_Not_Tested[key]
        result1.TFM_Not_Tested = TFM_Not_Tested[key]
        result1.HFM_Not_Tested = HFM_Not_Tested[key]
        result1.Unknown_Not_Tested = Unk_Not_Tested[key]

        json_string = json.dumps(result1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        file.write(json_string)
        file.write(',')


def file_check(path):
    file = open(path, "r")

    data = file.read()
    num = len(data)
    # print(num)
    if num < 2:
        open(path, 'w').close()


def summary_check(path):
    file = open(path, "r")

    data = file.read()
    num = len(data)
    # print(num)
    if num < 2:
        with open(path, 'w') as file:
            result1 = Results()
            result1.ModuleName = 'ADTL_Data_NotFound'
            result1.Status = 'KILL'
            result1.tpID = tp_id

            result1.LFM_Count = 0
            result1.TFM_Count = 0
            result1.HFM_Count = 0
            result1.Unknown_Count = 0

            result1.LFM_Kill_Count = 0
            result1.TFM_Kill_Count = 0
            result1.HFM_Kill_Count = 0
            result1.Unknown_Kill_Count = 0

            result1.LFM_Escape_Count = 0
            result1.TFM_Escape_Count = 0
            result1.HFM_Escape_Count = 0
            result1.Unknown_Escape_Count = 0

            result1.LFM_Not_Tested = 0
            result1.TFM_Not_Tested = 0
            result1.HFM_Not_Tested = 0
            result1.Unknown_Not_Tested = 0

            json_string = json.dumps(result1, default=lambda o: o.__dict__, sort_keys=True, indent=2)
            file.write("[")
            file.write(json_string)
            file.write("]")


def main(args1, args2):
    outPath = args2 + '/Summary.json'
    outPathEscapes = args2 + '/Escapes.json'
    outPathEquationStat = args2 + '/EquationStats.json'
    filePath = args1

    blocks = read_data(filePath)
    eqStat = equationStats(blocks)
    fm_module_cat = cout_FmModuleStatus(blocks)
    escapes = count_escapes(blocks)
    with open(outPathEscapes, 'w') as file:
        file.write("[")
        reds = red_alert(blocks, file)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.write("]")
    with open(outPath, 'w') as file2:
        file2.write("[")
        result_file2(file2, fm_module_cat, escapes, reds[0], reds[1])
        file2.seek(file2.tell() - 1, os.SEEK_SET)
        file2.write("]")
    with open(outPathEquationStat, 'w') as file:
        file.write("[")
        resultEquationStat(eqStat[0], eqStat[1], eqStat[2], file)
        file.seek(file.tell() - 1, os.SEEK_SET)
        file.write("]")

    summary_check(outPath)
    file_check(outPathEscapes)
