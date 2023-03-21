from ortools.sat.python import cp_model
import pandas as pd
import time
import random
import shutil
import datetime
import os
from time import perf_counter as time

def update_data():
    path = os.getcwd()
    df = pd.read_csv(path + "\output\lastsol\CantidadPedirTotal.csv")
    print(df)
    B=[1,2]
    I=list(df.id.unique())
    A=list(range(1,5))
    C=list(range(14))
    F=[1]
    kh=3000
    bh={1:1000,2:750}
    X=[1000*i + 1600*j for i in range(14) for j in range(14) if 1000*i + 1600*j <= 13600]
    X=list(set(X))
    df_prod=pd.read_csv(path + "\datasets\Productos.csv")
    P = {(b, i): 0 for b in B for i in I}
    for p in df_prod.itertuples():
        if p.Largo == 1600:
            b=2
            P[b,p.i]=p._8
            b=1
            P[b,p.i]=p._9
    u = {x: 1 + random.randint(1, 5) for x in X}
    print(u)

    for t in df.t.unique():
        dff = df.copy()
        df_fltr = dff[df.t==t]
        K=list(df_fltr.c.unique())
        # \textit{$M_{iktb}:$}       & Units transported of i with the type of box b by k in period t (units).
        M={(i,k,t,b): 0 for i in I for k in K for t in df.t.unique() for b in B}
        for row in dff.itertuples():
            if row.LargoBox==1600:
                b=2
                k1=4
            else:
                b=1
                k1=3
            M[row.id,row.c,row.t,b]=row.Products


        kl=13600
        l={b: 1000 if b==1 else 1600 for b in B}
        # print("camiones", K)
        # print("productos", I)
        # print("Altura", A)
        # print("Box", B)
        # print("filas", F)
        # print("Columnas", C)
        # print("M", M)

        model = cp_model.CpModel()
        # P_{bikcfa}\in [0,1]
        vP = {(b,i,c,k,f,a,x): model.NewIntVar(0, 1, "x") for b in B for i in I for c in C for k in K for f in F for a in A for x in X}
        vR= {(k,c,f,x): model.NewIntVar(0, 1, "y") for k in K for c in C for f in F for x in X}
        vR1= {(k,c,f,x): model.NewIntVar(0, 1, "y") for k in K for c in C for f in F for x in X}
        vL={(k,c,f): model.NewIntVar(0, 13610, "x") for k in K for c in C for f in F }
        vL1={(k,c,f,x) : model.NewBoolVar("x") for k in K for c in C for f in F for x in X}

        print(len(vP))
        # Objective function (minimize the number of boxes)
        model.Minimize(sum(vP[b,i,c,k,f,a,x]*u[x]*P[b,i] for b in B for i in I for c in C for k in K for f in F for a in A for x in X))
        # model.Minimize(sum(vR[k,c,f,x]*u[x] for k in K for c in C for f in F for x in X))

        # Assure one container its obove another container
        # \sum_b \sum_i P_{b i k c f a} \geq \sum_b \sum_i P_{b i k f,a+1} \forall k,f,c,a<|A|

        RAltura={(k,f,c,a): model.Add(sum([vP[(b,i,c,k,f,a,x)] for b in B for i in I for x in X] )
                                      >= sum([vP[(b,i,c,k,f,a+1, x)] for b in B for i in I for x in X]))
                 for k in K for f in F for c in C for a in A[:-1] }

        # Assure only one container per position
        # \sum_b \sum_i P_{b i k c f a}<= 1 \quad \forall a, k , c ,f
        RPosicion={(a,k,c,f): model.Add(sum([vP[(b,i,c,k,f,a,x)] for b in B for i in I for x in X]) <= 1)
                   for a in A for k in K for c in C for f in F }

        # Assure one container its by side of another container
        # \sum_b \sum_i P_{b i k c f a} \geq \sum_b \sum_i P_{b i k ,c+1 , f a}
        RColumnas={(k,c,f): model.Add(sum([vP[(b,i,c,k,f,1, x)] for b in B for i in I for x in X])
                                        >= sum([vP[(b,i,c+1,k,f,1,x )] for b in B for i in I for x in X]))
                   for k in K for c in C[:-1] for f in F }

        # Assure all products are transported
        # \sum_a \sum_c \sum_f \sum_k \sum_b \sum_i P_{b i k c f a}=\sum_k \sum_b \sum_i M_{i k t b}
        RCantidad={ (b,i) : model.Add(sum([vP[(b,i,c,k,f,a,x)]  for c in C for k  in K for f in F for a in A for x in X])
                                  == sum(M[(i,k,t,b)] for k in K )) for b in B for i in I }

        # Assure the lenght of the container is not exceeded
        # \sum_b \sum_l \sum_c P_{b i k c f 1} b_l \leq k_l
        RLongitud={(k,f): model.Add(sum([vP[(b,i,c,k,f,1,x)]*l[b] for b in B for i in I for c in C for x in X]) <= kl) for k in K for f in F }

        # Assure the height of the container is not exceeded
        # \sum_b \sum_i \sum_a P_{\text {bikcfa}} b_a \leq k_h \quad \forall  k,f, c
        RAltura1={(k,f,c): model.Add(sum([vP[(b,i,c,k,f,a,x)]*bh[b] for b in B for i in I for a in A for x in X])
                                     <= kh)
                  for k in K for f in F for c in C }


        # Assure all the boxes on the on the column are the same type
        #  \sum_i P_{b i k c f a} \geq  \sum_i P_{b i k f,a+1} \forall b,k,f,c,a<|A|
        RAltura2={(b,k,f,c,a): model.Add(sum([vP[(b,i,c,k,f,a,x)] for i in I for x in X] )
                                         >= sum([vP[(b,i,c,k,f,a+1,x)] for i in I for x in X])) for b in B for k in K for f in F for c in C for a in A[:-1] }


        # Lenght at each position
        # \sum_b \sum_i \sum_a P_{b i k c f a} b_l \leq L_{k c f}
        RLongitud2={(k,f,c): model.Add(sum([vP[(b,i,c1,k,f,1,x)]*l[b] for b in B for i in I for x in X for c1 in C[:c+1]]) == vL[(k,c,f)]) for k in K for f in F for c in C}

        # Assure only one lenght per position
        # \sum_b \sum_i \sum_a P_{b i k c f a} b_l \leq L_{k c f}
        RLongitud3={(k,f,c): model.Add(sum(vR[(k,c,f,x)] for x in X) <= 1) for k in K for f in F for c in C}

        # RAltura2={(b,k,f,c,a,a1): model.Add(sum(vP[(b,i,c,k,f,a)] for i in I)== sum(vP[(b,i,c,k,f,a1)] for i in I) ) for b in B for k in K for f in F for c in C for a in A for a1 in A }
        # \sum_i \sum_b \sum_c' P_{b i k c' f 1 x} \cdot b_{i k}=L_x \cdot R_{k c f c} \quad \forall c k f


        # Assure the lenght of the container is not exceeded

        #
        RLongitud1={(k,c,f,x): model.Add(  vL[(k,c,f)] == x*vR1[(k,c,f,x)]).OnlyEnforceIf(vL1[(k,c,f,x)]) for k in K for c in C for f in F for x in X}
        # RLongitud1={(k,c,f,x): model.Add(  vL[(k,c,f)] != x*vR1[(k,c,f,x)]).OnlyEnforceIf(vL1[(k,c,f,x)].Not())for k in K for c in C for f in F for x in X}
        # RLongitud1={(k,c,f,x): model.Add( vR[(k,c,f,x)]== vL1[(k,c,f,x)]) for k in K for c in C for f in F for x in X}
        RLongitud1={(k,c,f): model.Add( sum([vL1[(k,c,f,x)]
        for x in X]) == 1)for k in K for c in C  for f in F}

        # for k in K:
        #     for c in C:
        #         for f in F:
        #             for x in X:
        #                     model.Add(vR[(k,c,f,x)]==1 if vL[(k,c,f)] == x)

        a = time()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60*2*60
        solver.parameters.relative_gap_limit = 0.005
        status = solver.Solve(model)
        print(t, status, time() - a)
        camiones = []

        # if status == cp_model.OPTIMAL:
        #     print("Optimal")
        #     print(solver.ObjectiveValue())
        #     print(solver.WallTime())
        #     print(solver.ResponseStats())
        # elif status == cp_model.FEASIBLE:
        #     print("Feasible")
        #     print(solver.ObjectiveValue())
        #     print(solver.WallTime())
        #     print(solver.ResponseStats())
        # elif status == cp_model.INFEASIBLE:
        #     print("Infeasible")
        #     print(solver.WallTime())
        #     print(solver.ResponseStats())
        # else:
        #     print("No solution found")

        # Print lenght of columns
        print("Longitud de columnas", X[-1])
        for k in K:
            for f in F:
                for c in C:
                          camiones+=[solver.Value(vP[(b,i,c,k,f,a,x)]) for b in B for i in I for a in A for x in X]
                          print(k,sum(solver.Value(vP[(b,i,c1,k,f,1,x)])*l[b] for b in B for i in I for c1 in C[:c+1] for x in X),[sum(solver.Value(vP[(b,i,c,k,f,a,x)]) for b in B for i in I for x in X) for a in A])
        print(sum(camiones))
        print("Cantidad por camiones")
        for k in K:
            print(k, sum(solver.Value(vP[(b,i,c,k,f,a,x)]) for b in B for i in I for c in C for f in F for x in X for a in A))
        print(sum(M[(i,k,t,b)] for i in I for k in K for b in B))
        print("Cantidad por L")

        # for k in K:
        #     for f in F:
        #         for c in C:
        #             # print(k,f,c,solver.Value(vL[(k,c,f)]) in X, solver.Value(vL[(k,c,f)]), sum(solver.Value(vR[(k,c,f,x)]) for x in X))
        #             print(k,f,c,solver.Value(vL[(k,c,f)]),
        #                   "vL1",[ x*solver.Value(vL1[(k,c,f,x)])  for x in X if solver.Value(vL1[(k,c,f,x)])==1],
        #                   "VR1",[ x*solver.Value(vR1[(k,c,f,x)])  for x in X if solver.Value(vR1[(k,c,f,x)])==1] )
        # print("Siguiente t")
    return 2

if __name__ == '__main__':
    update_data()