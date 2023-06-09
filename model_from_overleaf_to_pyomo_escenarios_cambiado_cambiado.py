import copy

import time
import sys
import shutil
import datetime
from time import perf_counter as time
import pandas as pd
import os
import math
import pyomo.environ as pe
import pyomo.opt as po
class Truck():
    def __init__(self, id, Length, Width, Height, alpha=0.9):
        self.id = id
        self.Length = Length
        self.Width = Width
        self.Height = Height
        self.Volume = self.Length*self.Width*self.Height
        self.alpha = alpha

class Container():
    def __init__(self, id, Length, Width, Height):
        self.id = id
        self.Length = Length
        self.Width = Width
        self.Height = Height
        self.Volume = self.Length*self.Width*self.Height
def update_data(path=None, folder="default", now = datetime.datetime.now()  , planning_days=10):
    model = pe.ConcreteModel("Cargacamiones")

    if path is None:
        path = os.getcwd()
        if os.path.isdir(path + "/output/lastsol"):
            ## Clean all files in output/lastsol
            for filename in os.listdir(path + "/output/lastsol"):
                os.remove(path + "/output/lastsol/" + filename)
            ## Copy all files of output/backupsol to output/lastsol
            for filename in os.listdir(path + "/output/backup"):
                shutil.copy(path + "/output/backup/" + filename, path + "/output/lastsol/" + filename)
            pass
            # ## Copy all files of output/backupsol to output/lastsol
            # for filename in os.listdir(path + "/output/backup"):
            #     shutil.copy(path + "/output/backup/" + filename, path + "/output/lastsol/" + filename)
            # pass
        else:
            os.mkdir(path + "/output/lastsol")
            ## Copy all files of output/backupsol to output/lastsol
            for filename in os.listdir(path + "/output/backup"):
                shutil.copy(path + "/output/backup/" + filename, path + "/output/lastsol/" + filename)
        #     pass
        wd = os.getcwd() + "\output"
        path_save = wd + "\{}-{}-{}-time{}".format(now.day, now.month, now.year,planning_days)
        os.makedirs(path, exist_ok=True)
    elif os.path.isdir(os.getcwd() + "\output" + "\{}{}{}".format(now.day, now.month, now.year) + "\\" + folder):
        wd = os.getcwd() + "\output"
        path_save = wd + "\{}-{}-{}-time{}".format(now.day, now.month, now.year,planning_days)
        print("path_save with folder", path_save)

    else:
        wd = os.getcwd() + "\output"
        path_save = wd + "\{}-{}-{}-time{}".format(now.day, now.month, now.year,planning_days)
        path_save = path_save + "\\" + folder
        os.makedirs(path_save, exist_ok=True)
        for filename in os.listdir(os.getcwd() + "/output/backup"):
            shutil.copy(os.getcwd() + "/output/backup/" + filename, "{}\{}".format(path_save, filename))
    # \multicolumn{2}{|l|}{Sets of indices}                                                                   \\ \hline




    pd_productos=pd.read_csv(path+"\Productos.csv")
    pd_demanda =pd.read_csv(path+"\Demanda.csv")
    pd_dimensiones_camiones =pd.read_csv(path+"\Dimensiones_Camiones.csv")
    pd_dimensiones_contenedores =pd.read_csv(path+"\Dimensiones_Contenedores.csv")
    # Print check if path_save exists
    pd_productos.to_csv(path_save+"\Productos.csv", index=False)
    pd_demanda.to_csv(path_save+"\Demanda.csv", index=False)
    pd_dimensiones_contenedores.to_csv(path_save+"\Dimensiones_Contenedores.csv", index=False)
    pd_dimensiones_camiones.to_csv(path_save+"\Dimensiones_Camiones.csv", index=False)


    # \textit{I}       & Conjunto de contenedores (\textit{i} =1, 2,…,\textit{I})
    I=list(range(1,100))
    model.I=pe.Set(initialize=I, doc="Set of containers (i =1, 2,…,I)")

    N={i:i for i in pd_productos["i"].unique().tolist()}
    model.N = pe.Set(initialize=pd_productos["i"].unique().tolist(), doc="Set of products (i =1, 2,…,I)")
    # \textit{T}       & Set of planning periods \textit{(t} =1, 2…\textit{T)}                                        \\

    T=list(range(1,planning_days+1))
    model.T = pe.Set(initialize=T, doc="Set of planning periods (t =1, 2…T)")





    # \textit{C}       & Conjunto de tipos de contenedor contenedores (\textit{C} =1, 2,…,\textit{I})                                                                                              \\
    C = {}
    i=0
    for row in pd_dimensiones_contenedores.itertuples():
        C.update({row.id :Container(row.id,row.Length,row.Width,row.Heigth)})
        i+=1

    model.C = pe.Set(initialize=C.keys(), doc="Set of container types (C =1, 2,…,I)")

    # \textit{K}       & Set of trucks (\textit{k} =1, 2,…,\textit{K)}                                                        \\
    K = {}
    K_name = []
    i=0
    for row in pd_dimensiones_camiones.itertuples():
        for _ in range(3):
            K.update({ i :Truck(row.id,row.Length,row.Width,row.Heigth) })
            K_name.append(i)
            i += 1
    print(K)
    model.K = pe.Set(initialize=K_name, doc="Set of trucks (k =1, 2,…,K)")

    # \textit{I}       & Conjunto de contenedores (\textit{i} =1, 2,…,\textit{I})
    max_containers_per_truck=max(math.floor(K[k].Volume/C[b].Volume) for b in C for k in K)
    num_types_containers=len(C)

    # Parameters


    #\textit{$u_{in}$} & Cantidad de producto \textit{n} que cabe en un contenedor \textit{i}                             \\[0.2cm]

    u={}
    # for i in I:
    #     for n in N:
    #         u[i,n]=0
    for row in pd_productos.itertuples():
        for k ,c in enumerate(row.id_container.split("|")):
            # set the value of u if the contaner n has the same id as b
            u[c, row.i]=float(str(row.items_per_container).split("|")[k])

    model.u = pe.Param(model.C, model.N, initialize=u, doc="Amount of product n that fits in a container b",  default=0)

    # \textit{$w_{in}$} & Peso del contenedor que transporta el producto.                   \\[0.2cm]

    # \textit{$IC_n$} & de inventario de un producto i \\[0.2cm]
    CosteStock={}
    stockInicial={}
    for n in N:
        CosteStock[n] = pd_productos[pd_productos["i"] == n]["CosteStock"].values[0]
        stockInicial[n] = pd_productos[pd_productos["i"] == n]["Stock"].values[0]

    model.CosteStock = pe.Param(model.N, initialize=CosteStock, doc="Coste de almacenar un producto")
    model.stockInicial = pe.Param(model.N, initialize=stockInicial, doc="Stock inicial de cada producto")

    # \textit{M}& Un número grande utilizado para la lógica del modelo;\\[0.2cm]
    M=1000000
    # \textit{m} & Un número pequeño utilizado para la lógica del modelo;\\[0.2cm]
    m=0.000001
    # $\alpha$ & Área de apoyo a considerar en el modelo, puede asumir valores entre 0 y 1, donde 0 proporciona 0$ \% $ de área de apoyo y crece gradualmente hasta 1 que garantiza 100$ \% $ del área de apoyo de la caja;\\[0.2cm]
    alpha=0.5




    # \textit{$D_{nt}$}  & Demanda de producto \textit{n} en \textit{t}                             \\[0.2cm]
    D={}
    for row in pd_demanda.itertuples():
        if row.t in T:
            if row.i in N:
                D[row.i, row.t]=row.Demanda
    model.D = pe.Param(model.N, model.T, initialize=D, doc="Demand of product n in t")

    CosteStock={}
    stockInicial={}
    for n in N:
        CosteStock[n] = pd_productos[pd_productos["i"] == n]["CosteStock"].values[0]
        stockInicial[n] = pd_productos[pd_productos["i"] == n]["Stock"].values[0]

    model.CosteStock = pe.Param(model.I, initialize=CosteStock, doc="Coste de almacenar un producto")
    model.stockInicial = pe.Param(model.I, initialize=stockInicial, doc="Stock inicial de cada producto")
    # \textit{$SC_n$} & Número de días de cobertura de existencias para el producto i\\[0.2cm]
    SC={}
    for n in N:
        SC[n] = pd_productos[pd_productos["i"] == n]["Days_Stock_Coverage"].values[0]

    model.SC = pe.Param(model.N, initialize=SC, doc="Number of days of stock coverage for product n")




    # \multicolumn{2}{|l|}{Variables de decisión}
    #
    # \textit{I$_{nt}$} & Inventario del producto \textit{n} al final del período de tiempo \textit{t}                                \\

    model.vI=pe.Var(model.N, model.T, within=pe.NonNegativeReals, doc="Inventario del producto n al final del período de tiempo t")

     # \textit{Y$_{kt}$} & Variable binaria que indica si se ha utilizado un camión \textit{k} en el período de tiempo \textit{t}     \\[0.15cm]

    model.Y=pe.Var(model.K, model.T, within=pe.Binary, doc="Variable binaria que indica si se ha utilizado un camión k en el período de tiempo t")

    # \textit{$X^i_{kt}$} & Variable binaria que indica si el contenedor i va a ser usado en el tiempo de planificación t  \\[0.15cm]

    model.Xi=pe.Var(model.I, model.K, model.T, within=pe.Binary, doc="Variable binaria que indica si el contenedor i va a ser usado en el tiempo de planificación t")

    # \textit{$X^c_{ikt}$} & Variable binaria que indica si
    # el contenedor i va a ser del tipo c en el tiempo de planificación t en el camión k \\[0.15cm]

    model.Xc=pe.Var(model.C, model.I, model.K, model.T, within=pe.Binary, doc="Variable binaria que indica si el contenedor i va a ser del tipo c en el tiempo de planificación t en el camión k")

    # \textit{$X^n_{cikt}$} & Variable binaria que indica si la el contenedor i es del tipo c y va a ser usado en el tiempo de planificación t cargando el producto n  \\[0.15cm]

    model.Xn=pe.Var(model.N, model.C, model.I, model.K, model.T, within=pe.Binary, doc="Variable binaria que indica si la el contenedor i es del tipo c y va a ser usado en el tiempo de planificación t cargando el producto n")


    # \textit{$V^n_{t}$} & Variable entera que indica la cantidad abastecida del producto n durante el periodo de planificación t \\[0.15cm]

    model.Vn=pe.Var(model.N, model.T, within=pe.NonNegativeIntegers, doc="Variable entera que indica la cantidad abastecida del producto n durante el periodo de planificación t")

    # \textit{$V^k_{int}$} & Variable entera que indica la cantidad abastecida del producto n en el camión k por el contenedor i durante el periodo de planificación   \\[0.15cm]

    model.Vk=pe.Var(model.K, model.I, model.N, model.T, within=pe.NonNegativeIntegers, doc="Variable entera que indica la cantidad abastecida del producto n en el camión k por el contenedor i durante el periodo de planificación")

    # \textit{$x_{ikt},y_{ikt},z_{ikt}$} & Coordenadas de la esquina frontal inferior izquierda de la casilla i durante el periodo de planificación t;  \\[0.15cm]

    model.x=pe.Var(model.I, model.K, model.T, within=pe.NonNegativeIntegers, doc="Coordenadas de la esquina frontal inferior izquierda de la casilla i durante el periodo de planificación t")
    model.y=pe.Var(model.I, model.K, model.T, within=pe.NonNegativeIntegers, doc="Coordenadas de la esquina frontal inferior izquierda de la casilla i durante el periodo de planificación t")
    model.z=pe.Var(model.I, model.K, model.T, within=pe.NonNegativeIntegers, doc="Coordenadas de la esquina frontal inferior izquierda de la casilla i durante el periodo de planificación t")

    # \textit{$lx_{cikt},ly_{cikt},lz_{cikt}$} & Define si la longitud de la caja i es paralela al eje X, Y o Z en el periodo de planificación t. Por ejemplo, $lx_{cikt}t$ es igual a 1 si la longitud de la caja i es paralela al eje X, en caso contrario, $lx_{cikt}t$ es igual a 0;  \\[0.15cm]

    model.lx=pe.Var(model.C, model.I, model.K, model.T, within=pe.Binary, doc="Define si la longitud de la caja i es paralela al eje X en el periodo de planificación t")
    model.ly=pe.Var(model.C, model.I, model.K, model.T, within=pe.Binary, doc="Define si la longitud de la caja i es paralela al eje Y en el periodo de planificación t")
    model.lz=pe.Var(model.C, model.I, model.K, model.T, within=pe.Binary, doc="Define si la longitud de la caja i es paralela al eje Z en el periodo de planificación t")

    # \textit{$wx_{cikt},wy_{cikt},$ $ wz_{cikt}$} &  Define si la anchura de la caja i es paralela al eje X, Y o Z en el periodo de planificación t. Por ejemplo, $wx_{cikt}t$ es igual a 1 si la anchura de la caja i es paralela al eje X, en caso contrario, $wx_{cikt}t$ es igual a 0;  \\[0.15cm]

    model.wx=pe.Var(model.C, model.I, model.K, model.T, within=pe.Binary, doc="Define si la anchura de la caja i es paralela al eje X en el periodo de planificación t")
    model.wy=pe.Var(model.C, model.I, model.K, model.T, within=pe.Binary, doc="Define si la anchura de la caja i es paralela al eje Y en el periodo de planificación t")
    model.wz=pe.Var(model.C, model.I, model.K, model.T, within=pe.Binary, doc="Define si la anchura de la caja i es paralela al eje Z en el periodo de planificación t")

    # \textit{$hx_{cikt},hy_{cikt}$ $,hz_{cikt}$} & Define si la altura de la caja i es paralela al eje X, Y o Z en el periodo de planificación t. Por ejemplo, $hx_{cikt}t$ es igual a 1 si la altura de la caja i es paralela al eje X, en caso contrario, $hx_{cikt}t$ es igual a 0;  \\[0.15cm]

    model.hx=pe.Var(model.C, model.I, model.K, model.T, within=pe.Binary, doc="Define si la altura de la caja i es paralela al eje X en el periodo de planificación t")
    model.hy=pe.Var(model.C, model.I, model.K, model.T, within=pe.Binary, doc="Define si la altura de la caja i es paralela al eje Y en el periodo de planificación t")
    model.hz=pe.Var(model.C, model.I, model.K, model.T, within=pe.Binary, doc="Define si la altura de la caja i es paralela al eje Z en el periodo de planificación t")

    model.M= M
    # \textit{$a_{i j k t}, b_{i j k t}, c_{i j k t}$ $, d_{i j k t}, e_{i j k t}, f_{i j k t}$} & Variables binarias que indican la posición relativa entre dos casillas. La variable aik es igual a 1 si la casilla i está a la izquierda de la casilla k. Del mismo modo, las variables bik, cik, dik, eik, fik indican si la casilla i está a la derecha, detrás, delante, debajo o encima de la casilla k, respectivamente. Estas variables sólo son necesarias cuando i $\not = $ k.  \\[0.15cm]
    # \hline

    model.a=pe.Var(model.I, model.I, model.K, model.T, within=pe.Binary, doc="Variable binaria que indica si la casilla i está a la izquierda de la casilla k")
    model.b=pe.Var(model.I, model.I, model.K, model.T, within=pe.Binary, doc="Variable binaria que indica si la casilla i está a la derecha de la casilla k")
    model.c=pe.Var(model.I, model.I, model.K, model.T, within=pe.Binary, doc="Variable binaria que indica si la casilla i está detrás de la casilla k")
    model.d=pe.Var(model.I, model.I, model.K, model.T, within=pe.Binary, doc="Variable binaria que indica si la casilla i está delante de la casilla k")
    model.e=pe.Var(model.I, model.I, model.K, model.T, within=pe.Binary, doc="Variable binaria que indica si la casilla i está debajo de la casilla k")
    model.f=pe.Var(model.I, model.I, model.K, model.T, within=pe.Binary, doc="Variable binaria que indica si la casilla i está encima de la casilla k")


    # Restricciones

    # La siguiente restricción mantiene el nivel de inventario
    # $$ I_{nt}=I_{n t'}-D_{nt}+V^n_t \quad \forall n,t,t'\in T : t'=t+1 \text{ y } t\leq|T|$$

    def _I(model, n, t):
        if t == 1:
            return model.vI[n, t] == model.stockInicial[n] - model.D[n, t] + model.Vn[n, t]
        else:
            return model.vI[n, t] == model.vI[n, t - 1] - model.D[n, t] + model.Vn[n, t]

    model.ConsI = pe.Constraint(model.N, model.T, rule=_I, doc="Inventory level")
    # \begin{equation}
    #     I_{n t }\geq     \begin{cases}
    #         \sum_{s \in \lbrace 1 , \dots , SC_n \rbrace } D_{n,t+s} \quad & \text{if } n \in N, t \in \lbrace 1, \dots , |T|-SC_n \rbrace \\
    #         \sum_{s \in \lbrace 1 , \dots , SC_n \rbrace } D_{n,|T|-SC_n+s} & \text{else}
    #     \end{cases}
    # \end{equation}
    l1 = {}
    for n in N:
        for t in T:
            if t < len(T) - SC[n]+1:
                l1[n] = sum(D[n, t + s] for s in range(1, SC[n] + 1))

    def _I2(model, n, t):
        if t < len(T) - SC[n]+1:
            return model.vI[n, t] >= sum(model.D[n, t + s] for s in range(1, SC[n] + 1))
        else:
            return model.vI[n, t] >= l1[n]

    model.I2_rule = pe.Constraint(model.N, model.T, rule=_I2)

    # Las siguientes ecuaciones ligan el contenedor con el tipo de contenedor que va a ser.
    # \begin{align}
    #     \sum_c X^c_{ikt}\leq X^i_{kt} \\
    #     \sum_n X^n_{cikt}\leq X^c_{ikt}
    # \end{align}

    def rule_X(model, i, k, t):
        return sum(model.Xc[c, i, k, t] for c in model.C) <= model.Xi[i, k, t]

    model.rule_X = pe.Constraint(model.I, model.K, model.T, rule=rule_X, doc="Restricción que asegura que el contenedor i es del tipo k")

    def rule_X2(model,  c, i, k, t):
        return sum(model.Xn[n, c, i, k, t] for n in model.N) <= model.Xc[c, i, k, t]

    model.rule_X2 = pe.Constraint(model.C, model.I, model.K, model.T, rule=rule_X2, doc="Restricción que asegura que el contenedor i es del tipo k")


    # En la ecuación \ref{eq:CantidadContenedor} determinamos la cantidad de producto n que va a ser transportado por el camión k en el periodo de planificación t. Por otra parte, en en la ecuación \ref{eq:CantidadTransportadoProductoDia} calculamos la cantidad transportada del producto n durante el periodo de planificación t.
    # \begin{align}
    #     V^k_{int}&=\sum_{c\in T(n)}X^n_{cikt}u_{cn}\quad   &\forall i,k,n,t \label{eq:CantidadContenedor}\\
    #     V^n_t&=\sum_{i,k} V^k_{int} \quad &\forall i, t \label{eq:CantidadTransportadoProductoDia}
    # \end{align}

    def rule_V(model, n, i, k, t):
        return model.Vk[k, i, n, t] == sum(model.Xn[n, c, i, k, t] * model.u[c, n] for c in model.C)

    model.rule_V = pe.Constraint(model.N, model.I, model.K, model.T, rule=rule_V, doc="Cantidad de producto n que va a ser transportado por el camión k en el periodo de planificación t")

    def rule_V2(model, n, t):
        return model.Vn[n, t] == sum(model.Vk[k, i, n, t] for i in model.I for k in model.K)

    model.rule_V2 = pe.Constraint(model.N, model.T, rule=rule_V2, doc="Cantidad transportada del producto n durante el periodo de planificación t")

    # En este modelo nos aseguramos que dos contenedores no se superponen a partir de sus posiciones relativas. Es decir, si un contenedor esta a la derecha de otro entonces estos no se pueden solapar. Las ecuaciones \ref{eq:ra} y \ref{eq:rb} nos permiten identificar si una caja i esta a la izquierda o la derecha de otra caja j. Para determinar este hecho hace falta tener en cuenta las dimensiones del tipo de contenedor y de la orientación en que colocamos la caja. Por tanto, definimos las siguientes restricciones.
    # \begin{align}
    #     &x_{ikt}+\sum_{c \in C} (p_{ic} l x_{cikt}+ q_{ci}wx_{cikt}+ r_{ci}hx_{cikt})  \leq x_{jkt}+\left(1-a_{i j k t}\right)M \quad  &\forall i, j \in I: i \neq j,t
    #  \label{eq:ra}\\
    # &x_{jkt}+\sum_{c \in C} (p_{jc} l x_{cjkt}+ q_{cj}wx_{cjkt}+ r_{cj}hx_{cjkt} ) \leq x_{ikt}+\left(1-b_{i j k t}\right) M \quad  &\forall i, j \in I: i \neq j, t,k
    # \label{eq:rb}
    # \end{align}

    # p_{ic} = C[c].Length
    # q_{ic} = C[c].Width
    # r_{ic} = C[c].Height

    def rule_ra(model, i, j, k, t):
        if i!=j:
            return model.Xi[i,k,t]+sum(C[c].Length*model.lx[c,i,k,t]+C[c].Width*model.wx[c,i,k,t]+C[c].Height*model.hx[c,i,k,t]
                                      for c in model.C) <= model.x[j,k,t]+(1-model.a[i,j,k,t])*M
        else:
            return pe.Constraint.Skip

    model.rule_ra = pe.Constraint(model.I, model.I, model.K, model.T, rule=rule_ra, doc="Restricción que asegura que una caja i esta a la izquierda de otra caja j")

    def rule_rb(model, i, j, k, t):
        if i!=j:
            return model.x[j,k,t]+sum(C[c].Length*model.lx[c,j,k,t]+C[c].Width*model.wx[c,j,k,t]+C[c].Height*model.hx[c,j,k,t]
                                      for c in model.C) <= model.Xi[i,k,t]+(1-model.b[i,j,k,t])*M
        else:
            return pe.Constraint.Skip

    model.rule_rb = pe.Constraint(model.I, model.I, model.K, model.T, rule=rule_rb,
                                  doc="Restricción que asegura que una caja i esta a la derecha de otra caja j")
    #     #
    #  De forma similar imponemos las restricciones para determinar si una caja esta adelante o atrás de otra.
    # \begin{align}
    # &y_{ikt}+\sum_{c \in C} (q_{ci} w y_{cikt}+ p_{ic}ly_{cikt}+r_{ci}zy_{cikt})  \leq y_{jkt}+\left(1-c_{i j k t}\right) M \quad  &\forall i, j \in I: i \neq j, t \\[0.15cm]
    # &y_{jkt}+\sum_{c \in C} (q_{cj} w y_{cjkt}+ p_{jc}ly_{cjkt}+r_{cj}zy_{cjkt}) \leq y_{ikt}+\left(1-d_{i j k t}\right) M \quad  &\forall i, j \in I: i \neq j, t
    # \end{align}

    def rule_rc(model, i, j, k, t):
        if i!=j:
            return model.y[i,k,t]+sum(C[c].Width*model.wy[c,i,k,t]+C[c].Length*model.ly[c,i,k,t]+C[c].Height*model.hy[c,i,k,t]
                                      for c in model.C) <= model.y[j,k,t]+(1-model.c[i,j,k,t])*M
        else:
            return pe.Constraint.Skip

    model.rule_rc = pe.Constraint(model.I, model.I, model.K, model.T, rule=rule_rc,
                                    doc="Restricción que asegura que una caja i esta adelante de otra caja j")

    def rule_rd(model, i, j, k, t):
        if i!=j:
            return model.y[j,k,t]+sum(C[c].Width*model.wy[c,j,k,t]+C[c].Length*model.ly[c,j,k,t]+C[c].Height*model.hy[c,j,k,t]
                                      for c in model.C) <= model.y[i,k,t]+(1-model.d[i,j,k,t])*M
        else:
            return pe.Constraint.Skip

    model.rule_rd = pe.Constraint(model.I, model.I, model.K, model.T, rule=rule_rd,
                                    doc="Restricción que asegura que una caja i esta atras de otra caja j")

    #  Por último, falta definir las restricciones respecto al eje z. Es decir, determinar si una caja esta arriba o abajo de otra.
    # \begin{align}
    # &z_{ikt}+\sum_{c \in C} (r_{ci} h z_{cikt} + q_{ci}wz_{cikt}+ p_{ic} l z_{cikt}) \leq z_{jkt}+\left(1-e_{i j k t}\right) M  &\forall i, j \in I: i \neq j, t \\[0.15cm]
    # &z_{jkt}+\sum_{c \in C} (r_{cj} h z_{cjkt} q_{cj}wz_{cjkt}+ p_{jc} l z_{cjkt}) \leq z_{ikt}+\left(1-f_{i j k t}\right) M &\forall i, j \in I: i \neq j, t \label{eq7}\\[0.15cm]
    # \end{align}

    def rule_re(model, i, j, k, t):
        if i!=j:
            return model.z[i,k,t]+sum(C[c].Height*model.hz[c,i,k,t]+C[c].Width*model.wz[c,i,k,t]+C[c].Length*model.lz[c,i,k,t]
                                      for c in model.C) <= model.z[j,k,t]+(1-model.e[i,j,k,t])*M
        else:
            return pe.Constraint.Skip

    model.rule_re = pe.Constraint(model.I, model.I, model.K, model.T, rule=rule_re,
                                    doc="Restricción que asegura que una caja i esta arriba de otra caja j")

    def rule_rf(model, i, j, k, t):
        if i!=j:
            return model.z[j,k,t]+sum(C[c].Height*model.hz[c,j,k,t]+C[c].Width*model.wz[c,j,k,t]+C[c].Length*model.lz[c,j,k,t]
                                      for c in model.C) <= model.z[i,k,t]+(1-model.f[i,j,k,t])*M
        else:
            return pe.Constraint.Skip

    model.rule_rf = pe.Constraint(model.I, model.I, model.K, model.T, rule=rule_rf,
                                    doc="Restricción que asegura que una caja i esta abajo de otra caja j")


    # &a_{i j k t}+b_{i j k t}+c_{i j k t}+d_{i j k t}+e_{i j k t}+f_{i j k t}+(1-X^i_{kt})+(1-X^j_{kt}) \geq 1   &\forall i, j \in I: i \neq j, t , k \label{eq8}

    def rule_abc(model, i, j, k, t):
        if i!=j:
            return model.a[i,j,k,t]+model.b[i,j,k,t]+model.c[i,j,k,t]+model.d[i,j,k,t]+model.e[i,j,k,t]+model.f[i,j,k,t]+(1-model.Xi[i,k,t])+(1-model.Xi[j,k,t]) >= 1
        else:
            return pe.Constraint.Skip

    model.rule_abc = pe.Constraint(model.I, model.I, model.K, model.T, rule=rule_abc,
                                    doc="Restricción que asegura que una caja i esta arriba de otra caja j")


    #Las ecuaciones \ref{eq:rlxc}- \ref{eq:rhzc} ligan el tipo de caja escogido con la orientación que vamos a escoger.
    #
    #
    # \begin{align}
    #     lx_{cikt}\leq X^c_{ikt} \quad \forall c,i,k,t \label{eq:rlxc} \\
    #     ly_{cikt}\leq X^c_{ikt} \quad \forall c,i,k,t \\
    #     lz_{cikt}\leq X^c_{ikt} \quad \forall c,i,k,t \\
    #     wx_{cikt}\leq X^c_{ikt} \quad\forall c,i,k,t \\
    #     wy_{cikt}\leq X^c_{ikt} \quad\forall c,i,k,t \\
    #     wz_{cikt}\leq X^c_{ikt} \quad\forall c,i,k,t \\
    #     hx_{cikt}\leq X^c_{ikt} \quad\forall c,i,k,t \\
    #     hy_{cikt}\leq X^c_{ikt} \quad\forall c,i,k,t \\
    #     hz_{cikt}\leq X^c_{ikt} \quad\forall c,i,k,t \label{eq:rhzc} \\
    # \end{align}

    def rule_lx(model, c, i, k, t):
        return model.lx[c,i,k,t] <= model.Xc[c,i,k,t]

    model.rule_lx = pe.Constraint(model.C, model.I, model.K, model.T, rule=rule_lx,
                                    doc="Restricción que asegura que la caja i esta en la orientación lx")

    def rule_ly(model, c, i, k, t):
        return model.ly[c,i,k,t] <= model.Xc[c,i,k,t]

    model.rule_ly = pe.Constraint(model.C, model.I, model.K, model.T, rule=rule_ly,
                                    doc="Restricción que asegura que la caja i esta en la orientación ly")

    def rule_lz(model, c, i, k, t):
        return model.lz[c,i,k,t] <= model.Xc[c,i,k,t]

    model.rule_lz = pe.Constraint(model.C, model.I, model.K, model.T, rule=rule_lz,
                                    doc="Restricción que asegura que la caja i esta en la orientación lz")

    def rule_wx(model, c, i, k, t):
        return model.wx[c,i,k,t] <= model.Xc[c,i,k,t]

    model.rule_wx = pe.Constraint(model.C, model.I, model.K, model.T, rule=rule_wx,

                                    doc="Restricción que asegura que la caja i esta en la orientación wx")

    def rule_wy(model, c, i, k, t):
        return model.wy[c,i,k,t] <= model.Xc[c,i,k,t]

    model.rule_wy = pe.Constraint(model.C, model.I, model.K, model.T, rule=rule_wy,
                                    doc="Restricción que asegura que la caja i esta en la orientación wy")

    def rule_wz(model, c, i, k, t):
        return model.wz[c,i,k,t] <= model.Xc[c,i,k,t]

    model.rule_wz = pe.Constraint(model.C, model.I, model.K, model.T, rule=rule_wz,
                                    doc="Restricción que asegura que la caja i esta en la orientación wz")

    def rule_hx(model, c, i, k, t):
        return model.hx[c,i,k,t] <= model.Xc[c,i,k,t]

    model.rule_hx = pe.Constraint(model.C, model.I, model.K, model.T, rule=rule_hx,
                                    doc="Restricción que asegura que la caja i esta en la orientación hx")

    def rule_hy(model, c, i, k, t):
        return model.hy[c,i,k,t] <= model.Xc[c,i,k,t]

    model.rule_hy = pe.Constraint(model.C, model.I, model.K, model.T, rule=rule_hy,
                                    doc="Restricción que asegura que la caja i esta en la orientación hy")

    def rule_hz(model, c, i, k, t):
        return model.hz[c,i,k,t] <= model.Xc[c,i,k,t]

    model.rule_hz = pe.Constraint(model.C, model.I, model.K, model.T, rule=rule_hz,
                                    doc="Restricción que asegura que la caja i esta en la orientación hz")


    # La ecuación \ref{eq10} determina que si un vehículo contiene una caja entonces debe de ser utilizado.
    #
    # \begin{align}
    # \sum_{i} X^i_{kt} \leq M\cdot Y_{kt} \quad & \forall k, t \label{eq10}
    # \end{align}

    def rule_vehiculo(model, k, t):
        return sum(model.Xc[c,i,k,t] for c in model.C for i in model.I) <= model.M * model.Y[k, t]

    model.rule_vehiculo = pe.Constraint(model.K, model.T, rule=rule_vehiculo,
                                        doc="Restricción que asegura que si un vehículo contiene una caja entonces debe de ser utilizado")

    # Las ecuaciones \ref{eq:r_dim_1}-\ref{eq:r_dim_3} restringen el conjunto de soluciones para que se respeten las dimensiones del camión.
    # \begin{align}
    # &x_{ikt}+\sum_{c \in C} (p_{ic} l x_{cikt}+ q_{ci}wx_{cikt}+ r_{ci}hx_{cikt})  \leq L_k+\left(1-X^i_{kt}\right) M & \forall i,k,t \label{eq:r_dim_1}\\
    # &y_{ikt}+\sum_{c \in C} (q_{ci} w y_{cikt}+ p_{ic}ly_{cikt}+r_{ci}zy_{cikt})   \leq W_k+\left(1-X^i_{kt}\right) M & \forall i,k,t\\
    # &z_{ikt}+\sum_{c \in C} (r_{ci} h z_{cikt} + q_{ci}wz_{cikt}+ p_{ic} l z_{cikt}) \leq H_k+\left(1-X^i_{kt}\right) M & \forall i , k , t \label{eq:r_dim_3}
    # \end{align}


    # p_{ic} = C[c].Length
    # q_{ic} = C[c].Width
    # r_{ic} = C[c].Height

    # &x_{ikt}+\sum_{c \in C} (p_{ic} l x_{cikt}+ q_{ci}wx_{cikt}+ r_{ci}hx_{cikt})  \leq L_k+\left(1-X^i_{kt}\right) M & \forall i,k,t \label{eq:r_dim_1}\\
    def rule_dim_1(model, i, k, t):
        return model.x[i,k,t] + sum(model.lx[c,i,k,t] * C[c].Length + model.wx[c,i,k,t] * C[c].Width + model.hx[c,i,k,t] * C[c].Height for c in model.C)\
               <= K[k].Length + (1 - model.Xi[i,k,t]) * model.M

    model.rule_dim_1 = pe.Constraint(model.I, model.K, model.T, rule=rule_dim_1,
                                    doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección x")

    # &y_{ikt}+\sum_{c \in C} (q_{ci} w y_{cikt}+ p_{ic}ly_{cikt}+r_{ci}zy_{cikt})   \leq W_k+\left(1-X^i_{kt}\right) M & \forall i,k,t\\
    def rule_dim_2(model, i, k, t):
        return model.y[i,k,t] + sum(C[c].Width * model.wy[c,i,k,t] + C[c].Length * model.ly[c,i,k,t]
                                    + C[c].Height * model.hy[c,i,k,t] for c in model.C) <= \
               K[k].Width + (1 - model.Xi[i,k,t]) * model.M

    model.rule_dim_2 = pe.Constraint(model.I, model.K, model.T, rule=rule_dim_2,
                                    doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección y")
    # &z_{ikt}+\sum_{c \in C} (r_{ci} h z_{cikt} + q_{ci}wz_{cikt}+ p_{ic} l z_{cikt}) \leq H_k+\left(1-X^i_{kt}\right) M & \forall i , k , t \label{eq:r_dim_3}
    def rule_dim_3(model, i, k, t):
        return model.z[i,k,t] + sum(C[c].Height * model.hz[c,i,k,t] + C[c].Width * model.wz[c,i,k,t]
                                    + C[c].Length * model.lz[c,i,k,t] for c in model.C) <= \
               K[k].Height + (1 - model.Xi[i,k,t]) * model.M

    model.rule_dim_3 = pe.Constraint(model.I, model.K, model.T, rule=rule_dim_3,
                                     doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección z")

    #Para determinar una correcta orientación de los contenedores, se deben satifacer las siguientes restricciones.
            # \begin{align}
            # &\sum_{c \in C} (l x_{cikt}+l y_{cikt}+l z_{cikt})=X^i_{kt} & \forall i, t, k\\
    def rule_orient_1(model, i, k, t):
        return sum(model.lx[c,i,k,t] + model.ly[c,i,k,t] + model.lz[c,i,k,t] for c in model.C) == model.Xi[i,k,t]

    model.rule_orient_1 = pe.Constraint(model.I, model.K, model.T, rule=rule_orient_1,
                                        doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección z")

            # &\sum_{c \in C} (w x_{cikt}+w y_{cikt}+w z_{i t})=X^i_{kt} & \forall i, t, k\\
    def rule_orient_2(model, i, k, t):
        return sum(model.wx[c,i,k,t] + model.wy[c,i,k,t] + model.wz[c,i,k,t] for c in model.C) == model.Xi[i,k,t]

    model.rule_orient_2 = pe.Constraint(model.I, model.K, model.T, rule=rule_orient_2,
                                        doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección z")


            # &\sum_{c \in C} (h x_{cikt}+h y_{cikt}+h z_{cikt})=X^i_{kt} & \forall i, t, k \\
    def rule_orient_3(model, i, k, t):
        return sum(model.hx[c,i,k,t] + model.hy[c,i,k,t] + model.hz[c,i,k,t] for c in model.C) == model.Xi[i,k,t]

    model.rule_orient_3 = pe.Constraint(model.I, model.K, model.T, rule=rule_orient_3,
                                        doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección z")

            # &\sum_{c \in C} (l x_{cikt}+w x_{cikt}+h x_{cikt})=X^i_{kt} & \forall i, t, k\\
    def rule_orient_4(model, i, k, t):
        return sum(model.lx[c,i,k,t] + model.wx[c,i,k,t] + model.hx[c,i,k,t] for c in model.C) == model.Xi[i,k,t]

    model.rule_orient_4 = pe.Constraint(model.I, model.K, model.T, rule=rule_orient_4,
                                        doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección z")
            # &\sum_{c \in C} (l y_{cikt}+w y_{cikt}+h y_{cikt})=X^i_{kt} & \forall i, t, k\\
    def rule_orient_5(model, i, k, t):
        return sum(model.ly[c,i,k,t] + model.wy[c,i,k,t] + model.hy[c,i,k,t] for c in model.C) == model.Xi[i,k,t]

    model.rule_orient_5 = pe.Constraint(model.I, model.K, model.T, rule=rule_orient_5,
                                        doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección z")


            # &\sum_{c \in C} (l z_{cikt}+w z_{i t}+h z_{cikt})=X^i_{kt} & \forall i, t, k\\


    def rule_orient_6(model, i, k, t):
        return sum(model.lz[c,i,k,t] + model.wz[c,i,k,t] + model.hz[c,i,k,t] for c in model.C) == model.Xi[i,k,t]

    model.rule_orient_6 = pe.Constraint(model.I, model.K, model.T, rule=rule_orient_6,
                                        doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección z")

            # &x_{ikt}, y_{ikt}, z_{ikt} \geq 0 & \forall i, t,

    def rule_x0(model, i, k, t):
        return model.Xi[i,k,t] >= 0

    model.rule_x0 = pe.Constraint(model.I, model.K, model.T, rule=rule_x0,
                                        doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección z")

    def rule_y0(model, i, k, t):
        return model.y[i,k,t] >= 0

    model.rule_y0 = pe.Constraint(model.I, model.K, model.T, rule=rule_y0,
                                        doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección z")

    def rule_z0(model, i, k, t):
        return model.z[i,k,t] >= 0

    model.rule_z0 = pe.Constraint(model.I, model.K, model.T, rule=rule_z0,
                                        doc="Restricción que asegura que se respeten las dimensiones del camión en la dirección z")


    def _Y2(model, k, t):
        if k+1 in K:
            return model.Y[k,t]>=model.Y[k+1,t]
        else:
            return pe.Constraint.Skip

    model.Y2_rule = pe.Constraint(model.K, model.T, rule=_Y2)

    def _Y3(model, k, t):
        return model.Y[k, t]*K[k].Volume * 0.9 <= sum(model.Xc[c,i,k,t]*C[c].Volume for c in C for i in model.I)

    model.Y3_rule = pe.Constraint(model.K, model.T, rule=_Y3)

    def _Y4(model, i,k, t):
        if i+1 in model.I:
            return model.Xi[i,k,t]>=model.Xi[i+1,k,t]
        else:
            return pe.Constraint.Skip

    model.Y4_rule = pe.Constraint(model.I, model.K, model.T, rule=_Y4)

            # \end{align}


    #Funcion objetivo
    # El objetivo es minimizar el número de camiones utilizados.
    # \sum_k,t Y_{k t} \rightarrow \min
    num_camiones= sum(model.Y[k, t] for k in model.K for t in model.T)
    cost_stock= sum(model.vI[i,t] for i in model.N for t in model.T)
    expr = len(N)*max(D.values())*len(K)*len(T)*num_camiones + cost_stock

    model.objective = pe.Objective(expr=expr, sense=pe.minimize, doc="Función objetivo")

    solver = po.SolverFactory("gurobi")
    times = 60 *60*10
    solver.options["TimeLimit"] = times
    solver.options['slog'] = 1
    solver.options['MIPFocus'] = 1
    print("\n The instance is planning days {} and folder  {} \n".format(planning_days, folder),
          file=open("results.txt", "a"))
    try:
        results = solver.solve(model, tee=True, logfile=path_save + "\logfile.log", )

        # print to file the objective value, the status of the solution, and the gap
        print("Objective value: ", model.objective(), file=open("results.txt", "a"))
        print("Status: ", results.solver.status, file=open("results.txt", "a"))
        print("Gap: ", results.solver.termination_condition, file=open("results.txt", "a"))
        print("Time: ", results.solver.time, file=open("results.txt", "a"))
    except:
        print("No solution found", file=open("results.txt", "a"))
        print("Time: " + str(times), file=open("results.txt", "a"))
        return None
    original_stdout = sys.stdout # Save a reference to the original standard output

    print("Solucion guardada en: ", path_save)
    # Save the results
    f = open(path_save + r'\resultados_Modelo2.txt', 'w')
    sys.stdout = f
    model.pprint()
    f.close()
    print(path_save)


    # Save the results
    f = open(path_save+r'\Globales_Modelo2.txt', 'w')
    sys.stdout = f
    print("Status: ", results.solver.status)
    print("Gap: ", results.solver.termination_condition)
    print("Time: ", results.solver.time)
    print("Objective: ", model.objective())
    print("Numero de camiones:" , num_camiones)
    print(" Coste stock: ", cost_stock)
    f.close()

    # Return to the original stdout
    sys.stdout = original_stdout

if __name__ == '__main__':
    now = datetime.datetime.now()
    # Try to delete the file "results.txt" if it exists
    try:
        os.remove("results.txt")
    except OSError:
        pass

    for planning_days in [5 , 10 , 15 , 20]:
        for folder in [d for d in os.listdir(r"datasets") if os.path.isdir("datasets" + "\\" + d)]:
            print("Folder: ", folder)
            path = os.getcwd() + r"\datasets\\" + folder
            print(path)
            update_data(path=path, folder=folder, now = now, planning_days=planning_days)