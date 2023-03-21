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


# \textit{K}       & Conjunto de camiones (\textit{k} =1, 2,…,\textit{K)}                                                        \\

    # \textit{N}       & Conjunto de productos \textit{(n }=   1,…,\textit{N)}                                            \\


    N={i:i for i in pd_productos["i"].unique().tolist()}
    model.N = pe.Set(initialize=pd_productos["i"].unique().tolist(), doc="Set of products (i =1, 2,…,I)")
    # \textit{T}       & Set of planning periods \textit{(t} =1, 2…\textit{T)}                                        \\

    T=list(range(1,planning_days+1))
    model.T = pe.Set(initialize=T, doc="Set of planning periods (t =1, 2…T)")





    # \textit{B}       & Set of types of containers \textit{(b }=   1,…,\textit{B)}                                            \\
    B = {}
    i=0
    for row in pd_dimensiones_contenedores.itertuples():
        B.update({row.id :Container(row.id,row.Length,row.Width,row.Heigth)})
        i+=1


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
    max_containers_per_truck=max(math.floor(K[k].Volume/B[b].Volume) for b in B for k in K)
    num_types_containers=len(B)
    # Create a dictionary of containers, with the key being the index and the value being the container object
    I = {}
    I_name = []
    i=0
    for _1 in range(len(K)):
        for b in B:
            for _ in range(max_containers_per_truck):
                I.update({ i :Container(b,B[b].Length,B[b].Width,B[b].Height) })
                I_name.append(i)
                i += 1

    model.I = pe.Set(initialize=I_name, doc="Set of containers (i =1, 2,…,I)")
    model.J = pe.Set(initialize=copy.deepcopy(I_name), doc="Set of containers (j =1, 2,…,J)")

    # Parameters


#\textit{$u_{in}$} & Cantidad de producto \textit{n} que cabe en un contenedor \textit{i}                             \\[0.2cm]

    u={}
    # for i in I:
    #     for n in N:
    #         u[i,n]=0
    for row in pd_productos.itertuples():
        for b in row.id_container:
            # set the value of u if the contaner n has the same id as b
            for n in N:
                if row.i==n:
                    for i in I:
                        if I[i].id==b:
                            u[i,n]=row.items_per_container

    model.u = pe.Param(model.I, model.N, initialize=u, doc="Amount of product n that fits in a container b")

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
# $p_i, q_i, r_i$ & Longitud, anchura y altura de la caja i; \\[0.2cm]
# $L_j, W_j, H_j$ & Longitud, anchura y altura del compartimento del vehículo j;\\




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




