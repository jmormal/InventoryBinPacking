from Fabricas import Factory
import time
import rectpack as rp
import datetime
import os
import shutil
import pandas as pd
class Solver():
    def __init__(self):
        pass
    def solve(self, path=None, folder="default", now=datetime.datetime.now(), planning_days=10, alpha=0.9, rows=3):

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
            wd = os.getcwd() + "\output"
            path_save = wd + "\{}-{}-{}".format(now.day, now.month, now.year)
            path_save = path_save + "\\" + folder
            print("path_save with folder", path_save)
            print("current path", os.getcwd())
            os.makedirs(path_save, exist_ok=True, )
            print("current path", os.getcwd())

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


        ListOfSortingAlgorithms=[
            rp.MaxRectsBl,
            rp.MaxRectsBssf,
            rp.MaxRectsBaf,
            rp.MaxRectsBlsf,
            # rp.SkylineBl,
            # rp.SkylineBlWm,
            # rp.SkylineMwf,
            # rp.SkylineMwfl,
            # rp.SkylineMwfWm,
            # rp.SkylineMwflWm,
            # rp.GuillotineBssfSas, #Bueno
            # rp.GuillotineBssfLas,
            # rp.GuillotineBssfSlas,
            # rp.GuillotineBssfLlas, #Bueno
            # rp.GuillotineBssfMaxas,
            # rp.GuillotineBssfMinas,
            # rp.GuillotineBlsfSas,
            # rp.GuillotineBlsfLas,
            # rp.GuillotineBlsfSlas,
            # rp.GuillotineBlsfLlas,
            # rp.GuillotineBlsfMaxas,
            # rp.GuillotineBlsfMinas,
            # rp.GuillotineBafSas,
            # rp.GuillotineBafLas,
            # rp.GuillotineBafSlas,
            # rp.GuillotineBafLlas,
            # rp.GuillotineBafMaxas,
            # rp.GuillotineBafMinas,

        ]

        PresortList=[
        rp.SORT_NONE,
        rp.SORT_AREA,
        rp.SORT_PERI,
        rp.SORT_DIFF,
        rp.SORT_SSIDE,
        rp.SORT_LSIDE,
        rp.SORT_RATIO,
        ]

        a=time.time()

        F1=Factory("One")
        F1.SetTypeOfContainers(r"{}\Dimensiones_Contenedores.csv".format(path))
        F1.AddAllProducts(r"{}\Productos.csv".format(path))
        F1.SetDemand(r"{}\Demanda.csv".format(path))
        F1.SetSumDemandPerProduct()
        F1.SetAvaibleTrucks(r"{}\Dimensiones_Camiones.csv".format(path))

        F1.ListRectangles = []
        F1.maxSimTime= F1.GetMaxSimTime()
        for _ in range(F1.maxSimTime):
            F1.SetProyectedStock()
            F1.SetBoxesTobeLoaded()
            while any(value > 0 for value in F1.NumberOfPlantBoxType.values()):
                F1.max_utilization = 0
                for SortingAlgorithm in ListOfSortingAlgorithms:
                    for presort in PresortList[:1]:
                        for _ in range(10000):
                            F1.SetTemporaryProyectedStockWithoutTransport()
                            F1.SetBottomDistribution(SortingAlgorithm=SortingAlgorithm, PreSort=presort,)
                            if F1.TotalUtilization ==1:
                                break

                        if F1.TotalUtilization ==1:
                            break
                    if F1.TotalUtilization ==1:
                        break
                F1.TotalUtilization = 0
                F1.bins.append(F1.bin)
                F1.ListRectangles = []
                F1.UpdateNumberOfPlantBoxType()


            # print Stock

            F1.AssignContainersToTrucks()
            F1.UpdateStock()
            F1.Time+=1
            F1.bins=[]
        print(sum(b.utilization for b in F1.bins))
        print(F1.Products[0].Name)
        print(time.time()-a)
        print(len(F1.AllTrucks))
        F1.SaveResults(path_save)
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    solver = Solver()
    solver.solve(path=r"C:\Users\Juan\PycharmProjects\pythonProject1\datasets\Escenario1")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
