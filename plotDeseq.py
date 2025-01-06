from odFunctions import DSS
import consts as c
import pandas as pd
import matplotlib.pyplot as plt

#==Instancia a classe DSS==#
dss = DSS()
dss.compileFile(c.link_ieee13bus)

#==Pega os nomes dos barramentos, os barramentos trifásicos e as distâncias==#
bussesNames = dss.dssCircuit.AllBusNames
busses3phases = dss.BusNames()
dists = dss.distsBusses()

#==Pega as tensões de sequência==#
df = pd.DataFrame()
df = dss.dfSeqVolt()
listDeseq = list(df.iloc[:,5])

#==Cria um dicionário com os barramentos trifásicos, as distâncias e as tensões de sequência==#
dicionario = {'bus': [],'deseq': [], 'dists': []}
for bus in range(len(bussesNames)):
    dss.dssCircuit.SetActiveBus(bussesNames[bus])
    if dss.dssBus.NumNodes >= 3:
        dicionario['deseq'].append(listDeseq[bus])
        dicionario['dists'].append(dists[bus])
        dicionario['bus'].append(bussesNames[bus])

#==Cria um DataFrame com os dados==#
df = pd.DataFrame(dicionario)
print(df)

#==Cria o gráfico==#
fig, ax = plt.subplots()

ax.set_title("Desequilíbrio de tensão x Distância para IEEE13bus")

for i, busses3phases in enumerate(busses3phases):
    ax.annotate(busses3phases, (dicionario['dists'][i], dicionario['deseq'][i]), textcoords="offset points", xytext=(5,5), ha='center')

ax.plot(dicionario['dists'], dicionario['deseq'], 'x', color='blue')

ax.set_xlabel("Distância [km]")
ax.set_ylabel("Deseqquilíbrio de tensão [%]")
ax.grid(True)

plt.show()