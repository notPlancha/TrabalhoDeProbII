"""
Loja do cidadão
-RC: criar/renovar CC
-RP: criar/renovar passaporte
-QC: Questões Judiciais
Objetivo é desebnvolver um programa que
faça log das tarefas realizadas todas
--------------------------------------------------
3+1 incubências (T#[O])
T1-Criar tarefas
T2-Criar uma pilha de tarefas
T3-Criar um interface
T4O-Criar ficheiro do log do dia
APENAS UM FICHEIRO .py
TODO
para o T40, o meu plano é no if main por um try/finnaly para guardar as coisas da fila
Dps quando recomeçar poder escolher o dia de hoje ou fazer load de um dia specifico
(n consegue criar nada para a fila ai, apenas confirmar como feito e ver as antigas)
TODO O meu plano é criar um cli based, dps fazer um interface no pygame
"""
# TODO remove this
# file:///C:/Users/Andre/Downloads/Enunciado_B_Trabalho_Individual_1.pdf
from __future__ import annotations

import os
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Callable, TextIO

from dateutil.parser import parse
from numbers import Number
#classes
class Seccao(Enum):
    RC = "Criação / Renovação do cartão de cidadão"
    RP = "Criação / Renovação do passaporte"
    QC = "Questões judiciais"

class Cliente:
    class idType(Enum):
        Pass = "Passport"
        CCPort = "Cartão de cidadão português"
        CCEuro = "Cartão de cidadão de um pais membro da união europeia"
        CCEst = "Cartão de cidadão de um pais não membro da união europeia"
        NE = "Não especificado"

        @classmethod
        def _missing_(cls, value):
            return Cliente.idType.NE

    def __init__(self, ccOrPass: str, tipoId: idType):
        if not ccOrPass.isalnum(): raise ValueError("Identificacao não pode ter simbolos")
        self.id = ccOrPass
        self.tipoId = tipoId

    def __str__(self):
        return self.id

class Trabalhador:
    def __init__(self, idNumb: int):
        if idNumb <= 0 or idNumb > 9999:
            raise Trabalhador.InvalidId()
        self.id = idNumb

    def __str__(self):
        return f"T{self.id}"

    class InvalidId(ValueError):
        pass

@dataclass
class Tarefa:
    trabalhador: Trabalhador
    seccao: Seccao
    cliente: Cliente
    data: Number = datetime.now().timestamp()

    def __repr__(self):
        return f"{self.trabalhador.id}|{self.seccao.name}|{self.cliente.id}"

    @staticmethod
    def criarTarefa(
            idTrabalhador: int = None,
            seccao: Seccao = None,
            nId: tuple[str, Cliente.idType] = None,
            data: str | Number = None
    ) -> Tarefa:
        if idTrabalhador is None:
            idTrabalhador = input("Id do Trabalhador? ")
            if not idTrabalhador.isdigit():
                raise ValueError("Id do Trabalhador tem que ser um número")
            idTrabalhador = int(idTrabalhador)
        t = Trabalhador(idTrabalhador)
        if seccao is None:
            try:
                seccao = Seccao[chooseOptionCliwDict({i.name: i.value for i in Seccao})]
            except KeyError: # input inserido errado TODO verificar se e este o erro q levanta
                raise ValueError("Secção tem que existir")
        if nId is None:
            nId = (input("Id do cliente?"), Cliente.idType.NE)
        client = Cliente(nId[0], nId[1])
        if data is None:
            date = datetime.now()
        else:
            dataT = type(data)
            if dataT is str:
                date = parse(data).timestamp()
            elif dataT is Number:
                date = data
            else:
                raise TypeError
        return Tarefa(t, seccao, client, date)

    def __str__(self):
        # noinspection PyTypeChecker
        return f"Trabalhador: {self.trabalhador}; Secção: {self.seccao}; Cliente: {self.cliente}; " \
               f"Data Criada: {datetime.fromtimestamp(self.data)}; Realizada: {('Sim' if self.done else 'Não')}"

class PilhaTarefas:
    def __init__(self):
        self.l: list[Tarefa] = []

    def add(self, task: Tarefa = None):
        if task is None:
            task = Tarefa.criarTarefa()
            print(task)
            inp = input("Confirmar? [1]")
            if inp.strip() != "1":
                input("Cancelado")
                return
            else:
                print("Tarefa criada")
        self.l.insert(0, task)

    def get_last(self):
        return self.l[0]

    def remove_last(self):
        return self.l.pop(0)

    def number_of_tasks(self, sector: Seccao | str) -> int:
        if type(sector) is str:
            match sector:
                case "RC":
                    sector = Seccao.RC
                case "RP":
                    sector = Seccao.RP
                case "QC":
                    sector = Seccao.QC
                case _:
                    raise ValueError
        ret = 0
        if type(sector) is Seccao:
            for i in self.l:
                if i.seccao == sector:
                    ret += 1
            return ret
        else:
            raise TypeError

    def __len__(self):  # Apenas Tarefas realizadas
        return len(self.l)

    def __str__(self):
        ret = ""
        for i in self.l:
            ret += str(i) + "\n"
        return ret

    def __iter__(self):
        return self.l


#utils functions

#here, cancel will be last option
def chooseOptionCli(optionList : list[str], cancel : bool, pergunta : str  = "Qual opção?", loop = False) -> str:
    optionsDict = {}
    for i in range(len(optionList) - (1 if cancel else 0)):
        iToAdd = str(i + 1)
        optionsDict[iToAdd] = optionList[i]
    if cancel:
        optionsDict["0"] = optionList[-1]
    return chooseOptionCliwDict(optionsDict, pergunta, loop)
def chooseOptionCliwDict(optionDict: dict, pergunta : str = "Qual opção?", loop :bool = False) -> str:
    ass = []
    for a, b in optionDict:
        print(f"{a}: {b}")
        ass.append(a)
    if loop:
        inp = input(pergunta).strip()
        while inp not in ass:
            print("Não reconhecido, certificar-se que selecionou uma das opções")
            inp = input(pergunta).strip()
    else:
        inp = input(pergunta).strip()
    return inp
def formCli(questions : list[tuple[str, Callable, Exception, Callable]], responses:list = None) -> list:
    if responses is None: responses = [None for i in questions]
    for i in range(len(questions)):
        if responses[i] is not None: continue
        question, condition, err, trans = questions[i]
        inp = input(question)
        if condition is not None and not condition(inp):
            raise err
        else:
            responses[i] = (trans(inp) if trans is not None else inp)
    return responses
def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

#program functions
def menu(pilha : PilhaTarefas = None, tarefa : Tarefa = None, loop : bool = False, experimental : bool = False):
    if pilha is None:
        pilha = PilhaTarefas
    menuCiclo = True
    clearConsole()
    while menuCiclo:  #do/while alternative
        if not loop:
            menuCiclo = False
        menuOptions = [
            "Criar uma nova Pilha de Tarefas",
            "Adicionar à Pilha Uma Tarefa",
            "Ver Tarefa Do Topo da Fila",
            "Remover Tarefa Do Top da Fila",
            "Ver Número de Tarefas de um Setor",
            "Ver Número de Tarefas Total da Pilha"
            "Ver todas as tarefas realizadas",
            "Guardar Pilha de Tarefas",
            "Carregar Pilha de Tarefas"
        ]
        if experimental: menuOptions.append("Outros")
        if not loop: menuOptions.append("Sair")
        option = chooseOptionCli(menuOptions, cancel=loop)
        match option:
            case "0":
                menuCiclo = False
            case "1":
                inp = input("Esta opção vai criar uma nova pilha vazia. Continuar? [1]")
                if inp.strip() == "1":
                    pilha = PilhaTarefas()
                    input("Nova pilha criada")
                else:
                    input("Pilha não criada")
            case "2":
                try:
                    pilha.add(tarefa)
                except ValueError as e:
                    input(f"Erro! {e}")
                    continue
            case "3":
                if len(pilha) > 0:
                    input(pilha.get_last())
                else:
                    input("A pilha está vazia")
            case "4":
                inp = input("Esta opção vai remover a última. Continuar? [1]")
                if inp == "1":
                    if len(pilha) > 0:
                        input(f"pilha removida: {pilha.remove_last()}")
                    else:
                        input("A pilha está vazia")
                else:
                    input("Senha não removida")
            case "5":
                try:
                    seccao = Seccao[chooseOptionCliwDict({i.name: i.value for i in Seccao}, pergunta="Qual Secção? ")]
                except KeyError:
                    input("Seccão não reconhecida")
                    continue
                input(f"Há {pilha.number_of_tasks()} dessa secção nesta pilha")
            case "6":
                lp = len(pilha)
                if lp == 0:
                    input("A pilha está vazia")
                else:
                    input(f"Há {'apenas ' if lp == 1 else ''}{len(pilha)} tarefa{'' if lp == 1 else 's'} na pilha")
            case "7":
                input(pilha)
            case "8":
                inp = input("Nome da Pilha? ")
                if os.path.exists(fr"saves\{inp}.txt"):
                    cont = input("Essa pilha já existe, continuar ir'a substitui-la. Continuar? [y]")
                    if cont.strip() != "y":
                        continue
                with open(fr"saves\{inp}.txt", "w") as f:
                    savePilha(f, pilha)
                input("Salvo")
            case "9":
                if len(pilha) > 0:
                    inp = input("Esta opção vai substituir a pilha atual com a Pilha salva. Para evitar isto pode salvar a pilha atual. Conitnuar? [y]")
                    if inp.strip() != "y":
                        continue
                l = []
                fs = os.listdir("saves")
                for i in fs:
                    if i[-4:] != ".txt":
                        continue
                    l.append(i[:-4])
                if len(l) == 0:
                    input("Não há pilhas salvas!")
                    continue
                opt = chooseOptionCli(l, True, "Qual pilha?", True)
                with open(fr"saves\{opt}.txt", "r") as f:
                    pilha = loadPilha(f)
                input("Pilha carregada!")
            case _:
                raise NotImplemented

def savePilha(f : TextIO, pilha : PilhaTarefas):
    pass

def loadPilha(f : TextIO) -> PilhaTarefas:
    pass

def checkFormatForTarefa(TarInStr):
    pass

if __name__ == '__main__':
    PilhaMain = PilhaTarefas()
    ciclo = True
    menu(PilhaMain, loop= True)