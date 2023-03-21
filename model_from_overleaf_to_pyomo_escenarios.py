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

    # \textit{I}       & Set of products (\textit{i} =1, 2,…,\textit{I})                                                      \\

    I={i:i for i in pd_productos["i"].unique().tolist()}
    model.I = pe.Set(initialize=pd_productos["i"].unique().tolist(), doc="Set of products (i =1, 2,…,I)")
    # \textit{T}       & Set of planning periods \textit{(t} =1, 2…\textit{T)}                                        \\

    T=list(range(1,planning_days+1))
    model.T = pe.Set(initialize=T, doc="Set of planning periods (t =1, 2…T)")


    # \textit{F}       & Set of possible rows inside a   truck \textit{(f} =1,2,...,\textit{F)}                              \\

    F=list(range(3))
    model.F = pe.Set(initialize=F, doc="Set of possible rows inside a truck (f =1,2,...,F)")

    # \textit{C}       & Set of possible columns inside a   truck \textit{(c} =1,2,...,\textit{C)}                              \\


    # \textit{B}       & Set of types of containers \textit{(b }=   1,…,\textit{B)}                                            \\
    B = {}
    i=0
    for row in pd_dimensiones_contenedores.itertuples():

        B.update({str(row.id)+"r0" :Container(row.id,row.Length,row.Width,row.Heigth)})
        B.update({str(row.id)+"r1" :Container(row.id,row.Width,row.Length,row.Heigth)})
        i+=1
    model.B = list(B.keys())

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

    # \textit{W}       & Set of possible box widths \textit{(w} =1, 2…\textit{W)}                                        \\ \hline
    W=list(set(pd_dimensiones_contenedores["Width"].unique().tolist()+pd_dimensiones_contenedores["Length"].unique().tolist()))


    model.W = pe.Set(initialize=W, doc="Set of possible box widths (w =1, 2,…,W)")




# \textit{L(w)}       & Set of containers such that they have the width \textit{w}
    L={}
    for w in W:
        L.update({w:[b for b in B if B[b].Width==w]})
    model.L = pe.Set(model.W, initialize=L, doc="Set of containers such that they have the width w")

# Parameters



# \multicolumn{2}{|l|}{Parameters}                                                                        \\ \hline
# \textit{$u_{ib}$}      & Amount of product \textit{i} that fits in a container \textit{b}                             \\
    u={}
    # for i in I:
    #     for n in N:
    #         u[i,n]=0
    for row in pd_productos.itertuples():
        for k ,c in enumerate(row.id_container.split("|")):
            # set the value of u if the contaner n has the same id as b
            u[row.i, str(c)+"r0"]=float(str(row.items_per_container).split("|")[k])
            u[row.i, str(c)+"r1"]=float(str(row.items_per_container).split("|")[k])
    model.u = pe.Param(model.I, model.B, initialize=u, doc="Amount of product i that fits in a container b",  default=0)








# \textit{$D_{it}$}     & Demand of product \textit{i} in \textit{t}                             \\
    D={}
    for row in pd_demanda.itertuples():
        if row.t in T:
            if row.i in I:
               D[(row.i, row.t)] = row.Demanda
    model.D = pe.Param(model.I, model.T, initialize=D, doc="Demand of product i in t")

    CosteStock={}
    stockInicial={}
    for i in I:
        CosteStock[i] = pd_productos[pd_productos["i"] == i]["CosteStock"].values[0]
        stockInicial[i] = pd_productos[pd_productos["i"] == i]["Stock"].values[0]

    model.CosteStock = pe.Param(model.I, initialize=CosteStock, doc="Coste de almacenar un producto")
    model.stockInicial = pe.Param(model.I, initialize=stockInicial, doc="Stock inicial de cada producto")
# \textit{$SC_i$} & Number of days of stock coverage for product i
    SC={}
    for i in I:
        SC[i] = pd_productos[pd_productos["i"] == i]["Days_Stock_Coverage"].values[0]

    model.SC = pe.Param(model.I, initialize=SC, doc="Number of days of stock coverage for product i")
