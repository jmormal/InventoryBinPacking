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
    C=list(range(14))
    F=[1]
    kh=3000
    mkh={1:3,2:4}
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
        vP = {(b,i,c,k,f,x): model.NewIntVar(0, 6, "x") for b in B for i in I for c in C for k in K for f in F for x in X}
        vR= {(k,c,f): model.NewIntVar(0, 1, "y") for k in K for c in C for f in F for x in X}
        vR1= {(k,c,f,x): model.NewIntVar(0, 1, "y") for k in K for c in C for f in F for x in X}
        vL={(k,c,f): model.NewIntVar(0, 13610, "x") for k in K for c in C for f in F }
        vL1={(k,c,f,x) : model.NewBoolVar("x") for k in K for c in C for f in F for x in X}
        vA={(b,k,f,c): model.NewIntVar(0, 1, "x") for b in B for k in K for f in F for c in C}

        print(len(vP))
        # Objective function (minimize the number of boxes)
        model.Minimize(sum(vP[b,i,c,k,f,x]*u[x]*P[b,i] for b in B for i in I for c in C for k in K for f in F for x in X))
        # model.Minimize(sum(vR[k,c,f,x]*u[x] for k in K for c in C for f in F for x in X))

        # Assure all products are transported
        # \sum_a \sum_c \sum_f \sum_k \sum_b \sum_i P_{b i k c f a}=\sum_k \sum_b \sum_i M_{i k t b}
        RCantidad={ (b,i) : model.Add(sum([vP[(b,i,c,k,f,x)]  for c in C for k  in K for f in F for x in X])
                                  == sum(M[(i,k,t,b)] for k in K )) for b in B for i in I }



        # \sum_i \sum_x P_{bikcfx}=A_{bkfc}\left\lfloor\frac{k_h}{b_h}\right\rfloor  \quad \forall bkfc

        RCapacidad={(b,k,f,c): model.Add(sum([vP[(b,i,c,k,f,x)] for i in I for x in X]) <= vA[(b,k,f,c)]*mkh[b]) for b in B for k in K for f in F for c in C}


        #     \sum_b A_{bkfc}\leq 1 \quad \forall kfc
        rA = {(k,f,c): model.Add(sum([vA[(b,k,f,c)] for b in B]) <= 1) for k in K for f in F for c in C}


        # R_{kfc} = \sum_b A_{bkfc} \quad \forall kfc
        rR = {(k,f,c): model.Add(sum([vA[(b,k,f,c)] for b in B]) == vR[(k,c,f)]) for k in K for f in F for c in C}

        # R_{kcf} \geq R_{k,c+1,f} \quad \forall kcf
        rR1 = {(k,f,c): model.Add(vR[(k,c,f)] >= vR[(k,c+1,f)]) for k in K for f in F for c in C if c < len(C)-1}

        #     L_{kcf}= \sum_x \sum_b \sum_i \sum_{c'\in \lbrace 1, \dots , c \rbrace }   A_{bkfc} b_l \quad \forall kfc
        rL = {(k,f,c): model.Add(vL[(k,c,f)] == sum([vA[(b,k,f,c1)] * l[b] for b in B for c1 in C if c1 <= c])) for k in K for f in F for c in C}

        #    L_{kcf} \leq k_l \quad \forall kfc
        rL1 = {(k,f,c): model.Add(vL[(k,c,f)] <= kl) for k in K for f in F for c in C}

        RLongitud1 = {(k, c, f, x): model.Add(vL[(k, c, f)] == x * vR1[(k, c, f, x)]).OnlyEnforceIf(vL1[(k, c, f, x)])
                      for k in K for c in C for f in F for x in X}
        # RLongitud1={(k,c,f,x): model.Add(  vL[(k,c,f)] != x*vR1[(k,c,f,x)]).OnlyEnforceIf(vL1[(k,c,f,x)].Not())for k in K for c in C for f in F for x in X}
        # RLongitud1={(k,c,f,x): model.Add( vR[(k,c,f,x)]== vL1[(k,c,f,x)]) for k in K for c in C for f in F for x in X}
        RLongitud1 = {(k, c, f): model.Add(sum([vL1[(k, c, f, x)]
                                                for x in X]) == 1) for k in K for c in C for f in F}

        a = time()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60*2*60
        solver.parameters.relative_gap_limit = 0.005
        status = solver.Solve(model)
        print(t, status, time() - a)
        camiones = []

        if status == cp_model.OPTIMAL:
            print("Optimal")
            print(solver.ObjectiveValue())
            print(solver.WallTime())
            print(solver.ResponseStats())
        elif status == cp_model.FEASIBLE:
            print("Feasible")
            print(solver.ObjectiveValue())
            print(solver.WallTime())
            print(solver.ResponseStats())
        elif status == cp_model.INFEASIBLE:
            print("Infeasible")
            print(solver.WallTime())
            print(solver.ResponseStats())
        else:
            print("No solution found")

        #Print lenght of columns
        print("Longitud de columnas", X[-1])
        for k in K:
            for f in F:
                for c in C:
                          camiones+=[solver.Value(vP[(b,i,c,k,f,x)]) for b in B for i in I for x in X]
                          print(k, solver.Value(vL[(k,c,f)]),[sum(solver.Value(vP[(b,i,c,k,f,x)]) for b in B for i in I for x in X)])
        print(sum(camiones))
        print("Cantidad por camiones")
        for k in K:
            print(k, sum(solver.Value(vP[(b,i,c,k,f,x)]) for b in B for i in I for c in C for f in F for x in X))
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