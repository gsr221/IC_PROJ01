from deap import creator, base, tools, algorithms
import numpy as np
from odFunctions import DSS
import consts as c
import random

class AG():
    def __init__(self):
        self.dss = DSS()
        self.dss.compileFile(c.link_ieee13bus)
        self.barras = self.dss.BusNames()
        self.pmList = []
       
        
    def alocaPot(self, barramento, listaPoten):
        self.dss.clearAll()
        self.dss.compileFile(c.link_ieee13bus)
        self.dss.dssCircuit.SetActiveBus(barramento)
        kVBaseBarra = self.dss.dssBus.kVBase
        for fase in range(len(listaPoten)):
            comando = "New Load.NEW"+str(fase+1)+" Bus1="+str(barramento)+"."+str(fase+1)+" Phases=1 Conn=Wye Model=1 kV="+str(round(kVBaseBarra, 2))+" kW="+str(listaPoten[fase])+" kvar=0"
            self.dss.dssTxt.Command = comando
        
        
    def FOB(self, indiv):
        barra = indiv[-1]
        pots = indiv[:3]
        
        if barra > len(self.barras)-1 or barra < 0:
            return 100, 

        self.alocaPot(barramento=self.barras[barra], listaPoten=pots)
        
        self.dss.solve(1)
        
        dfSeqVoltages = self.dss.dfSeqVolt()
        dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
        deseq = dicSecVoltages[' %V2/V1']
        fobVal = max(deseq)
        
        return fobVal,
    
    
    def restricao (self, indiv):
        barra = indiv[-1]
        pots = indiv[:3]
        
        if barra > len(self.barras)-1: return False

        if sum(pots) != 0: return False
        
        if any(pots[idx] > self.pmList[idx] for idx in range(len(pots))): return False
        
        self.alocaPot(barramento=self.barras[barra], listaPoten=pots)
        
        self.dss.solve(1)
        dfSeqVoltages = self.dss.dfSeqVolt()
        dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
        deseq = dicSecVoltages[' %V2/V1']
        
        if any(x > 2 for x in deseq): return False
        
        return True

        
    def penalidade (self, indiv):
        barra = indiv[-1]
        pots = indiv[:3]
        
        deltaSumPots = sum(pots)
        deltaPots = (pots[idx]-self.pmList[idx] for idx in range(len(pots)))
        
        self.alocaPot(barramento=self.barras[barra], listaPoten=pots)
        
        self.dss.solve(1)
        dfSeqVoltages = self.dss.dfSeqVolt()
        dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
        deseq = dicSecVoltages[' %V2/V1']
        deltaDeseq = (deseqVal-2 for deseqVal in deseq)
        
        deltaTot = deltaSumPots + sum(deltaPots) + sum(deltaDeseq)
        
        return deltaTot
        
        
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
        crom = [random.randint(-self.pmList[0], self.pmList[0]), 
                random.randint(-self.pmList[1], self.pmList[1]), 
                random.randint(-self.pmList[2], self.pmList[2]),
                random.randint(0,12)]
        
        return crom
    
    def execAg(self, pms, cxpb, mutpb, ngen, numRep):
        #Objeto toolbox
        toolbox = base.Toolbox()
        #Lista com os valores de Potencia máxima por fase
        self.pmList = pms
        #Criando uma classe de Fitness minimizado
        creator.create("fitnessMulti", base.Fitness, weights=(-1.0, ))
        #Criando a classe do indivíduo
        creator.create("estrIndiv", list, fitness = creator.fitnessMulti)
        dicMelhoresIndiv = {"cromossomos": [],
                                "fobs": []}
        
        for _ in range(numRep):
            #Definindo como criar um indivíduo (cromossomo) com 4 genes inteiros
            toolbox.register("indiv", tools.initIterate, creator.estrIndiv, self.criaCrom)
            #Definindo a população
            toolbox.register("pop", tools.initRepeat, list, toolbox.indiv)
            #Criando uma população
            populacao = toolbox.pop(n=10)
            #Definindo maneiras de cruzamento e de mutação
            toolbox.register("mate", tools.cxOnePoint)
            toolbox.register("mutate", self.mutateFun)
            #Definindo o tipo de seleção
            toolbox.register("select", tools.selTournament, tournsize=3)
            #Definindo a fob e as restrições
            toolbox.register("evaluate", self.FOB)
            toolbox.register("evaluate", tools.DeltaPenalty(self.restricao, 1e6, self.penalidade))
            hof = tools.HallOfFame(1)
            result, log = algorithms.eaSimple(populacao, toolbox, cxpb=0.8, mutpb=0, ngen=100, halloffame=hof, verbose=False)
            dicMelhoresIndiv["cromossomos"].append(hof[0])
            dicMelhoresIndiv["fobs"].append(hof[0].fitness.values[0])
        
        return result, log, dicMelhoresIndiv