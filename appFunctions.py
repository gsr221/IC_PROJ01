import pandas as pd
from odFunctions import DSS
import tkinter as tk
import consts as c
from modeloAg import AG

perc = 2

class AppFunctions():
    def __init__(self):
        #==link do arquivo do barramento==#
        self.busFileLink = c.link_ieee13bus
        #==Objeto da classe DSS e AG==#
        self.dss = DSS()
        self.ag = AG()
    
    #==Limpa os dados da TreeView==#
    def clearData(self, tv):
        tv.delete(*tv.get_children())
        
    #==Função para o botão de calcular barras desequilibradas==#
    def calcDesqButtFun(self, tv):
        self.clearData(tv)
        #==Recebe um DataFrame com as tensões de sequência==#
        dfSeqVoltages = self.dss.dfSeqVolt()
        #==Verifica se o DataFrame está vazio==#
        if dfSeqVoltages.empty:
            tk.messagebox.showerror("Informativo", "Houve algum problema com o diretório do arquivo 'IEEE13Nodeckt_EXP_SEQVOLTAGES.CSV'; verifique o diretório no arquivo consts.py")
            return None
        #==Remove as colunas que não serão utilizadas==#
        dfSeqVoltages = dfSeqVoltages.drop(['  p.u.', 'Base kV',' %V0/V1', ' Vresidual', ' %NEMA'], axis=1)
        #==Seleciona as barras com desequilíbrio maior que 2%==#
        dfBarrasDeseq = dfSeqVoltages.loc[dfSeqVoltages[dfSeqVoltages.columns[3]] > perc]
        #==Cria uma TreeView com as barras desequilibradas==#
        tv["column"] = list(dfBarrasDeseq)
        tv["show"] = "headings"
        for column in tv["columns"]:
            tv.heading(column, text=column)   
        df_rows = dfBarrasDeseq.to_numpy().tolist()
        for row in df_rows:
            tv.insert("", "end", values=row)
        #==Cria um dicionário com as barras desequilibradas==#
        self.dicBarrasDesq = dfBarrasDeseq.to_dict(orient = 'list')
            
        return None
    
    #==Função para o botão de calcular equilíbrio==#
    def equilButtFun(self, tv, entryPma, entryPmb, entryPmc):
        #==Recebe os valores de Pma, Pmb e Pmc==#
        pms = [entryPma.get(), entryPmb.get(), entryPmc.get()]
        #==Verifica se algum dos valores está vazio==#
        if '' in pms:
            tk.messagebox.showerror("Informativo", "Insira valores para Pma, Pmb e Pmc")
            return None
        self.clearData(tv)
        #==Converte os valores para inteiros==#
        pms = [int(pm) for pm in pms]
        #==Executa o algoritmo genético==#
        results, log, dicMelhoresIndiv = self.ag.execAg(pms=pms, numRep=5)
        #==Cria uma TreeView com os melhores indivíduos==#
        dfMelhoresIndiv = pd.DataFrame(dicMelhoresIndiv)
        
        tv["column"] = list(dfMelhoresIndiv)
        tv["show"] = "headings"
        for column in tv["columns"]:
            tv.heading(column, text=column) 
        df_rows = dfMelhoresIndiv.to_numpy().tolist()
        for row in df_rows:
            tv.insert("", "end", values=row)

        return None