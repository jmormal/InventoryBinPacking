from ortools.sat.python import cp_model
import pandas as pd
import time
import random
import shutil
import datetime
import os
from time import perf_counter as time

def update_data(default_time=60, default_days=True):
    path = os.getcwd()

    path=r"C:\Users\jmormal\PycharmProjects\pythonProject1"
    path1=r"C:\Users\jmormal\PycharmProjects\pythonProject1"
    os.chdir(path)
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
    now = datetime.datetime.now()
    wd= os.getcwd()+"\output"
    path=wd+"\{}{}{}_s{}".format(now.day, now.month, now.year, now.minute)
    os.makedirs(path, exist_ok=True )
    random.seed(0)

    ##

    pd_productos=pd.read_csv(path1+"\datasets\Productos.csv")
    pd_demanda =pd.read_csv(path1+"\datasets\Demanda.csv")

    # print("Demanda", pd_demanda)

    # print(pd_productos)


    productos=pd_productos["i"].tolist()
    if default_days==True:
        dias = pd_demanda["t"].unique().tolist()
    else:
        dias = list(range(1, default_days+1))
    CosteStock={}
    stockInicial={}
    piezascont={}
    piezas_largo_box={}
    for row in pd_productos.itertuples():
        CosteStock.update({row.i:1})
        stockInicial.update({row.i:row.Stock})
        piezascont.update({row.i:row.piezascont})
        piezas_largo_box.update({row.i:row.Largo})





    # Extract demand from demanda dataframe
    demanda={}
    for row in pd_demanda.itertuples():
        demanda.update({(row.i,row.t):row.Demanda})

    num_col_camion = 2
    dias_stock_cobertura = 3
    camiones=list(range(10))

    model = cp_model.CpModel()
    vCantidadPedir = {(i,c,t):model.NewIntVar(0, 2000, "x") for i in productos for c in camiones for t in dias}
    vStock = {(i,t):model.NewIntVar(0, 200000, "x") for i in productos for t in dias}
    vY = {(c,t):model.NewIntVar(0, 1, "x") for c in camiones for t in dias}
    vA = {(c,t):model.NewIntVar(0, 20, "x") for c in camiones for t in dias}
    vB = {(c,t):model.NewIntVar(0, 20, "x") for c in camiones for t in dias}

    # Minimize sum(10000*model.Y[c,t]  for c in model.c for t in model.t)

    model.Minimize(sum(17*2*(dias_stock_cobertura+1)*len(dias)*len(productos)*pd_productos["Stock"].max()*vY[c,t]  for c in camiones for t in dias))
                   # +sum(demanda[(i,t)]+num_col_camion*
                   #     sum(vCantidadPedir[(i,c,t)]*piezascont[i] for c in camiones) for i in productos for t in dias))
    #+sum(CosteStock[i]*vStock[i,t] for i in productos for t in dias))



    # STOOOOCKS
    rStocks1={(i):model.Add(vStock[(i,1)]==stockInicial[i]-demanda[(i,1)]
                       +num_col_camion*sum(vCantidadPedir[(i,c,1)]for c in camiones)*piezascont[i]  ) for i in productos}



    rStocks={(i,t):model.Add(vStock[(i,t)]==vStock[(i,t-1)]-demanda[(i,t)]+num_col_camion*
                       sum(vCantidadPedir[(i,c,t)]*piezascont[i] for c in camiones)) for i in productos for t in dias[1:]}



    rDimensionesCamion={(c,t):model.Add(13600*vY[c,t]>=(vA[c,t]*1600+vB[c,t]*1000)) for c in camiones for t in dias}



    rCajasTotales={(c,t):
                       model.Add(
                           sum(vCantidadPedir[(i,c,t)] for i in productos)<=(vA[c,t]*4+vB[c,t]*3))
        for c in camiones for t in dias}



    rCajasTipoA={(c,t):
                     model.Add(
                         sum(vCantidadPedir[(i,c,t)]*float(int(piezas_largo_box[i])==int(1600)) for i in productos)<=(vA[c,t]*4))
        for c in camiones for t in dias}

    rCargaMaxima={}
    for c in camiones:
        for t in dias:
            for caja in range(2):
                if caja==0:
                    rCargaMaxima.update({(c,t,caja):model.Add(sum(vCantidadPedir[(i,c,t)] for i in productos if int(piezas_largo_box[i])==int(1600))==4*vA[c,t])})
                else:
                    rCargaMaxima.update({(c,t,caja):model.Add(sum(vCantidadPedir[(i,c,t)] for i in productos if int(piezas_largo_box[i])==int(1000))==3*vB[c,t])})




    rCajasTipoB={(c,t):model.Add(sum(vCantidadPedir[(i,c,t)]*float(int(piezas_largo_box[i])==int(1000)) for i in productos)<=(vB[c,t]*3)) for c in camiones for t in dias}
    stock_seguridad = []
    l1={i:0 for i in productos}
    for i in productos:
        for t in dias[:len(dias)-dias_stock_cobertura]:
            model.Add(vStock[(i,t)]>=sum(demanda[(i,t2)] for t2 in dias[t:t+dias_stock_cobertura]))
            # print(sum(demanda[(i,t2)] for t2 in dias[t:t+dias_stock_cobertura]))
            stock_seguridad.append([i,t,sum(demanda[(i,t2)] for t2 in dias[t:t+dias_stock_cobertura])])
        l1[i]=sum(demanda[(i,t2)] for t2 in dias[t:t+dias_stock_cobertura])
    print(productos)
    print(l1)
    for i in productos:
        for t in dias[len(dias)-dias_stock_cobertura:]:
            model.Add(vStock[(i,t)]>=l1[i])
            stock_seguridad.append([i,t,l1[i]])
    df_stock_seguridad = pd.DataFrame(stock_seguridad,columns=["Producto","Dia","Stock_seguridad"])
    df_stock_seguridad.to_csv(path1+"\output\lastsol\stock_seguridad.csv",index=False)


    rCVolumenminimo={(c,t):model.Add(num_col_camion*(sum(vCantidadPedir[i,c,t] for i in productos if int(piezas_largo_box[i])==int(1600))*750*1200*1600
            +(sum(vCantidadPedir[i,c,t] for i in productos if int(piezas_largo_box[i])==int(1000)))*1000*1000*1200)
                                     >=vY[c,t]*int(0.93*(3000*2400*13600))) for c in camiones for t in dias}


    a=time()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 120
    # solver.parameters.absolute_gap_limit  = (dias_stock_cobertura+1)*len(dias)*len(productos)*pd_productos["Stock"].max()-1

    # solver.parameters.relative_gap_limit = 0.005
    status = solver.Solve(model)
    print(status, time()-a)
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Optimal solution found")
        print("Objective value:", solver.ObjectiveValue())
        # Print sum of trucks
        print("Sum of trucks:", sum(solver.Value(vY[c,t]) for c in camiones for t in dias))
        # Print relative gap
        print("Relative gap:", (solver.BestObjectiveBound() - solver.ObjectiveValue())/ solver.ObjectiveValue())



    CamionesDia=[]
    for t in dias:
        CamionesDia.append(sum(solver.Value(vY[c,t]) for c in camiones))
    df_CamionesDia=pd.DataFrame(CamionesDia,columns=["CamionesDia"])
    df_CamionesDia.to_csv(path1+"\CamionesDia.csv")
    df_CamionesDia.to_csv(wd+"\CamionesDia.csv")

    stock=[]
    for t in dias:
        for i in productos:
            stock.append([t,i, solver.Value( vStock[i,t])])
    df_stock=pd.DataFrame(stock,columns=["t","id","Stock"])
    df_stock.to_csv(path1+"\Stock.csv")
    df_stock.to_csv(wd+"\Stock.csv")



    cantidadpedir_acu=[]
    for t in dias:
        pro=[]
        for i in productos:
            pro.append(sum(solver.Value(vCantidadPedir[i,c,t1]) for c in camiones for t1 in dias[0:t+1]))
        cantidadpedir_acu.append(pro)


    df_cantidadpedir_acu=pd.DataFrame(cantidadpedir_acu, columns=[str(i) for i in productos])
    # df_cantidadpedir_acu["2"]
    df_cantidadpedir_acu.to_csv(path1+"\CantidadPedirAcumulado.csv")
    df_cantidadpedir_acu.to_csv(wd+"\CantidadPedirAcumulado.csv")

    now = datetime.datetime.now()
    wd= os.getcwd()+"\output"
    path=wd+"\{}{}{}_s{}".format(now.day, now.month, now.year, now.minute)
    os.makedirs(path, exist_ok=True )
    wd=wd+"\lastsol"
    os.makedirs(wd, exist_ok=True )

    # Save cantidad_pedir by day, truck and product
    cantidad_pedir=[]
    for t in dias:
        for c in camiones:
            for i in productos:
                cantidad_pedir.append([t,c,i, solver.Value(vCantidadPedir[i,c,t])])
    df_cantidad_pedir=pd.DataFrame(cantidad_pedir,columns=["t","c","producto","CantidadPedir"])
    df_cantidad_pedir.to_csv(path1+"\CantidadPedir.csv")
    df_cantidad_pedir.to_csv(wd+"\CantidadPedir.csv")

    # Save numbers of trucks by day
    CamionesDia=[]
    for t in dias:
        CamionesDia.append(sum(solver.Value(vY[c,t]) for c in camiones))
    df_CamionesDia=pd.DataFrame(CamionesDia,columns=["CamionesDia"])
    df_CamionesDia.to_csv(path+"\CamionesDia.csv")
    df_CamionesDia.to_csv(wd+"\CamionesDia.csv")

    # Save stock by day and product
    stock=[]
    for t in dias:
        for i in productos:
            stock.append([t,i, solver.Value( vStock[i,t])])
    df_stock=pd.DataFrame(stock,columns=["t","product","Stock"])
    df_stock.to_csv(path1+"\Stock.csv")
    df_stock.to_csv(wd+"\Stock.csv")

    # Save demand by day and product
    demanda1=[]
    for t in dias:
        for i in productos:
            demanda1.append([t,i, demanda[(i,t)]])
    df_demanda=pd.DataFrame(demanda1,columns=["t","id","Demanda"])
    df_demanda.to_csv(path1+"\Demanda.csv")
    df_demanda.to_csv(wd+"\Demanda.csv")


    # save the model
    sol_camiones_total=[]
    for t in dias:
        k1=0
        for c in camiones:
            sol_dia = []

            if solver.Value(vY[c, t]) == 1:
                k1=k1+1
                for i in productos:
                    ## if the product is in the truck
                    if solver.Value(vCantidadPedir[i, c, t]) > 0:
                        ## product, vA, vB
                        sol_dia.append([i,solver.Value(vCantidadPedir[(i,c,t)]), solver.Value(vA[(c,t)]), solver.Value(vB[(c,t)]), piezas_largo_box[i]])
                        sol_camiones_total.append([t,k1,i,solver.Value(vCantidadPedir[(i,c,t)]), solver.Value(vA[(c,t)]), solver.Value(vB[(c,t)]),
                                                   piezas_largo_box[i],

                                                   2*((sum(solver.Value(vCantidadPedir[i,c,t]) for i in productos if int(piezas_largo_box[i])==int(1600))*750*1200*1600
            +(sum(solver.Value(vCantidadPedir[i,c,t]) for i in productos if int(piezas_largo_box[i])==int(1000)))*1000*1000*1200)
            /(3000*2400*13600))])
                df_sol_dia=pd.DataFrame(sol_dia, columns=["id","Products","vA","vB","LargoBox"])
                df_sol_dia.to_csv(path+"\CantidadPedirDia{}Camion{}.csv".format(t,k1))
                df_sol_dia.to_csv(wd+"\CantidadPedirDia{}Camion{}.csv".format(t,k1))
    df_sol_camiones_total=pd.DataFrame(sol_camiones_total, columns=["t","c","id","Products","vA","vB","LargoBox", "Volumen"])
    df_sol_camiones_total.to_csv(path+"\CantidadPedirTotal.csv")
    df_sol_camiones_total.to_csv(wd+"\CantidadPedirTotal.csv")
    print(wd+"\CantidadPedirTotal.csv")


    # Print the total number of containers with length 1600 and 1000

    print("Total number of containers with length 1600: ", sum(2*solver.Value(vCantidadPedir[i,c,t]) for i in productos for c in camiones for t in dias if int(piezas_largo_box[i])==int(1600)))
    print("Total number of containers with length 1000: ", sum(2*solver.Value(vCantidadPedir[i,c,t]) for i in productos for c in camiones for t in dias if int(piezas_largo_box[i])==int(1000)))


    return 2

if __name__ == '__main__':
    update_data(default_time=500)