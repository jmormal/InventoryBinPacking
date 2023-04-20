
import webbrowser
from threading import Timer
import shutil
from apps import Productos, Principal, Dias, Generar_solucion, DistCamion
import os
from dash import  dash_table, dcc, html, Input, Output
from app import app
path = os.getcwd()
import datetime

now=datetime.datetime.now()
wd = os.getcwd() + "\output"
path_save = wd + "\{}-{}-{}".format(now.day, now.month, now.year)
if not os.path.exists(path_save):
    os.makedirs(path_save)

style={'font-family': 'Times New Roman, Times, serif', 'font-weight': 'bold',  'margin-left': 'auto', 'margin-right': 'auto',}

if os.path.isdir(path + "/output/lastsol"):
    # ## Clean all files in output/lastsol
    # for filename in os.listdir(path + "/output/lastsol"):
    #     os.remove(path + "/output/lastsol/" + filename)
    #
    # ## Copy all files of output/backupsol to output/lastsol
    # for filename in os.listdir(path + "/output/backup"):
    #     shutil.copy(path + "/output/backup/" + filename, path + "/output/lastsol/" + filename)
    pass
else:
    os.mkdir(path + "/output/lastsol")
    ## Copy all files of output/backupsol to output/lastsol
    for filename in os.listdir(path + "/output/backup"):
        shutil.copy(path + "/output/backup/" + filename, path + "/output/lastsol/" + filename)
    pass

# Connect to your app pages
# Check if output/lastsol exists

# Check if datasets exists
if os.path.isdir(path + "/datasets"):
    pass
else:
    os.mkdir(path + "/datasets")
    pass


app.layout = html.Div(
            className="content",
            children=[
    dcc.Location(id='url', refresh=False),

html.Div(
    className="left_menu",
    children=[
html.A(
    href="https://cigip.webs.upv.es/index.php/es/",
    children=[
        html.Img(
            alt="Link to my twitter",
            src=app.get_asset_url('logo.png'),
            style={'width': '50%', 'height': 'auto', 'margin-left': 'auto', 'margin-right': 'auto', 'display': 'block'}
        )
    ]
),
        html.Ul([
            html.Li(dcc.Link('Generar Solución', href='/apps/GSolucion', style=style)),
            html.Li(dcc.Link('Información General', href='/apps/Principal', style=style)),
            html.Li(dcc.Link(' Información por Producto', href='/apps/Iproductos', style=style)),
            html.Li(dcc.Link(' Información por día', href='/apps/Idias', style=style)),
            html.Li(dcc.Link(' Información por camion ', href='/apps/DCamion',  style=style))
        ])
    ]
),

html.Div(
    className="right_content",
    children=[html.Div(id='page-content', children=[])

    ]
),

                ]
            )

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    try:
        if pathname == '/apps/GSolucion':
            return Generar_solucion.layout
        elif pathname == '/apps/Iproductos':
            return Productos.layout
        elif pathname == '/apps/Idias':
            return Dias.layout

        elif pathname == '/apps/Principal':
            return Principal.layout
        elif pathname == '/apps/DCamion':
            return DistCamion.layout


        else:
            return "404 Page Error! Please choose a link"
    except:
        return "404 Page Error! Please choose a link"

port = 8080 # or simply open on the default `8050` port

def open_browser():
	webbrowser.open_new("http://localhost:{}".format(port))
if __name__ == '__main__':
    Timer(2, open_browser).start()
    app.run_server( debug= False ,port=port)
