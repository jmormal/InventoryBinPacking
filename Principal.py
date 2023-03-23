#!/usr/bin/env python
# coding: utf-8

from dash import  dcc, html, Input, Output
from app import app
import pandas as pd
import os
# os.chdir(r"C:\Users\jmormal\PycharmProjects\pythonProject3")
path=os.getcwd()
if os.path.isdir(path+"\output\lastsol"):

    path = os.getcwd()

    layout = html.Div(children=[
        dcc.Interval(
            id='interval-component',
            interval=15 * 1000,  # in milliseconds
            n_intervals=0,
        ),

        html.H1(children='Número de camiones utilizados por día')
        ,
        dcc.Dropdown(
            id='days-dropdown', value=[d for d in os.listdir(r"output") if os.path.isdir("output" + "/" + d)][0],
            clearable=False,
            persistence=True, persistence_type='session',
            options=[{'label': x, 'value': x} for x in
                     [d for d in os.listdir(r"output") if os.path.isdir("output" + "/" + d)]]
        ),
        dcc.Dropdown(
            id='proveedor-dropdown', value=[d for d in os.listdir(r"output") if os.path.isdir("output" + "/" + d)][0],
            clearable=False,
            persistence=True, persistence_type='session',
            options=[{'label': x, 'value': x} for x in
                     [d for d in os.listdir(r"output") if os.path.isdir("output" + "/" + d)]]
        ),

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
                 children=['Apreta el boton para generar una solución porfavor']
                 )

    ])

@app.callback(
    Output('Camiones', 'figure'),
    Output("total_camiones", "children"),
    Input('button', 'n_clicks'),
    Input('days-dropdown', 'value'),
    Input('proveedor-dropdown', 'value'),
)
def update_solution(n_clicks, day_chosen, proveedor_chosen):
    path = os.getcwd()
    file_name = "{}/output/{}/{}/NumberOfTrucksPerDay.csv".format(path, day_chosen, proveedor_chosen)
    df_camiones = pd.read_csv(file_name)
    figure = {
        'data': [
            {'x': df_camiones.index, 'y': df_camiones["NumberOfTrucks"], 'type': 'bar', 'name': 'Camiones'},
        ],
        'layout': {
            'title': 'Camiones por dia'
        }
    }
    return figure, 'El número total de camiones es ' + str(df_camiones["NumberOfTrucks"].sum())


