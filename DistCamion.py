#!/usr/bin/env python
# coding: utf-

import os
from dash import  dash_table, dcc, html, Input, Output
import pandas as pd
import dash_bootstrap_components as dbc
from app import app
from drawing_truckv2 import  draw_truck

path=os.getcwd()
print(path)






# Need to use Python 3.8 or higher and Dash 2.2.0 or higher




colors=["blue","red","hotpink","green","yellow","orange","purple","brown","black","grey","pink","cyan","magenta","lime","olive","teal","navy","maroon","aqua","fuchsia","silver","gold","indigo","violet","coral","crimson","khaki","lavender","turquoise","beige","azure","wheat","salmon","sienna","tan","chocolate","firebrick","forestgreen","limegreen","seagreen","darkblue","darkcyan","darkgoldenrod","darkgray","darkgreen","darkgrey","darkkhaki","darkmagenta","darkolivegreen","darkorange","darkorchid","darkred","darksalmon","darkseagreen","darkslateblue","darkslategray","darkslategrey","darkturquoise","darkviolet","deeppink","deepskyblue","dimgray","dimgrey","dodgerblue","goldenrod","greenyellow","lightblue","lightcoral","lightcyan","lightgoldenrodyellow","lightgray","lightgreen","lightgrey","lightpink","lightsalmon","lightseagreen","lightskyblue","lightslategray","lightslategrey","lightsteelblue","lightyellow","mediumblue","mediumorchid","mediumpurple","mediumseagreen","mediumslateblue","mediumspringgreen","mediumturquoise","mediumvioletred","midnightblue","mintcream","mistyrose","moccasin","navajowhite","oldlace","orangered","orchid","palegoldenrod","palegreen","paleturquoise","palevioletred","papayawhip","peachpuff","peru","powderblue","rosybrown","royalblue","saddlebrown","sandybrown","seashell","slateblue","slategray","slategrey","springgreen","steelblue","tomato","yellowgreen","rebeccapurple","blueviolet","chartreuse","darkorange","darkorchid","darkred","darksalmon","darkseagreen","darkslateblue","darkslategray","darkslategrey","darkturquoise","darkviolet","deeppink","deepskyblue","dimgray","dimgrey","dodgerblue","goldenrod","greenyellow","lightblue","lightcoral","lightcyan","lightgoldenrodyellow"]
colors=["cyan","grey","hotpink","lime","cyan","yellow","orange","purple","brown","black","grey","pink","cyan","magenta","lime","olive","teal","navy","maroon","aqua","fuchsia","silver","gold","indigo","violet","coral","crimson","khaki","lavender","turquoise","beige","azure","wheat","salmon","sienna","tan","chocolate","firebrick","forestgreen","limegreen","seagreen","darkblue","darkcyan","darkgoldenrod","darkgray","darkgreen","darkgrey","darkkhaki","darkmagenta","darkolivegreen","darkorange","darkorchid","darkred","darksalmon","darkseagreen","darkslateblue","darkslategray","darkslategrey","darkturquoise","darkviolet","deeppink","deepskyblue","dimgray","dimgrey","dodgerblue","goldenrod","greenyellow","lightblue","lightcoral","lightcyan","lightgoldenrodyellow","lightgray","lightgreen","lightgrey","lightpink","lightsalmon","lightseagreen","lightskyblue","lightslategray","lightslategrey","lightsteelblue","lightyellow","mediumblue","mediumorchid","mediumpurple","mediumseagreen","mediumslateblue","mediumspringgreen","mediumturquoise","mediumvioletred","midnightblue","mintcream","mistyrose","moccasin","navajowhite","oldlace","orangered","orchid","palegoldenrod","palegreen","paleturquoise","palevioletred","papayawhip","peachpuff","peru","powderblue","rosybrown","royalblue","saddlebrown","sandybrown","seashell","slateblue","slategray","slategrey","springgreen","steelblue","tomato","yellowgreen","rebeccapurple","blueviolet","chartreuse","darkorange","darkorchid","darkred","darksalmon","darkseagreen","darkslateblue","darkslategray","darkslategrey","darkturquoise","darkviolet","deeppink","deepskyblue","dimgray","dimgrey","dodgerblue","goldenrod","greenyellow","lightblue","lightcoral","lightcyan","lightgoldenrodyellow"]


