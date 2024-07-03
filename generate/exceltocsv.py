#pip install pandas
#pip install xlrd
#pip install openpyxl


import glob,os
import pandas as pd


inputdirectory = "C:\\devinpiano\\testing\\tennis\\data\\archive\\wta_womens_tour"
inputdirectory = "C:\\devinpiano\\testing\\tennis\\data\\archive\\atp_mens_tour"

for xls_file in glob.glob(os.path.join(inputdirectory,"*.xls*")):
    data_xls = pd.read_excel(xls_file, index_col=None)
    csv_file = os.path.splitext(xls_file)[0]+".csv"
    data_xls.to_csv(csv_file, encoding='utf-8', index=False)
