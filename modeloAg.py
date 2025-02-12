from deap import creator, base, tools, algorithms
from odFunctions import DSS
import consts as c
import random

class AG():
    def __init__(self):
        self.dss = DSS()
        self.dss.compileFile(c.link_ieee13bus)
        self.barras = self.dss.BusNames()
        self.pmList = []
        creator.create("fitnessMulti", base.Fitness, weights=(-1.0, ))
        #Criando a classe do indivíduo
        creator.create("estrIndiv", list, fitness = creator.fitnessMulti)
        
    
    #==Função objetivo Bateria==#
    def FOBBat(self, indiv):
        #==Recebe os valores de potência máxima e o barramento==#
        barraBat = indiv[-1]
        potsBat = indiv[:2]
        potsBat.append(-potsBat[0]-potsBat[1])
        
        #==Verifica se o barramento é válido==#
        if barraBat > len(self.barras)-1 or barraBat < 0: return 99999,

        #==Aloca as potências no barramento e os bancos de capacitores e resolve o sistema==#
        self.dss.alocaPot(barramento=self.barras[barraBat], listaPoten=potsBat)
        self.dss.solve(1)
        
        #==Recebe as tensões de sequência e as coloca em um dicionário==#
        dfSeqVoltages = self.dss.dfSeqVolt()
        dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
        deseq = dicSecVoltages[' %V2/V1']
        
        #==Recebe o valor da função objetivo==#
        fobVal = max(deseq)
        
        #==Restrições==#
        restricoes = [
            abs(potsBat[0]) - self.pmList[0],
            abs(potsBat[1]) - self.pmList[1],
            abs(-potsBat[0] - potsBat[1]) - self.pmList[2],
            fobVal - 2
        ]
        #==Penalidade==#
        penalidade = sum(max(0, restricao) for restricao in restricoes)
        penalidadeVal = 1000
        
        return fobVal + penalidadeVal * penalidade,
    
    
    def FOBBatCap(self, indiv):
        #==Recebe os valores de potência máxima e o barramento==#
        barraBat = indiv[-1]
        potsBat = indiv[:2]
        potsBat.append(-potsBat[0]-potsBat[1])
        
        #==Recebe os valores dos capacitores==#
        barrasCaps = indiv[3:5]
        numCaps = indiv[5:7]
        fasesCaps = indiv[7:]
        
        #==Verifica se o barramento é válido==#
        if barraBat > len(self.barras)-1 or barraBat < 0: return 99999,
        #==Verifica se as barras e fases dos capacitores são válidas==#
        for idx in range(len(barrasCaps)):
            if barrasCaps[idx] > len(self.barras)-1 or barrasCaps[idx] < 0 or fasesCaps[idx] > 3 or fasesCaps[idx] < 1: return 99999,

        #==Aloca as potências no barramento e os bancos de capacitores e resolve o sistema==#
        self.dss.alocaPot(barramento=self.barras[barraBat], listaPoten=potsBat)
        for idx in range(len(barrasCaps)):
            self.dss.alocaCap(barramento=self.barras[barrasCaps[idx]], numCaps=numCaps[idx], fase=fasesCaps[idx], nome=str(numCaps[idx]*50)+'x'+str(idx))
        
        self.dss.solve(1)
        
        #==Recebe as tensões de sequência e as coloca em um dicionário==#
        dfSeqVoltages = self.dss.dfSeqVolt()
        dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
        deseq = dicSecVoltages[' %V2/V1']
        
        #==Recebe o valor da função objetivo==#
        fobVal = max(deseq)
        
        #==Restrições==#
        restricoes = [
            abs(potsBat[0]) - self.pmList[0],
            abs(potsBat[1]) - self.pmList[1],
            abs(-potsBat[0] - potsBat[1]) - self.pmList[2],
            fobVal - 2
        ]
        
        #==Penalidade==#
        penalidade = sum(max(0, restricao) for restricao in restricoes)
        penalidadeVal = 1000
        
        return fobVal + penalidadeVal * penalidade,
        
    
    def FOBCap(self, indiv):
        #==Recebe os valores dos capacitores==#
        barra = indiv[0:3]
        numCaps = indiv[3:5]
        fase = indiv[5:]
        
        #==Verifica se o barramento é válido==#
        for idx in range(len(barra)):
            if barra[idx] > len(self.barras)-1 or barra[idx] < 0 or fase[idx] > 3 or fase[idx] < 1: return 99999,
        
        #==Aloca os bancos de capacitores e resolve o sistema==#
        for idx in range(2):    
            self.dss.alocaCap(barramento=self.barras[barra[idx]], numCaps=numCaps[idx], fase=fase[idx], nome=str(numCaps[idx]*50)+'_'+str(idx))
        
        self.dss.solve(1)
        
        #==Recebe as tensões de sequência e as coloca em um dicionário==#
        dfSeqVoltages = self.dss.dfSeqVolt()
        dicSecVoltages = dfSeqVoltages.to_dict(orient = 'list')
        deseq = dicSecVoltages[' %V2/V1']
        
        #==Recebe o valor da função objetivo==#
        fobVal = max(deseq)
        
        # restricoes = [
        #     fobVal - 2
        # ]
        
        # penalidade = sum(max(0, restricao) for restricao in restricoes)
        # penalidadeVal = 1000
        
        return fobVal ,
    
    
    #==Cria cromossomo para alocação de capacitores [barras / numCaps / fases]==#
    def criaCromCap(self):
        indiv = [random.randint(0, len(self.barras)), random.randint(0, len(self.barras)), random.randint(0, len(self.barras)),
                random.randint(1, 25), random.randint(1, 25), random.randint(1, 25),
                random.randint(1, 3), random.randint(1, 3), random.randint(1, 3)]
        return indiv
    
    
    #==Cria cromossomo para alocação de baterias e capacitores [pots / barramento / barras / numCaps / fases]==#
    def criaCromBatCap(self):
        g1 = random.randint(-self.pmList[0], self.pmList[0])
        g2 = random.randint(-self.pmList[1], self.pmList[1])
        indiv = [g1,
                g2, 
                random.randint(0,len(self.barras)),

                random.randint(0, len(self.barras)), random.randint(0, len(self.barras)),
                random.randint(1, 25), random.randint(1, 25),
                random.randint(1, 3), random.randint(1, 3)]
        return indiv
    
    
    #==Cria cromossomo para alocação de baterias [pots / barramento]==#
    def criaCromBat(self):
        g1 = random.randint(-self.pmList[0], self.pmList[0])
        g2 = random.randint(-self.pmList[1], self.pmList[1])
        indiv = [g1, 
                g2, 
                random.randint(0,len(self.barras))]
        return indiv
    
    
    def mutateFun(self, indiv):
        indiv = self.criaCrom()
        return indiv
    
    #==Método de cruzamento alfa==#
    def cruzamentoFunAlfa(self, indiv1, indiv2):
        #==Recebe um valor de alfa aleatório==#
        alfa = round(random.uniform(0, 1), 2)
        newIndiv1 = indiv1
        newIndiv2 = indiv2
        #==Cria um novo indivíduo com a proporção alfa e alfa-1 dos genes dos pais==#
        for gene in range(len(indiv1)):
            # Use o valor de alfa conforme necessário
            newIndiv1[gene] = int(alfa*indiv1[gene] + (1-alfa)*indiv2[gene])
            newIndiv2[gene] = int((1-alfa)*indiv1[gene] + alfa*indiv2[gene])
            
        return newIndiv1, newIndiv2
    
    #==Método de cruzamento BLX==#
    def cruzamentoFunBLX(self, indiv1, indiv2):
        newIndiv1 = indiv1
        newIndiv2 = indiv2
        #==Recebe um valor de alfa aleatório==#
        alfa = random.uniform(0.3, 0.5)
        #==Cria um novo indivíduo==#
        for gene in range(len(indiv1)):
            #==calcula o delta==#
            delta = abs(indiv1[gene] - indiv2[gene])
            #==Calcula o mínimo e o máximo==#
            minGene = int(min(indiv1[gene], indiv2[gene]) - alfa*delta)
            maxGene = int(max(indiv1[gene], indiv2[gene]) + alfa*delta)
            if minGene != maxGene:
                #==Sorteia o novo gene entre o mínimo e o máximo==#
                newIndiv1[gene] = random.randint(minGene, maxGene)
                newIndiv2[gene] = random.randint(minGene, maxGene)
            else:
                newIndiv1[gene] = minGene
                newIndiv2[gene] = minGene
            
        return newIndiv1, newIndiv2
    
    
    def execAg(self, pms, probCruz=0.9, probMut=0, numGen=100, numRep=1):
        #Objeto toolbox
        toolbox = base.Toolbox()
        #Lista com os valores de Potencia máxima por fase
        self.pmList = pms
        #Criando uma classe de Fitness minimizado
        dicMelhoresIndiv = {"cromossomos": [],
                            "fobs": []}
        #Definindo maneiras de cruzamento e de mutação
        toolbox.register("mate", self.cruzamentoFunBLX)
        toolbox.register("mutate", self.mutateFun)
        
        #Definindo o tipo de seleção
        toolbox.register("select", tools.selTournament, tournsize=10)

        #Definindo a fob e as restrições
        toolbox.register("evaluate", self.FOBBat)

        for rep in range(numRep):
            #Definindo como criar um indivíduo (cromossomo) com 4 genes inteiros
            toolbox.register("indiv", tools.initIterate, creator.estrIndiv, self.criaCromBat)

            #Definindo a população
            toolbox.register("pop", tools.initRepeat, list, toolbox.indiv)

            #Criando uma população
            populacao = toolbox.pop(n=30)

            hof = tools.HallOfFame(1)
            result, log = algorithms.eaSimple(populacao, toolbox, cxpb=probCruz, mutpb=probMut, ngen=numGen, halloffame=hof, verbose=False)
            dicMelhoresIndiv["cromossomos"].append(hof[0])
            dicMelhoresIndiv["fobs"].append(hof[0].fitness.values[0])
            print(f"Rep: {rep+1} - FOB: {hof[0].fitness.values[0]}")
        
        return result, log, dicMelhoresIndiv