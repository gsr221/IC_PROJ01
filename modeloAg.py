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
        
    def FOB (self, indiv):
        barra = indiv[-1]
        pots = indiv[:3]
        
        if barra > len(self.barras)-1:
            return 100

        #Reseta o arquivo do openDSS
        self.dss.clearAll()
        self.dss.compileFile(c.link_ieee13bus)
        self.dss.dssBus.SetActiveBus(self.barras[barra])
        kVbaseBarra = self.dss.dssBus.kVBaseBus(self.barras[barra])

        #Cria as novas cargas
        for pot in range(len(pots)):
            self.dss.dssTxt.Command = "New Load.NEW"+str(pot+1)+" Bus1="+str(self.barras[barra])+"."+str(pot+1)+"Phases=1 Conn=Wye Model=1 kV="+str(round(kVbaseBarra, 2))+" kW="+str(pots[pot])+" kvar=0"
        
        self.dss.solve(1)
        
        dfSeqVoltages = self.dss.dfSeqVolt()
        dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
        deseq = dicSecVoltages[' %V2/V1']
        fobVal = max(deseq)
        
        return fobVal,
    
    
    def restricao (self, indiv):
        barra = indiv[-1]
        pots = indiv[:3]
        
        if barra > len(self.barras)-1:
            return False
        
        self.dss.clearAll()
        self.dss.compileFile(c.link_ieee13bus)
        self.dss.dssBus.SetActiveBus(self.barras[barra])
        kVbaseBarra = self.dss.dssBus.kVBaseBus(self.barras[barra])

        #Cria as novas cargas
        for pot in range(len(pots)):
            self.dss.dssTxt.Command = "New Load.NEW"+str(pot+1)+" Bus1="+str(self.barras[barra])+"."+str(pot+1)+"Phases=1 Conn=Wye Model=1 kV="+str(round(kVbaseBarra, 2))+" kW="+str(pots[pot])+" kvar=0"
        
        self.dss.solve(1)
        
        dfSeqVoltages = self.dss.dfSeqVolt()
        dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
        deseq = dicSecVoltages[' %V2/V1']
        deseqState = all(x <= 2 for x in deseq)
        potMaxState = all(pots[idx] <= self.pmList[idx] for idx in range(len(pots)))
        somaPots = sum(pots)
        if somaPots == 0: somaPotsState = True
        else: somaPotsState = False
        states = [deseqState, potMaxState, somaPotsState]
        
        return all(state == True for state in states)
        
    
    def penalidade (self, indiv):
        return 50
        
        
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
    
    
    def configAg(self, pms):
        #Lista com os valores de Potencia máxima por fase
        self.pmList = pms
        #Criando uma classe de Fitness minimizado
        creator.create("fitnessMulti", base.Fitness, weights=(-1.0,))
        #Criando a classe do indivíduo
        creator.create("estrIndiv", list, fitness=creator.FitnessMulti)
        #Objeto toolbox
        self.toolbox = base.Toolbox()
        #Definindo um atributo que será um inteiro de -max até um valor +max
        self.toolbox.register("gene", random.randint, -max(self.pmList), max(self.pmList))
        #Definindo como criar um indivíduo (cromossomo) com 4 genes inteiros
        self.toolbox.register("indiv", tools.initRepeat, creator.estrIndiv, self.toolbox.gene, n=4)
        #Definindo a população
        self.toolbox.register("pop", tools.initRepeat, list, self.toolbox.indiv)
        #Criando uma população
        pop = self.toolbox.pop(n=10)
        #Definindo maneiras de cruzamento e de mutação
        self.toolbox.register("mate", tools.cxOnePoint)
        self.toolbox.register("mutate", self.mutateFun, indpb=0.1)
        #Definindo o tipo de seleção
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        #Definindo a fob e as restrições
        self.toolbox.register("evaluate", self.FOB)
        self.toolbox.register("evaluate", tools.DeltaPenalty(self.restricao, 1e6, self.penalidade))