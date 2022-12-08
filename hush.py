f = open("\\\\pjwade-desk.ger.corp.intel.com\\AXEL_ADTL_REPORTS\\MTL_8PRP_MTL\\8PRP_H68Y10_2\\Sigma8Run\\vmincount.txt", "r")
content = f.read()
words = content.split(', ')
for i in range(len(words)):
    print(words[i])
f.close()
