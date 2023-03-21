#!/usr/bin/env python
# coding: utf-
from dash import  dcc, html, Input, Output, State, ctx
from app import app
import pandas as pd
import cp_satvv as cp
import base64
import io
import os
# os.chdir(r"C:\Users\jmormal\PycharmProjects\pythonProject3")
# path=r"C:\Users\jmormal\PycharmProjects\pythonProject3"
if os.path.isdir(r"C:\Users\jmormal\PycharmProjects\pythonProject3\output\lastsol"):

    path = os.getcwd()
    df_demanda = pd.read_csv(path + "/output/lastsol/Demanda.csv")
    df_stock = pd.read_csv(path + "/output/lastsol/Stock.csv")
    df_camiones = pd.read_csv(path + "/output/lastsol/CamionesDia.csv")
    df_cantidadpedir = pd.read_csv(path + "/output/lastsol/CantidadPedir.csv")
    layout = html.Div(children=[
        html.H2(children='Para generar siga las instrucciones'),
        html.H4(children='Cargue los datos de demanda (i = producto, t =  día, Demanda)'),
        dcc.Upload(
            id='upload-demanda',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        html.H3(id='output-demanda'),
        html.H4(children='Cargue los datos de los productos (name = nombre del producto, i = producto, piezascont = piezas por contenedor, Stock = stock inicial, CosteStock = coste de inventario)'),
        dcc.Upload(
            id='upload-productos',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        html.H3(id='output-productos'),



        html.Button('Genera una solución', id="button",n_clicks=0),
        html.Div(id='container-button-basic-solution2',
                 children=['Apreta el boton para generar una solución']
                 )



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


# Save productos to csv
def parse_contents_productos(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            df.to_csv(path+r"\datasets\Productos.csv")
            return "Archivo cargado correctamente"
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            df.to_csv(path+r"\datasets\Productos.csv")
            return "Archivo cargado correctamente"
        else:
            return "Archivo no cargado, por favor cargue un archivo .csv o .xls"
    except Exception as e:
        print(e)
        return "Archivo no cargado, error en el archivo"


# Save demanda to csv
def parse_contents_demanda(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            df.to_csv(path+r"\datasets\Demanda.csv")
            return "Archivo cargado correctamente"
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            df.to_csv(path+r"\datasets\Demanda.csv")
            return "Archivo cargado correctamente"
        else:
            return "Archivo no cargado, por favor cargue un archivo .csv o .xls"
    except Exception as e:
        print(e)
        return "Archivo no cargado, error en el archivo"


@app.callback(
    Output('container-button-basic-solution2', 'children'),
    Input("button" ,'n_clicks'),
)
def update_solution(n_clicks):
    print(n_clicks,ctx.triggered)
    if "button" == ctx.triggered_id:
        print("generando solucion")
        cp.update_data()
        print("Se actualizo la data")
        return 'Solucion Generada'

# Update demanda
@app.callback(Output('output-demanda', 'children'),
              Input('upload-demanda', 'contents'),
              State('upload-demanda', 'filename'),
              State('upload-demanda', 'last_modified'))
def update_output_demanda(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents_demanda(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children[0]

# Update productos
@app.callback(Output('output-productos', 'children'),
                Input('upload-productos', 'contents'),
                State('upload-productos', 'filename'),
                State('upload-productos', 'last_modified'))
def update_output_productos(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents_productos(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children[0]
