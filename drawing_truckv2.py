import pandas as pd
import os
import plotly.graph_objects as go
import datetime


class Truck():
    def __init__(self, id, Length, Width, Height, alpha=0.9):
        self.id = id
        self.Length = Length
        self.Width = Width
        self.Height = Height
        self.Volume = self.Length*self.Width*self.Height
        self.alpha = alpha

class Container():
    def __init__(self, id, Length, Width, Height):
        self.id = id
        self.Length = Length
        self.Width = Width
        self.Height = Height
        self.Volume = self.Length*self.Width*self.Height
def draw_truck(path, dff):
    pd_productos = pd.read_csv(path + "\Productos.csv")
    pd_demanda = pd.read_csv(path + "\Demanda.csv")
    pd_dimensiones_camiones = pd.read_csv(path + "\Dimensiones_Camiones.csv")
    pd_dimensiones_contenedores = pd.read_csv(path + "\Dimensiones_Contenedores.csv")

    # Create a dictionary of containers
    B = {}
    print(pd_dimensiones_contenedores)
    for row in pd_dimensiones_contenedores.itertuples():
        B[row.id] = Container(row.id, row.Length, row.Width, row.Heigth)

    # Create a dictionary of trucks
    K = {}
    for row in pd_dimensiones_camiones.itertuples():
        K[row.id] = Truck(row.id, row.Length, row.Width, row.Heigth)
    colors = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "grey", "black"]
    # Reverse the list of colors
    colors.reverse()
    box_to_color = { b:colors.pop() for b in B}

    print(box_to_color)

    # Draw the truck as rectangle, with the boxes inside
    # The dimensions of the truck are given by df_truck["LargoCamion"].iloc[0] and df_truck["AnchoCamion"].iloc[0]
    # Draw the truck as a rectangle with plt
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 0, max(K[k].Length for k in K), max(K[k].Length for k in K), 0],
                                y=[0, max(K[k].Width for k in K), max(K[k].Width for k in K), 0, 0],
                                mode='lines',
                                name='Truck'))

    # Draw the boxes that are in the dff dataframe
    # , k, t, i, b, x, y, z, r
    for w, s, k, t, i, b, x, y, z, r , Volume in dff.itertuples():
        if z== 0:
                    fig.add_shape( type="rect",
                        x0=x,
                        y0=y,
                        x1=x + (1-r)*B[b].Length+r*B[b].Width,
                        y1=y + r*B[b].Length+(1-r)*B[b].Width,
                        line_color="black",
                        fillcolor=box_to_color[b],
                        opacity=0.5,



                    )
                    # Get all the i values that have the same k, t, b, x, y
                    # and put them in a list
                    i_list = [i for w, s, k1, t1, i, b1, x1, y1, z, r, vol in dff.itertuples() if k1 == k and t1 == t and b1 == b and x1 == x and y1 == y]

                    fig.add_trace(go.Scatter(x=[(2*x + (1-r)*B[b].Length+r*B[b].Width)/2], y=[(2*y + r*B[b].Length+(1-r)*B[b].Width)/2],
                                    name="Hoverinfo \n" + str(i + 1),
                                 showlegend=False,
                                 mode='markers',
                                hovertemplate= str(i_list),
                                marker=dict(symbol='circle', opacity=0 , size=12, color= "black")))

    # fig.update_layout(
    #     autosize=False,
    #     width=df_truck["LargoCamion"].iloc[0]/4,
    #     height=df_truck["AnchoCamion"].iloc[0]/4, )

    # Set the axis limits
    fig.update_xaxes(range=[0, max(K[k].Length for k in K)])
    fig.update_yaxes(range=[0, max(K[k].Width for k in K)])
    # Set the aspect ratio
    fig.update_layout(
        xaxis=dict(
            scaleanchor="y",
            scaleratio=1,
        )
    )
    # Calculate the percentage of the truck that is filled
    Volume_truck = max(K[k].Volume for k in K)
    Volume_boxes = sum(B[b].Volume for w, s, k, t, i, b, x, y, z, r, Volume in dff.itertuples())
    percentage = Volume_boxes/Volume_truck
    print("Percentage of the truck that is filled: ", percentage)
    return fig, percentage
if __name__ == "__main__":
    day=2
    camion=1
    p=r'C:\Users\jmormal\PycharmProjects\pythonProject1\output\7-12-2022\Prov1'
    # Get a list of the files that are un  r"C:\Users\jmormal\PycharmProjects\pythonProject1\output\7-12-2022\Prov1" and start as "Catudad"
    files = [p +"\\" + f for f in os.listdir(r"C:\Users\jmormal\PycharmProjects\pythonProject1\output\7-12-2022\Prov1") if
                f.startswith("CantidadPedirDia") and f.endswith("Box.csv")]

    for path in files:
        draw_truck(path)


