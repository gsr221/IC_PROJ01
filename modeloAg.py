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
        
    
    #==Função objetivo==#
    def FOB(self, indiv):
        #==Recebe os valores de potência máxima e o barramento==#
        barra = indiv[-1]
        pots = indiv[:3]
        
        #==Verifica se o barramento é válido==#
        if barra > len(self.barras)-1 or barra < 0: return 99999, 

        #==Aloca as potências no barramento e resolve o sistema==#
        self.dss.alocaPot(barramento=self.barras[barra], listaPoten=pots)
        self.dss.solve(1)
        
        #==Recebe as tensões de sequência e as coloca em um dicionário==#
        dfSeqVoltages = self.dss.dfSeqVolt()
        dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
        deseq = dicSecVoltages[' %V2/V1']
        
        fobVal = max(deseq)
        
        restricoes = [
            abs(pots[0]) - self.pmList[0],
            abs(pots[1]) - self.pmList[1],
            abs(pots[2]) - self.pmList[2],
            sum(pots),
            -sum(pots),
            fobVal - 2
        ]
        
        penalidade = sum(max(0, restricao) for restricao in restricoes)
        penalidadeVal = 1000
        
        return fobVal + penalidadeVal * penalidade,
        
    
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
    
    
    def mutateFun(self, indiv):
        indiv = self.criaCrom()
        return indiv, 
    
    
    def cruzamentoFun(self, indiv1, indiv2):
        for gene in range(len(indiv1)):
            t = round(random.uniform(0, 1), 2)
            newIndiv1 = indiv1
            newIndiv2 = indiv2
            # Use o valor de t conforme necessário
            newIndiv1[gene] = int(t*indiv1[gene] + (1-t)*indiv2[gene])
            newIndiv2[gene] = int((1-t)*indiv1[gene] + t*indiv2[gene])
            
        return newIndiv1, newIndiv2
    
    
    def execAg(self, pms, probCruz=0.9, probMut=0, numGen=100, numRep=1):
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
        
        return result, log, dicMelhoresIndiv