# \multicolumn{2}{|l|}{Variables de decisión}                                                                \\ \hline
    # \textit{Q$_{nkt}$} & Unidades transportadas del producto \textit{i} por \textit{k} en \textit{t}                                  \\[0.15cm]

    model.Q = pe.Var(model.N, model.K, model.T, domain=pe.NonNegativeReals, doc="Units transported of product n by k in t")
    # \textit{I$_{nt}$} & Inventario de \textit{i} al final del período de tiempo \textit{t}                                \\[0.15cm]
    model.vI = pe.Var(model.N, model.T, domain=pe.NonNegativeReals, doc="Inventory of n at the end of time period t")
    # \textit{Y$_{kt}$} & Variable binaria que indica si se ha utilizado un camión \textit{k} en el período de tiempo \textit{t}     \\[0.15cm]
    model.Y = pe.Var(model.K, model.T, domain=pe.Binary, doc="Binary variable that indicates if truck k has been used in time period t")
    # \textit{$X^i_{t}$} & Variable binaria que indica si la el contenedor i va a ser usado en el tiempo de planificación t  \\[0.15cm]
    model.Xi = pe.Var(model.I, model.T, domain=pe.Binary, doc="Binary variable that indicates if the container i is going to be used in the planning time t")
    # \textit{$X^k_{int}$} & Variable binaria que indica si la el contenedor i va a ser usado en el tiempo de planificación t cargando el producto n  \\[0.15cm]
    model.Xk = pe.Var(model.I, model.K, model.N, model.T, domain=pe.Binary, doc="Binary variable that indicates if the container i is going to be used in the planning time t loading the product n")
    # \textit{$V^n_{t}$} & Variable entera que indica la cantidad abastecida del producto n durante el periodo de planificación  \\[0.15cm]
    model.V = pe.Var(model.N, model.T, domain=pe.NonNegativeIntegers, doc="Integer variable that indicates the amount supplied of the product n during the planning period")
    # \textit{$V^k_{int}$} & Variable entera que indica la cantidad abastecida del producto n en el camión k por el contenedor i durante el periodo de planificación   \\[0.15cm]
    model.Vk = pe.Var(model.I, model.K, model.N, model.T , domain=pe.NonNegativeIntegers, doc="Integer variable that indicates the amount supplied of the product n in the truck k by the container i during the planning period")
    # \textit{$x_{it},y_{it},z_{it}$} & Coordenadas de la esquina frontal inferior izquierda de la casilla i durante el periodo de planificación t;  \\[0.15cm]
    model.x = pe.Var(model.I, model.T, domain=pe.NonNegativeReals, doc="x coordinate of the front lower left corner of the box i during the planning period t")
    model.y = pe.Var(model.I, model.T, domain=pe.NonNegativeReals, doc="y coordinate of the front lower left corner of the box i during the planning period t")
    model.z = pe.Var(model.I, model.T, domain=pe.NonNegativeReals, doc="z coordinate of the front lower left corner of the box i during the planning period t")

    # \textit{$lx_{it},ly_{it},lz_{it}$} & Define si la longitud de la caja i es paralela al eje X, Y o Z en el periodo de planificación t. Por ejemplo, $lx_{it}t$ es igual a 1 si la longitud de la caja i es paralela al eje X, en caso contrario, $lx_{it}t$ es igual a 0;  \\[0.15cm]
    model.lx = pe.Var(model.I, model.T, domain=pe.Binary, doc="Define if the length of the box i is parallel to the X axis, Y axis or Z axis in the planning period t. For example, lx_{it} is equal to 1 if the length of the box i is parallel to the X axis, otherwise, lx_{it} is equal to 0")
    model.ly = pe.Var(model.I, model.T, domain=pe.Binary, doc="Define if the length of the box i is parallel to the X axis, Y axis or Z axis in the planning period t. For example, ly_{it} is equal to 1 if the length of the box i is parallel to the Y axis, otherwise, ly_{it} is equal to 0")
    model.lz = pe.Var(model.I, model.T, domain=pe.Binary, doc="Define if the length of the box i is parallel to the X axis, Y axis or Z axis in the planning period t. For example, lz_{it} is equal to 1 if the length of the box i is parallel to the Z axis, otherwise, lz_{it} is equal to 0")

    # \textit{$wx_{it},wy_{it},$ $ wz_{it}$} &  Define si la anchura de la caja i es paralela al eje X, Y o Z en el periodo de planificación t. Por ejemplo, $wx_{it}t$ es igual a 1 si la anchura de la caja i es paralela al eje X, en caso contrario, $wx_{it}t$ es igual a 0;  \\[0.15cm]
    model.wx = pe.Var(model.I, model.T, domain=pe.Binary, doc="Define if the width of the box i is parallel to the X axis, Y axis or Z axis in the planning period t. For example, wx_{it} is equal to 1 if the width of the box i is parallel to the X axis, otherwise, wx_{it} is equal to 0")
    model.wy = pe.Var(model.I, model.T, domain=pe.Binary, doc="Define if the width of the box i is parallel to the X axis, Y axis or Z axis in the planning period t. For example, wy_{it} is equal to 1 if the width of the box i is parallel to the Y axis, otherwise, wy_{it} is equal to 0")
    model.wz = pe.Var(model.I, model.T, domain=pe.Binary, doc="Define if the width of the box i is parallel to the X axis, Y axis or Z axis in the planning period t. For example, wz_{it} is equal to 1 if the width of the box i is parallel to the Z axis, otherwise, wz_{it} is equal to 0")

    # \textit{$hx_{it},hy_{it}$ $,hz_{it}$} & Define si la altura de la caja i es paralela al eje X, Y o Z en el periodo de planificación t. Por ejemplo, $hx_{it}t$ es igual a 1 si la altura de la caja i es paralela al eje X, en caso contrario, $hx_{it}t$ es igual a 0;  \\[0.15cm]
    model.hx = pe.Var(model.I, model.T, domain=pe.Binary, doc="Define if the height of the box i is parallel to the X axis, Y axis or Z axis in the planning period t. For example, hx_{it} is equal to 1 if the height of the box i is parallel to the X axis, otherwise, hx_{it} is equal to 0")
    model.hy = pe.Var(model.I, model.T, domain=pe.Binary, doc="Define if the height of the box i is parallel to the X axis, Y axis or Z axis in the planning period t. For example, hy_{it} is equal to 1 if the height of the box i is parallel to the Y axis, otherwise, hy_{it} is equal to 0")
    model.hz = pe.Var(model.I, model.T, domain=pe.Binary, doc="Define if the height of the box i is parallel to the X axis, Y axis or Z axis in the planning period t. For example, hz_{it} is equal to 1 if the height of the box i is parallel to the Z axis, otherwise, hz_{it} is equal to 0")


    # \textit{$s_{ikt}$} & Variable binaria que indica si la caja i está colocada en el vehículo k. Es igual a 1 si la caja i ha sido colocada en el vehículo k y 0 en caso contrario; \\[0.15cm]
    model.s = pe.Var(model.I, model.K, model.T, domain=pe.Binary, doc="Binary variable that indicates if the box i is placed in the vehicle k. It is equal to 1 if the box i has been placed in the vehicle k and 0 otherwise")

    # \textit{$\delta_{ijkt}$} & Variable binaria que indica si la caja i está colocada en el vehículo k. Es igual a 1 si la caja i ha sido colocada en el vehículo k y 0 en caso contrario; \\[0.15cm]
    model.delta = pe.Var(model.I, model.I, model.K, model.T, domain=pe.Binary, doc="Binary variable that indicates if the box i is placed in the vehicle k. It is equal to 1 if the box i has been placed in the vehicle k and 0 otherwise")

    # \textit{$a_{i  j t}, b_{i j t}, c_{i j t}$ $, d_{i j t}, e_{i j t}, f_{i j t}$} & Variables binarias que indican la posición relativa entre dos casillas. La variable aik es igual a 1 si la casilla i está a la izquierda de la casilla k. Del mismo modo, las variables bik, cik, dik, eik, fik indican si la casilla i está a la derecha, detrás, delante, debajo o encima de la casilla k, respectivamente. Estas variables sólo son necesarias cuando i $\not = $ k.  \\[0.15cm]
    model.a = pe.Var(model.I, model.I, model.T, domain=pe.Binary, doc="Binary variables that indicate the relative position between two boxes. The variable a_{i j t} is equal to 1 if the box i is to the left of the box j. In the same way, the variables b_{i j t}, c_{i j t}, d_{i j t}, e_{i j t}, f_{i j t} indicate if the box i is to the right, behind, in front, below or above the box j, respectively. These variables are only necessary when i $\not = $ j.")
    model.b = pe.Var(model.I, model.I, model.T, domain=pe.Binary, doc="Binary variables that indicate the relative position between two boxes. The variable a_{i j t} is equal to 1 if the box i is to the left of the box j. In the same way, the variables b_{i j t}, c_{i j t}, d_{i j t}, e_{i j t}, f_{i j t} indicate if the box i is to the right, behind, in front, below or above the box j, respectively. These variables are only necessary when i $\not = $ j.")
    model.c = pe.Var(model.I, model.I, model.T, domain=pe.Binary, doc="Binary variables that indicate the relative position between two boxes. The variable a_{i j t} is equal to 1 if the box i is to the left of the box j. In the same way, the variables b_{i j t}, c_{i j t}, d_{i j t}, e_{i j t}, f_{i j t} indicate if the box i is to the right, behind, in front, below or above the box j, respectively. These variables are only necessary when i $\not = $ j.")
    model.d = pe.Var(model.I, model.I, model.T, domain=pe.Binary, doc="Binary variables that indicate the relative position between two boxes. The variable a_{i j t} is equal to 1 if the box i is to the left of the box j. In the same way, the variables b_{i j t}, c_{i j t}, d_{i j t}, e_{i j t}, f_{i j t} indicate if the box i is to the right, behind, in front, below or above the box j, respectively. These variables are only necessary when i $\not = $ j.")
    model.e = pe.Var(model.I, model.I, model.T, domain=pe.Binary, doc="Binary variables that indicate the relative position between two boxes. The variable a_{i j t} is equal to 1 if the box i is to the left of the box j. In the same way, the variables b_{i j t}, c_{i j t}, d_{i j t}, e_{i j t}, f_{i j t} indicate if the box i is to the right, behind, in front, below or above the box j, respectively. These variables are only necessary when i $\not = $ j.")
    model.f = pe.Var(model.I, model.I, model.T, domain=pe.Binary, doc="Binary variables that indicate the relative position between two boxes. The variable a_{i j t} is equal to 1 if the box i is to the left of the box j. In the same way, the variables b_{i j t}, c_{i j t}, d_{i j t}, e_{i j t}, f_{i j t} indicate if the box i is to the right, behind, in front, below or above the box j, respectively. These variables are only necessary when i $\not = $ j.")

    #
    # \hline


    # La siguiente restricción mantiene el nivel de inventario
    # $$ I_{nt}=I_{n t'}-D_{nt}+V^n_t \quad \forall n,t,t'\in T : t'=t+1 \text{ y } t\leq|T|$$


    def _I(model, n, t):
        if t == 1:
            return model.vI[n, t] == model.stockInicial[n] - model.D[n, t] + model.V[n, t]
        else:
            return model.vI[n, t] == model.vI[n, t - 1] - model.D[n, t] + model.V[n, t]

    model.ConsI = pe.Constraint(model.N, model.T, rule=_I, doc="Inventory level")
    # \begin{equation}
    #     I_{n t }\geq     \begin{cases}
    #         \sum_{s \in \lbrace 1 , \dots , SC_n \rbrace } D_{n,t+s} \quad & \text{if } n \in N, t \in \lbrace 1, \dots , |T|-SC_n \rbrace \\
    #         \sum_{s \in \lbrace 1 , \dots , SC_n \rbrace } D_{n,|T|-SC_n+s} & \text{else}
    #     \end{cases}
    # \end{equation}
    l1={}
    for n in N:
        for t in T:
            if t < len(T)-SC[n]:
                l1[n] = sum(D[n,t+s] for s in range(1,SC[n]+1))


    def _I2(model, n, t):
        if t < len(T)-SC[n]:
            return model.vI[n, t] >= sum(model.D[n, t + s] for s in range(1, SC[n] + 1))
        else:
            return model.vI[n, t] >= l1[n]

    model.I2_rule = pe.Constraint(model.N, model.T, rule=_I2)

    #Las siguientes ecuaciones ligan la condición de que un contenedor esta en un camión determinado con el producto que carga

    #     X^k_{int} &\leq S_{ikt} \quad  &\forall i,k,n,t\\
    def _X(model, i, k, n, t):
        return model.Xk[i, k, n, t] <= model.s[i, k, t]
    model.X_rule = pe.Constraint(model.I, model.K, model.N, model.T, rule=_X)


    #     \sum_{n,k} X^k_{int}&\leq 1 \quad &\forall i,k,t\\
    def _X2(model, i, k, t):
        return sum(model.Xk[i, k, n, t] for n in model.N) <= 1

    model.X2_rule = pe.Constraint(model.I, model.K, model.T, rule=_X2)
    #     X^i_t&= \sum_{i,k,n}X^k_{int} \quad &\forall i,t
    def _X3(model, i, t):
        return sum(model.Xk[i, k, n, t] for k in model.K for n in model.N) == model.Xi[i, t]

    model.X3_rule = pe.Constraint(model.I, model.T, rule=_X3)



    #    V^k_{int}&=X^k_{int}\mu_{in}\quad   &\forall i,k,n,t \label{eq:CantidadContenedor}\\
    def _V(model, i, k, n, t):
        # try:
            if (i,n) in u:
                return model.Vk[i, k, n, t] == model.Xk[i, k, n, t] * model.u[i, n]
            else:
                return model.Vk[i, k, n, t] == 0
        # except:
        #     pass

    model.V_rule = pe.Constraint(model.I, model.K, model.N, model.T, rule=_V)

    # V^n_t&=\sum_{i,k} V^k_{int} \quad &\forall i, t \label{eq:CantidadTransportadoProductoDia}
    def _V2(model, n, t):
        return sum(model.Vk[i, k, n, t] for i in model.I for k in model.K) == model.V[n, t]

    model.V2_rule = pe.Constraint(model.N, model.T, rule=_V2)
    # Orientation restrictions
    # &x_{it}+p_i l x_{it}+q_i\left(l z_{it}-w y_{it}+h z_{it}\right)
    # +r_i\left(1-l x_{it}-l z_{it}+w y_{it}-h z_{it}\right)-\delta_{i j k t} M
    # \leq x_{kt}+\left(1-a_{i j t}\right) M  &\forall i, j \in I: i \neq j,t  \label{eq2}\\[0.15cm]
    def _O(model, i, j, k ,t):
        if i!=j:
            return model.x[i, t] + B[I[i].id].Length * model.lx[i, t] + B[I[i].id].Width * (model.lz[i,t] - model.wy[i,t] + model.hz[i,t]) \
               + B[I[i].id].Height * (1 - model.lx[i,t] - model.lz[i,t] + model.wy[i,t] - model.hz[i,t]) - model.delta[i,j,k,t] * M \
               <= model.x[j,t] + (1 - model.a[i,j,t]) * M
        else:
            return pe.Constraint.Skip


    model.O_rule = pe.Constraint(model.I, model.I, model.K, model.T, rule=_O)


    # &x_{jt}+p_k l x_{jt}+q_k\left(l z_{jt}-w y_{jt}+h z_{jt}\right)+r_k\left(1-l x_{jt}-l z_{jt}+w y_{jt}-h z_{jt}\right)-\delta_{i j k t} M \leq x_{it}+\left(1-b_{i j t}\right) M  &\forall i, j \in I: i \neq j, t \\[0.15cm]
    def _O2(model, i, j, k, t):
        if i != j:
            return model.x[j, t] + B[I[j].id].Length * model.lx[j, t] + B[I[j].id].Width * (model.lz[j,t] - model.wy[j,t] + model.hz[j,t]) \
                   + B[I[j].id].Height * (1 - model.lx[j,t] - model.lz[j,t] + model.wy[j,t] - model.hz[j,t]) - model.delta[i,j,k,t] * M \
                   <= model.x[i,t] + (1 - model.b[i,j,t]) * M
        else:
            return pe.Constraint.Skip


    model.O2_rule = pe.Constraint(model.I, model.I, model.K, model.T, rule=_O2)



    # &y_{it}+q_i w y_{it}+p_i\left(1-l x_{it}-l z_{it}\right)+r_i\left(l x_{it}+l z_{it}-w y_{it}\right)-\delta_{i j k} M y_{jt}+\left(1-c_{i j t}\right) M  &\forall i, j \in I: i \neq j, t \\[0.15cm]

    def _O3(model, i, j, k, t):
        if i != j:
            return model.y[i, t] + B[I[i].id].Width * model.wy[i, t] + B[I[i].id].Length * (1 - model.lx[i,t] - model.lz[i,t]) \
                   + B[I[i].id].Height * (model.lx[i,t] + model.lz[i,t] - model.wy[i,t]) - model.delta[i,j,k,t] * M \
                   <= model.y[j,t] + (1 - model.c[i,j,t]) * M
        else:
            return pe.Constraint.Skip

    model.O3_rule = pe.Constraint(model.I, model.I, model.K, model.T, rule=_O3)

    # &y_{jt}+q_{jt} w y_{jt}+p_k\left(1-l x_{jt}-l z_{jt}\right)+r_k\left(l x_{jt}+l z_{jt}-w y_{jt}\right)-\delta_{i j k t} M \leq y_{it}+\left(1-d_{i j t}\right) M  &\forall i, j \in I: i \neq j, t \\[0.15cm]
    def _O4(model, i, j, k, t):
        if i != j:
            return model.y[j, t] + B[I[j].id].Width * model.wy[j, t] + B[I[j].id].Length * (1 - model.lx[j,t] - model.lz[j,t]) \
                   + B[I[j].id].Height * (model.lx[j,t] + model.lz[j,t] - model.wy[j,t]) - model.delta[i,j,k,t] * M \
                   <= model.y[i,t] + (1 - model.d[i,j,t]) * M
        else:
            return pe.Constraint.Skip

    model.O4_rule = pe.Constraint(model.I, model.I, model.K, model.T, rule=_O4)



    # &z_{it}+r_i h z_{it}+q_i\left(1-l z_{it}-h z_{it}\right)+p_i l z_{it}-\delta_{i j k} M \leq z_{jt}+\left(1-e_{i j t}\right) M  &\forall i, j \in I: i \neq j, t \\[0.15cm]

    def _O5(model, i, j, k, t):
        if i != j:
            return model.z[i, t] + B[I[i].id].Height * model.hz[i, t] + B[I[i].id].Width * (1 - model.lz[i,t] - model.hz[i,t]) \
                   + B[I[i].id].Length * model.lz[i,t] - model.delta[i,j,k,t] * M \
                   <= model.z[j,t] + (1 - model.e[i,j,t]) * M
        else:
            return pe.Constraint.Skip

    model.O5_rule = pe.Constraint(model.I, model.I, model.K, model.T, rule=_O5)


    # &z_{jt}+r_k h z_\textbf{}+q_k\left(1-l z_{jt}-h z_{jt}\right)+p_k l z_{jt}-\delta_{i j k t} M\leq z_{it}+\left(1-f_{i j t}\right) M &\forall i, j \in I: i \neq j, t \label{eq7}\\[0.15cm]

    def _O6(model, i, j, k, t):
        if i != j:
            return model.z[j, t] + B[I[j].id].Height * model.hz[j, t] + B[I[j].id].Width * (1 - model.lz[j,t] - model.hz[j,t]) \
                   + B[I[j].id].Length * model.lz[j,t] - model.delta[i,j,k,t] * M \
                   <= model.z[i,t] + (1 - model.f[i,j,t]) * M
        else:
            return pe.Constraint.Skip
    model.O6_rule = pe.Constraint(model.I, model.I, model.K, model.T, rule=_O6)
    # &a_{i j t}+b_{i j t}+c_{i j t}+d_{i j t}+e_{i j t}+f_{i j t} \geq 1-\delta_{i j k t}   &\forall i, j \in I: i \neq j, t , k \label{eq8}

    def _O7(model, i, j, t, k):
        if i != j:
            return model.a[i,j,t] + model.b[i,j,t] + model.c[i,j,t] + model.d[i,j,t] + model.e[i,j,t] + model.f[i,j,t] \
                +M*model.Xi[i,t]   >= 1 - model.delta[i,j,k,t]
        else:
            return pe.Constraint.Skip

    model.O7_rule = pe.Constraint(model.I, model.I, model.T, model.K, rule=_O7)



    #     \sum_{k} s_{i k t}\leq 1 \quad & \forall i,t \label{eq9} \\
    def _K1(model, i, t):
        return sum(model.s[i,k,t] for k in model.K) <= 1


    model.K1_rule = pe.Constraint(model.I, model.T, rule=_K1)
    # \sum_{i} s_{i k t} \leq M\cdot Y_{kt} \quad & \forall k, t \label{eq10}
    def _K2(model, k, t):
        return sum(model.s[i,k,t] for i in model.I) <= model.Y[k,t] * M

    model.K2_rule = pe.Constraint(model.K, model.T, rule=_K2)

    # Restricciones dimensionesCamion
    #&x_{it}+p_i \cdot l x_{it}+q_i \cdot\left(l z_{it}-w y_{it}+h z_{it}\right)+r_i \cdot\left(1-l x_{it}-l z_{it}+w y_{it}-h z_{it}\right) \leq L_j+\left(1-s_{i k t}\right) M & \forall i,k,t \\

    def _KX(model, i, k, t):
        return model.x[i,t] + B[I[i].id].Length * model.lx[i,t] + B[I[i].id].Width * (model.lz[i,t] - model.wy[i,t] + model.hz[i,t]) \
               + B[I[i].id].Height * (1 - model.lx[i,t] - model.lz[i,t] + model.wy[i,t] - model.hz[i,t]) \
               <= K[k].Length + (1 - model.s[i,k,t]) * M

    model.KX_rule = pe.Constraint(model.I, model.K, model.T, rule=_KX)

    # &y_{it}+q_i w y_{it}+p_i\left(1-l x_{it}-l z_{it}\right)+r_i\left(l x_{it}+l z_{it}-w y_{it}\right) \leq W_j+\left(1-s_{i k t}\right) M & \forall i,k,t\\

    def _KY(model, i, k, t):
        return model.y[i,t] + B[I[i].id].Width * model.wy[i,t] + B[I[i].id].Length * (1 - model.lx[i,t] - model.lz[i,t]) \
               + B[I[i].id].Height * (model.lx[i,t] + model.lz[i,t] - model.wy[i,t]) \
               <= K[k].Width + (1 - model.s[i,k,t]) * M

    model.KY_rule = pe.Constraint(model.I, model.K, model.T, rule=_KY)

    # &z_{it}+r_i h z_{it}+q_i\left(1-l z_{it}-h z_{it}\right)+p_i l z_{it} \leq H_j+\left(1-s_{i k t}\right) M & \forall i , k , t

    def _KZ(model, i, k, t):
        return model.z[i,t] + B[I[i].id].Height * model.hz[i,t] + B[I[i].id].Width * (1 - model.lz[i,t] - model.hz[i,t]) \
               + B[I[i].id].Length * model.lz[i,t] \
               <= K[k].Height + (1 - model.s[i,k,t]) * M

    model.KZ_rule = pe.Constraint(model.I, model.K, model.T, rule=_KZ)


    # Restrcciones Paralelismo
    # &l x_{it}+l y_{it}+l z_{it}=1 & \forall i, t\\
    def _PL(model, i, t):
        return model.lx[i,t] + model.ly[i,t] + model.lz[i,t] == 1

    model.PL_rule = pe.Constraint(model.I, model.T, rule=_PL)
    # &w x_{it}+w y_{it}+w z_{i t}=1 & \forall i, t\\
    def _PW(model, i, t):
        return model.wx[i,t] + model.wy[i,t] + model.wz[i,t] == 1

    model.PW_rule = pe.Constraint(model.I, model.T, rule=_PW)
    # &h x_{it}+h y_{it}+h z_{it}=1 & \forall i, t\\

    def _PH(model, i, t):
        return model.hx[i,t] + model.hy[i,t] + model.hz[i,t] == 1

    model.PH_rule = pe.Constraint(model.I, model.T, rule=_PH)


    # &l x_{it}+w x_{it}+h x_{it}=1 & \forall i, t\\
    def _PX(model, i, t):
        return model.lx[i,t] + model.wx[i,t] + model.hx[i,t] == 1

    model.PX_rule = pe.Constraint(model.I, model.T, rule=_PX)

    # &l y_{it}+w y_{it}+h y_{it}=1 & \forall i, t\\

    def _PY(model, i, t):
        return model.ly[i,t] + model.wy[i,t] + model.hy[i,t] == 1

    model.PY_rule = pe.Constraint(model.I, model.T, rule=_PY)

    # &l z_{it}+w z_{i t}+h z_{it}=1 & \forall i, t\\

    def _PZ(model, i, t):
        return model.lz[i,t] + model.wz[i,t] + model.hz[i,t] == 1

    model.PZ_rule = pe.Constraint(model.I, model.T, rule=_PZ)


    # &2-s_{i k t}-s_{j k t} \geq m \delta_{i j k t} & \forall i, j, k, t\\

    # def _P1(model, i, j, k, t):
    #     return 2 - model.s[i,k,t] - model.s[j,k,t] >= M * model.delta[i,j,k,t]
    #
    # model.P1_rule = pe.Constraint(model.I, model.I, model.K, model.T, rule=_P1)
    #
    #
    # # &2-s_{i k t}-s_{j k t} \leq M \delta_{i j k t} & \forall i, j, k, t\\
    #
    # def _P2(model, i, j, k, t):
    #     return 2 - model.s[i,k,t] - model.s[j,k,t] <= M * model.delta[i,j,k,t]
    #
    # model.P2_rule = pe.Constraint(model.I, model.I, model.K, model.T, rule=_P2)
    #
    #
    # # &x_{it}, y_{it}, z_{it} \geq 0 & \forall i, t
    #
    # def _P3(model, i, t):
    #     return model.x[i,t] >= 0
    #
    # model.P3_rule = pe.Constraint(model.I, model.T, rule=_P3)
    #
    # def _P4(model, i, t):
    #     return model.y[i,t] >= 0
    #
    # model.P4_rule = pe.Constraint(model.I, model.T, rule=_P4)
    #
    # def _P5(model, i, t):
    #     return model.z[i,t] >= 0
    #
    # model.P5_rule = pe.Constraint(model.I, model.T, rule=_P5)
    #


    # Restricciones rotaciones

    # &l x_{it}+l y_{it}+l z_{it}+w x_{it}+w y_{it}+w z_{it}+h x_{it}+h y_{it}+h z_{it}=3 & \forall i, t\\

    def _PR1(model, i, t):
        return model.lx[i,t] + model.ly[i,t] + model.lz[i,t] + model.wx[i,t] + model.wy[i,t] + model.wz[i,t] + model.hx[i,t] + model.hy[i,t] + model.hz[i,t] == 3

    model.PR1_rule = pe.Constraint(model.I, model.T, rule=_PR1)

    # &a_{i j t}=b_{j i t} & \forall i, j \in I: i \neq j, t \\

    def _PR2(model, i, j, t):

        if i != j:
            return model.a[i,j,t] == model.b[j,i,t]
        else:
            return pe.Constraint.Skip

    model.PR2_rule = pe.Constraint(model.I, model.I, model.T, rule=_PR2)

    # &c_{i j t}=d_{j i t} & \forall i, j \in I: i \neq j, t \\
    def _PR3(model, i, j, t):
        if i != j:
            return model.c[i,j,t] == model.d[j,i,t]
        else:
            return pe.Constraint.Skip


    model.PR3_rule = pe.Constraint(model.I, model.I, model.T, rule=_PR2)

    # &e_{i j t}=f_{j i t} & \forall i, j \in I: i \neq j, t \\

    def _PR4(model, i, j, t):
        if i != j:
            return model.e[i,j,t] == model.f[j,i,t]
        else:
            return pe.Constraint.Skip

    model.PR4_rule = pe.Constraint(model.I, model.I, model.T, rule=_PR4)


    # & hz_{it}=1 & \forall i, t

    def _PR5(model, i, t):
        return model.hz[i,t] == 1

    model.PR5_rule = pe.Constraint(model.I, model.T, rule=_PR5)

    # Restricciones soporte

    # &x_{it}+p_i l x_{it}+q_i\left(1-l x_{it}\right)+\left(1-e_{i j t}\right) M \geq x_{jt} & \forall i, j \in I: i \neq j, t \\

    def _PS1(model, i, j, t):
        if i != j:
            return model.x[i,t] + B[I[i].id].Length * model.lx[i,t] + B[I[i].id].Width * (1 - model.lx[i,t]) + (1 - model.e[i,j,t]) * M >= model.x[j,t]
        else:
            return pe.Constraint.Skip

    model.PS1_rule = pe.Constraint(model.I, model.I, model.T, rule=_PS1)
    # &x_{it}+p_i l x_{it}+q_i\left(1-l x_{it}\right)-x_{jt}+\left(1-e_{i j t}\right) M \geq\left(p_k l x_{jt}+q_k\left(1-l x_{jt}\right)\right)\gamma & \forall i, j \in I: i \neq j, t \\

    def _PS2(model, i, j, t):
        if i != j:
            return model.x[i,t] + B[I[i].id].Length * model.lx[i,t] + B[I[i].id].Width * (1 - model.lx[i,t]) - model.x[j,t] + (1 - model.e[i,j,t]) * M >= (B[I[j].id].Length * model.lx[j,t] + B[I[j].id].Width * (1 - model.lx[j,t])) * alpha
        else:
            return pe.Constraint.Skip

    model.PS2_rule = pe.Constraint(model.I, model.I, model.T, rule=_PS2)
    # &y_{it}+p_i l y_{it}+q_i\left(1-l y_{it}\right)+\left(1-e_{i j t}\right) M \geq y_k & \forall i, j \in I: i \neq j, t \\

    def _PS3(model, i, j, t):
        if i != j:
            return model.y[i,t] + B[I[i].id].Length * model.ly[i,t] + B[I[i].id].Width * (1 - model.ly[i,t]) + (1 - model.e[i,j,t]) * M >= model.y[j,t]
        else:
            return pe.Constraint.Skip

    model.PS3_rule = pe.Constraint(model.I, model.I, model.T, rule=_PS3)
    # &y_{it}+p_i l y_{it}+q_i\left(1-l y_{it}\right)-y_k+\left(1-e_{i j t}\right) M \geq\left(p_k l y_k+q_k\left(1-l y_k\right)\right)\alpha & \forall i, j \in I: i \neq j, t

    def _PS4(model, i, j, t):
        if i != j:
            return model.y[i,t] + B[I[i].id].Length * model.ly[i,t] + B[I[i].id].Width * (1 - model.ly[i,t]) - model.y[j,t] + (1 - model.e[i,j,t]) * M >= (B[I[j].id].Length * model.ly[j,t] + B[I[j].id].Width * (1 - model.ly[j,t])) * alpha
        else:
            return pe.Constraint.Skip


    model.PS4_rule = pe.Constraint(model.I, model.I, model.T, rule=_PS4)


    expr = 3*max(D.values())*23*sum(
        model.Y[k, t]  for k in model.K for t in
        model.T)+sum(model.vI[n,t] for n in model.N for t in model.T)


    # Coste Transporte
    model.objective = pe.Objective(sense=pe.minimize, expr=expr)
    solver = po.SolverFactory("gurobi")
    times=60*60*3
    solver.options["TimeLimit"]=times
    solver.options['slog'] = 1
    print("\n The instance is planning days {} and folder  {} \n".format(planning_days, folder), file=open("results.txt", "a"))
    try:
        results = solver.solve(model, tee=True , logfile=path_save+"\logfile.log",)

        # print to file the objective value, the status of the solution, and the gap
        print("Objective value: ", model.objective(), file=open("results.txt", "a"))
        print("Status: ", results.solver.status, file=open("results.txt", "a"))
        print("Gap: ", results.solver.termination_condition, file=open("results.txt", "a"))
        print("Time: ", results.solver.time, file=open("results.txt", "a"))
    except:
        print("No solution found", file=open("results.txt", "a"))
        print("Time: "+str(times), file=open("results.txt", "a"))
        return None


    CamionesDia=[]

    for t in T:
        # CamionesDia.append(sum(solver.Value(Y[k,t]) for k in K))
        CamionesDia.append(sum(model.Y[k,t].value for k in K))
    df_CamionesDia=pd.DataFrame(CamionesDia,columns=["CamionesDia"])
    df_CamionesDia.to_csv(path_save+"\CamionesDia.csv")



    stock=[]
    for t in T:
        for i in I:
            # stock.append([t,i, solver.Value( vI[i,t])])
            stock.append([t,i, model.vI[i,t].value])
    df_stock=pd.DataFrame(stock,columns=["t","id","Stock"])
    df_stock.to_csv(path_save+"\Stock.csv")






    cantidadpedir_acu=[]
    for t in T:
        pro=[]
        for i in I:
            # pro.append(sum(solver.Value(Q[i,k,t1]) for k in K for t1 in T[0:t]))
            pro.append(sum(model.Q[i,k,t1].value for k in K for t1 in T[0:t]))
        cantidadpedir_acu.append(pro)
    df_cantidadpedir_acu=pd.DataFrame(cantidadpedir_acu,columns=I)
    df_cantidadpedir_acu.to_csv(path_save+"\cantidadpedir_acu.csv")




