#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pyodbc
import pandas as pd
import pyomo.environ as pe
import pyomo.opt as po
model = pe.ConcreteModel("Cargacamiones")
import random
import sys
random.seed(0)


# ## Preprocesado de los datos

# In[2]:



# In[ ]:





# In[ ]:





# In[6]:


path= r"/Carga de camiones/Transporte_cubicaje.mdb"
conn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+path+';')
cursor = conn.cursor()


# Familias Carga de datos

# In[7]:


cursor.execute('select IdProducto from Productos')
productos=[]
for row in cursor.fetchall():
    productos.append(row[0])


# In[8]:


cursor.execute('select IdFamilia from Familias')
familias=[]
for row in cursor.fetchall():
    familias.append(row[0])


# In[9]:


cursor.execute('select IdCamion from Camiones WHERE IdCamion<4')
camiones=[]
for i in range(1,7):
    camiones.append(i)


# In[10]:

cursor.execute('select  IdProducto , IdDia, Demanda from Demanda')
demanda={}
for row in cursor.fetchall():
    # if row[0]>=13:
    #     demanda.update({(row[0],row[1]):row[2]})
    # else:
        demanda.update({(row[0],row[1]):row[2]})

cursor.execute('select IdDia from Dias WHERE "IdDia"<=19')
dias=[]
for row in cursor.fetchall():
    dias.append(row[0])
        


# In[11]:


cursor.execute('select IdDia from Dias')
dias1=[]
for row in cursor.fetchall():
    dias1.append(row[0])



# In[12]:


columnas=[1,2]
A1=[6,7]
B1=[4,2]
productos


# ## Familias Pyomo

# In[13]:


model.i = pe.Set(initialize=productos)
model.f = pe.Set(initialize=familias)
model.c = pe.Set(initialize=camiones)
model.t = pe.Set(initialize=dias)
model.t1 = pe.Set(initialize=dias1)
model.col=pe.Set(initialize=columnas)
model.A1=pe.Set(initialize=A1)
model.B1=pe.Set(initialize=B1)



# ## Carga de datos productos

# In[14]:


cursor.execute('select IdFamilia, LotePedido from Familias')
lotepedido={}
for row in cursor.fetchall():
    lotepedido.update({row[0]:row[1]})


# In[15]:


cursor.execute('select IdFamilia, LotePedido from Familias')
CosteStock={}
for row in cursor.fetchall():
    CosteStock.update({row[0]:random.randint(7, 10)*0.001})


# In[16]:


cursor.execute('select IdProducto , PiezasCont from Productos')
piezascont={}
for row in cursor.fetchall():
    piezascont.update({row[0]:row[1]})


# In[17]:


cursor.execute('select IdProducto , LargoContedor from Productos')
piezas_largo_box={}
for row in cursor.fetchall():
    piezas_largo_box.update({row[0]:row[1]})


# In[18]:


cursor.execute('select IdProducto , IdFamilia, beta from beta')
b={}
for row in cursor.fetchall():
    b.update({(row[0],row[1]):row[2]})


# In[19]:


cursor.execute('select  IdProducto , IdDia, Demanda from Demanda')
demanda={}
for row in cursor.fetchall():
    # if row[0]>=13:
    #     demanda.update({(row[0],row[1]):row[2]})
    # else:
        demanda.update({(row[0],row[1]):row[2]})    


# In[20]:


# cursor.execute('select IdProducto , StockInicial from Productos')
stockInicial={}
# for row in cursor.fetchall():
#     stockInicial.update({row[0]:row[1]})
cursor.execute('select  IdProducto , Demanda from Demanda where IdDia=1')

for row in cursor.fetchall():
    stockInicial.update({row[0]:row[1]*0})


# In[21]:


model.i.__dict__["_init_values"]


# In[22]:


cursor.execute('select  IdProducto , Valor from Productos')
valor={}
for row in cursor.fetchall():
    valor.update({row[0]:row[1]})


# In[23]:


PC={}
for camion in camiones:
    PC.update({camion:1000})


