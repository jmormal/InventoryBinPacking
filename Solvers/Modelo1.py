import time
import sys
import shutil
import datetime
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
class Solver():
    def __init__(self):
        pass

    def solve(self,path=None, folder="default", now = datetime.datetime.now()  , planning_days=10, alpha=0.9,rows=3):
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
            path_save = wd + "\{}-{}-{}-time{}".format(now.day, now.month, now.year)
            os.makedirs(path, exist_ok=True)
        elif os.path.isdir(path + "\output" + "\{}{}{}".format(now.day, now.month, now.year) + "\\" + folder):
            wd = os.getcwd() + "\output"
            path_save = wd + "\{}-{}-{}".format(now.day, now.month, now.year)
            print("path_save with folder", path_save)

        else:
            wd = os.getcwd() +  "\output"
            path_save = wd + "\{}-{}-{}".format(now.day, now.month, now.year)
            path_save = path_save + "\\" + folder
            print("path_save with folder", path_save)
            print( "current path", os.getcwd())
            os.makedirs(path_save, exist_ok=True, )
            print( "current path", os.getcwd())

            for filename in os.listdir(os.getcwd() + "/output/backup"):
                shutil.copy(os.getcwd() + "/output/backup/" + filename, "{}\{}".format(path_save, filename))
    # \multicolumn{2}{|l|}{Sets of indices}                                                                   \\ \hline

        print("path_save", path_save)

        path
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
        T=list(range(1,len(pd_demanda["t"].unique().tolist())+1))
        T=list(range(1,10+1))
        model.T = pe.Set(initialize=T, doc="Set of planning periods (t =1, 2…T)")


        # \textit{F}       & Set of possible rows inside a   truck \textit{(f} =1,2,...,\textit{F)}                              \\

        F=list(range(rows))
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
            for _ in range(4):
                K.update({ i :Truck(row.id,row.Length,row.Width,row.Heigth,alpha=  alpha) })
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

    # Find the minimum length for each width
        L_m={}
        for w in W:
            L_m[w]=min([B[b].Length for b in L[w]])



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
        model.Lmin = pe.Var(model.K, model.F, model.W, model.T, domain=pe.NonNegativeReals,)


        print(list(model.T))

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
        print(l1 )

        def _Q(model, i, k, t):
            return model.Q[i,k,t]==sum(model.M[i,k,t,b,f]*model.u[i,b] for b in model.B for f in model.F  if (i,b) in model.u)

        model.Q_rule = pe.Constraint(model.I,model.K, model.T , rule=_Q)



        def _M(model, b, k, t, f):
            return sum(model.M[i,k,t,b,f] for i in I  )==model.V[k,b,f,t]*math.floor(K[k].Height/B[b].Height)

        model.M_rule = pe.Constraint(model.B, model.K, model.T, model.F, rule=_M)


        def _V(model, k, t, f):
            return sum(model.V[k,b,f,t]*B[b].Length for b in B)<=K[k].Length*model.Y[k,t]

        model.V_rule = pe.Constraint(model.K, model.T, model.F , rule=_V)
        # \begin{equation}
        #     (1-X_{kfat})Lm_a=Lmin_{kfat}
        # \end{equation}

        def _Lmin(model, k, f, w, t):
            return (model.X[k,f,w,t])*L_m[w]==model.Lmin[k,f,w,t]

        model.Lmin_rule = pe.Constraint(model.K, model.F, model.W, model.T, rule=_Lmin)

        # \begin{equation}
        # \sum_b V_{b k f t} l_b + \sum_a Lmin_{kfat} \geq l_k \quad \forall k, t,  f
        # \end{equation}

        def _Lmin2(model, k, f, t):
            return sum(model.V[k,b,f,t]*B[b].Length for b in B)+sum(model.Lmin[k,f,w,t] for w in W)\
                   +100000*(1-sum(model.X[k,f,w,t] for w in model.W))>=K[k].Length*model.Y[k,t]

        model.Lmin2_rule = pe.Constraint(model.K, model.F, model.T, rule=_Lmin2)


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
        cost_stock = sum(model.vI[i, t]/max(model.u[i,b] for b in model.B) for i in model.I for t in model.T)
        expr = 10000*num_camiones+cost_stock


        # Coste Transporte
        model.objective = pe.Objective(sense=pe.minimize, expr=expr)
        solver = po.SolverFactory("gurobi")
        times=60*2
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
            CamionesDia.append([t,sum(model.Y[k,t].value for k in K)    ])
        df_CamionesDia=pd.DataFrame(CamionesDia,columns=["t","NumberOfTrucks"])
        df_CamionesDia.to_csv(path_save+r"\NumberOfTrucksPerDay.csv")

        # Now we are going to save the Proyected Stock in a csv file. The header of the file is i, t, ProyectedStock
        stock=[]
        for t in T:
            for i in I:
                # stock.append([t,i, solver.Value( vI[i,t])])
                stock.append([t,i, model.vI[i,t].value])
        df_stock=pd.DataFrame(stock,columns=["t","id","ProyectedStock"])
        df_stock.to_csv(path_save+"\ProyectedStock.csv")

        # Now we are going to save the Needed Stock in a csv file. The header of the file is i, t, NeededStock
        needed_stock=[]
        l1={}
        for i in I:
            for t in T:
                if t < len(T) - SC[i]+1:
                    l1[i] = sum(  D[i,t+s] for s in range(1,SC[i]+1)  )

                needed_stock.append([t,i, l1[i]])
        df_needed_stock=pd.DataFrame(needed_stock,columns=["t","id","NeededStock"])
        df_needed_stock.to_csv(path_save+r"\NeededStock.csv")
        # Print the values of model.Lmin = pe.Var(model.K, model.F, model.W, model.T
        # for k in K:
        #     for t in T:
        #         for f in F:
        #                 print(sum(model.Lmin[k,f,w,t].value for w in W))

        # Now we are going to save the distribution of the products in the trucks in a csv file. The header of the file is k, t, i, b, x, y, z
        distribution=[]
        for k in K:
            for t in T:
                current_length = 0
                current_width = 0
                for f in model.F:
                    current_height = 0
                    for w in model.W:
                        if model.X[k,f,w,t].value > 0:
                            for b in model.B:
                                    if int(sum(model.M[i,k,t,b,f].value for i in model.I)) > 0:
                                        # if t==2 and k==1:
                                        #     print(int(model.M[i,k,t,b,f].value))
                                        #     print(int(K[k].Height//B[b].Height))
                                        #     pass
                                        print(" \n \n \n")
                                        d1 = {i: model.M[i, k, t, b, f].value for i in model.I}

                                        for k1 in range(1,int(sum(model.M[i,k,t,b,f].value for i in model.I))+1):
                                            # Get a dictionry i->M[i,k,t,b,f].value
                                            # Get the key of the maximum value
                                            i = max(d1, key=d1.get)
                                            # Get the value of the maximum value
                                            print(d1)
                                            distribution.append([k,t,i,b[:-2],current_length,current_width,current_height,b[-1],B[b].Volume])
                                            d1[i] -= 1
                                            if k1% int(K[k].Height//B[b].Height) == 0:
                                                current_length += B[b].Length
                                                current_height = 0
                                            elif k1 == int(sum(model.M[i,k,t,b,f].value for i in model.I)):
                                                current_length += B[b].Length
                                                current_height = 0
                                            else:
                                                current_height += B[b].Height
                            current_width += w
                            current_length = 0
                            print( " w " , w)
                            print( " f " , f)

        df_distribution=pd.DataFrame(distribution,columns=["k","t","i","b","x","y","z", "r", "Volume"])
        df_distribution.to_csv(path_save+r"\\TruckDistribution.csv")


        num_camiones = sum(model.Y[k, t].value for k in model.K for t in model.T)
        cost_stock = sum(model.vI[i, t].value for i in model.I for t in model.T)






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
        print("Numero de camiones: ", num_camiones)
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

    # Print working directory
    print("Working directory: ", os.getcwd())
    # Change working directory to the folder above
    os.chdir("..")
    print("Working directory: ", os.getcwd())

    for planning_days in [ 10  ]:
        for folder in [d for d in os.listdir(r"datasets") if os.path.isdir("datasets" + "\\" + d)]:
            print("Folder: ", folder)
            path = os.getcwd() + r"\datasets\\" + folder
            print(path)
            solver=Solver()
            solver.solve( path=path, folder=folder, now=now, planning_days=planning_days)