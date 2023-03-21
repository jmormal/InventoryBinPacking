from ortools.sat.python import cp_model
import time
import sys
import shutil
import datetime
from time import perf_counter as time
import pandas as pd
import os
import math
from mip import Model, xsum, minimize
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
def update_data(path=None, folder="default", now = datetime.datetime.now()  ):

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
        path_save = wd + "\{}-{}-{}".format(now.day, now.month, now.year)
        os.makedirs(path, exist_ok=True)
    elif os.path.isdir(os.getcwd() + "\output" + "\{}{}{}".format(now.day, now.month, now.year) + "\\" + folder):
        wd = os.getcwd() + "\output"
        path_save = wd + "\{}-{}-{}".format(now.day, now.month, now.year) + "\\" + folder
        print("path_save with folder", path_save)

    else:
        wd = os.getcwd() + "\output"
        path_save = wd + "\{}-{}-{}".format(now.day, now.month, now.year)
        path_save = path_save + "\\" + folder
        os.makedirs(path_save, exist_ok=True)
        for filename in os.listdir(os.getcwd() + "/output/backup"):
            shutil.copy(os.getcwd() + "/output/backup/" + filename, "{}\{}".format(path_save, filename))



    pd_productos=pd.read_csv(path+"\Productos.csv")
    pd_demanda =pd.read_csv(path+"\Demanda.csv")
    pd_dimensiones_camiones =pd.read_csv(path+"\Dimensiones_Camiones.csv")
    pd_dimensiones_contenedores =pd.read_csv(path+"\Dimensiones_Contenedores.csv")
    # Print check if path_save exists
    pd_productos.to_csv(path_save+"\Productos.csv", index=False)
    pd_demanda.to_csv(path_save+"\Demanda.csv", index=False)
    pd_dimensiones_contenedores.to_csv(path_save+"\Dimensiones_Contenedores.csv", index=False)
    pd_dimensiones_camiones.to_csv(path_save+"\Dimensiones_Camiones.csv", index=False)

    # \textit{I}       & Set of products (\textit{i} =1, 2,…,\textit{I})                                                      \\

    I = {i: i for i in pd_productos["i"].unique().tolist()}
    # \textit{T}       & Set of planning periods \textit{(t} =1, 2…\textit{T)}                                        \\

    T = pd_demanda["t"].unique().tolist()

    # \textit{F}       & Set of possible rows inside a   truck \textit{(f} =1,2,...,\textit{F)}                              \\

    F = list(range(3))

    # \textit{C}       & Set of possible columns inside a   truck \textit{(c} =1,2,...,\textit{C)}                              \\

    # \textit{B}       & Set of types of containers \textit{(b }=   1,…,\textit{B)}                                            \\
    B = {}
    i = 0
    for row in pd_dimensiones_contenedores.itertuples():
        B.update({row.id: Container(row.id, row.Length, row.Width, row.Heigth)})
        i += 1


    # \textit{K}       & Set of trucks (\textit{k} =1, 2,…,\textit{K)}                                                        \\
    K = {}
    i = 0
    for row in pd_dimensiones_camiones.itertuples():
        for _ in range(3):
            K.update({i: Truck(row.id, row.Length, row.Width, row.Heigth)})
            i += 1
    print(K)

    # \textit{W}       & Set of possible box widths \textit{(w} =1, 2…\textit{W)}                                        \\ \hline
    W = pd_dimensiones_contenedores["Width"].unique().tolist()


    # \textit{L(w)}       & Set of containers such that they have the width \textit{w}
    L = {}
    for w in W:
        L.update({w: [b for b in B if B[b].Width == w]})

    # Parameters

    # \multicolumn{2}{|l|}{Parameters}                                                                        \\ \hline
    # \textit{$u_{ib}$}      & Amount of product \textit{i} that fits in a container \textit{b}                             \\

    u = {}
    for row in pd_productos.itertuples():
        for b in list(row.id_container):
            u[(row.i, b)] = row.items_per_container


    # \textit{$D_{it}$}     & Demand of product \textit{i} in \textit{t}                             \\
    D = {}
    for row in pd_demanda.itertuples():
        D[(row.i, row.t)] = row.Demanda

    CosteStock = {}
    stockInicial = {}
    for i in I:
        CosteStock[i] = pd_productos[pd_productos["i"] == i]["CosteStock"].values[0]
        stockInicial[i] = pd_productos[pd_productos["i"] == i]["Stock"].values[0]

    # \textit{$SC_i$} & Number of days of stock coverage for product i
    SC = {}
    for i in I:
        SC[i] = pd_productos[pd_productos["i"] == i]["Days_Stock_Coverage"].values[0]


    # Create model
    model = Model("Modelo", solver_name="CBC")


    # \begin{array}{l|l}
    # Q_{i k t} & \text { Units transported of } i \text { by } k \text { in period } t
    # \end{array

    Q = {}
    for i in I:
        for k in K:
            for t in T:
                Q[(i, k, t)] = model.add_var(var_type="I",name="Q_{}_{}_{}".format(i, k, t))

    # \textit{M$_{iktbf}$}       & Containers transported of \textit{i} with the type of container \textit{b} by \textit{k} in time period

    M = {}
    for i in I:
        for k in K:
            for t in T:
                for b in B:
                    for f in F:
                            M[(i, k, t, b, f)] = model.add_var(var_type="I",name="M_{}_{}_{}_{}_{}".format(i, k, t, b, f))



    # \textit{I$_{it}$}     & Inventory amount of \textit{i} at the end of the time period \textit{t}

    vI = {}
    for i in I:
        for t in T:
            vI[(i, t)] = model.add_var(var_type="I",name="I_{}_{}".format(i, t))



    # \textit{V$_{bkft}$}

    V = {}
    for k in K:
        for b in B:
            for f in F:
                for t in T:
                    V[(k, b, f, t)] = model.add_var(var_type="I",name="V_{}_{}_{}_{}".format(k, b, f, t))
