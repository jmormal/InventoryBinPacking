from ortools.sat.python import cp_model
import time
import sys
import shutil
import datetime
from time import perf_counter as time
import pandas as pd
import os
import math
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

    # \textit{I}       & Set of products (\textit{i} =1, 2,…,\textit{I})                                                      \\

    I=pd_productos["i"].unique().tolist()

    # \textit{T}       & Set of planning periods \textit{(t} =1, 2…\textit{T)}                                        \\

    T=pd_demanda["t"].unique().tolist()


    # \textit{F}       & Set of possible rows inside a   truck \textit{(f} =1,2,...,\textit{F)}                              \\

    F=list(range(3))

    # \textit{C}       & Set of possible columns inside a   truck \textit{(c} =1,2,...,\textit{C)}                              \\
    C=list(range(13))


    # \textit{B}       & Set of types of containers \textit{(b }=   1,…,\textit{B)}                                            \\
    B = {}
    i=0
    for row in pd_dimensiones_contenedores.itertuples():
        B.update({row.id :Container(row.id,row.Length,row.Width,row.Heigth)})
        i+=1
    # \textit{K}       & Set of trucks (\textit{k} =1, 2,…,\textit{K)}                                                        \\
    K = {}
    for row in pd_dimensiones_camiones.itertuples():
        K={i :Truck(row.id,row.Length,row.Width,row.Heigth) for i in range(3)}

    # \textit{W}       & Set of possible box widths \textit{(w} =1, 2…\textit{W)}                                        \\ \hline
    W=pd_dimensiones_contenedores["Width"].unique().tolist()




# \textit{L(w)}       & Set of containers such that they have the width \textit{w}
    L={}
    for w in W:
        L.update({w:[b for b in B if B[b].Width==w]})


# \multicolumn{2}{|l|}{Parameters}                                                                        \\ \hline
# \textit{$u_{ib}$}      & Amount of product \textit{i} that fits in a container \textit{b}                             \\

    u={}
    for row in pd_productos.itertuples():
        u[(row.i, row.id_container)] = row.items_per_container
# \textit{$D_{it}$}     & Demand of product \textit{i} in \textit{t}                             \\
    D={}
    for row in pd_demanda.itertuples():
        D[(row.i, row.t)] = row.Demanda


    CosteStock={}
    stockInicial={}
    for i in I:
        CosteStock[i] = pd_productos[pd_productos["i"] == i]["CosteStock"].values[0]
        stockInicial[i] = pd_productos[pd_productos["i"] == i]["Stock"].values[0]
# \textit{$SC_i$} & Number of days of stock coverage for product i
    SC={}
    for i in I:
        SC[i] = pd_productos[pd_productos["i"] == i]["Days_Stock_Coverage"].values[0]


# \multicolumn{2}{|l|}{Decision variables}                                                                \\ \hline
# \textit{Q$_{ikt}$}       & Units transported of \textit{i} by \textit{k} in period \textit{t}                                  \\

    model = cp_model.CpModel()

    Q  = {(i, k , t): model.NewIntVar(0, 200000, "x") for i in I for k in K for t in T}



# \textit{M$_{iktbf}$}       & Units transported of \textit{i} with the type of container \textit{b} by \textit{k} in time period \textit{t}             \\
    M  = {(i, k , t, b, f, c): model.NewIntVar(0, 90, "x") for i in I for k in K for t in T for b in B for f in F for c in C}
# \textit{I$_{it}$}     & Inventory amount of \textit{i} at the end of the time period \textit{t}                                \\
    vI  = {(i, t): model.NewIntVar(0, 100000, "x") for i in I for t in T}
# \textit{V$_{bckf}$}    & Number of containers of type \textit{b}   that are on the bottom layer at the column \textit{c} of \textit{k} \\
    V  = {(k, b, f,t): model.NewIntVar(0, 20, "x") for k in K for b in B for f in F for t in T}
# \textit{Y$_{kt}$}     & Binary variable indicating   whether a truck \textit{k} has been   used in time period \textit{t}     \\
    Y  = {(k, t): model.NewIntVar(0, 1, "x") for k in K for t in T}
