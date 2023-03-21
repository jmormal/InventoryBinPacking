#!/usr/bin/env python
# coding: utf-

import os
from dash import  dash_table, dcc, html, Input, Output
import pandas as pd
import dash_bootstrap_components as dbc
from app import app




path=os.getcwd()
print(path)
df=pd.read_csv(path+"\output\lastsol\CantidadPedirTotal.csv")


df

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
    row_drop := dcc.Dropdown(value=10, clearable=False, style={'width':'35%'},
                             options=[10, 25, 50, 100]),

    dbc.Row([
html.Pre(children="Elija un día", style={"fontSize":"150%"}),
        dbc.Col([
            continent_drop := dcc.Dropdown(id="dp_id_t")
        ], width=3),
html.Pre(children="Elija un camión", style={"fontSize":"150%"}),
        dbc.Col([
            country_drop := dcc.Dropdown(id= "dp_id_c" , multi=True)
        ], width=3),
html.Pre(children="Elija un producto", style={"fontSize":"150%"}),
        dbc.Col([
            product_drop := dcc.Dropdown(id = "dp_id_i", multi=True)
        ], width=3),
    ], justify="between", className='mt-3 mb-4'),
    my_table := dash_table.DataTable(
        columns=[
            {'name': 'Día', 'id': 't', 'type': 'numeric'},
            {'name': 'Camión', 'id': 'c', 'type': 'text'},
            {'name': 'Producto', 'id': 'id', 'type': 'text'},
            {'name': 'Cantidad de cajas por producto', 'id': 'Products', 'type': 'numeric'},
            {'name': 'A- Cajas totales', 'id': 'vA', 'type': 'text'},
            {'name': 'B- Cajas totales', 'id': 'vB', 'type': 'text'},
            {'name': '% de utilización', 'id': 'Volumen', 'type': 'numeric'},
        ],
        data=df.to_dict('records'),
        filter_action='native',
        page_size=10,
        style_data_conditional=(
            [{"if":{"filter_query": "{c}="+str(i) }, "backgroundColor" : colors[i]  } for i in range(1,10)]
        ),
        style_data={
            'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        }
    ),

])

@app.callback(
    Output(my_table, 'data'),
    Output(my_table, 'page_size'),
    Output('dp_id_t', 'options'),
    Output('dp_id_c', 'options'),
    Output('dp_id_i', 'options'),
    Input(continent_drop, 'value'),
    Input(country_drop, 'value'),
    Input(product_drop, 'value'),
    Input(row_drop, 'value')
)
def update_dropdown_options(cont_v, country_v, prouct_v ,row_v):
    path = os.getcwd()
    df = pd.read_csv(path + "\output\lastsol\CantidadPedirTotal.csv")
    print(df)
    dff = df.copy()
    if cont_v:
        dff = dff[dff.t==cont_v]
    if country_v:
        dff = dff[dff.c.isin(country_v)]

    if prouct_v:
        dff = dff[dff.Products.isin(prouct_v)]



    return dff.to_dict('records'), row_v ,[x for x in sorted(df.t.unique())], [x for x in sorted(dff.c.unique())], [x for x in sorted(dff.id.unique())]

#
# @app.callback(Output('dp_id_t', 'options'),
#               [Input('interval-component', 'n_intervals')])
# def update_figures(n):
#     path = os.getcwd()
#     df = pd.read_csv(path + "\output\lastsol\CantidadPedirTotal.csv")
#     print(df)
#     return [x for x in sorted(df.t.unique())]