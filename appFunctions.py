import pandas as pd
from odFunctions import DSS
import tkinter as tk
import consts as c
from modeloAg import AG

perc = 2

class AppFunctions():
    def __init__(self):
        self.busFileLink = c.link_ieee13bus
        self.dss = DSS()
        self.ag = AG()
    
    def clearData(self, tv):
        tv.delete(*tv.get_children())
        
    def calcDesqButtFun(self, tv):
        self.clearData(tv)
        dfSeqVoltages = self.dss.dfSeqVolt()
        if dfSeqVoltages.empty:
            tk.messagebox.showerror("Informativo", "Houve algum problema com o diretório do arquivo 'IEEE13Nodeckt_EXP_SEQVOLTAGES.CSV'; verifique o diretório no arquivo consts.py")
            return None
        dfSeqVoltages = dfSeqVoltages.drop(['  p.u.', 'Base kV',' %V0/V1', ' Vresidual', ' %NEMA'], axis=1)
        dfBarrasDeseq = dfSeqVoltages.loc[dfSeqVoltages[dfSeqVoltages.columns[3]] > perc]
        
        tv["column"] = list(dfBarrasDeseq)
        tv["show"] = "headings"
        for column in tv["columns"]:
            tv.heading(column, text=column)
            
        df_rows = dfBarrasDeseq.to_numpy().tolist()
        for row in df_rows:
            tv.insert("", "end", values=row)
            
        self.dicBarrasDesq = dfBarrasDeseq.to_dict(orient = 'list')
            
        return None
    
    def equilButtFun(self, tv, entryPma, entryPmb, entryPmc):
        self.clearData(tv)
        pms = [entryPma.get(), entryPmb.get(), entryPmc.get()]
        pms = [int(pm) for pm in pms]
        if '' in pms:
            tk.messagebox.showerror("Informativo", "Insira valores para Pma, Pmb e Pmc")
            return None
        results, log, dicMelhoresIndiv = self.ag.execAg(pms=pms,
                                                        cxpb=0.8,
                                                        mutpb=0.1,
                                                        ngen=400,
                                                        numRep=1)
        dfMelhoresIndiv = pd.DataFrame(dicMelhoresIndiv)
        
        tv["column"] = list(dfMelhoresIndiv)
        tv["show"] = "headings"
        for column in tv["columns"]:
            tv.heading(column, text=column)
            
        df_rows = dfMelhoresIndiv.to_numpy().tolist()
        for row in df_rows:
            tv.insert("", "end", values=row)

        return None
        