layout = dbc.Container([
    dcc.Interval(
            id='interval-component',
            interval=15*1000, # in milliseconds
            n_intervals=0,
        ),
    dcc.Markdown('# Información sobre los camiones por día', style={'textAlign':'center'}),

    dbc.Label("Número de filas que se muestran"),

    dcc.Dropdown(
        id='days-dropdown', value=[d for d in os.listdir(r"output") if os.path.isdir("output" + "/" + d)][0],
        clearable=False,
        persistence=True, persistence_type='session',
        options=[{'label': x, 'value': x} for x in
                 [d for d in os.listdir(r"output") if os.path.isdir("output" + "/" + d)]]
    ),
    dcc.Dropdown(
        id='proveedor-dropdown',  value=[d for d in os.listdir(r"output") if os.path.isdir("output" + "/" + d)][0],
        clearable=False,
        persistence=True, persistence_type='session',
        options=[{'label': x, 'value': x} for x in
                 [d for d in os.listdir(r"output") if os.path.isdir("output" + "/" + d)]]
    ),

    dcc.Dropdown(
        id= "camion-day-dropdown-1",
    ),
    dcc.Dropdown(
        id= "camion-dropdown-2",
    ),
    # Create a graph
    dcc.Graph(id='graph-truck' , figure={}),
    dcc.Markdown(id="porcien", style={'textAlign': 'center'}),

])

# Update camion-day-dropdown-1

@app.callback(
    Output('camion-day-dropdown-1', 'options'),
    Output('camion-day-dropdown-1', "value"),
    Input('days-dropdown', 'value'),
    Input('proveedor-dropdown', 'value'),
)
def update_dropdown_options21(day_chosen, proveedor_chosen):
    # The options are the list of days that are in the folder "{}/output/{}/{}/TruckDistribution.csv".format(path, day_chosen, proveedor_chosen)

    path = os.getcwd()
    print(path)
    try:
        file_name = "{}/output/{}/{}/TruckDistribution.csv".format(path, day_chosen, proveedor_chosen)
        print(file_name)
        df = pd.read_csv(file_name)
    except:
        print("No se ha encontrado el archivo")
    options=[{'label': x, 'value': x} for x in df.t.unique()]
    return options, options[0]['value']

# Update camion-dropdown-2

@app.callback(
    Output('camion-dropdown-2', 'options'),
    Output('camion-dropdown-2', "value"),
    Input('days-dropdown', 'value'),
    Input('proveedor-dropdown', 'value'),
    Input('camion-day-dropdown-1', 'value'),
)
def update_dropdown_options2(day_chosen, proveedor_chosen, truck_day_chosen):
    # The options are the list of days that are in the folder "{}/output/{}/{}/TruckDistribution.csv".format(path, day_chosen, proveedor_chosen)

    path = os.getcwd()
    print(path)
    try:
        file_name = "{}/output/{}/{}/TruckDistribution.csv".format(path, day_chosen, proveedor_chosen)
        print(file_name)
        df = pd.read_csv(file_name)
    except:
        print("No se ha encontrado el archivo")

    df = df[df.t == truck_day_chosen]

    options=[{'label': x, 'value': x} for x in df.k.unique()]
    # options=[ {'label': x, 'value': x} for x in range(1,2)]
    return options, options[0]['value']


@app.callback(
    Output("graph-truck", "figure"),
    Output("porcien", "children"),
    Input('days-dropdown', 'value'),
    Input('proveedor-dropdown', 'value'),
    Input('camion-day-dropdown-1', 'value'),
    Input('camion-dropdown-2', 'value'),
)
def update_dropdown_options4(day_chosen, proveedor_chosen, truck_day_chosen, truck_chosen):
    path = os.getcwd()
    print(path)
    try:
        file_name = "{}/output/{}/{}/TruckDistribution.csv".format(path, day_chosen, proveedor_chosen)
        print(file_name)
        df = pd.read_csv(file_name)
    except:
        print("No se ha encontrado el archivo")
    print("\n \n Entro ")
    dff = df[df.t == truck_day_chosen]
    dff = dff[dff.k == truck_chosen]
    # We are going to print all the rows of the dataframe
    pd.set_option('display.max_rows', dff.shape[0]+1)

    print(dff)

    path ="{}/output/{}/{}".format(path, day_chosen, proveedor_chosen)
    figure,percentage = draw_truck(path,  dff )
    percentage='# El porcentaje de utilizacón es: ' + str(percentage)
    return figure, percentage

