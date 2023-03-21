import pandas as pd
import os
import plotly.graph_objects as go
import datetime
def draw_truck(path):

    df_truck = pd.read_csv(path)
    # Order df by filas
    df_truck = df_truck.sort_values(by=['Fila'])
    # Only keep one entry with the same "Fila" and "id_box"
    df_truck = df_truck.drop_duplicates(subset=['Fila', 'id_box'], keep='first')



    # Draw the truck as rectangle, with the boxes inside
    # The dimensions of the truck are given by df_truck["LargoCamion"].iloc[0] and df_truck["AnchoCamion"].iloc[0]
    # Draw the truck as a rectangle with plt
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 0, df_truck["LargoCamion"].iloc[0],
                                df_truck["LargoCamion"].iloc[0], 0],
                                y=[0, df_truck["AnchoCamion"].iloc[0],
                                    df_truck["AnchoCamion"].iloc[0], 0, 0],
                                mode='lines',
                                name='Truck'))
    # Draw the boxes, first the ones in the first row, then the ones in the second row, etc.
    current_length_of_row=0
    # The width of the box is given by BoxWidth and the length by BoxLength
    filas= df_truck["Fila"].unique()
    current_width_of_row = 0
    colors=["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "grey", "black"]
    boxes=df_truck["id_box"].unique()
    # dictionary of box to co
    box_to_color = {box: colors[i] for i, box in enumerate(boxes)}
    for f in filas:
        current_length_of_row = 0
        for row in df_truck.itertuples():
            if row.Fila == f:
                for r1 in range(int(row.Cantidad)):
                    fig.add_shape( type="rect",
                        x0=current_length_of_row,
                        y0=current_width_of_row,
                        x1=current_length_of_row + row.BoxLength,
                        y1=current_width_of_row + row.BoxWidth,
                        line_color="black",
                        fillcolor=box_to_color[row.id_box],
                    )
                    current_length_of_row += row.BoxLength
                    width=row.BoxWidth
        current_width_of_row = width
        print(f)

    # fig.update_layout(
    #     autosize=False,
    #     width=df_truck["LargoCamion"].iloc[0]/4,
    #     height=df_truck["AnchoCamion"].iloc[0]/4, )
    fig.show()

if __name__ == "__main__":
    day=2
    camion=1
    p=r'C:\Users\jmormal\PycharmProjects\pythonProject1\output\7-12-2022\Prov1'
    # Get a list of the files that are un  r"C:\Users\jmormal\PycharmProjects\pythonProject1\output\7-12-2022\Prov1" and start as "Catudad"
    files = [p +"\\" + f for f in os.listdir(r"C:\Users\jmormal\PycharmProjects\pythonProject1\output\7-12-2022\Prov1") if
                f.startswith("CantidadPedirDia") and f.endswith("Box.csv")]

    for path in files:
        draw_truck(path)


