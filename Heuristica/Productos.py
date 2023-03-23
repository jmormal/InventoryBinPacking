from copy import deepcopy
class Product():
    def __init__(self, id, stock, Name, StockCoverage, Cost, Stock):
        self.id=id
        self.stock=stock
        self.Name=Name
        self.StockCoverage=StockCoverage
        self.Cost=Cost
        self.Stock=Stock
        self.ListOfContainers=[]


    def SetDemand(self, list_of_demands):
        self.Demand=list_of_demands
    def SetContainers(self,container):
        self.ListOfContainers.append(deepcopy(container))
    def SetProyectedStockWithoutTransport(self, time, maxSimTime):

        #ProyectStockWithoutTransport = this->Stock;

        ProyectStockWithoutTransport = self.Stock
        #for (int i = 0; i < this->StockCoverage+1; ++i) {
        ProyectStockWithoutTransport -= self.Demand[time]
        if time < maxSimTime - self.StockCoverage:
            d = sum([x for x in self.Demand[time + 1: time + self.StockCoverage + 1]])
        else:
            d = sum(self.Demand[-self.StockCoverage+maxSimTime:+maxSimTime])

        ProyectStockWithoutTransport -= d
        self.ProyectStockWithoutTransport=ProyectStockWithoutTransport
        self.ProyectStockWithoutTransportAdded=0

    def SetTemporaryProyectedStockWithoutTransport(self, ):
        self.TemporaryProyectedStock=self.ProyectStockWithoutTransport
