import os
import pandas as pd
from Heuristica.Productos import Product
from Heuristica.Contenedores import Container
from copy import copy, deepcopy
from Heuristica.Trucks import Truck
import rectpack as rp
import random
import numpy as np

def shuffle_beta(lst, alpha, beta):
    """
    Shuffle a list according to a beta distribution.
    Args:
    lst: A list of elements to be shuffled.
    alpha: The alpha parameter of the beta distribution.
    beta: The beta parameter of the beta distribution.
    Returns:
    A new list with the same elements as the input list, but shuffled according to a beta distribution.
    """
    n = len(lst)
    weights = np.random.beta(alpha, beta, n)
    indices = np.argsort(weights)
    return [lst[i] for i in indices]

class Factory():
    def __init__(self, Name):
        self.Name=Name
        self.Time=0
        self.Products=[]
        self.max_utilization=0
        self.bins=[]
        self.AllTrucks=[]
        self.AllContainers=[]
        self.dicc_stocks={}
        self.diccSumDemandPerProduct={}

    def SetTypeOfContainers(self, path):
        df = pd.read_csv(path)
        self.dicc_containers = {}

        # The header of df is id,Length,Width,Heigth
        for row in df.itertuples():
            self.dicc_containers[row.id] = Container(row.id, row.Length, row.Width, row.Heigth)

    def SetAvaibleTrucks(self, path, number_of_trucks=1):
        df = pd.read_csv(path)
        self.dicc_trucks = {}

        # The header of df is id,Length,Width,Heigth

        for row in df.itertuples():
            for i in range(number_of_trucks):
                self.dicc_trucks[str(row.id) + str(i)] = Truck(row.id, row.Length, row.Width, row.Heigth)


    def AddAllProducts(self, path):
        df=pd.read_csv(path)
        # The header of df is id,i,id_container,items_per_container,Stock,Days_Stock_Coverage,name_of_product,CosteStock
        self.Products=[]
        self.diccProducts={}

        for row in df.itertuples():
            # split the id_container by the character "|"
            self.Products.append(Product(row.id,row.Stock,row.name_of_product,row.Days_Stock_Coverage,row.CosteStock,row.Stock))
            for i,container in enumerate(row.id_container.split("|")):
                self.Products[-1].SetContainers(self.dicc_containers[container])
                self.Products[-1].ListOfContainers[-1].SetAttributes(int(str(row.items_per_container).split("|")[i]),row.id)
            self.diccProducts[row.id]=self.Products[-1]
        self.dicc_stocks={i:[] for i in self.diccProducts.keys()}
    def SetDemand(self, path):
        df=pd.read_csv(path)
        # The header of df is i,t,Demanda

        # Order the dataframe by t, so the demand is in order for 0 to T
        df.sort_values(by=['t'], inplace=True)

        for i in self.diccProducts.keys():
            # Create a list of demands for each product
            # Get a list of Demanda by i
            self.diccProducts[i].SetDemand(df.loc[df['i'] == i, 'Demanda'].tolist())

    def SetSumDemandPerProduct(self):
        for i in self.diccProducts.keys():
            self.diccSumDemandPerProduct[i]=sum(self.diccProducts[i].Demand[:3])

    def SetProyectedStock(self):

        for i in self.diccProducts.keys():
            self.diccProducts[i].SetProyectedStockWithoutTransport(self.Time,self.maxSimTime)

    def SetBoxesTobeLoaded(self):
        # Create a dictionary
        # key: container type
        # value: list of products that can be loaded in that container
        diccContainersToBeLoaded = {i: [] for i in self.dicc_containers.keys()}

        # while the ProyectStockWithoutTransport of each product is less than 0 loop
        while any([self.diccProducts[i].ProyectStockWithoutTransport <= 0 for i in self.diccProducts.keys()]):
            # get the product with the lowest ProyectStockWithoutTransport
            product = min(self.diccProducts.values(), key=lambda x: x.ProyectStockWithoutTransport)
            # get the container with the lowest cost
            c=deepcopy(random.choice(self.diccProducts[product.id].ListOfContainers))
            diccContainersToBeLoaded[c.type].append(c)
            # update the ProyectStockWithoutTransport of the product
            self.diccProducts[product.id].ProyectStockWithoutTransport += c.number_of_items
        self.diccContainersToBeLoaded = diccContainersToBeLoaded

        Truck_Height = self.dicc_trucks[list(self.dicc_trucks.keys())[0]].Height

        self.NumberOfPlantBoxType={i:0 for i in self.dicc_containers.keys()}
        for i in self.diccContainersToBeLoaded.keys():
            for j in range(len(self.diccContainersToBeLoaded[i])):
                if j% int(Truck_Height/self.dicc_containers[i].Height) == 0:
                    self.NumberOfPlantBoxType[i]+=1

    def UpdateNumberOfPlantBoxType(self):
        for r in self.bin:
            self.NumberOfPlantBoxType[r.rid]-=1



    def SetBottomDistribution(self, SortingAlgorithm=None, PreSort=0):

        bins = []
        for i in self.dicc_trucks.keys():
            bins.append((self.dicc_trucks[i].Length, self.dicc_trucks[i].Width))

        if random.random()<0.25 or  len(self.ListRectangles)==0:
            rectangles = []
            for i in self.diccContainersToBeLoaded.keys():
                for j in range(self.NumberOfPlantBoxType[i]):
                        rectangles.append((self.dicc_containers[i].Length, self.dicc_containers[i].Width, self.dicc_containers[i].type))
            op= " Loaded with random"
            random.shuffle(rectangles)
        else:
            rectangles = shuffle_beta(self.ListRectangles, 1,5)
            op= " Loaded with prior"
        need_rectangles = []
        RectaglesArea = sum(r[0] * r[1] for r in rectangles)
        TruckArea = sum(b[0] * b[1] for b in bins)
        if RectaglesArea / TruckArea<0.95:
            need_rectangles = rectangles
            new_rectangles = []
            # print("Print it is the last one \n")
            while RectaglesArea / TruckArea<1.5:
                product = min(
                    [x for x in self.diccProducts.values()]
                    , key=lambda x: (x.ProyectStockWithoutTransportAdded+x.ProyectStockWithoutTransport )/
                                    x.ListOfContainers[0].number_of_items)
                # product = random.choice(self.diccProducts.values())
                box = copy([y for y in product.ListOfContainers][0])

                # self.diccContainersToBeLoaded[box.type].append(box)
                product.ProyectStockWithoutTransportAdded += box.number_of_items
                Truck_Height = self.dicc_trucks[list(self.dicc_trucks.keys())[0]].Height
                i= box.type
                new_rectangles.append(
                    (self.dicc_containers[i].Length, self.dicc_containers[i].Width, self.dicc_containers[i].type))
                RectaglesArea = sum(r[0] * r[1] for r in rectangles+new_rectangles)
                current_stack=1

                while current_stack*self.dicc_containers[i].Height<Truck_Height:
                    # get a product box with the same type of the current box
                    product = min( [x for x in self.diccProducts.values() if x.ListOfContainers[0].type==box.type]
                        , key=lambda x: (x.ProyectStockWithoutTransportAdded+x.ProyectStockWithoutTransport )
                                   / x.ListOfContainers[0].number_of_items/self.diccSumDemandPerProduct[x.id])
                    # Get the box with the same type of the current box
                    box = copy([y for y in product.ListOfContainers if y.type==box.type][0])
                    # self.diccContainersToBeLoaded[box.type].append(box)
                    product.ProyectStockWithoutTransportAdded += box.number_of_items

                    current_stack += 1

            new_rectangles = shuffle_beta(new_rectangles, 1,5)
            rectangles = rectangles + new_rectangles

        # if RectaglesArea / TruckArea<0.95:
        #     # print("Print it is the last one \n")
        #     while RectaglesArea / TruckArea<0.96:
        #         i = random.choice(list(self.dicc_containers.keys()))
        #         rectangles.append(
        #         (self.dicc_containers[i].Length, self.dicc_containers[i].Width, self.dicc_containers[i].type))
        #         RectaglesArea = sum(r[0] * r[1] for r in rectangles)

        packer = rp.newPacker( pack_algo=SortingAlgorithm, sort_algo=PreSort)

        # Add the rectangles to packing queue
        for r in rectangles:
            packer.add_rect(*r)

        # Add the bins where the rectangles will be placed
        for b in bins:
            packer.add_bin(*b)

        # Start packing
        packer.pack()

        colors = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "grey", "black"]
        # Reverse the list of colors
        colors.reverse()
        box_to_color = {b: colors.pop() for b in self.dicc_containers.keys()}
        # Plot the solution
        # For each bin we will print the placed rectangles
        TotalUtilization=0
        for i, b in enumerate(packer):

            # Calculate utilization percantage
            TruckArea=b.width*b.height
            RectaglesArea=sum(r.width*r.height for r in b)
            TotalUtilization+=RectaglesArea/TruckArea
            #
            # check that all needed rectangles are in the bin#
            # Create a dictionary counting the number of rectangles of each type in the bin
            dicc_rectangles_in_bin = {r: 0 for r in self.dicc_containers}
            for r in b:
                dicc_rectangles_in_bin[r.rid] += 1
            # create a dictionary counting the number of rectangles of each type in the need_rectangles
            dicc_rectangles_in_need = { r: 0 for r in self.dicc_containers}
            for r in need_rectangles:
                dicc_rectangles_in_need[r[2]] += 1
             # Check that the number of rectangles of each type
            # in the bin is equal or greater than the number of rectangles of each type in the need_rectangles
            bool1 = all(dicc_rectangles_in_bin[k] >= dicc_rectangles_in_need[k]
                        for k in dicc_rectangles_in_need.keys()) or len(need_rectangles)==0
            if RectaglesArea/TruckArea>self.max_utilization and bool1:
                # print("porcentaje de utilizavción {}  abd the sorting Algorithm is {} and opt is by {}".
                #       format(RectaglesArea/TruckArea,SortingAlgorithm, op))
                self.max_utilization=RectaglesArea/TruckArea
                b.utilization=RectaglesArea/TruckArea
                self.bin=b
                if len(need_rectangles)==0:
                    need_rectangles=rectangles
                self.ListRectangles=need_rectangles

        # self.BreakCurrentSearch= RectaglesArea/TruckArea==1 or RectaglesArea/TruckArea==sum(r.width*r.height for r in rectangles)/TruckArea

        self.TotalUtilization=TotalUtilization
        # print(" Total {} Number of Trucks {} \n".format( TotalUtilization, len(packer)) )

    pass

    def AssignContainersToTrucks(self):
        self.ContainersLoaded= []
        self.ProductsLoaded = {i :0 for i in self.diccProducts.keys()}
        k1=-1
        # print({id1: len(l) for id1, l in self.diccContainersToBeLoaded.items()} )

        for b in self.bins:
            k1+=1
            for r in b:
                Truck_Height = self.dicc_trucks[list(self.dicc_trucks.keys())[0]].Height
                current_stack=0

                while current_stack*self.dicc_containers[r.rid].Height<Truck_Height:

                    try:
                        # print({id1: len(l) for id1, l in self.diccContainersToBeLoaded.items()})

                        box =self.diccContainersToBeLoaded[r.rid].pop()
                        # print("box {} ".format(r.rid))
                    except:
                        # print("There is no more boxes of type {} ".format(r.rid))
                        # If there are no more needed to be loaded, we create a new one
                        # Get the product that has the lowest ProyectStockWithoutTransport
                        product = min([x for x in self.diccProducts.values() if
                                       any(y.type==r.rid for y in x.ListOfContainers)]
                        , key=lambda x: x.TemporaryProyectedStock/x.ListOfContainers[0].number_of_items/self.diccSumDemandPerProduct[x.id])
                        # product = random.choice(self.diccProducts.values())

                        box = copy([y for y in product.ListOfContainers if y.type==r.rid][0])
                        product.TemporaryProyectedStock+=box.number_of_items
                    self.ContainersLoaded.append( box)
                    self.ProductsLoaded[box.product_id]+= box.number_of_items
                    box.truck = k1
                    box.x = r.x
                    box.y = r.y
                    box.z = current_stack*self.dicc_containers[r.rid].Height
                    box.Time = self.Time
                    if r.width == self.dicc_containers[r.rid].Length and r.height == self.dicc_containers[r.rid].Width:
                        box.r = 0
                    else:
                        box.r = 1
                    current_stack+=1
        self.AllTrucks+=self.bins
        self.AllContainers+=self.ContainersLoaded
        # print(self.diccContainersToBeLoaded , self.ProductsLoaded)




    def UpdateStock(self):
        for p, product in self.diccProducts.items():
            self.diccProducts[p].Stock += self.ProductsLoaded[p]-product.Demand[self.Time]
            self.dicc_stocks[p].append(self.diccProducts[p].Stock)


    def SaveResults(self,path=os.getcwd()):
        path=path+"/"
