import pandas as pd
import dash
from dash import dcc
from dash import html
import plotly_express as px
from dash.dependencies import Input, Output
from datetime import datetime as dt
import dash_bootstrap_components as dbc
from dateutil.relativedelta import relativedelta

#############################################################################
######################     PREPARACION DE LOS DATOS     #####################
#############################################################################

# DATA WRANGLING RESUMEN DE CUENTAS PARA RANKING DE PROVEEDORES

df_cta_cte = pd.read_excel(
    "C:/Users/Agus/Desktop/Coding/Python/dashenv/archivos/comprasdash/ranking proveedores.xlsx"
)

df_cta_cte["IMPORTE"] = df_cta_cte["DEBE"] + df_cta_cte["HABER"]

df_cta_cte = df_cta_cte[["NOMBR_PRO", "FECHA_EMIS", "IMPORTE"]]


# DATA WRANGLING SOLICITUDES DE PEDIDO

df_pedidos = pd.read_excel(
    "C:/Users/Agus/Desktop/Coding/Python/dashenv/archivos/comprasdash/Solicitudes de Pedido.xlsx",
    header=3,
)

df_pedidos = df_pedidos.drop(["Unnamed: 0"], axis=1)

df_pedidos = df_pedidos[["Fecha", "Sector", "Tipo", "Estado"]]

# DATA WRANGLING LISTADO PROVEEDORES

df_proveed = pd.read_excel(
    "C:/Users/Agus/Desktop/Coding/Python/dashenv/archivos/comprasdash/evaluación proveedores.xlsx",
    header=4,
)

df_proveed = df_proveed.drop(["Unnamed: 0"], axis=1)

df_proveed["Legajo"] = pd.to_datetime(df_proveed["Legajo"], dayfirst=True)

df_proveed = df_proveed[["TIPO", "CLASE", "Legajo"]]

df_proveed = df_proveed.dropna()

df_proveed["TIPO"] = df_proveed["TIPO"].replace(
    ["C", "Co", "S", "EA", "BU"],
    ["Calibracion", "Consumibles", "Servicios", "Ensayos de aptitud", "Bien de Uso"],
)

dff_tipo = df_proveed.groupby("TIPO").count().reset_index(level=0)

df_proveed["CLASE"] = df_proveed["CLASE"].replace(
    ["A", "B", "-"], ["Confiable", "Confianza media", "Suspendido"]
)

dff_clase = df_proveed.groupby("CLASE").count().reset_index(level=0)

overdue = dt.now() - relativedelta(years=1)

df_proveed["Legajo"] = (df_proveed["Legajo"] < overdue).astype(bool)

df_proveed["Legajo"] = df_proveed["Legajo"].replace(
    [True, False], ["Vencido", "Evaluación al dia"]
)

dff_legajo = df_proveed.groupby("Legajo").count().reset_index(level=0)


#############################################################################
#########################     COMIENZO DE LA APP      #######################
#############################################################################

app = dash.Dash(
    __name__,
)