# Save cantidad_pedir by day, truck and product
    cantidad_pedir=[]
    for t in T:
        for k in K:
            for i in I:
                # cantidad_pedir.append([t,k,i, solver.Value(Q[i,k,t])])
                cantidad_pedir.append([t,k,i, model.Q[i,k,t].value])
    df_cantidad_pedir=pd.DataFrame(cantidad_pedir,columns=["t","k","producto","CantidadPedir"])
    df_cantidad_pedir.to_csv(path_save+"\CantidadPedir.csv")




    # Save numbers of trucks by day
    CamionesDia=[]
    for t in T:
        # CamionesDia.append(sum(solver.Value(Y[k,t]) for k in K))
        CamionesDia.append(sum(model.Y[k,t].value for k in K))
    df_CamionesDia=pd.DataFrame(CamionesDia,columns=["CamionesDia"])
    df_CamionesDia.to_csv(path_save+"\CamionesDia.csv")






    # Save stock by day and product
    stock=[]
    for t in T:
        for i in I:
            # stock.append([t,i, solver.Value( vI[i,t])])
            stock.append([t,i, model.vI[i,t].value])
    df_stock=pd.DataFrame(stock,columns=["t","product","Stock"])




    # save the model
    sol_camiones_total=[]
    for t in T:
        k1=0
        for k in K:
            sol_dia = []
            sol_dia1=[]

            # if solver.Value(Y[k, t]) == 1:
            if model.Y[k, t].value == 1:
                k1=k1+1
                for i in I:
                    ## if the product is in the truck
                    # if solver.Value(Q[i, k, t]) > 0:
                    if model.Q[i, k, t].value > 0:
                        ## product, vA, vB
                        # sol_dia.append([i,solver.Value(Q[i, k, t]), sum(solver.Value(M[i,k,t,b,f])  for f in F for b in B if B[b].id=="a"),
                        #                 sum(solver.Value(M[i,k,t,b,f])   for f in F  for b in B if B[b].id=="b"), 1000])
                        sol_dia.append([i,model.Q[i, k, t].value, sum(model.M[i,k,t,b,f].value  for f in F for b in B if B[b].id=="a"),
                                        sum(model.M[i,k,t,b,f].value   for f in F  for b in B if B[b].id=="b"), 1000])
                        for b in B:
                            for f in F:
                                # if solver.Value(M[i,k,t,b,f])>0:
                                if model.M[i,k,t,b,f].value>0:
                                    # sol_dia1.append([i,b,f,solver.Value(M[i,k,t,b,f])])
                                    sol_dia1.append([i,b,B[b].Length, B[b].Width,B[b].Height,
                                                     f,model.V[k,b,f,t].value,K[k].id, K[k].Length, K[k].Width])

                        sol_camiones_total.append([t,k1,i,model.Q[i, k, t].value,
                                                    sum(model.M[i,k,t,b,f].value  for i in I  for f in F for b in B if B[b].id=="a"),
                                                    sum(model.M[i,k,t,b,f].value  for i in I  for f in F for b in B if B[b].id=="b"),
                                                    1200,
                                                    sum(sum(model.M[i,k,t,b,f].value for i in I  for f in F)*
                                                        B[b].Height*B[b].Width*B[b].Length for b in B)/K[k].Volume])


                df_sol_dia=pd.DataFrame(sol_dia, columns=["id","Products","vA","vB","LargoBox"])
                df_sol_dia.to_csv(path_save+"\CantidadPedirDia{}Camion{}.csv".format(t,k1))
                df_sol_dia1=pd.DataFrame(sol_dia1, columns=["id_producto","id_box","BoxLength","BoxWidth", "BoxHeight","Fila","Cantidad","id_camion","LargoCamion","AnchoCamion"])
                df_sol_dia1.to_csv(path_save+"\CantidadPedirDia{}Camion{}Box.csv".format(t,k1))
    df_sol_camiones_total=pd.DataFrame(sol_camiones_total, columns=["t","c","id","Products","vA","vB","LargoBox", "Volumen"])
    df_sol_camiones_total.to_csv(path_save+"\CantidadPedirTotal.csv")


    print(path_save)

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