#         Create a dataframe with the following columns
#          k,t,i,b,x,y,z,r,Volume
        df = pd.DataFrame(columns=["k","t","i","b","x","y","z","r","Volume"])

        # for container in self.ContainersLoaded:
        #     df = df.append({"k":container.truck,
        #                     "t":container.Time,
        #                     "i":container.product_id,
        #                     "b":container.type,
        #                     "x":container.x,
        #                     "y":container.y,
        #                     "z":container.z,
        #                     "r":container.r,
        #                     "Volume":container.Volume
        #                    }, ignore_index=True)
        # Append is very slow, so we use a list of dictionaries
        list_of_dicts = []
        for container in self.AllContainers:
            list_of_dicts.append({"k":container.truck,
                            "t":container.Time+1,
                            "i":container.product_id,
                            "b":container.type,
                            "x":container.x,
                            "y":container.y,
                            "z":container.z,
                            "r":container.r,
                            "Volume":container.Volume
                           })
        df = df.append(list_of_dicts)

        df.to_csv(path+"TruckDistribution.csv")

        # Count the number of trucks per time
        df = pd.DataFrame(columns=["t","k"])
        list_of_dicts = []
        for truck in self.AllContainers:
            list_of_dicts.append({"t":truck.Time+1,
                            "NumberOfTrucks":truck.truck
                           })
        df = df.append(list_of_dicts)
        # Get unique values
        df = df.groupby(["t","NumberOfTrucks"]).size().reset_index(name='counts')
        # Get the number of trucks per day
        df = df.groupby(["t"]).size().reset_index(name='NumberOfTrucks')

        df.to_csv(path+"NumberOfTrucksPerDay.csv")
        # Now we are going to save the stock
        # Create a dataframe with the following columns
        # t,id,ProyectedStock
        df = pd.DataFrame(columns=["t","id","ProyectedStock"])
        list_of_dicts = []
        for product, listStocks in self.dicc_stocks.items():
            for t, stock in enumerate(listStocks):
                list_of_dicts.append({"t":t+1,
                                "id":product,
                                "ProyectedStock":stock
                               })
        df = df.append(list_of_dicts)
        df.to_csv(path+"ProyectedStock.csv")

        # Now we are going to get the NeededStock

        # Create a dataframe with the following columns
#         t,id,NeededStock

        df = pd.DataFrame(columns=["t","id","NeededStock"])
        list_of_dicts = []
        for p, products in self.diccProducts.items():
            for t, demand in enumerate(products.Demand[:self.maxSimTime]):
                if t<self.maxSimTime-products.StockCoverage  :
                    d=sum([x for x in products.Demand[t+1: t+products.StockCoverage+1]])


                list_of_dicts.append({"t":t+1,
                                "id":p,
                                "NeededStock":d
                               })

        df = df.append(list_of_dicts, ignore_index=True)
        df.to_csv(path+"NeededStock.csv")
    def SetTemporaryProyectedStockWithoutTransport(self):
        for p, product in self.diccProducts.items():
            product.SetTemporaryProyectedStockWithoutTransport()

    def GetMaxSimTime(self):
        return max([len(x.Demand) for x in self.diccProducts.values()])
def erase_some_recangles(packer):
    for _ in range(10):
        packer._open_bins[0].rectangles.pop(1)