# In[24]:


L=78
nu=26/30
NT_lw=5
NT_up=10


# In[25]:


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
model.CS=pe.Param(model.i, initialize=CosteStock)


# # # Varibles

# In[26]:


model.CantidadPedir = pe.Var(model.i, model.c, model.t,model.col, domain=pe.Integers)


# In[27]:


model.CantidadPedir2 = pe.Var(model.i,model.f, model.c, model.t,model.col, domain=pe.Integers, bounds=(0,None) )
model.ContenedoresCamion=pe.Var(model.c,model.t,model.col,model.i, domain=pe.Integers)


# In[28]:


model.Stock=pe.Var(model.i,model.t, bounds=(0,None))


# In[29]:


model.RetrasoDemanda=pe.Var(model.i,model.t, bounds=(0,None))


# In[30]:


model.K=pe.Var(model.f,model.c,model.t,model.col ,domain=pe.Integers)


# In[31]:


model.Y=pe.Var(model.c,model.t ,domain=pe.Binary, initialize=0)


# In[32]:


model.A=pe.Var(model.c,model.col,model.t, domain=pe.Integers, bounds=(0,4.5))
model.B=pe.Var(model.c,model.col, model.t, domain=pe.Integers, bounds=(0,12.5))
# model.A=pe.Var(model.c,model.col,model.t, domain=pe.Integers, bounds=(0,13))
# model.B=pe.Var(model.c,model.col, model.t, domain=pe.Integers, bounds=(0,13))


# ## Función Objetivo
# Minimizar el número de camiones usado
# $$\sum_{c,t}PC(c)Y(c,t)+ \sum CS(i)Stock(i,t)$$

# In[33]:


expr = sum(model.PC[c]*model.Y[c,t] +sum(model.CS[i]*model.Stock[i,t] for i in model.i) for c in model.c for t in model.t)


# In[34]:


#Coste Transporte
model.objective = pe.Objective(sense=pe.minimize, expr=expr)


# ## Funciones auxiliares

# In[35]:


def UsoCamion(model):
    return sum(model.L*model.Y[c,t] for c in model.c for t in model.t)-\
        sum(model.ContenedoresCamion[c,t] for c in model.c for t in model.t)


# In[36]:


def CTransporte(model):
    return sum(model.PC[c]*model.Y[c,t] for c in model.c for t in model.t)


# In[37]:


def NumeroCamiones(model):
    return sum(model.Y[c,t] for c in model.c for t in model.t)


# ## Restricciones

# In[38]:


model.stocks=pe.ConstraintList()


# $$Stock(i,t)=Stock(i,t-1)+\sum_{c,col}CantidadPedir(i,c,t,col)PiezasCont[i] -Demanda(i,t)$$

# In[39]:


for i in model.i:
        lhs=model.Stock[i,1]
        rhs=model.StockInicial[i]-model.demanda[i,1]+sum(model.CantidadPedir[i,c,1,col]*model.PiezasCont[i] for c in model.c for col in model.col )
        model.stocks.add(lhs==rhs)


# In[40]:


for t in list(model.t)[1:]:
    for i in model.i:
            lhs=model.Stock[i,t]
            rhs=model.Stock[i,t-1]-model.demanda[i,t]+sum(model.CantidadPedir[i,c,t,col]*model.PiezasCont[i] for c in model.c for col in model.col)
            model.stocks.add(lhs==rhs)


# In[41]:


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

# In[44]:


for i in model.i:
    for c in model.c:
        for t in model.t:
            for col in model.col:
                lhs=model.CantidadPedir[i,c,t,col]
                rhs=sum(model.CantidadPedir2[i,f,c,t,col] for f in model.f)
                model.RcantidadPedir2.add(lhs==rhs)


# In[45]:


model.RDimensionesCamion=pe.ConstraintList()


# $$ 1600A_{c,col,t} +1000B_{c,col,t}   \leq 13600* Y[c,t]$$

# In[46]:


for c in model.c:
    for t in model.t:
        for col in model.col:
            lhs=13600*model.Y[c,t]
            rhs=(model.A[c,col,t]*1600+model.B[c,col,t]*1000)
            model.RDimensionesCamion.add(lhs>=rhs)


# In[47]:


model.RCajasTotales=pe.ConstraintList()


# $$ \forall c \in C \quad \forall t \in T \quad \sum_i CantidadPedir(i,c,t,col) \leq A_{c,col,t}*4+B_{c,col,t}*3 $$

# In[48]:


for c in model.c:
    for t in model.t:
        for col in model.col:
            lhs=sum(model.CantidadPedir[i,c,t,col] for i in model.i)
            rhs=(model.A[c,col,t]*4+model.B[c,col,t]*3)
            model.RCajasTotales.add(lhs<=rhs)


# In[49]:


model.RCajasTipoA=pe.ConstraintList()


# $$ \sum_i CantidadPedir(i,c,t,col)_{tipo a}\leq A_{c,col,t}*4 $$

# In[50]:


for c in model.c:
    for t in model.t:
        for col in model.col:
            lhs=sum(model.CantidadPedir[i,c,t,col]*float(int(model.LargoCont[i])==int(1600)) for i in model.i)
            rhs=model.A[c,col,t]*4
            model.RCajasTipoA.add(lhs<=rhs)


# $$ \sum_i CantidadPedir(i,c,t,col)_{tipo b}\leq B_{c,col,t}*3 $$

# In[51]:


model.RCajasTipoB=pe.ConstraintList()


# In[52]:


for c in model.c:
    for t in model.t:
        for col in model.col:
            lhs=sum(model.CantidadPedir[i,c,t,col]*float(int(model.LargoCont[i])==int(1000)) for i in model.i)
            rhs=model.B[c,col,t]*3
            model.RCajasTipoB.add(lhs<=rhs)


# In[53]:


model.RColumnasCamion=pe.ConstraintList()
for c in model.c:
    for t in model.t:
         model.RColumnasCamion.add(model.A[c,2,t]== model.A[c,1,t])
         model.RColumnasCamion.add(model.B[c,2,t]== model.B[c,1,t])


# $$\forall i,t  \quad Stock[i,t]\geq \sum_{j \in [1,2,3,4]} Demanda[i,t+j]$$

# In[54]:


model.RCobertura=pe.ConstraintList()
l=list(range(25))
for i in model.i:
    for t in range(1,7):
        lhs=model.Stock[i,t]
        #rhs=(model.demanda[i,t+1]+model.demanda[i,t+2]+model.demanda[i,t+3])
        rhs=0

        model.RCobertura.add(lhs>=rhs)
        l[i]=rhs
for i in model.i:
    for t in range(7,10):
        lhs=model.Stock[i,t]
        
        #rhs=l[i]
        rhs=0

        model.RCobertura.add(lhs>=rhs)


# In[55]:


model.RCVolumenminimo=pe.ConstraintList()


# In[56]:


for t in model.t:
    for c in model.c:
        lhs=(sum(model.CantidadPedir[i,c,t,col] for i in model.i for col in model.col if int(model.LargoCont[i])==int(1600))*750*1200*1600+
                                     +(sum(model.CantidadPedir[i,c,t,col] for i in model.i for col in model.col if int(model.LargoCont[i])==int(1000)))*1000*1000*1200)/(3000*2400*13600)
        rhs=0.98*model.Y[c,t]
        model.RCVolumenminimo.add(lhs >= rhs)


# In[57]:


model.bounds=pe.ConstraintList()
for i in model.i:
    for t in model.t:
        model.bounds.add(model.Stock[i,t]>=0)


solver = po.SolverFactory("gurobi")
solver.options["TimeLimit"]=60
# solver.options["MIPFocus"] = 0
solver.options["MIPGap"] = 0.01
results = solver.solve(model, tee=True)

