#!/usr/bin/env python
# coding: utf-
from dash import  dcc, html, Input, Output, State, ctx
from app import app
import pandas as pd
import base64
import io
import datetime
import os, shutil
import zipfile
import importlib
import dash_bootstrap_components as dbc

from zipfile import ZipFile
# os.chdir(r"C:\Users\jmormal\PycharmProjects\pythonProject3")
# path=r"C:\Users\jmormal\PycharmProjects\pythonProject3"
path=os.getcwd()
def remove_py_extension(string):
    if string.endswith('.py'):
        return string[:-3]
    else:
        return string
if os.path.isdir(path+"\output\lastsol"):

    path = os.getcwd()
    layout =  dbc.Container([
        html.H2(children='Para generar siga las instrucciones'),
        html.H4(children='Cargue los datos de demanda (i = producto, t =  día, Demanda)'),
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

        dcc.Dropdown(
            id='solver-dropdown', value=[remove_py_extension(d) for d in os.listdir(r"Solvers")][0],
            clearable=False,
            persistence=True, persistence_type='Solvers',
            options=[{'label': x, 'value': x} for x in
                     [remove_py_extension(d) for d in os.listdir(r"Solvers")]]
        ),

        html.Button('Genera una solución', id="button",n_clicks=0),
        html.Div(id='container-button-basic-solution2',
                 children=['Apreta el boton para generar una solución']
                 )



    ])
    print( [os.path.basename(d) for d in os.listdir(r"Solvers")])
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

        if "zip" in filename:
            # Clear the folder folders
            for the_file in os.listdir(path+r"\datasets"):
                file_path = os.path.join(path+r"\datasets", the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    print(e)




            content_type, content_string = contents.split(',')
            # Decode the base64 string
            content_decoded = base64.b64decode(content_string)
            # Use BytesIO to handle the decoded content
            zip_str = io.BytesIO(content_decoded)
            # Now you can use ZipFile to take the BytesIO output
            with zipfile.ZipFile(zip_str, 'r') as zip_ref:
                zip_ref.extractall(path)

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
    State('solver-dropdown', 'value'),
)
def update_solution(n_clicks, solver_path):
    if "button" == ctx.triggered_id:
        # loop around all the folder of the dataset
        now= datetime.datetime.now()
        solver_maker = importlib.import_module("Solvers."+solver_path)

        for folder in [ d for d in os.listdir(r"datasets") if os.path.isdir("datasets"+"/"+d)]:
            print("Folder: ", folder)
            path= os.getcwd()+r"\datasets/"+folder
            solver=solver_maker.Solver()
            solver.solve(path=path, folder=folder, now = now)
            print("Se actualizo la data de la carpeta: ", folder)

        return 'Solucion Generada'

# # Update demanda
# @app.callback(Output('output-demanda', 'children'),
#               Input('upload-demanda', 'contents'),
#               State('upload-demanda', 'filename'),
#               State('upload-demanda', 'last_modified'))
# def update_output_demanda(list_of_contents, list_of_names, list_of_dates):
#     if list_of_contents is not None:
#         children = [
#             parse_contents_demanda(c, n, d) for c, n, d in
#             zip(list_of_contents, list_of_names, list_of_dates)]
#         return children[0]

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