app.layout = dbc.Container(
    [
        # BANNER PRINCIPAL
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Dashboard Compras",
                            className="text-center bg-info text-white mb-4 p-2",
                        )
                    ],
                    width=12,
                ),
            ]
        ),
        ############    SECCION RANKING PROVEEDORES   ##########
        # BANNER RANKING PROVEEDORES
        dbc.Row(
            [
                html.H2(
                    "Ranking Proveedores",
                    className="bg-primary text-white mb-2 p-2 d-inline-block",
                ),
            ]
        ),
        # DATE PICKER RANGE RANKING PROVEEDORES
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Elige un rango de fecha"),
                        dcc.DatePickerRange(
                            id="rango_fecha_proveedores",
                            calendar_orientation="horizontal",
                            day_size=30,
                            with_portal=False,
                            first_day_of_week=0,
                            reopen_calendar_on_clear=True,
                            is_RTL=False,
                            clearable=True,
                            number_of_months_shown=1,
                            min_date_allowed=dt(2021, 1, 1),
                            max_date_allowed=dt.today(),
                            initial_visible_month=dt(2022, 1, 1),
                            start_date=dt(2022, 1, 1).date(),
                            end_date=dt.today(),
                            display_format="D, MMMM, YYYY",
                            month_format="MMMM, YYYY",
                            persistence=True,
                            persisted_props=["start_date", "end_date"],
                            persistence_type="session",
                            updatemode="bothdates",
                        ),
                    ],
                    width={"size": 4},
                ),
                # RADIO BUTTONS RANKING PROVEEDORES/ TOP 5, TOP 10, TOP 15
                dbc.Col(
                    [
                        html.P("Seleccionar ranking"),
                        dcc.RadioItems(
                            id="proveedores-radioitems",
                            labelStyle={"display": "inline-block"},
                            options=[
                                {"label": "Top 5", "value": "top5"},
                                {"label": "Top 10", "value": "top10"},
                                {"label": "Top 15", "value": "top15"},
                            ],
                            value="top10",
                        ),
                    ],
                    width={"size": 4},
                ),
            ],
            justify="center",
        ),
        # GRAFICOS RANKING DE PROVEEDORES
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Graph(id="proveedores_barchart", figure={})], width={"size": 6}
                ),
                dbc.Col(
                    [dcc.Graph(id="proveedores_piechart", figure={})], width={"size": 6}
                ),
            ]
        ),
        # DASH CORE COMPONENT STORE (dcc.Store) RANKING PROVEEDORES
        dcc.Store(id="store-data-ranking", data=[], storage_type="memory"),
        ############    SECCION SOLICITUDES DE PEDIDO   ##########
        # BANNER SOLICITUDES DE PEDIDO
        dbc.Row(
            [
                html.H2(
                    "Estado Solicitudes de Pedido",
                    className="bg-primary text-white mb-2 p-2 d-inline-block",
                ),
            ]
        ),
        # DATE PICKER SOLICITUDES DE PEDIDO
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Elige un rango de fecha"),
                        dcc.DatePickerRange(
                            id="rango_fecha_pedidos",
                            calendar_orientation="horizontal",
                            day_size=30,
                            with_portal=False,
                            first_day_of_week=0,
                            reopen_calendar_on_clear=True,
                            is_RTL=False,
                            clearable=True,
                            number_of_months_shown=1,
                            min_date_allowed=dt(2022, 4, 1),
                            max_date_allowed=dt.today(),
                            initial_visible_month=dt(2022, 4, 1),
                            start_date=dt(2022, 4, 1).date(),
                            end_date=dt.today(),
                            display_format="D, MMMM, YYYY",
                            month_format="MMMM, YYYY",
                            persistence=True,
                            persisted_props=["start_date", "end_date"],
                            persistence_type="session",
                            updatemode="bothdates",
                        ),
                    ],
                    width={"size": 4},
                ),
            ],
            justify="center",
        ),
        # GRAFICOS SOLICITUDES DE PEDIDOS
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Graph(id="piechart_pedidos_1", figure={})], width={"size": 4}
                ),
                dbc.Col(
                    [dcc.Graph(id="piechart_pedidos_2", figure={})], width={"size": 4}
                ),
                dbc.Col(
                    [dcc.Graph(id="piechart_pedidos_3", figure={})], width={"size": 4}
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Graph(id="barchart_pedidos", figure={})], width={"size": 10}
                ),
            ]
        ),
        # DASH CORE COMPONENT STORE (dcc.Store) SOLICITUDES DE PEDIDO
        dcc.Store(id="store-data-pedidos", data=[], storage_type="memory"),
        ############    SECCION EVALUACION PROVEED.   ##########
        # BANNER EVALUACIÓN DE PROVEEDORES
        dbc.Row(
            [
                html.H2(
                    "Estado Evaluación de Proveedores",
                    className="bg-primary text-white mb-2 p-2 d-inline-block",
                ),
            ]
        ),
        # GRAFICOS EVALUACION DE PROVEEDORES
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="piechart_evaluacion_1",
                            figure=px.pie(
                                data_frame=dff_tipo,
                                names="TIPO",
                                values="CLASE",
                                title="Porcentaje por tipo de proveedor",
                                labels={"TIPO": "Tipo", "CLASE": "cantidad"},
                                color_discrete_sequence=px.colors.qualitative.Vivid,
                                hole=0.4,
                            ),
                        )
                    ],
                    width={"size": 4},
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="piechart_evaluacion_2",
                            figure=px.pie(
                                data_frame=dff_clase,
                                names="CLASE",
                                values="TIPO",
                                title="Porcentaje por clase de proveedor",
                                labels={"CLASE": "Clase", "TIPO": "cantidad"},
                                color="CLASE",
                                color_discrete_map={
                                    "Confiable": "#191970",
                                    "Confianza media": "#7B68EE",
                                    "Suspendido": "#C0C0C0",
                                },
                                hole=0.4,
                            ),
                        )
                    ],
                    width={"size": 4},
                ),
                dbc.Col(
                    [
                        dcc.Graph(
                            id="piechart_evaluacion_3",
                            figure=px.pie(
                                data_frame=dff_legajo,
                                names="Legajo",
                                values="CLASE",
                                title="Estado de vencimiento",
                                labels={"Legajo": "Estado", "CLASE": "cantidad"},
                                color="Legajo",
                                color_discrete_map={
                                    "Evaluación al dia": "#3CB371",
                                    "Vencido": "#DC143C",
                                },
                                hole=0.4,
                            ),
                        )
                    ],
                    width={"size": 4},
                ),
            ]
        ),
    ],
    fluid=True,
)