#
# solvername='glpk'
# solverpath_exe=r"C:\Users\jmormal\Downloads\cbc-win64\cbc.exe"
# solverpath_exe=r"C:\Users\jmormal\Downloads\winglpk-4.65 (1)\glpk-4.65\w64\glpsol.exe"
# # solverpath_exe=r"C:\Users\jmormal\Downloads\Cbc-2.10-x86_64-w64-mingw32-dbg (1)\bin"
#
# solver = po.SolverFactory(solvername,executable=solverpath_exe)
# # solver.options["TimeLimit"]=60
# # # solver.options["MIPFocus"] = 0
# # solver.options["MIPGap"] = 0.01
# results = solver.solve(model,tee=True)

print(results)


# In[59]:


for t in range(1,6):
    print(t,model.Stock[i,t].value,-model.demanda[i,t+1]-model.demanda[i,t+2]-model.demanda[i,t+3] ,
          model.Stock[i,t].value-model.demanda[i,t+1]-model.demanda[i,t+2]-model.demanda[i,t+3])
    a=-model.demanda[i,t+1]-model.demanda[i,t+2]-model.demanda[i,t+3]-model.demanda[i,t+4]
for t in range(6,10):
    print(t,model.Stock[i,t].value,a ,model.Stock[i,t].value+a)
def mean(x):
    return sum(x)/len(x)


# In[60]:

#
# for t in model.t:
#     for c in model.c:
#         print(t,c,model.Y[c,t].value)


# In[61]:


utilizacion=0
volumen_por_camion=[]
for t in model.t:
    for c in model.c:
        if model.Y[c,t].value==1:
            volumen_por_camion.append(((sum(model.CantidadPedir[i,c,t,col].value for i in model.i for col in model.col if int(model.LargoCont[i])==int(1600))*750*1200*1600+
                                     +(sum(model.CantidadPedir[i,c,t,col].value for i in model.i for col in model.col if int(model.LargoCont[i])==int(1000)))*1000*1000*1200)/
                                     (3000*2400*13600)))
print(volumen_por_camion)
print(mean(volumen_por_camion))
print(len(volumen_por_camion))


# In[62]:
#
#
# for t in model.t:
#     print(sum(model.Y[c,t].value for c in model.c))


# In[63]:


l=[]
for t in model.t:
    for i in model.i:
        1
        # print(t,i,model.Stock[i,t].value, sum(model.Y[c,t].value  for c in model.c if model.CantidadPedir[i,c,t,col].value>0))

            # if model.Y[c,t].value==1:
            #     print(t,model.A[c,col,t].value,model.B[c,col,t].value,((sum(model.CantidadPedir[i,c,t,col].value/model.PiezasCont[i] for i in model.i for col in model.col if int(model.LargoCont[i])==int(1600))*750*1200*1600+
            #                          +(sum(model.CantidadPedir[i,c,t,col].value/model.PiezasCont[i] for i in model.i for col in model.col if int(model.LargoCont[i])==int(1000)))*1000*1000*1200)/
            #                          (3000*2400*13600)))


# In[64]:


l=[]
for t in model.t:
    for c in model.c:
        for col in model.col:

            if model.Y[c,t].value==1:
                l.append([c,col,t,model.A[c,col,t].value,model.B[c,col,t].value,((sum(model.CantidadPedir[i,c,t,col].value for i in model.i for col in model.col if int(model.LargoCont[i])==int(1600))*750*1200*1600+
                                     +(sum(model.CantidadPedir[i,c,t,col].value for i in model.i for col in model.col if int(model.LargoCont[i])==int(1000)))*1000*1000*1200)/
                                     (3000*2400*13600),[model.CantidadPedir[i,c,t,col].value for i in model.i])])
                # print([model.CantidadPedir[i,c,t,col].value for i in model.i])
                # print(t,model.A[c,col,t].value,model.B[c,col,t].value,((sum(model.CantidadPedir[i,c,t,col].value for i in model.i for col in model.col if int(model.LargoCont[i])==int(1600))*750*1200*1600+
                #                      +(sum(model.CantidadPedir[i,c,t,col].value for i in model.i for col in model.col if int(model.LargoCont[i])==int(1000)))*1000*1000*1200)/
                #                      (3000*2400*13600)),
                #     sum(model.CantidadPedir[i,c,t,col].value for i in model.i for col in model.col if int(model.LargoCont[i])==int(1600))
                #       ,sum(model.CantidadPedir[i,c,t,col].value for i in model.i for col in model.col if int(model.LargoCont[i])==int(1000)))


