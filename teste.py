lista = [10, 20, 30]
valorMax = [30, 19, 31]
algum_maior = all(lista[idx] < valorMax[idx] for idx in range(len(lista)))
print(algum_maior)  # True