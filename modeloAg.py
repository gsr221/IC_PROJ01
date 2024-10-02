from deap import creator, base, tools, algorithms
from odFunctions import DSS
import consts as c
import random
import pandas as pd

class AG():
    def __init__(self):
        self.dss = DSS()
        self.dss.compileFile(c.link_ieee13bus)
        self.barras = self.dss.BusNames()
        self.pmList = []
        creator.create("fitnessMulti", base.Fitness, weights=(-1.0, ))
        #Criando a classe do indivíduo
        creator.create("estrIndiv", list, fitness = creator.fitnessMulti)
        self.indivDic = {"cromossomo": [], 
                         "fob": []}
       
        
    def alocaPot(self, barramento, listaPoten):
        self.dss.clearAll()
        self.dss.compileFile(c.link_ieee13bus)
        self.dss.dssCircuit.SetActiveBus(barramento)
        kVBaseBarra = self.dss.dssBus.kVBase
        for fase in range(3):
            comando = "New Load.NEW"+str(fase+1)+" Bus1="+str(barramento)+"."+str(fase+1)+" Phases=1 Conn=Wye Model=1 kV="+str(round(kVBaseBarra, 2))+" kW="+str(listaPoten[fase])+" kvar=0"
            self.dss.dssTxt.Command = comando
        
        
    def FOB(self, indiv):
        barra = indiv[-1]
        pots = indiv[:3]
        
        if barra > len(self.barras)-1 or barra < 0: return 99999, 

        self.alocaPot(barramento=self.barras[barra], listaPoten=pots)
        
        self.dss.solve(1)
        
        dfSeqVoltages = self.dss.dfSeqVolt()
        dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
        deseq = dicSecVoltages[' %V2/V1']
        fobVal = max(deseq)
        
        restricoes = [
            abs(pots[0]) - self.pmList[0],
            abs(pots[1]) - self.pmList[1],
            abs(pots[2]) - self.pmList[2],
            sum(pots),
            -sum(pots)
        ]
        
        penalidade = sum(max(0, restricao) for restricao in restricoes)
        penalidadeVal = 1000
        
        self.indivDic["cromossomo"].append(indiv)
        self.indivDic["fob"].append(fobVal + penalidadeVal * penalidade)
        
        return fobVal + penalidadeVal * penalidade,
    
    
    # def restricao (self, indiv):
    #     barra = indiv[-1]
    #     pots = indiv[:3]
        
    #     if barra > len(self.barras)-1: return False

    #     if sum(pots) != 0: return False
        
    #     if any(pots[idx] > self.pmList[idx] for idx in range(len(pots))): return False
        
    #     self.alocaPot(barramento=self.barras[barra], listaPoten=pots)
        
    #     self.dss.solve(1)
    #     dfSeqVoltages = self.dss.dfSeqVolt()
    #     dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
    #     deseq = dicSecVoltages[' %V2/V1']
        
    #     if any(x > 2 for x in deseq): return False
        
    #     return True

        
    # def penalidade (self, indiv):
    #     barra = indiv[-1]
    #     pots = indiv[:3]
        
    #     deltaSumPots = sum(pots)
    #     deltaPots = (pots[idx]-self.pmList[idx] for idx in range(len(pots)))
        
    #     self.alocaPot(barramento=self.barras[barra], listaPoten=pots)
        
    #     self.dss.solve(1)
    #     dfSeqVoltages = self.dss.dfSeqVolt()
    #     dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
    #     deseq = dicSecVoltages[' %V2/V1']
    #     deltaDeseq = (deseqVal-2 for deseqVal in deseq)
        
    #     deltaTot = deltaSumPots + sum(deltaPots) + sum(deltaDeseq)
        
    #     return deltaTot
        
        
    def mutateFun(self, indiv):
        idx = random.randint(0,len(indiv)-1)
        #Se o gene escolhido for de potência fara Bx +- 10% da pot maxima da fase
        if idx >= 0 and idx < 3:
            if random.choice([True, False]):
                indiv[idx] = indiv[idx] + self.pmList[idx]/10
            else:
                indiv[idx] = indiv[idx] - self.pmList[idx]/10
        #Se o gene escolhido for de uma barra, será sorteada uma nova barra para alocar as potências
        else:
            indiv[idx] = random.randint(0, len(self.barras))
    
    
    def criaCrom (self):
        g1 = random.randint(-self.pmList[0], self.pmList[0])
        g2 = random.randint(-self.pmList[1], self.pmList[1])
        g3 = - g1 - g2
        indiv = [g1, 
                g2, 
                g3,
                random.randint(0,len(self.barras))
                ]
        
        return indiv
    
    
    def cruzamentoFun(self, indiv1, indiv2):
        for gene in range(len(indiv1)):
            t = round(random.uniform(0, 1), 2)
            # Use o valor de t conforme necessário
            indiv1[gene] = int(t*indiv1[gene] + (1-t)*indiv2[gene])
            indiv2[gene] = int((1-t)*indiv1[gene] + t*indiv2[gene])
            
        return indiv1, indiv2
    
    
    def execAg(self, pms, probCruz=0.8, probMut=0, numGen=100, numRep=1):
        #Objeto toolbox
        toolbox = base.Toolbox()
        #Lista com os valores de Potencia máxima por fase
        self.pmList = pms
        #Criando uma classe de Fitness minimizado
        dicMelhoresIndiv = {"cromossomos": [],
                                "fobs": []}
        
        for _ in range(numRep):
            #Definindo como criar um indivíduo (cromossomo) com 4 genes inteiros
            toolbox.register("indiv", tools.initIterate, creator.estrIndiv, self.criaCrom)
            
            #Definindo a população
            toolbox.register("pop", tools.initRepeat, list, toolbox.indiv)
            
            #Criando uma população
            populacao = toolbox.pop(n=15)
            
            #Definindo maneiras de cruzamento e de mutação
            toolbox.register("mate", self.cruzamentoFun)
            toolbox.register("mutate", self.mutateFun)
            
            #Definindo o tipo de seleção
            toolbox.register("select", tools.selTournament, tournsize=5)
            
            #Definindo a fob e as restrições
            toolbox.register("evaluate", self.FOB)
            # toolbox.register("evaluate", tools.DeltaPenalty(self.restricao, 1e6, self.penalidade))
            
            hof = tools.HallOfFame(1)
            result, log = algorithms.eaSimple(populacao, toolbox, cxpb=probCruz, mutpb=probMut, ngen=numGen, halloffame=hof, verbose=False)
            dicMelhoresIndiv["cromossomos"].append(hof[0])
            dicMelhoresIndiv["fobs"].append(hof[0].fitness.values[0])
            
            # print(self.indivDic)
        
        return result, log, dicMelhoresIndiv