# In[65]:


df1=pd.DataFrame(l,columns=["c", "col", "t", "A", "B", "Volumen",])
df1


# In[66]:


for t in model.t:
    for c in model.c:
        for i in model.i:
            print(model.CantidadPedir[i,c,t,col].value)#*float(int(model.LargoCont[i])==int(1000)))


# In[67]:


l1=[]
a=list(range(25))
for t in range(1,7):
    for i in model.i:
            l1.append([t,i,model.Stock[i,t].value,-model.demanda[i,t+1]-model.demanda[i,t+2]-model.demanda[i,t+3] ,
          model.Stock[i,t].value-model.demanda[i,t+1]-model.demanda[i,t+2]-model.demanda[i,t+3]])
            a[i]=-model.demanda[i,t+1]-model.demanda[i,t+2]-model.demanda[i,t+3]
for t in range(7,9):
    for i in model.i:
            l1.append([t,i,model.Stock[i,t].value,a[i] ,
          model.Stock[i,t].value+a[i]])


# In[68]:


df2=pd.DataFrame(l1,columns=["t","id","Stock","Demanda Proximos Dias","Diferencia Demanda"])
pd.set_option('display.max_rows', None)
df2


# In[69]:


# for t in model.t:
#     print(t,sum(model.CantidadPedir[i,c,t,col].value for c in model.c for i in model.i for col in model.col if int(model.LargoCont[i])==int(1000)))
print(sum(model.CantidadPedir[i,c,t,col].value for t in model.t for c in model.c for i in model.i for col in model.col if int(model.LargoCont[i])==int(1600)))
print(sum(model.CantidadPedir[i,c,t,col].value for t in model.t for c in model.c for i in model.i for col in model.col if int(model.LargoCont[i])==int(1000)))


# In[70]:




# In[71]:


CamionesDia=[]
for t in model.t:
    CamionesDia.append(sum(model.Y[c,t].value for c in model.c))
df_CamionesDia=pd.DataFrame(CamionesDia,columns=["CamionesDia"])
df_CamionesDia.to_csv("CamionesDia.csv")


# In[72]:


stock=[]
for t in model.t:
    for i in model.i:
        stock.append([t,i,model.Stock[i,t].value])
df_stock=pd.DataFrame(stock,columns=["t","id","Stock"])
df_stock.to_csv("Stock.csv")


# In[ ]:





# In[73]:


df2.loc[df2["id"]==1]["t"]


# In[74]:


cantidadpedir_pro=[]
for t in model.t:
    pro=[]
    for i in model.i:
        pro.append(sum(model.CantidadPedir[i,c,t,col].value  for c in model.c for col in model.col))
    cantidadpedir_pro.append(pro)
df_cantidadpedir_pro=pd.DataFrame(cantidadpedir_pro,columns=[str(i) for i in model.i])


# In[75]:


df_cantidadpedir_pro.to_csv("CantidadPedir.csv")


# In[76]:


cantidadpedir_acu=[]
for t in model.t:
    pro=[]
    for i in model.i:
        pro.append(sum(model.CantidadPedir[i,c,t1,col].value  for c in model.c for col in model.col for t1 in list(model.t)[0:t]))
    cantidadpedir_acu.append(pro)


# In[ ]:





# In[77]:


df_cantidadpedir_acu=pd.DataFrame(cantidadpedir_acu, columns=[str(i) for i in model.i])
df_cantidadpedir_acu["2"]
df_cantidadpedir_acu.to_csv("CantidadPedirAcumulado.csv")


# In[ ]:





# In[ ]:




