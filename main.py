import numpy as np
import random as rd
import matplotlib.pyplot as plt

import tkinter as tk

GERADOR = {
    "LIGADO": 0,
    "DESLIGADO": 1
}

def get_user_input():
    def submit():
        global tamCromossomo, pc, pm, numGeracoes, tamPopulacao
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

def calcula_potencia_liquida(potencia_total, potencia_perdida, potencia_demandada):
    potencia_liquida = potencia_total - potencia_perdida - potencia_demandada
    return max(0, potencia_liquida)

def calculo_aptidao(individuo, pt, potencias_dos_geradores, potencia_demandada_por_trimestre, trimestres):
    lista_de_potencia_liquida = []

    for i in range(trimestres):
        potencia_perdida = sum(potencias_dos_geradores[j] for j in range(len(potencias_dos_geradores)) if individuo[j] == GERADOR["DESLIGADO"])
        potencia_liquida = calcula_potencia_liquida(pt, potencia_perdida, potencia_demandada_por_trimestre[i])
        lista_de_potencia_liquida.append(potencia_liquida)

    return np.std(lista_de_potencia_liquida)

def inicializa_populacao(tam_populacao, tam_cromossomo, potencias_dos_geradores, trimestres):
    populacao = np.zeros((tam_populacao, tam_cromossomo))
    
    for i in range(tam_populacao):
        valores_aleatorios = [rd.randint(0, 2) if x < 2 else rd.randint(0, 3) for x in range(len(potencias_dos_geradores))]
        
        for j in range(len(potencias_dos_geradores)):
            for t in range(trimestres):
                if j < 2:
                    populacao[i][j + t * len(potencias_dos_geradores)] = array_de_geradores_um_e_dois_por_trimestre[valores_aleatorios[j]][t]
                else:
                    populacao[i][j + t * len(potencias_dos_geradores)] = array_de_geradores_do_tres_ao_sete_por_trimestre[valores_aleatorios[j]][t]

    return populacao

def cruzamento(pai1, pai2, pc, tam_cromossomo, potencias_dos_geradores):
    if pc > rd.uniform(0, 1):
        c = rd.randint(1, 3) * len(potencias_dos_geradores)
        gene11, gene12 = pai1[:c], pai1[c:]
        gene21, gene22 = pai2[:c], pai2[c:]
        filho1 = np.concatenate((gene11, gene22), axis=None)
        filho2 = np.concatenate((gene21, gene12), axis=None)
        return filho1, filho2
    else:
        return pai1, pai2

def mutacao(individuo, pm):
    if pm > rd.uniform(0, 1):
        d = rd.randint(0, len(individuo) - 1)
        individuo[d] = 1 if individuo[d] == 0 else 0
    return individuo

# Obtém os parâmetros do usuário
tamCromossomo, pc, pm, numGeracoes, tamPopulacao = get_user_input()

# Configuração das variáveis específicas do problema
potenciasDosGeradores = [20, 15, 35, 40, 15, 15, 10]
pt = sum(potenciasDosGeradores)
potenciaDemandadaPorTrimestre = [80, 90, 65, 70]
trimestres = 4
array_de_geradores_um_e_dois_por_trimestre = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]]
array_de_geradores_do_tres_ao_sete_por_trimestre = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

# Geração da população inicial
populacao = inicializa_populacao(tamPopulacao, tamCromossomo, potenciasDosGeradores, trimestres)

# Configuração do AG
melhor_aptidao = 0
melhor_individuo = []
melhor_geracao = 0


# Antes do loop principal, adicione:
contadorMelhorGeracao = 0
melhor_aptidao = 0  # Inicialize com um valor que garanta a primeira atualização

for geracoes in range(numGeracoes + 1):
    nova_geracao = np.zeros((tamPopulacao, tamCromossomo))
    
    for novos_individuos in range(0, tamPopulacao, 2):
        # Cálculo da aptidão
        aptidao = [calculo_aptidao(populacao[i], pt, potenciasDosGeradores, potenciaDemandadaPorTrimestre, trimestres) for i in range(tamPopulacao)]
        total_aptidao = sum(aptidao)

        # Seleção dos pais para o cruzamento (roleta)
        probabilidade_individual = aptidao / total_aptidao
        probabilidade_acumulada = np.cumsum(probabilidade_individual)

        pai1_idx = np.searchsorted(probabilidade_acumulada, rd.uniform(0, 1))
        pai2_idx = np.searchsorted(probabilidade_acumulada, rd.uniform(0, 1))

        pai1 = populacao[pai1_idx]
        pai2 = populacao[pai2_idx]

        # Operação de cruzamento
        filho1, filho2 = cruzamento(pai1, pai2, pc, tamCromossomo, potenciasDosGeradores)

        # Operação de mutação
        filho1 = mutacao(filho1, pm)
        filho2 = mutacao(filho2, pm)

        nova_geracao[novos_individuos, :] = filho1
        nova_geracao[novos_individuos + 1, :] = filho2

    # Avaliação do melhor indivíduo
    melhor_idx = np.argmax(aptidao)
    melhor_aptidao_atual = aptidao[melhor_idx]
    
    if melhor_aptidao_atual > melhor_aptidao:
        melhor_aptidao = melhor_aptidao_atual
        melhor_individuo = populacao[melhor_idx]
        melhor_geracao = geracoes
        contadorMelhorGeracao = 0  # Zera o contador quando há uma atualização

    populacao = nova_geracao
    contadorMelhorGeracao += 1


# Resultados finais
print("Melhor Indivíduo:", melhor_individuo)
print("Aptidão da melhor solução na geração {}: {}".format(melhor_geracao, melhor_aptidao))
print('contadorMelhorGeracao: ', contadorMelhorGeracao)
# Após a linha que imprime o melhor indivíduo, adicione:

print("Melhor Geração:", melhor_geracao)
print("Melhor Aptidão:", melhor_aptidao)

# Gráfico da aptidão ao longo das gerações
geracoes_list = list(range(numGeracoes + 1))
aptidao_list = [np.mean([calculo_aptidao(populacao[i], pt, potenciasDosGeradores, potenciaDemandadaPorTrimestre, trimestres) for i in range(tamPopulacao)]) for _ in range(numGeracoes + 1)]
plt.plot(geracoes_list, aptidao_list)
plt.xlabel('Geração')
plt.ylabel('Aptidão Média')
plt.title('Evolução da Aptidão ao Longo das Gerações')
plt.show()

# Histograma das potências líquidas do melhor indivíduo
melhor_pl = [calcula_potencia_liquida(pt, sum(potenciasDosGeradores[j] for j in range(len(potenciasDosGeradores)) if melhor_individuo[j] == GERADOR["DESLIGADO"]), potenciaDemandadaPorTrimestre[i]) for i in range(trimestres)]
plt.hist(melhor_pl, bins=10, color='blue', edgecolor='black')
plt.xlabel('Potência Líquida')
plt.ylabel('Frequência')
plt.title('Histograma das Potências Líquidas do Melhor Indivíduo')
plt.show()