# \textit{X$_{kfwt}$}     & Binary variable indicating   whether the row \textit{f} of the truck \textit{k} is carrying containers of width \textit{w} at time \textit{t}     \\ \hline
    X  = {(k, f, w, t): model.NewIntVar(0, 1, "x") for k in K for f in F for w in W for t in T}



# \begin{flalign}
# I_{i t}=I_{i, t-1}-D_{i t}+\sum_{k \in K} Q_{i k t} \quad  \forall i,t
# \end{flalign}

    for i in I:
        for t in T:
            if t==1:
                model.Add(vI[i,t]==stockInicial[i]-D[i,t]+sum(Q[i,k,t] for k in K))
            else:
                model.Add(vI[i,t]==vI[i,t-1]-D[i,t]+sum(Q[i,k,t] for k in K))
# \begin{equation}
#     I_{i t }\geq \sum_{s \in \lbrace 1 , \dots SC_i \rbrace } D_{i,t+s} \quad \forall t
# \end{equation}
    l1={}
    for i in I:
        for t in T:
            if t < len(T) - SC[i]+1:
                model.Add(vI[i,t]>=sum(  D[i,t+s] for s in range(1,SC[i]+1)  ))
                l1[i] = sum(  D[i,t+s] for s in range(1,SC[i]+1)  )
            else:
                model.Add(vI[i,t]>=l1[i])
    print(l1)

# \begin{equation}
# Q_{i k t}=\sum_b \sum_c \sum_f M_{i k t b f} u_{i b} \quad \forall i,k,t
# \end{equation}

    for i in I:
        for k in K:
            for t in T:
                model.Add(Q[i,k,t]==sum(M[i,k,t,b,f,c]*u[i,b] for b in B for f in F for c in C if (i,b) in u))

# \begin{equation}
# \sum_i M_{i k t b f}=V_{b c k f}\left\lfloor\frac{k_h}{b_h}\right\rfloor \quad \forall b, k, t, c
# \end{equation}


    for b in B:
        for k in K:
            for t in T:
                    for f in F:
                        model.Add(sum(M[i,k,t,b,f,c] for i in I  for c in C)==V[k,b,f,t]*math.floor(K[k].Height/B[b].Height))
# \begin{equation}
# \sum_ c\sum_b V_{b c k f} b_l \leq k_l \cdot Y_{k t} \quad \forall k, t, c, f
# \end{equation}

    for k in K:
        for t in T:
            for f in F:
                model.Add(sum(V[k,b,f,t]*B[b].Length for b in B)<=K[k].Length*Y[k,t])
# \begin{equation}
# \sum_c \sum_i \sum_b \sum_f M_{i k t b f} \prod_{d\in {h,l,w}} d_b \geq \alpha_k  Y_{k t} \quad \forall k, t
# \end{equation}
#
    for k in K:
        for t in T:
            model.Add(sum(M[i,k,t,b,f,c]*B[b].Height*B[b].Length*B[b].Width for i in I for b in B for f in F for c in C)>=int(K[k].alpha*K[k].Volume)*Y[k,t])
# \begin{equation}
#     \sum_{l \in L(w)} V_{lckf} \leq X_{kfwt} \max_{b,k} \left\lfloor\frac{h_k w_k l_k }{h_b w_b l_b}\right\rfloor \ \quad \forall k, f, w, t
# \end{equation}

    for k in K:
        for f in F:
            for w in W:
                for t in T:
                    model.Add(sum(V[k,b,f,t] for b in B if B[b].Width==w)
                              <=
                              X[k,f,w,t]*max(math.floor(K[k].Volume/B[b].Volume) for b in B for k in K))

# \begin{equation}
#     \sum_{w} X_{kfwt} = 1 \quad \forall k, f,  t
# \end{equation}

    for k in K:
        for f in F:
            for t in T:
                model.Add(sum(X[k,f,w,t] for w in W)<=Y[k,t])
# \begin{equation}
#     \sum_w \sum_f X_{kfwt} w \leq w_k \quad \forall w, f
# \end{equation}

    for k in K:
        for t in T:
            model.Add(sum(X[k,f,w,t]*w for w in W for f in F)<=K[k].Width)

# \begin{equation}
#     Y_{ct} \geq Y_{ct'} \quad \forall t<|T| ,c ,t'=t+1
# \end{equation}

    for k in K:
        for t in T:
            if k+1 in K:
                model.Add(Y[k,t]>=Y[k+1,t])




# \textit{z1}      & Total number of trucks utilized                                                  \\ \hline


# \begin{equation}
#     \text{\textit{Min} } z= \sum_k Y_{k,t}
# \end{equation}

    model.Minimize(sum(Y[k,t] for k in K for t in T))
    a = time()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = int(3.5 * 60)
    # solver.parameters.relative_gap_limit = 0.0001
    # solver.parameters.num_search_workers = 1
    original_stdout = sys.stdout
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL:

        print("Optimal solution found")
        print("Objective value:", solver.ObjectiveValue())
        # print("Numero de camiones:", sum(solver.Value(vY[c, t]) for c in camiones for t in dias))
        print("Numero de camiones:", solver.ObjectiveValue())

        print(" Tiempo de ejecucion:", time() - a)
    elif status == cp_model.FEASIBLE:
        print("Feasible solution found")
        print("Objective value:", solver.ObjectiveValue())
        print("Best objective Bound:", solver.BestObjectiveBound())
        # print("Numero de camiones:", sum(solver.Value(vY[c, t]) for c in camiones for t in dias))
        print("Numero de camiones:", solver.ObjectiveValue())
        print(" Tiempo de ejecucion:", time() - a)

    elif status == cp_model.INFEASIBLE:
        print("Infeasible solution")
        print(" Tiempo de ejecucion:", time() - a)

    elif status == cp_model.UNKNOWN:
        print("Unknown solution")
        print(" Tiempo de ejecucion:", time() - a)
    print(path_save)
    with open(path_save + "\log.txt", 'w') as f:
        sys.stdout = f
        if status == cp_model.OPTIMAL:

            print("Optimal solution found")
            print("Objective value:", solver.ObjectiveValue())
            # print("Numero de camiones:", sum(solver.Value(vY[c, t]) for c in camiones for t in dias))
            print("Numero de camiones:", solver.ObjectiveValue())


            print(" Tiempo de ejecucion:", time() - a)
        elif status == cp_model.FEASIBLE:
            print("Feasible solution found")
            print("Objective value:", solver.ObjectiveValue())
            print("Best objective Bound:", solver.BestObjectiveBound())
            # print("Numero de camiones:", sum(solver.Value(vY[c, t]) for c in camiones for t in dias))
            print("Numero de camiones:", solver.ObjectiveValue())
            print(" Tiempo de ejecucion:", time() - a)

        elif status == cp_model.INFEASIBLE:
            print("Infeasible solution")
            print(" Tiempo de ejecucion:", time() - a)

        elif status == cp_model.UNKNOWN:
            print("Unknown solution")
            print(" Tiempo de ejecucion:", time() - a)

            sys.stdout = original_stdout
            return None

    sys.stdout = original_stdout





    CamionesDia=[]
    for t in T:
        CamionesDia.append(sum(solver.Value(Y[k,t]) for k in K))
    df_CamionesDia=pd.DataFrame(CamionesDia,columns=["CamionesDia"])
    df_CamionesDia.to_csv(path_save+"\CamionesDia.csv")



    stock=[]
    for t in T:
        for i in I:
            stock.append([t,i, solver.Value( vI[i,t])])
    df_stock=pd.DataFrame(stock,columns=["t","id","Stock"])
    df_stock.to_csv(path_save+"\Stock.csv")






    cantidadpedir_acu=[]
    for t in T:
        pro=[]
        for i in I:
            pro.append(sum(solver.Value(Q[i,k,t1]) for k in K for t1 in T[0:t]))
        cantidadpedir_acu.append(pro)
    df_cantidadpedir_acu=pd.DataFrame(cantidadpedir_acu,columns=I)
    df_cantidadpedir_acu.to_csv(path_save+"\cantidadpedir_acu.csv")




# Save cantidad_pedir by day, truck and product
    cantidad_pedir=[]
    for t in T:
        for k in K:
            for i in I:
                cantidad_pedir.append([t,k,i, solver.Value(Q[i,k,t])])
    df_cantidad_pedir=pd.DataFrame(cantidad_pedir,columns=["t","k","producto","CantidadPedir"])
    df_cantidad_pedir.to_csv(path_save+"\CantidadPedir.csv")




    # Save numbers of trucks by day
    CamionesDia=[]
    for t in T:
        CamionesDia.append(sum(solver.Value(Y[k,t]) for k in K))
    df_CamionesDia=pd.DataFrame(CamionesDia,columns=["CamionesDia"])
    df_CamionesDia.to_csv(path_save+"\CamionesDia.csv")






    # Save stock by day and product
    stock=[]
    for t in T:
        for i in I:
            stock.append([t,i, solver.Value( vI[i,t])])
    df_stock=pd.DataFrame(stock,columns=["t","product","Stock"])




    # save the model
    sol_camiones_total=[]
    for t in T:
        k1=0
        for k in K:
            sol_dia = []

            if solver.Value(Y[k, t]) == 1:
                k1=k1+1
                for i in I:
                    ## if the product is in the truck
                    if solver.Value(Q[i, k, t]) > 0:
                        ## product, vA, vB
                        sol_dia.append([i,solver.Value(Q[i, k, t]), sum(solver.Value(M[i,k,t,b,f,c]) for c in C for f in F for b in B if B[b].id=="a"),
                                        sum(solver.Value(M[i,k,t,b,f,c])  for c in C for f in F  for b in B if B[b].id=="b"), 1000])
                        sol_camiones_total.append([t,k1,i,solver.Value(Q[i, k, t]),
                                                   sum(solver.Value(M[i,k,t,b,f,c])  for i in I for c in C for f in F for b in B if B[b].id=="a"),
                                                   sum(solver.Value(M[i,k,t,b,f,c])  for i in I for c in C for f in F for b in B if B[b].id=="b"),
                                                   1200,
                                                   sum(sum(solver.Value(M[i,k,t,b,f,c]) for i in I for c in C for f in F)*
                                                       B[b].Height*B[b].Width*B[b].Length for b in B)/K[k].Volume])
                df_sol_dia=pd.DataFrame(sol_dia, columns=["id","Products","vA","vB","LargoBox"])
                df_sol_dia.to_csv(path_save+"\CantidadPedirDia{}Camion{}.csv".format(t,k1))
    df_sol_camiones_total=pd.DataFrame(sol_camiones_total, columns=["t","c","id","Products","vA","vB","LargoBox", "Volumen"])
    df_sol_camiones_total.to_csv(path_save+"\CantidadPedirTotal.csv")


    for t in T:
        for k in K:
            if solver.Value(Y[k, t]) == 1:
                print("Dia: ", t, "Camion: ", k)
                for f in F:
                    # Print Length of row
                    print("Fila: ", f, "Largo: ", sum(solver.Value(V[k,b,f,t])*B[b].Length for b in B))
                    # print average height of row
                    print("Fila: ", f, "Altura: ", list((sum(solver.Value(M[i,k,t,b,f,c])*B[b].Height  for c in C for i in I)/solver.Value(V[k,b,f,t]) for b in B if solver.Value(V[k,b,f,t])>0)))
                    # print
                    print(
                    sum(solver.Value(M[i, k, t, b, f, c]) for i in I for c in C for b in B if
                        B[b].id == "a"),
                    sum(solver.Value(M[i, k, t, b, f, c]) for i in I for c in C for b in B if
                        B[b].id == "b"),
                    )
                 ## if the product is in the truck


if __name__ == '__main__':
    now = datetime.datetime.now()
    for folder in [d for d in os.listdir(r"datasets") if os.path.isdir("datasets" + "\\" + d)]:
        print("Folder: ", folder)
        path = os.getcwd() + r"\datasets\\" + folder
        update_data(path=path, folder=folder, now = now)