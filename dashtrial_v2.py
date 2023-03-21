#!/usr/bin/env python
# coding: utf-
import dash
from dash import Dash, dcc, html, Input, Output, State, ctx

import pandas as pd
import cp_sat as cp
df_stock=pd.read_csv("Codigo Antiguo/Stock.csv")
df_camiones=pd.read_csv("CamionesDia.csv")
df_cantidadpedir=pd.read_csv("CantidadPedir.csv")
df_cantidadpedir_acu=pd.read_csv("CantidadPedirAcumulado.csv")
app = dash.Dash()


app.layout = html.Div(children=[
    html.H1(children='Cubicaje de camiones'),
    html.H2(children='Ahora veremos el cubicaje de camiones por dia')    ,
    dcc.Graph(
        id='example',
        figure={
            'data': [
                {'x':df_stock.loc[df_stock["id"]==1]["t"], 'y': df_stock.loc[df_stock["id"]==1]["Stock"], 'type': 'line', 'name': 'Producto 1'},
                {'x': df_stock.loc[df_stock["id"] == 1]["t"], 'y': df_stock.loc[df_stock["id"] == 2]["Stock"],
                 'type': 'line', 'name': 'Producto 2'}
            ],
            'layout': {
                'title': 'Stock de producto por día'
            }
        }
    ),
    html.H2(children='El número total de camiones es ' + str(df_camiones["CamionesDia"].sum())),
    dcc.Graph(
        id='Camiones',
        figure={
            'data': [
                {'x':df_camiones.index, 'y': df_camiones["CamionesDia"], 'type': 'bar', 'name': 'Camiones'},
            ],
            'layout': {
                'title': 'Camiones por dia'
            }
        }
    ),
    dcc.Graph(
        id='CantidadPedir',
        figure={
            'data': [
                {'x':df_cantidadpedir.index, 'y': df_cantidadpedir[i], 'type': 'line', 'name': i} for i in df_cantidadpedir.columns[1:]

            ],
            'layout': {
                'title': 'CantidadPedir'
            }
        }
    ),
    dcc.Graph(
        id='CantidadPedir_Acumulado',
        figure={
            'data': [
                {'x':df_cantidadpedir_acu.index, 'y': df_cantidadpedir_acu["2"], 'type': 'line', 'name': '2'},
                {'x':df_cantidadpedir_acu.index, 'y': df_cantidadpedir_acu["1"], 'type': 'line', 'name': '1'}
            ],
            'layout': {
                'title': 'CantidadPedir'
            }
        }
    ),


    html.Button('Genera una solución', id="button",n_clicks=0),
    html.Div(id='container-button-basic-solution',
             children=['Apreta el boton para generar una solución']
             )



])


@app.callback(
    Output('container-button-basic-solution', 'children'),
    Input("button" ,'n_clicks'),
)
def update_solution(n_clicks):
    print(n_clicks,ctx.triggered)
    if "button" == ctx.triggered_id:
        print("generando solucion")
        cp.update_data()
        print("Se actualizo la data")
        return 'Solucion Generada'

if __name__ == '__main__':
    print("Starting server")
    app.run_server(debug=True)
