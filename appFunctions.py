import pandas as pd
from odFunctions import DSS
import json
import tkinter as tk

class AppFunctions():
    def __init__(self):
        file = open('infos.json')
        infos = json.load(file)
        self.busFileLink = infos['link_ieee13bus']
        self.dss = DSS()
    
    def clearData(self, tv):
        tv.delete(*tv.get_children())
        
    def equilButtFun(self):
        ...
        
    def calcDesqButtFun(self, tv):
        self.dss.clearAll()
        self.dss.compileFile(self.busFileLink)
        # self.dss.dssTxt.Command = "New Load.Nova Bus1=671.1  Phases=1 Conn=wye Model=1 kV=4.16 kW=2000 kvar=660"
        self.dss.solve(1)
        self.dss.exportSeqVoltages()
        
        try:
            dfSeqVoltages = pd.read_csv("C:/Users/gsr_f/Documents/IC/Segundo_ano/13Bus/IEEE13Nodeckt_EXP_SEQVOLTAGES.CSV")
        except FileNotFoundError:
            tk.messagebox.showerror("Informativo", "Houve algum problema ao ler o arquivo .csv, o arquivo não foi encontrado no seguinte diretório: C:/Users/gsr_f/Documents/IC/Segundo_ano/13Bus/IEEE13Nodeckt_EXP_SEQVOLTAGES.CSV")

        self.clearData(tv)
        dfColumns = dfSeqVoltages.columns
        dfSeqVoltages = dfSeqVoltages.drop(['  p.u.', 'Base kV',' %V0/V1',
       ' Vresidual', ' %NEMA'], axis=1)
        
        dfBarrasDeseq = dfSeqVoltages.loc[dfSeqVoltages[dfSeqVoltages.columns[3]] > 2]
        
        tv["column"] = list(dfBarrasDeseq)
        tv["show"] = "headings"
        for column in tv["columns"]:
            tv.heading(column, text=column)
            
        df_rows = dfBarrasDeseq.to_numpy().tolist()
        for row in df_rows:
            tv.insert("", "end", values=row)
            
        return None