#!/usr/bin/env python
# coding: utf-8

from dash import  dcc, html, Input, Output
from app import app
import pandas as pd
import os
# os.chdir(r"C:\Users\jmormal\PycharmProjects\pythonProject3")
if os.path.isdir(r"C:\Users\jmormal\PycharmProjects\pythonProject3\output\lastsol"):

    path = os.getcwd()
    df_demanda = pd.read_csv(path + "/output/lastsol/Demanda.csv")
    df_stock = pd.read_csv(path + "/output/lastsol/Stock.csv")
    df_camiones = pd.read_csv(path + "/output/lastsol/CamionesDia.csv")
    df_cantidadpedir = pd.read_csv(path + "/output/lastsol/CantidadPedir.csv")

    layout = html.Div(children=[
        dcc.Interval(
            id='interval-component',
            interval=15 * 1000,  # in milliseconds
            n_intervals=0,
        ),
        html.H1(children='Número de camiones utilizados por día'),
        dcc.Graph(
            id='Camiones',

        ),
        html.H2(id="total_camiones", ),

        html.Button('Actualiza Solución', id="button",n_clicks=1),




    ])
else:

    layout = html.Div(children=[
        html.H1(children='Cubicaje de camiones'),
        html.H2(children='Genera una solución'),
        html.Button('Genera una solución', id="button", n_clicks=0),
        html.Div(id='container-button-basic-solution1',
                 children=['Apreta el boton para generar una solución']
                 )

    ])

@app.callback(
    Output('Camiones', 'figure'),
    Output("total_camiones", "children"),
    Input('button', 'n_clicks'),
)
def update_solution(n_clicks):
    if n_clicks > 0:
        path = os.getcwd()
        df_camiones = pd.read_csv(path + "/output/lastsol/CamionesDia.csv")
        figure = {
            'data': [
                {'x': df_camiones.index, 'y': df_camiones["CamionesDia"], 'type': 'bar', 'name': 'Camiones'},
            ],
            'layout': {
                'title': 'Camiones por dia'
            }
        }
        return figure, 'El número total de camiones es ' + str(df_camiones["CamionesDia"].sum())


