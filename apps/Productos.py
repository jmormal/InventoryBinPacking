#!/usr/bin/env python
# coding: utf-
from dash import  dcc, html, Input, Output,  ctx
from app import app

import pandas as pd
import os
import plotly.express as px
import dash_bootstrap_components as dbc


path=os.getcwd()


layout = dbc.Container([
    html.H1(children='Elija un producto'),
    html.Pre(children="Producto ", style={"fontSize":"150%"}),
    dcc.Dropdown(
            id='days-dropdown', value=[ d for d in os.listdir(r"output") if os.path.isdir("output"+"\\"+d)][0], clearable=False,
            persistence=True, persistence_type='session',
            options=[{'label': x, 'value': x} for x in  [ d for d in os.listdir(r"output") if os.path.isdir("output"+"\\"+d)]]
        ),
    dcc.Dropdown(
        id='proveedor-dropdown', value=[d for d in os.listdir(r"output") if os.path.isdir("output" + "\\" + d)][0],
        clearable=False,
        persistence=True, persistence_type='session'
    ),
    dcc.Dropdown(
            id='pymnt-dropdown', value='1', clearable=False,
            persistence=True, persistence_type='session'
        ),
    # dcc.Graph(id='my-map-stock-dia', figure={}),
    # dcc.Graph(id='my-map-cantidad-pedir-dia', figure={}),
    dcc.Graph(id='my-map-demanda-dia', figure={}),
    html.Button('Actualiza los productos', id="button_update",n_clicks=0),
])

# Graph Stock
@app.callback(
    Output(component_id='my-map-stock-dia', component_property='figure'),
    Input(component_id='pymnt-dropdown', component_property='value'),
    Input("proveedor-dropdown", 'value'),
    Input("days-dropdown", 'value')
)
def display_value(product_chosen, proveedor_chosen, days_chosen):
    path = os.getcwd()+"/output/"+days_chosen+"/"+proveedor_chosen

    df_stock = pd.read_csv(path + "/Stock.csv")
    df_stock_fltrd = df_stock[(df_stock['product'] == int(product_chosen))]
    fig = px.line(df_stock_fltrd, x="t", y="Stock", title='Stock de producto por día')

    return fig

# Graph Cantidad Pedir
@app.callback(
    Output(component_id='my-map-cantidad-pedir-dia', component_property='figure'),
    Input(component_id='pymnt-dropdown', component_property='value'),
    Input("proveedor-dropdown", 'value'),
    Input("days-dropdown", 'value')
)
def display_value(product_chosen,proveedor_chosen , days_chosen, ):
    path = os.getcwd()+"/output/"+days_chosen+"/"+proveedor_chosen
    df_cantidadpedir = pd.read_csv(path + "/CantidadPedir.csv")
    df_cp = df_cantidadpedir[(df_cantidadpedir['producto'] == int(product_chosen))]
    df_cp= df_cp.groupby(['t'])[["CantidadPedir"]].sum()
    fig = px.line(df_cp, x=df_cp.index, y="CantidadPedir", title='Cajas de producto a cargar por día')

    return fig
# Graph Camiones


# Graph Demanda

@app.callback(
    Output(component_id='my-map-demanda-dia', component_property='figure'),
    Input(component_id='pymnt-dropdown', component_property='value'),
    Input("proveedor-dropdown", 'value'),
    Input("days-dropdown", 'value')
)
def display_value(product_chosen,proveedor_chosen,days_chosen):
    path = os.getcwd()+"/output/"+days_chosen+"/"+proveedor_chosen
    df_proyected_stock = pd.read_csv(path + "/ProyectedStock.csv")
    df_need_stock = pd.read_csv(path + "/NeededStock.csv")
    df_proyected_stock_fltrd = df_proyected_stock[(df_proyected_stock['id'] == int(product_chosen))]
    df_need_stock_fltrd = df_need_stock[(df_need_stock['id'] == int(product_chosen))]

    fig = {
        'data': [
            {'x': df_proyected_stock_fltrd['t'], 'y': df_proyected_stock_fltrd['ProyectedStock'], 'type': 'line', 'name': u'Stock'},
            {'x': df_need_stock_fltrd['t'], 'y': df_need_stock_fltrd['NeededStock'], 'type': 'line', 'name': u'StockSeguridad'},
        ],
        'layout': {
            'title': 'Stock de producto por día'
        }
    }
    return fig



@app.callback(
    Output('pymnt-dropdown', 'options'),
    Input("button_update" ,'n_clicks'),
    Input("proveedor-dropdown" ,'value'),
    Input("days-dropdown" ,'value'),
)
def update_solution(n_clicks,proveedor_chosen,day_chosen):
    path = os.getcwd()
    file_name="{}/output/{}/{}/ProyectedStock.csv".format(path,day_chosen,proveedor_chosen)
    df_stock = pd.read_csv(file_name)


    return [{'label': x, 'value': x} for x in sorted(df_stock["id"].unique())]



@app.callback(
    Output('proveedor-dropdown', 'options'),
    Output('proveedor-dropdown', 'value'),
    Input('days-dropdown' ,'value'),
)
def update_solution(name):
    # path = os.getcwd()
    # df_stock = pd.read_csv(path + "/output/lastsol/Stock.csv")
    options= [d for d in os.listdir(r"output"+"\\"+name) if os.path.isdir("output" + "\\"+name+"\\" + d)]
    value = options[0]
    return options, value