# \multicolumn{2}{|l|}{Decision variables}                                                                \\ \hline
# \textit{Q$_{ikt}$}       & Units transported of \textit{i} by \textit{k} in period \textit{t}                                  \\





#     model = cp_model.CpModel()
#
#     Q  = {(i, k , t): model.NewIntVar(0, 200000, "x") for i in I for k in K for t in T}

    model.Q = pe.Var(model.I, model.K, model.T, domain=pe.NonNegativeIntegers, doc="Units transported of i by k in period t")


#
#
# # \textit{M$_{iktbf}$}       & Units transported of \textit{i} with the type of container \textit{b} by \textit{k} in time period \textit{t}             \\

    model.M = pe.Var(model.I, model.K, model.T, model.B, model.F , domain=pe.NonNegativeIntegers,
                     doc="Units transported of i with the type of container b by k in time period t")
#     M  = {(i, k , t, b, f): model.NewIntVar(0, 90, "x") for i in I for k in K for t in T for b in B for f in F }
# # \textit{I$_{it}$}     & Inventory amount of \textit{i} at the end of the time period \textit{t}                                \\
    model.vI = pe.Var(model.I, model.T, domain=pe.NonNegativeIntegers,
                     doc="Inventory amount of i at the end of the time period t")
#     vI  = {(i, t): model.NewIntVar(0, 100000, "x") for i in I for t in T}
# # \textit{V$_{bckf}$}    & Number of containers of type \textit{b}   that are on the bottom layer at the column \textit{c} of \textit{k} \\
    model.V = pe.Var(model.K, model.B, model.F, model.T, domain=pe.NonNegativeIntegers,
                     doc="Number of containers of type b that are on the bottom layer at the column c of k")
#     V  = {(k, b, f,t): model.NewIntVar(0, 20, "x") for k in K for b in B for f in F for t in T}
# # \textit{Y$_{kt}$}     & Binary variable indicating   whether a truck \textit{k} has been   used in time period \textit{t}     \\
    model.Y = pe.Var(model.K, model.T, domain=pe.Binary,
                     doc="Binary variable indicating whether a truck k has been used in time period t")
#     Y  = {(k, t): model.NewIntVar(0, 1, "x") for k in K for t in T}
# # \textit{X$_{kfwt}$}     & Binary variable indicating   whether the row \textit{f} of the truck \textit{k} is carrying containers of width \textit{w} at time \textit{t}     \\ \hline
    model.X = pe.Var(model.K, model.F, model.W, model.T, domain=pe.Binary,
                     doc="Binary variable indicating whether the row f of the truck k is carrying containers of width w at time t")









    def _I(model, i, t):
        if t == 1:
            return model.vI[i, t] == model.stockInicial[i] - model.D[i, t] + sum(model.Q[i, k, t] for k in model.K)
        else:
            return model.vI[i, t] == model.vI[i, t - 1] - model.D[i, t] + sum(model.Q[i, k, t] for k in model.K)

    model.I_rule = pe.Constraint(model.I, model.T, rule=_I)


    l1={}
    for i in I:
        for t in T:
            if t < len(T) - SC[i]+1:
                l1[i] = sum(  D[i,t+s] for s in range(1,SC[i]+1)  )

    def _I2(model, i, t):
        if t < len(T) - model.SC[i]+1:
            return model.vI[i,t]>=sum(  model.D[i,t+s] for s in range(1,model.SC[i]+1)  )
        else:
            return model.vI[i,t]>=l1[i]

    model.I2_rule = pe.Constraint(model.I, model.T, rule=_I2)


    def _Q(model, i, k, t):
        return model.Q[i,k,t]==sum(model.M[i,k,t,b,f]*model.u[i,b] for b in model.B for f in model.F  if (i,b) in model.u)

    model.Q_rule = pe.Constraint(model.I,model.K, model.T , rule=_Q)



    def _M(model, b, k, t, f):
        return sum(model.M[i,k,t,b,f] for i in I  )==model.V[k,b,f,t]*math.floor(K[k].Height/B[b].Height)

    model.M_rule = pe.Constraint(model.B, model.K, model.T, model.F, rule=_M)


    def _V(model, k, t, f):
        return sum(model.V[k,b,f,t]*B[b].Length for b in B)<=K[k].Length*model.Y[k,t]

    model.V_rule = pe.Constraint(model.K, model.T, model.F , rule=_V)

    def _Y(model, k, t):
        return sum(model.M[i,k,t,b,f]*B[b].Volume for i in I for b in B for f in F )>=int(K[k].alpha*K[k].Volume)*model.Y[k,t]

    model.Y_rule = pe.Constraint(model.K, model.T, rule=_Y)



    def _X(model, k, f, w, t):
        return sum(model.V[k,b,f,t] for b in B if B[b].Width==w)<=model.X[k,f,w,t]*max(math.floor(K[k].Volume/B[b].Volume) for b in B for k in K)

    model.X_rule = pe.Constraint(model.K, model.F, model.W, model.T, rule=_X)


    def _X2(model, k, f, t):
        return sum(model.X[k,f,w,t] for w in W)<=model.Y[k,t]

    model.X2_rule = pe.Constraint(model.K, model.F, model.T, rule=_X2)



    def _X3(model, k, t):
        return sum(model.X[k,f,w,t]*w for w in W for f in F)<=K[k].Width

    model.X3_rule = pe.Constraint(model.K, model.T, rule=_X3)



    def _Y2(model, k, t):
        if k+1 in K:
            return model.Y[k,t]>=model.Y[k+1,t]
        else:
            return pe.Constraint.Skip

    model.Y2_rule = pe.Constraint(model.K, model.T, rule=_Y2)


    def _X4(model, k, f, t):
        if f+1 in F:
            return sum(model.X[k,f,w,t] for w in W)>=sum(model.X[k,f+1,w,t] for w in W)
        else:
            return pe.Constraint.Skip

    model.X4_rule = pe.Constraint(model.K, model.F, model.T, rule=_X4)

    # expr = 3*max(D.values())*23*sum(
    #     model.Y[k, t]  for k in model.K for t in
    #     model.T)+sum(model.vI[i,t] for i in model.I for t in model.T)
    num_camiones = sum(model.Y[k, t] for k in model.K for t in model.T)
    cost_stock = sum(model.vI[i, t] for i in model.I for t in model.T)
    expr = len(I)*max(D.values())*len(K)*len(T)*num_camiones + cost_stock


    # Coste Transporte
    model.objective = pe.Objective(sense=pe.minimize, expr=expr)
    solver = po.SolverFactory("gurobi")
    times=60*60*10
    solver.options["TimeLimit"]=times
    solver.options['slog'] = 1
    print("\n The instance is planning days {} and folder  {} \n".format(planning_days, folder), file=open("results.txt", "a"))
    try:
        results = solver.solve(model, tee=True , logfile=path_save+"\logfile.log",)
        for k in K:
            for t in T:
                if model.Y[k, t].value > 0:
                    print(
                        sum(model.M[i, k, t, b, f].value * B[b].Volume / K[k].Volume
                            for i in I for b in B for f in F))

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
        CamionesDia.append(c)
    df_CamionesDia=pd.DataFrame(CamionesDia,columns=["CamionesDia"])
    df_CamionesDia.to_csv(path_save+"\CamionesDia.csv")

    num_camiones = sum(model.Y[k, t].value for k in model.K for t in model.T)
    cost_stock = sum(model.vI[i, t].value for i in model.I for t in model.T)

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
    print("Solucion guardada en: ", path_save)
    # Save the results
    original_stdout = sys.stdout # Save a reference to the original standard output
    f = open(path_save+r'\resultados_Modelo1.txt', 'w')
    sys.stdout = f
    model.pprint()
    f.close()


    # Save the results
    f = open(path_save+r'\Globales_Modelo1.txt', 'w')
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