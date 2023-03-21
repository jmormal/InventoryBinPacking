#!/usr/bin/env python
# coding: utf-

import os
from dash import  dash_table, dcc, html, Input, Output
import pandas as pd
import dash_bootstrap_components as dbc
from app import app



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
    row_drop := dcc.Dropdown(value=10, clearable=False, style={'width':'35%'},
                             options=[10, 25, 50, 100]),
    dcc.Dropdown(
        id='days-dropdown', value=[d for d in os.listdir(r"output") if os.path.isdir("output" + "\\" + d)][0],
        clearable=False,
        persistence=True, persistence_type='session',
        options=[{'label': x, 'value': x} for x in
                 [d for d in os.listdir(r"output") if os.path.isdir("output" + "\\" + d)]]
    ),
    dcc.Dropdown(
        id='proveedor-dropdown',
        clearable=False,
        persistence=True, persistence_type='session',
        # options=[{'label': x, 'value': x} for x in
        #          [d for d in os.listdir(r"output") if os.path.isdir("output" + "\\" + d)]]
    ),
    dbc.Row([
html.Pre(children="Elija un día", style={"fontSize":"150%"}),
        dbc.Col([
            continent_drop := dcc.Dropdown(id="dp_id_t",
                                           persistence=True, persistence_type='session', multi=False)
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
            {'name': 'Camión', 'id': 'k', 'type': 'text'},
            {'name': 'Producto', 'id': 'i', 'type': 'text'},
            {'name': 'Tipo de Caja', 'id': 'b', 'type': 'numeric'},
            {'name': 'Cajas totales', 'id': 'counts', 'type': 'text'},
            # {'name': 'B- Cajas totales', 'id': 'vB', 'type': 'text'},
            # {'name': '% de utilización', 'id': 'Volumen', 'type': 'numeric'},
        ],
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
    my_table2 := dash_table.DataTable(
        columns=[
            {'name': 'Día', 'id': 't', 'type': 'numeric'},
            {'name': 'Tipo de Caja', 'id': 'b', 'type': 'numeric'},
            {'name': 'Cajas totales', 'id': 'counts', 'type': 'text'},
            # {'name': 'B- Cajas totales', 'id': 'vB', 'type': 'text'},
            # {'name': '% de utilización', 'id': 'Volumen', 'type': 'numeric'},
        ],
        filter_action='native',
        page_size=10,
        style_data_conditional=(
            [{"if": {"filter_query": "{c}=" + str(i)}, "backgroundColor": colors[i]} for i in range(1, 10)]
        ),
        style_data={
            'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        }
    ),
])
#
# @app.callback(
# Output("proveedor-dropdown", "options"),
# Output("proveedor-dropdown", "value"),
# Input("days-dropdown", "value"),
# )
# def update_proveedor_options1(day_chosen):
#     path = os.getcwd()
#     print(path)
#     file_name = "{}/output/{}".format(path, day_chosen)
#     # The options are the list of files in the directory
#     options = [{'label': i, 'value': i} for i in os.listdir(file_name)]
#     return options, options[0]['value']


@app.callback(
    Output(my_table, 'data'),
    Output(my_table, 'page_size'),
    Output('dp_id_t', 'options'),
    Output('dp_id_c', 'options'),
    Output('dp_id_i', 'options'),
    Output(my_table2, 'data'),
    Input(continent_drop, 'value'),
    Input(country_drop, 'value'),
    Input(product_drop, 'value'),
    Input(row_drop, 'value'),
    Input('days-dropdown', 'value'),
    Input('proveedor-dropdown', 'value'),
)
def update_dropdown_options(cont_v, country_v, prouct_v ,row_v, day_chosen, proveedor_chosen):
    path = os.getcwd()
    print(path)
    try:
        file_name = "{}/output/{}/{}/TruckDistribution.csv".format(path, day_chosen, proveedor_chosen)
        df = pd.read_csv(file_name)
    except:
        print("No se ha encontrado el archivo")
    print(df)
    dff = df.copy()
    if cont_v:
        dff = dff[dff.t==cont_v]
    if country_v:
        dff = dff[dff.k.isin(country_v)]

    if prouct_v:
        dff = dff[dff.i.isin(prouct_v)]
    print(dff)
    #  Group by so dff is a dataframe that counts the number of times each combination of t, k, i, b appears
    dff1 = dff.groupby(['t', "b"]).size().reset_index(name='counts')
    dff = dff.groupby(['t', 'k', 'i', "b"]).size().reset_index(name='counts')
    print(dff)
    #
    # dff.groupby(['t', 'k', 'i',"b"]).count()
    return dff.to_dict('records'), row_v ,[x for x in sorted(df.t.unique())], [x for x in sorted(dff.k.unique())], [x for x in sorted(dff.i.unique())], dff1.to_dict('records')

#
# @app.callback(Output('dp_id_t', 'options'),
#               [Input('interval-component', 'n_intervals')])
# def update_figures(n):
#     path = os.getcwd()
#     df = pd.read_csv(path + "\output\lastsol\CantidadPedirTotal.csv")
#     print(df)
#     return [x for x in sorted(df.t.unique())]