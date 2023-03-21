#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import pyomo.environ as pe
import pyomo.opt as po
model = pe.ConcreteModel("Cargacamiones")
import random
import sys
import pickle
random.seed(0)

def main():
    file = open("v.obj", 'rb')
    productos,familias,camiones,dias, dias1 ,columnas,A1,B1 = pickle.load(file)
    file.close()
    print(columnas)
    print(len(camiones))
    columnas=[1]
    model.i = pe.Set(initialize=productos)
    model.f = pe.Set(initialize=familias)
    model.c = pe.Set(initialize=camiones)
    model.t = pe.Set(initialize=dias)
    model.t1 = pe.Set(initialize=dias1)
    model.col=pe.Set(initialize=columnas)
    model.A1=pe.Set(initialize=A1)
    model.B1=pe.Set(initialize=B1)
    print(list(model.f))


    # ## Carga de datos productos



    L=78
    nu=26/30
    NT_lw=5
    NT_up=10


    file = open("v1.obj", 'rb')
    lotepedido,CosteStock,piezascont,piezas_largo_box,b,demanda,stockInicial,valor,PC,L,nu,NT_lw,NT_up,piezas_largo_box,CosteStock = pickle.load(file)
    file.close()
    for i in demanda:
        demanda[i]=int(demanda[i]/2)
    print(demanda)
    k=0
    for i in CosteStock:
        CosteStock[i]=2+k
        k=k+1
    model.LotePedido = pe.Param(model.f , initialize=lotepedido)
    model.PiezasCont= pe.Param(model.i ,initialize=piezascont)
    model.b= pe.Param(model.i, model.f ,initialize=b, default=0)
    model.StockInicial= pe.Param(model.i, initialize=stockInicial)
    model.demanda= pe.Param(model.i, model.t1,  initialize=demanda)
    model.valor=pe.Param(model.i, initialize=stockInicial)
    model.PC=pe.Param(model.c, initialize=PC)
    model.L=pe.Param(initialize=L)
    model.nu=pe.Param(initialize=nu)
    model.NT_lw=pe.Param(initialize=NT_lw)
    model.NT_up=pe.Param(initialize=NT_up)
    model.LargoCont=pe.Param(model.i,initialize=piezas_largo_box)
    # model.CS=pe.Param(model.i, initialize=CosteStock)





    model.CantidadPedir = pe.Var(model.i, model.c, model.t,model.col, domain=pe.Integers)



    model.CantidadPedir2 = pe.Var(model.i,model.f, model.c, model.t,model.col, domain=pe.Integers, bounds=(0,None) )
    model.ContenedoresCamion=pe.Var(model.c,model.t,model.col,model.i, domain=pe.Integers)


    model.Stock=pe.Var(model.i,model.t, bounds=(0,None))


    model.RetrasoDemanda=pe.Var(model.i,model.t, bounds=(0,None))



    model.K=pe.Var(model.f,model.c,model.t,model.col ,domain=pe.Integers)



    model.Y=pe.Var(model.c,model.t ,domain=pe.Binary, initialize=0)



    model.A=pe.Var(model.c,model.col,model.t, domain=pe.Integers, bounds=(0,4.5))
    model.B=pe.Var(model.c,model.col, model.t, domain=pe.Integers, bounds=(0,12.5))
    # model.A=pe.Var(model.c,model.col,model.t, domain=pe.Integers, bounds=(0,13))
    # model.B=pe.Var(model.c,model.col, model.t, domain=pe.Integers, bounds=(0,13))


    # ## Función Objetivo
    # Minimizar el número de camiones usado
    # $$\sum_{c,t}PC(c)Y(c,t)+ \sum CS(i)Stock(i,t)$$


    expr = sum(10000*model.Y[c,t]  for c in model.c for t in model.t)


    # In[34]:
    print(list(model.col))

    #Coste Transporte
    model.objective = pe.Objective(sense=pe.minimize, expr=expr)


    # ## Funciones auxiliares


    # ## Restricciones


    model.stocks=pe.ConstraintList()


    # $$Stock(i,t)=Stock(i,t-1)+\sum_{c,col}CantidadPedir(i,c,t,col)PiezasCont[i] -Demanda(i,t)$$

    for i in model.i:
            lhs=model.Stock[i,1]
            rhs=model.StockInicial[i]-model.demanda[i,1]+sum(model.CantidadPedir[i,c,1,col]*model.PiezasCont[i] for c in model.c for col in model.col )
            model.stocks.add(lhs==rhs)



    for t in list(model.t)[1:]:
        for i in model.i:
                lhs=model.Stock[i,t]
                rhs=model.Stock[i,t-1]-model.demanda[i,t]+sum(model.CantidadPedir[i,c,t,col]*model.PiezasCont[i] for c in model.c for col in model.col)
                model.stocks.add(lhs==rhs)



    model.RcantidadPedir=pe.ConstraintList()


    # $$CantidadPedir2_{i,f,c,t,col}=K(f,c,t,col)*LotePedido(f)*b(i,f)$$

    # In[42]:


    for i in model.i:
        for f in model.f:
            for c in model.c:
                for t in model.t:
                    for col in model.col:
                        lhs=model.CantidadPedir2[i,f,c,t,col]
                        rhs=model.K[f,c,t,col]*model.LotePedido[f]*model.b[i,f]
                        model.RcantidadPedir.add(lhs==rhs)


    # In[43]:


    model.RcantidadPedir2=pe.ConstraintList()


    # $$CantidadPedir_{i,c,t,col}= \sum_f CanitdadPedir2(i,f,c,t,col)$$



    for i in model.i:
        for c in model.c:
            for t in model.t:
                for col in model.col:
                    lhs=model.CantidadPedir[i,c,t,col]
                    rhs=sum(model.CantidadPedir2[i,f,c,t,col] for f in model.f)
                    model.RcantidadPedir2.add(lhs==rhs)




    model.RDimensionesCamion=pe.ConstraintList()


    # $$ 1600A_{c,col,t} +1000B_{c,col,t}   \leq 13600* Y[c,t]$$


    for c in model.c:
        for t in model.t:
            for col in model.col:
                lhs=13600*model.Y[c,t]
                rhs=(model.A[c,col,t]*1600+model.B[c,col,t]*1000)
                model.RDimensionesCamion.add(lhs>=rhs)



    model.RCajasTotales=pe.ConstraintList()


    # $$ \forall c \in C \quad \forall t \in T \quad \sum_i CantidadPedir(i,c,t,col) \leq A_{c,col,t}*4+B_{c,col,t}*3 $$



    for c in model.c:
        for t in model.t:
            for col in model.col:
                lhs=sum(model.CantidadPedir[i,c,t,col] for i in model.i)
                rhs=(model.A[c,col,t]*4+model.B[c,col,t]*3)
                model.RCajasTotales.add(lhs<=rhs)




    model.RCajasTipoA=pe.ConstraintList()



    for c in model.c:
        for t in model.t:
            for col in model.col:
                lhs=sum(model.CantidadPedir[i,c,t,col]*float(int(model.LargoCont[i])==int(1600)) for i in model.i)
                rhs=model.A[c,col,t]*4
                model.RCajasTipoA.add(lhs<=rhs)




    model.RCajasTipoB=pe.ConstraintList()



    for c in model.c:
        for t in model.t:
            for col in model.col:
                lhs=sum(model.CantidadPedir[i,c,t,col]*float(int(model.LargoCont[i])==int(1000)) for i in model.i)
                rhs=model.B[c,col,t]*3
                model.RCajasTipoB.add(lhs<=rhs)



    # $$\forall i,t  \quad Stock[i,t]\geq \sum_{j \in [1,2,3,4]} Demanda[i,t+j]$$

    model.RCobertura=pe.ConstraintList()
    l=list(range(25))
    for i in model.i:
        for t in range(1,19-3):
            lhs=model.Stock[i,t]
            #rhs=(model.demanda[i,t+1]+model.demanda[i,t+2]+model.demanda[i,t+3])
            rhs=0

            model.RCobertura.add(lhs>=rhs)
            l[i]=rhs
    for i in model.i:
        for t in range(19-3,19):
            lhs=model.Stock[i,t]

            #rhs=l[i]
            rhs=0

            model.RCobertura.add(lhs>=rhs)



    model.RCVolumenminimo=pe.ConstraintList()




    for t in model.t:
        for c in model.c:
            lhs=(sum(model.CantidadPedir[i,c,t,col] for i in model.i for col in model.col if int(model.LargoCont[i])==int(1600))*750*1200*1600+
                                         +(sum(model.CantidadPedir[i,c,t,col] for i in model.i for col in model.col if int(model.LargoCont[i])==int(1000)))*1000*1000*1200)/(3000*2400*13600)
            rhs=0.48*model.Y[c,t]
            model.RCVolumenminimo.add(lhs >= rhs)


    # model.estabilidad=pe.ConstraintList()
    # for t in range(2 , 17):
    #     lhs=(sum(model.Y[c,t] for c in model.c))-(sum(model.Y[c,t-1] for c in model.c))
    #     rhs=1
    #     model.estabilidad.add(lhs <= rhs)
    # # In[57]:
    #
    # for t in range(2 , 17):
    #     lhs=(-sum(model.Y[c,t] for c in model.c))+(sum(model.Y[c,t-1] for c in model.c))
    #     rhs=1
    #     model.estabilidad.add(lhs <= rhs)
    # model.bounds=pe.ConstraintList()
    # for i in model.i:
    #     for t in model.t:
    #         model.bounds.add(model.Stock[i,t]>=0)

    #
    # solver = po.SolverFactory("gurobi")
    # solver.options["TimeLimit"]=60
    # # solver.options["MIPFocus"] = 0
    # solver.options["MIPGap"] = 0.01
    # results = solver.solve(model, tee=True)

    #
    # solvername='glpk'
    # solverpath_exe=r"C:\Users\jmormal\Downloads\cbc-win64\cbc.exe"
    # solverpath_exe=r"C:\Users\jmormal\Downloads\winglpk-4.65 (1)\glpk-4.65\w64\glpsol.exe"
    # # solverpath_exe=r"C:\Users\jmormal\Downloads\Cbc-2.10-x86_64-w64-mingw32-dbg (1)\bin"
    #
    solver = po.SolverFactory("cbc")
    # solver.options["parallel/maxnthreads"]=32
    # solver.options["parallel/minnthreads"]=5

    # # solver.options["MIPFocus"] = 0
    # solver.options["MIPGap"] = 0.01
    solver.options["seconds"]=60*10*30
    solver.options["threads"]=30
    #
    # # solvername='cbc'
    # solverpath_exe=r"C:\Users\jmormal\Downloads\cbc-win64\cbc.exe"
    # # solverpath_exe=r"C:\Users\jmormal\Downloads\Cbc-2.10-x86_64-w64-mingw32-dbg (1)\bin"
    #
    # solver = po.SolverFactory(solvername,executable=solverpath_exe)
    # # solver.options["TimeLimit"]=60
    # # # solver.options["MIPFocus"] = 0
    # # solver.options["MIPGap"] = 0.01
    # solver.options = {'sec': 100}
    results = solver.solve(model,tee=True)




    print(results)


    def mean(x):
        return sum(x)/len(x)




    df2=pd.DataFrame(l1,columns=["t","id","Stock","Demanda Proximos Dias","Diferencia Demanda"])
    pd.set_option('display.max_rows', None)
    df2



    CamionesDia=[]
    for t in model.t:
        CamionesDia.append(sum(model.Y[c,t].value for c in model.c))
    df_CamionesDia=pd.DataFrame(CamionesDia,columns=["CamionesDia"])
    df_CamionesDia.to_csv("CamionesDia.csv")



    stock=[]
    for t in model.t:
        for i in model.i:
            stock.append([t,i,model.Stock[i,t].value])
    df_stock=pd.DataFrame(stock,columns=["t","id","Stock"])
    df_stock.to_csv("Stock.csv")




    df2.loc[df2["id"]==1]["t"]


    cantidadpedir_pro=[]
    for t in model.t:
        pro=[]
        for i in model.i:
            pro.append(sum(model.CantidadPedir[i,c,t,col].value  for c in model.c for col in model.col))
        cantidadpedir_pro.append(pro)
    df_cantidadpedir_pro=pd.DataFrame(cantidadpedir_pro,columns=[str(i) for i in model.i])




    df_cantidadpedir_pro.to_csv("CantidadPedir.csv")



    cantidadpedir_acu=[]
    for t in model.t:
        pro=[]
        for i in model.i:
            pro.append(sum(model.CantidadPedir[i,c,t1,col].value  for c in model.c for col in model.col for t1 in list(model.t)[0:t]))
        cantidadpedir_acu.append(pro)




    df_cantidadpedir_acu=pd.DataFrame(cantidadpedir_acu, columns=[str(i) for i in model.i])
    df_cantidadpedir_acu["2"]
    df_cantidadpedir_acu.to_csv("CantidadPedirAcumulado.csv")





if __name__== '__main__':
    main()