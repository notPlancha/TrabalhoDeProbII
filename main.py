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


# classes
class Seccao(Enum):
    RC = "Criação / Renovação do cartão de cidadão"
    RP = "Criação / Renovação do passaporte"
    QC = "Questões judiciais"


class Cliente:
    class idType(Enum):
        Pass = "Passaporte"
        CCPort = "Cartão de cidadão português"
        CCEuro = "Cartão de cidadão de um pais membro da união europeia"
        CCEst = "Cartão de cidadão de um pais não membro da união europeia"
        NE = "Não especificado"

        @classmethod
        def _missing_(cls, value):
            return Cliente.idType.NE

    def __init__(self, ccOrPass: str, tipoId: Cliente.idType):
        if not ccOrPass.isalnum(): raise ValueError("Identificacao não pode ter simbolos")
        self.id = ccOrPass
        self.tipoId = tipoId

    def __str__(self):
        return self.id


class Trabalhador:
    def __init__(self, idNumb: int):
        if idNumb <= 0 or idNumb > 9999:
            raise Trabalhador.InvalidId("Id tem que ser entre 0 e 9999")
        self.id = idNumb

    def __str__(self):
        i = len(str(self.id))
        return f"T{'0' * (4 - i)}{self.id}"

    class InvalidId(ValueError):
        pass


@dataclass
class Tarefa:
    trabalhador: Trabalhador
    seccao: Seccao
    cliente: Cliente
    data: int | float = datetime.now().timestamp()

    @staticmethod
    def criarTarefa(
            idTrabalhador: int = None,
            seccao: Seccao = None,
            nId: tuple[str, Cliente.idType] = None,
            data: str | int | float = None
    ) -> Tarefa:
        if idTrabalhador is None:
            idTrabalhador = input("Id do Trabalhador? ")
            if not idTrabalhador.isdigit():
                raise ValueError("Id do Trabalhador tem que ser um número")
            idTrabalhador = int(idTrabalhador)
        t = Trabalhador(idTrabalhador)
        if seccao is None:
            try:
                seccao = Seccao[chooseOptionCliwDict({i.name: i.value for i in Seccao}).upper()]
            except KeyError:
                raise ValueError("Secção tem que existir")
        if nId is None:
            nId = (input("Id do cliente?"), Cliente.idType.NE)
        client = Cliente(nId[0], nId[1])
        if data is None:
            date = datetime.now().timestamp()
        else:
            dataT = type(data)
            if dataT is str:
                date = parse(data).timestamp()
            elif dataT is int or dataT is float:
                date = data
            else:
                raise TypeError
        return Tarefa(t, seccao, client, date)

    @staticmethod
    def fromRepr(reprStr) -> Tarefa:
        id, seccao, cliId, cliIdT, data = reprStr.split("|")
        return Tarefa.criarTarefa(int(id), Seccao[seccao], (cliId, Cliente.idType[cliIdT]), float(data))

    def __repr__(self):
        return f"{self.trabalhador.id}|{self.seccao.name}|{self.cliente.id}|{self.cliente.tipoId.name}|{self.data}"

    def __str__(self):
        # noinspection PyTypeChecker
        return f"Trabalhador: {self.trabalhador}; Secção: {self.seccao.name}; Cliente: {self.cliente}; " \
               f"Data Criada: {datetime.fromtimestamp(self.data)};"


class PilhaTarefas:
    def __init__(self):
        self.l: list[Tarefa] = []

    def add(self, task: Tarefa = None):
        if task is None:
            task = Tarefa.criarTarefa()
            print(task)
            inp = input("Confirmar? [y]")
            if inp.strip() != "y":
                input("Cancelado")
                return
            else:
                input("Tarefa criada")
        self.l.insert(0, task)

    def get_last(self):
        return self.l[0]

    def remove_last(self):
        return self.l.pop(0)

    def number_of_tasks(self, sector: Seccao | str) -> int:
        if type(sector) is str:
            sector = Seccao[sector]
        ret = 0
        for i in self.l:
            if i.seccao == sector:
                ret += 1
        return ret

    def __len__(self):  # Apenas Tarefas realizadas
        return len(self.l)

    def __str__(self):
        ret = ""
        for i in self.l:
            ret += str(i) + "\n"
        return ret

    def __iter__(self):
        for i in self.l:
            yield i


# utils functions

# here, cancel will be last option
def chooseOptionCli(optionList: list[str], cancel: bool, pergunta: str = "Qual opção?", loop=False) -> str:
    optionsDict = {}
    for i in range(len(optionList) - (1 if cancel else 0)):
        iToAdd = str(i + 1)
        optionsDict[iToAdd] = optionList[i]
    if cancel:
        optionsDict["0"] = optionList[-1]
    return chooseOptionCliwDict(optionsDict, pergunta, loop)


def chooseOptionCliwDict(optionDict: dict, pergunta: str = "Qual opção?", loop: bool = False) -> str:
    ass = []
    for a in optionDict:
        print(f"{a}: {optionDict[a]}")
        ass.append(a.upper())
    if loop:
        inp = input(pergunta).strip()
        while inp.upper() not in ass:
            print("Não reconhecido, certificar-se que selecionou uma das opções")
            inp = input(pergunta).strip()
    else:
        inp = input(pergunta).strip()
    return inp


def formCli(questions: list[tuple[str, Callable, Exception, Callable]], responses: list = None) -> list:
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


# program functions
def menu(pilha: PilhaTarefas = None, tarefa: Tarefa = None, loop: bool = False, experimental: bool = False):
    if pilha is None:
        pilha = PilhaTarefas
    menuCiclo = True
    clearConsole()
    while menuCiclo:  # do/while alternative
        if not loop:
            menuCiclo = False
        menuOptions = [
            "Criar uma nova Pilha de Tarefas",
            "Adicionar à Pilha Uma Tarefa",
            "Ver Tarefa Do Topo da Fila",
            "Remover Tarefa Do Top da Fila",
            "Ver Número de Tarefas de um Setor",
            "Ver Número de Tarefas Total da Pilha",
            "Guardar Pilha de Tarefas",
            "Carregar Pilha de Tarefas"
        ]
        if experimental: menuOptions.append("Outros")
        if loop: menuOptions.append("Sair")
        option = chooseOptionCli(menuOptions, cancel=loop)
        match option:
            case "0":
                menuCiclo = False
            case "1":
                inp = input("Esta opção vai criar uma nova pilha vazia. Continuar? [y]")
                if inp.strip() == "y":
                    pilha = PilhaTarefas()
                    input("Nova pilha criada")
                else:
                    input("Pilha não criada")
            case "2":
                try:
                    pilha.add(tarefa)
                except ValueError as e:
                    input(f"Erro! {str(e)}")
                    continue
            case "3":
                if len(pilha) > 0:
                    input(pilha.get_last())
                else:
                    input("A pilha está vazia")
            case "4":
                inp = input("Esta opção vai remover a última. Continuar? [y]")
                if inp.strip() == "y":
                    if len(pilha) > 0:
                        input(f"pilha removida: {pilha.remove_last()}")
                    else:
                        input("A pilha está vazia")
                else:
                    input("Senha não removida")
            case "5":
                try:
                    seccao = chooseOptionCliwDict({i.name: i.value for i in Seccao}, pergunta="Qual Secção?")
                    input(f"Há {pilha.number_of_tasks(seccao.upper())} dessa secção nesta pilha")
                except KeyError:
                    input("Seccão não reconhecida")
            case "6":
                lp = len(pilha)
                if lp == 0:
                    input("A pilha está vazia")
                else:
                    input(f"Há {'apenas ' if lp == 1 else ''}{len(pilha)} tarefa{'' if lp == 1 else 's'} na pilha")
            case "7":
                inp = input("Nome da Pilha? ")
                if not os.path.exists("saves"):
                    os.mkdir("saves")
                elif os.path.exists(fr"saves\{inp}.txt"):
                    cont = input("Essa pilha já existe, continuar irá substitui-la. Continuar? [y]")
                    if cont.strip() != "y":
                        input("Cancelado")
                        continue

                with open(fr"saves\{inp}.txt", "w") as f:
                    savePilha(f, pilha)
                input("Salvo")
            case "8":
                if len(pilha) > 0:
                    inp = input(
                        "Esta opção vai substituir a pilha atual com a Pilha salva. Para evitar isto pode salvar a pilha atual. Conitnuar? [y]")
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
                l.append("Cancelar")
                opt = chooseOptionCli(l, True, "Qual pilha?", True)
                if opt == "0":
                    input("Cancelado")
                    continue
                with open(fr"saves\{l[int(opt) - 1]}.txt", "r") as f:
                    pilha = loadPilha(f)
                input("Pilha carregada!")
            case _:
                input("Não reconhecido, certifique-se que selecionou uma das opções")


def savePilha(f: TextIO, pilha: PilhaTarefas):
    first = pilha.get_last()
    for i in pilha:
        if not i == first:
            f.write("\n")
        f.write(repr(i))


def loadPilha(f: TextIO) -> PilhaTarefas:
    ret = PilhaTarefas()
    for line in f.readlines():
        ret.l.append(Tarefa.fromRepr(line))  # here is append because the lines are in coordenance with it's order
    return ret


if __name__ == '__main__':
    PilhaMain = PilhaTarefas()
    ciclo = True
    menu(PilhaMain, loop=True)
