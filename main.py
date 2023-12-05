import numpy as np
import random as rd
import matplotlib.pyplot as plt

import tkinter as tk

def get_user_input():
    def submit():
        tamCromossomo = int(entry1.get())
        pc = float(entry2.get())
        pm = float(entry3.get())
        numGeracoes = int(entry4.get())
        tamPopulacao = int(entry5.get())
        root.destroy()

    root = tk.Tk()

    tk.Label(root, text="Tamanho do cromossomo:").grid(row=0)
    tk.Label(root, text="Probabilidade de crossover:").grid(row=1)
    tk.Label(root, text="Probabilidade de mutação:").grid(row=2)
    tk.Label(root, text="Número de gerações:").grid(row=3)
    tk.Label(root, text="Tamanho da população:").grid(row=4)

    entry1 = tk.Entry(root)
    entry2 = tk.Entry(root)
    entry3 = tk.Entry(root)
    entry4 = tk.Entry(root)
    entry5 = tk.Entry(root)

    entry1.grid(row=0, column=1)
    entry2.grid(row=1, column=1)
    entry3.grid(row=2, column=1)
    entry4.grid(row=3, column=1)
    entry5.grid(row=4, column=1)

    tk.Button(root, text='Enviar', command=submit).grid(row=5, column=1, sticky=tk.W, pady=4)

    root.mainloop()

    return tamCromossomo, pc, pm, numGeracoes, tamPopulacao

tamCromossomo, pc, pm, numGeracoes, tamPopulacao = get_user_input()

#------------------
pGeradores = [20, 15, 35, 40, 15, 15, 10]
pt = sum(pGeradores) # potência total
pDemanda = [80, 90, 65, 70]
trimestres = 1
g12 = [[1,1,0,0], [0,1,1,0], [0,0,1,1]]
g37 = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]


def potenciaLiquida(pt, pp, pd):
    apt = pt - pp - pd
    if (apt) < 0:
        return 0
    return apt


def calculoAptidao(individuo):     
    pl = []
    for i in range(trimestres):
        pp = 0
        for j in range(len(pGeradores)):
            if individuo[j] == 1:
                pp += pGeradores[j]
            pl.append(potenciaLiquida(pt, pp, pDemanda[i])) 

    print(np.std(pl))

    return np.std(pl)


#geração da população inicial
p = np.zeros((tamPopulacao, tamCromossomo))
for i in range(tamPopulacao):   
    vAleatorios = []
    for x in range(len(pGeradores)):
        if x < 2:
            vAleatorios.append(rd.randint(0, 2))
        else:
            vAleatorios.append(rd.randint(0, 3))    
    
    for j in range(len(pGeradores)):          
        for t in range(trimestres):                           
            if j < 2:           
                p[i][j+t*7] = g12[vAleatorios[j]][t]                
            else:
                p[i][j+t*7] = g37[vAleatorios[j]][t]       

#criação de variáveis do AG
ind = np.zeros(tamCromossomo)
individuo = np.zeros(tamPopulacao)
aptidao = np.zeros(tamPopulacao)
novaGeracao = np.zeros((tamPopulacao, tamCromossomo))
geracoes = 0

#iniciando o algoritmo
while geracoes <= numGeracoes:
    novosIndividuos = 0
    while novosIndividuos < (tamPopulacao - 1):
        totalAptidao = 0
        for i in range(tamPopulacao):                                    
            aptidao[i] = calculoAptidao(p[i])
            totalAptidao += aptidao[i]

        
        # seleção dos pais para o cruzamento - roleta
        #identificando a probabilidade de cada indivíduo
        pic = np.zeros(tamPopulacao)
        piTotal = np.zeros(tamPopulacao)
        pic = (1/totalAptidao) * aptidao

        #criando a roleta
        for i in range(tamPopulacao):
            if(i == 0):
                piTotal[i] = pic[i]
            else:
                piTotal[i] = pic[i] + piTotal[i-1]

        #sorteando os pais de acordo com a probabilidade
        roleta1 = rd.uniform(0,1)
        i = 0
        while roleta1 > piTotal[i]:            
            i+=1
        
        pai1 = i                

        roleta2 = rd.uniform(0,1)
        i = 0
        while roleta2 > piTotal[i]:
            i+=1
        pai2 = i

        while pai1 == pai2:
            roleta2 = rd.uniform(0,1)
            i=0
            while roleta2 > piTotal[i]:
                i+=1
            pai2 = i
                
        #operação de cruzamento
        if pc > rd.uniform(0,1):            
            c = rd.randint(1, 3) * len(pGeradores) #posições 7, 14, 21                   
            gene11 = p[pai1][0:c]
            gene12 = p[pai1][c:tamCromossomo]
            gene21 = p[pai2][0:c]
            gene22 = p[pai2][c:tamCromossomo]
            filho1 = np.concatenate((gene11, gene22), axis=None)
            filho2 = np.concatenate((gene21, gene12), axis=None)

            novaGeracao[novosIndividuos, :] = filho1
            novosIndividuos += 1
            novaGeracao[novosIndividuos, :] = filho2
            novosIndividuos += 1

        #operação de mutação
        if pm > rd.uniform(0,1):
            d = round(1 + (tamCromossomo - 2) * rd.uniform(0,1))
            if novaGeracao[novosIndividuos - 2][d] == 0:
                novaGeracao[novosIndividuos - 2][d] = 1
            else:
                novaGeracao[novosIndividuos - 2][d] = 0
            if novaGeracao[novosIndividuos - 1][d] == 0:
                novaGeracao[novosIndividuos - 1][d] = 1
            else:
                novaGeracao[novosIndividuos - 1][d] = 0

    indice = aptidao.argmax()
    # elem = individuo[indice]    
    elem = aptidao[indice]
        
    if geracoes > 0:
        if elem > melhorAptidao:
            melhorAptidao = elem
            indiceMelhorAptidao = indice
            melhorIndividuo = p[indice]            
            melhorGeracao = geracoes
            populacao = novaGeracao
    else:
        melhorAptidao = elem
        indiceMelhorAptidao = indice
        melhorIndividuo = p[indice]        
        melhorGeracao = 0
        populacao = p

    p = novaGeracao
    geracoes += 1

print(melhorIndividuo, melhorGeracao, aptidao[indiceMelhorAptidao])


        
            
                
        

        

                
                