#############################################################################
##############################     CALLBACKS     ############################
#############################################################################

#  callback store data ranking proveedores
@app.callback(
    Output("store-data-ranking", "data"),
    Input("rango_fecha_proveedores", "start_date"),
    Input("rango_fecha_proveedores", "end_date"),
)
def date_range(start_date, end_date):

    dataset = df_cta_cte[
        df_cta_cte["FECHA_EMIS"].isin(pd.date_range(start_date, end_date))
    ]

    diccionario = dataset.to_dict()

    return diccionario

    #  callback barchart ranking proveedores


@app.callback(
    Output("proveedores_barchart", "figure"),
    Input("store-data-ranking", "data"),
    Input("proveedores-radioitems", "value"),
)
def update_barchart(data, value):

    dff = pd.DataFrame(data)

    dff_agrupado_proveedor = dff.groupby(["NOMBR_PRO"], as_index=False)[
        ["IMPORTE"]
    ].sum()

    dff_ordenado_impo_total = dff_agrupado_proveedor.sort_values(
        "IMPORTE", ascending=False
    )

    if value == "top5":

        dff_impo_total_top5 = dff_ordenado_impo_total.iloc[0:5]

        fig = px.bar(
            data_frame=dff_impo_total_top5,
            x="IMPORTE",
            y="NOMBR_PRO",
            title="Ranking proveedores por importe total contabilizado",
            labels={
                "IMPORTE": "Importe contabilizado",
                "NOMBR_PRO": "Nombre Proveedor",
            },
            color_discrete_sequence=px.colors.sequential.haline,
            orientation="h",
        ).update_yaxes(autorange="reversed")

    elif value == "top10":

        dff_impo_total_top10 = dff_ordenado_impo_total.iloc[0:10]

        fig = px.bar(
            data_frame=dff_impo_total_top10,
            x="IMPORTE",
            y="NOMBR_PRO",
            title="Ranking proveedores por importe total contabilizado",
            labels={
                "IMPORTE": "Importe contabilizado",
                "NOMBR_PRO": "Nombre Proveedor",
            },
            color_discrete_sequence=px.colors.sequential.haline,
            orientation="h",
        ).update_yaxes(autorange="reversed")
    else:

        dff_impo_total_top15 = dff_ordenado_impo_total.iloc[0:15]

        fig = px.bar(
            data_frame=dff_impo_total_top15,
            x="IMPORTE",
            y="NOMBR_PRO",
            title="Ranking proveedores por importe total contabilizado",
            labels={
                "IMPORTE": "Importe contabilizado",
                "NOMBR_PRO": "Nombre Proveedor",
            },
            orientation="h",
            color_discrete_sequence=px.colors.sequential.haline,
        ).update_yaxes(autorange="reversed")
    return fig

    # callback piechart ranking proveedores


@app.callback(
    Output("proveedores_piechart", "figure"),
    Input("store-data-ranking", "data"),
    Input("proveedores-radioitems", "value"),
)
def update_piechart(data, value):

    dff = pd.DataFrame(data)

    dff_agrupado_proveedor = dff.groupby(["NOMBR_PRO"], as_index=False)[
        ["IMPORTE"]
    ].sum()

    dff_ordenado_impo_total = dff_agrupado_proveedor.sort_values(
        "IMPORTE", ascending=False
    )

    if value == "top5":

        dff_impo_total_top5 = dff_ordenado_impo_total.iloc[0:5]

        fig2 = px.pie(
            data_frame=dff_impo_total_top5,
            names="NOMBR_PRO",
            values="IMPORTE",
            title="Porcentaje del total contabilizado",
            labels={
                "IMPORTE": "Importe contabilizado",
                "NOMBR_PRO": "Nombre Proveedor",
            },
            color_discrete_sequence=px.colors.sequential.haline,
        )
    elif value == "top10":

        dff_impo_total_top10 = dff_ordenado_impo_total.iloc[0:10]

        fig2 = px.pie(
            data_frame=dff_impo_total_top10,
            names="NOMBR_PRO",
            values="IMPORTE",
            title="Porcentaje del total contabilizado",
            labels={
                "IMPORTE": "Importe contabilizado",
                "NOMBR_PRO": "Nombre Proveedor",
            },
            color_discrete_sequence=px.colors.sequential.haline,
        )
    else:

        dff_impo_total_top15 = dff_ordenado_impo_total.iloc[0:15]

        fig2 = px.pie(
            data_frame=dff_impo_total_top15,
            names="NOMBR_PRO",
            values="IMPORTE",
            title="Porcentaje del total contabilizado",
            labels={
                "IMPORTE": "Importe contabilizado",
                "NOMBR_PRO": "Nombre Proveedor",
            },
            color_discrete_sequence=px.colors.sequential.haline,
        )
    return fig2

    #  callback store data solicitude de pedido


