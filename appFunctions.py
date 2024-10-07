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
        self.dss.compileFile(c.link_ieee13bus)
        self.barras = self.dss.BusNames()
    
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
        #dfBarrasDeseq = dfSeqVoltages.loc[dfSeqVoltages[dfSeqVoltages.columns[3]] > perc]
        dfBarrasDeseq = dfSeqVoltages
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
        results, log, dicMelhoresIndiv = self.ag.execAg(pms=pms, 
                                                        numRep=5)
        #==Cria uma TreeView com os melhores indivíduos==#
        #=Cria o dicionario com as potencias em cada fase, barramento e valor da fob
        dicResultadoAg = {'Pot A':[], 'Pot B':[], 'Pot C':[], 'Barramento':[], 'FOB':[]}
        chaves = list(dicResultadoAg.keys())

        for idx1 in range(len(dicMelhoresIndiv['cromossomos'])):
            for idx2 in range(len(chaves)):
                if idx2 < 3:
                    dicResultadoAg[chaves[idx2]].append(dicMelhoresIndiv['cromossomos'][idx1][idx2])
                elif idx2 == 3:
                    dicResultadoAg[chaves[idx2]].append(self.barras[dicMelhoresIndiv['cromossomos'][idx1][idx2]])
                else:
                    dicResultadoAg[chaves[idx2]].append(dicMelhoresIndiv['fobs'][idx1])

        dfResultadoAg = pd.DataFrame(dicResultadoAg)

        tv["column"] = list(dfResultadoAg)
        tv["show"] = "headings"
        for column in tv["columns"]:
            tv.heading(column, text=column) 
        df_rows = dfResultadoAg.to_numpy().tolist()
        for row in df_rows:
            tv.insert("", "end", values=row)

        return None

    def alocaButtFun(self, tv, entryPa, entryPb, entryPc, entryBarra):
        #==Recebe os dados ditos pelo usuário==#
        dados = [entryPa.get(), entryPb.get(), entryPc.get(), entryBarra.get()]
        #==Verifica se algum dos valores está vazio==#
        if '' in dados:
            tk.messagebox.showerror("Informativo", "Insira valores para Pma, Pmb e Pmc")
            return None
        self.clearData(tv)
        for idx in range(3):
            dados[idx]=int(dados[idx])
        print(dados)

        self.ag.alocaPot(dados[-1], dados[:3])
        self.dss.solve(1)

        dfSeqVoltages = self.dss.dfSeqVolt()
        #==Verifica se o DataFrame está vazio==#
        if dfSeqVoltages.empty:
            tk.messagebox.showerror("Informativo", "Houve algum problema com o diretório do arquivo 'IEEE13Nodeckt_EXP_SEQVOLTAGES.CSV'; verifique o diretório no arquivo consts.py")
            return None
        #==Remove as colunas que não serão utilizadas==#
        dfSeqVoltages = dfSeqVoltages.drop(['  p.u.', 'Base kV',' %V0/V1', ' Vresidual', ' %NEMA'], axis=1)
        #==Cria uma TreeView com as barras desequilibradas==#
        tv["column"] = list(dfSeqVoltages)
        tv["show"] = "headings"
        for column in tv["columns"]:
            tv.heading(column, text=column)   
        df_rows = dfSeqVoltages.to_numpy().tolist()
        for row in df_rows:
            tv.insert("", "end", values=row)

        return None