# \textit{Y$_{kt}$}     & Binary variable indicating   whether a truck \textit{k} has been   used in time period \textit{t}     \\

    Y = {}
    for k in K:
        for t in T:
            Y[(k, t)] = model.add_var(var_type="B",name="Y_{}_{}".format(k, t))


# \textit{X$_{kfwt}$}     & Binary variable indicating   whether the row \textit{f} of the truck \textit{k} is carrying containers of width \textit{w} at time \textit{t}


    X = {}
    for k in K:
        for f in F:
            for w in W:
                for t in T:
                    X[(k, f, w, t)] = model.add_var(var_type="B",name="X_{}_{}_{}_{}".format(k, f, w, t))


    # Create the objective function

    # $$\sum_k Y_{k, t}

    model.objective = minimize(xsum(Y[(k, t)] for k in K for t in T))

    # Now we are going to add the constraints

    # $$
    # I_{i t}=I_{i, t-1}-D_{i t}+\sum_{k \in K} Q_{i k t} \quad \forall i, t
    # $$

    Constraint1 = {}

    for i in I:
        for t in T:
            if t == 1:
                Constraint1[(i, t)] = model.add_constr(vI[(i, t)] == stockInicial[i] - D[(i, t)] + xsum(Q[(i, k, t)] for k in K))
            else:
                Constraint1[(i, t)] = model.add_constr(vI[(i, t)] == vI[(i, t - 1)] - D[(i, t)] + xsum(Q[(i, k, t)] for k in K))

    # \begin{equation}
    #     I_{i t }\geq     \begin{cases}
    #         \sum_{s \in \lbrace 1 , \dots , SC_i \rbrace } D_{i,t+s} \quad & \text{if } i \in I, t \in \lbrace 1, \dots , |T|-SC_i \rbrace \\
    #         \sum_{s \in \lbrace 1 , \dots , SC_i \rbrace } D_{i,|T|-SC_i+s} & \text{else}
    #     \end{cases}
    # \end{equation}

    Constraint2 = {}
    for i in I:
        for t in T:
            if t <= len(T) - SC[i]:
                Constraint2[(i, t)] = model.add_constr(vI[(i, t)] >= xsum(D[(i, t + s)] for s in range(1, SC[i] + 1)))
            else:
                Constraint2[(i, t)] = model.add_constr(vI[(i, t)] >= xsum(D[(i, len(T) - SC[i] + s)] for s in range(1, SC[i] + 1)))

    # \begin{equation}
    # Q_{i k t}=\sum_b  \sum_f M_{i k t b f} u_{i b} \quad \forall i,k,t
    # \end{equation}

    Constraint3 = {}
    for i in I:
        for k in K:
            for t in T:
                Constraint3[(i, k, t)] = model.add_constr(Q[(i, k, t)] == xsum(M[(i, k, t, b, f)] * u[(i, b)] for b in B for f in F
                                                                               if (i, b) in u))


    # \begin{equation}
    # pK_k\geq\sum_i \sum_b  \sum_f M_{i k t b f} u_{i b} \quad \forall k,t
    # \end{equation}

    # Constraint4 = {}
    # for k in K:
    #     for t in T:
    #         Constraint4[(k, t)] = model.add_constr(pK[k] >= xsum(M[(i, k, t, b, f)] * u[(i, b)] for i in I for b in B for f in F))


    #
    # \begin{equation}
    # \sum_i M_{i k t b f}=V_{b k f t}\left\lfloor\frac{h_k}{h_b}\right\rfloor \quad \forall b, f, k, t
    # \end{equation}

    Constraint5 = {}
    for k in K:
        for b in B:
            for f in F:
                for t in T:
                    Constraint5[(k, b, f, t)] = model.add_constr(xsum(M[(i, k, t, b, f)] for i in I)
                                                                 ==
                                                                 V[(k, b, f, t)] * math.floor(K[k].Height / B[b].Height))


    #
    # \begin{equation}
    # \sum_b V_{b k f t} b_l \leq k_l \cdot Y_{k t} \quad \forall k, t,  f
    # \end{equation}

    Constraint6 = {}
    for k in K:
        for t in T:
            for f in F:
                Constraint6[(k, t, f)] = model.add_constr(xsum(V[(k, b, f, t)] * B[b].Length for b in B)
                                                          <=
                                                          K[k].Length * Y[(k, t)])


    # \begin{equation}
    # \sum_i \sum_b \sum_f M_{i k t b f} \prod_{d\in {h,l,w}} d_b \geq \alpha_k*Y_{kt} \quad \forall k, t
    # \end{equation}

    # Constraint7 = {}
    # for k in K:
    #     for t in T:
    #         Constraint7[(k, t)] = model.add_constr(xsum(M[(i, k, t, b, f)] * B[b].Volume for i in I for b in B for f in F)
    #                                                >=
    #                                                K[k].alpha * Y[(k, t)])


    # \begin{equation}
    #     \sum_{l \in L(w)} V_{lkft} \leq X_{kfwt} \max_{b,k} \left\lfloor\frac{h_k w_k l_k }{h_b w_b l_b}\right\rfloor \ \quad \forall k, f, w, t
    # \end{equation}

    Constraint8 = {}
    for k in K:
        for f in F:
            for w in W:
                for t in T:
                    Constraint8[(k, f, w, t)] = model.add_constr(xsum(V[(k, b, f, t)] for b in B if B[b].Width == w) <= X[(k, f, w, t)] *int(max(K[k].Volume/B[b].Volume for b in B for k in K)+1))

    #\begin{equation}
    #     \sum_{w} X_{kfwt} \leq Y_{kt} \quad \forall k, f,  t
    # \end{equation}

    Constraint9 = {}
    for k in K:
        for f in F:
            for t in T:
                Constraint9[(k, f, t)] = model.add_constr(xsum(X[(k, f, w, t)] for w in W) <= Y[(k, t)])

    # \begin{equation}
    #     \sum_w \sum_f X_{kfwt} w \leq w_k \quad \forall w, f
    # \end{equation}

    Constraint10 = {}
    for k in K:
        for f in F:
            for t in T:
                Constraint10[(k, f, w)] = model.add_constr(xsum(X[(k, f, w, t)] * w for f in F for w in W) <= K[k].Width)


    # \begin{equation}
    #     Y_{kt} \geq Y_{k't} \quad \forall k, k'=k+1, t
    # \end{equation}

    Constraint11 = {}
    for k in K:
        for t in T:
            if k < len(K) - 1:
                Constraint11[(k, t)] = model.add_constr(Y[(k, t)] >= Y[(k + 1, t)])
            else:
                Constraint11[(k, t)] = model.add_constr(Y[(k, t)] >= 0)

    # \begin{equation}
    #     \sum_{w} X_{kfwt} \geq \sum_{w} X_{kf'wt} \quad \forall k, f, f'=f+1,  t
    # \end{equation}

    Constraint12 = {}
    for k in K:
        for f in F:
            for t in T:
                if f < len(F) - 1:
                    Constraint12[(k, f, t)] = model.add_constr(xsum(X[(k, f, w, t)] for w in W) >= xsum(X[(k, f + 1, w, t)] for w in W))
                else:
                    Constraint12[(k, f, t)] = model.add_constr(xsum(X[(k, f, w, t)] for w in W) >= 0)



    # Solve model
    model.optimize()

     # Print Status
    print('Status:', model.status)
    # Print Objective Value
    print('Optimal value:', model.objective.x)
    # Print the inventory levels
    for k in K:
        for t in T:
            print('Y[', k, ',', t, ']:', Y[(k, t)].x)
    # Print the inventory levels
    for t in T:
        for i in I:
            print("vI[", i, ",", t, "]:", vI[(i, t)].x)
if __name__ == '__main__':
    now = datetime.datetime.now()
    for folder in [d for d in os.listdir(r"datasets") if os.path.isdir("datasets" + "\\" + d)]:
        print("Folder: ", folder)
        path = os.getcwd() + r"\datasets\\" + folder
        print(path)
        update_data(path=path, folder=folder, now = now)