@app.callback(
    Output("store-data-pedidos", "data"),
    Input("rango_fecha_pedidos", "start_date"),
    Input("rango_fecha_pedidos", "end_date"),
)
def date_range(start_date, end_date):

    dataset = df_pedidos[df_pedidos["Fecha"].isin(pd.date_range(start_date, end_date))]

    diccionario = dataset.to_dict()

    return diccionario

    # callback piechart 1 pedidos


@app.callback(
    Output("piechart_pedidos_1", "figure"),
    Input("store-data-pedidos", "data"),
)
def update_piechart_pedidos_1(data):

    dff = pd.DataFrame(data)

    dff = dff.groupby("Sector").count()

    dff = dff.reset_index(level=0)

    fig3 = px.pie(
        data_frame=dff,
        names="Sector",
        values="Estado",
        title="Porcentaje de pedidos por sector",
        labels={"Sector": "Sector", "Estado": "cantidad de pedidos"},
        color_discrete_sequence=px.colors.qualitative.Prism,
    )

    return fig3

    # callback piechart 2 pedidos


@app.callback(
    Output("piechart_pedidos_2", "figure"),
    Input("store-data-pedidos", "data"),
)
def update_piechart_pedidos_2(data):

    dff = pd.DataFrame(data)

    dff = dff.groupby("Tipo").count()

    dff = dff.reset_index(level=0)

    fig4 = px.pie(
        data_frame=dff,
        names="Tipo",
        values="Estado",
        title="Porcentaje de tipos de pedido",
        labels={"Tipo": "Tipo de pedido", "Estado": "cantidad"},
        color_discrete_sequence=px.colors.qualitative.Bold,
    )

    return fig4

    # callback piechart 3 pedidos


@app.callback(
    Output("piechart_pedidos_3", "figure"),
    Input("store-data-pedidos", "data"),
)
def update_piechart_pedidos_3(data):

    dff = pd.DataFrame(data)

    dff = dff.groupby("Estado").count()

    dff = dff.reset_index(level=0)

    fig5 = px.pie(
        data_frame=dff,
        names="Estado",
        values="Tipo",
        title="Porcentaje de cumplimiento",
        labels={"Estado": "Estado", "Tipo": "cantidad"},
        color="Estado",
        color_discrete_map={
            "CANCELADO": "#DC143C",
            "CUMPLIDO": "#3CB371",
            "EN PROCESO": "#48D1CC",
        },
    )

    return fig5

    # callback barchart pedidos


@app.callback(
    Output("barchart_pedidos", "figure"),
    Input("store-data-pedidos", "data"),
)
def update_barchart_pedidos(data):

    df_barchart_pedidos = pd.DataFrame(data)

    dff = df_barchart_pedidos.groupby(["Sector", "Estado"], as_index=False).count()

    dff = dff.pivot(index="Sector", columns="Estado", values="Tipo").fillna(0)

    dff = dff.reset_index(level=0)

    try:
        dff[["CANCELADO", "CUMPLIDO", "EN PROCESO"]] = dff[
            ["CANCELADO", "CUMPLIDO", "EN PROCESO"]
        ].astype(int)

        fig6 = px.bar(
            data_frame=dff,
            x="Sector",
            y=["CANCELADO", "CUMPLIDO", "EN PROCESO"],
            title="Estado de pedidos por sector",
            color_discrete_map={
                "CANCELADO": "#DC143C",
                "CUMPLIDO": "#3CB371",
                "EN PROCESO": "#48D1CC",
            },
        )
        return fig6
    except KeyError:
        dff[["CUMPLIDO", "EN PROCESO"]] = dff[["CUMPLIDO", "EN PROCESO"]].astype(int)

        fig6 = px.bar(
            data_frame=dff,
            x="Sector",
            y=["CUMPLIDO", "EN PROCESO"],
            title="Estado de pedidos por sector",
            color_discrete_map={"CUMPLIDO": "#3CB371", "EN PROCESO": "#48D1CC"},
        )
        return fig6


if __name__ == ("__main__"):
    app.run_server(debug=False)
