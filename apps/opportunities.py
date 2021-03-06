# -*- coding: utf-8 -*-
import math
import json
from datetime import date
import dateutil.parser

import pandas as pd
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go

# from app import app, indicator, millify, df_to_table, sf_manager
from app import app, indicator, sf_manager

header_names =[ 'sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'class']
df = pd.read_csv('iris.csv',names=header_names)


def converted_opportunities(period, source, df):
    df["CreatedDate"] = pd.to_datetime(df["CreatedDate"], format="%Y-%m-%d")

    # source filtering
    if source == "all_s":
        df = df[df["IsWon"] == 1]
    else:
        df = df[(df["LeadSource"] == source) & (df["IsWon"] == 1)]

    # period filtering
    if period == "W-MON":
        df["CreatedDate"] = pd.to_datetime(df["CreatedDate"]) - pd.to_timedelta(
            7, unit="d"
        )
    df = (
        df.groupby([pd.Grouper(key="CreatedDate", freq=period)])
            .count()
            .reset_index()
            .sort_values("CreatedDate")
    )

    # if no results were found
    if df.empty:
        layout = dict(annotations=[dict(text="No results found", showarrow=False)])
        return {"data": [], "layout": layout}

    trace = go.Scatter(
        x=df["CreatedDate"],
        y=df["IsWon"],
        name="converted opportunities",
        fill="tozeroy",
        fillcolor="#e6f2ff",
    )

    data = [trace]

    layout = go.Layout(
        xaxis=dict(showgrid=False),
        margin=dict(l=35, r=25, b=23, t=5, pad=4),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return {"data": data, "layout": layout}


# returns heat map figure
# def heat_map_fig(df, x, y):
def heat_map_fig(df):
    # z = []
    # for lead_type in y:
    #     z_row = []
    #     for stage in x:
    #         probability = df[(df["StageName"] == stage) & (df["Type"] == lead_type)][
    #             "Probability"
    #         ].mean()
    #         z_row.append(probability)
    #     z.append(z_row)

    trace = [
                go.Scatter(
                    x=df[df['class'] == i]['petal_length'],
                    y=df[df['class'] == i]['sepal_length'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df['class'].unique()
            ],
    layout = go.Layout(
                xaxis={'title': 'Petal Length'},
                yaxis={'title': 'Sepal Length'},
                margin={'l': 200, 'b': 40, 't': 100, 'r': 200},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )

    return go.Figure(data=[trace], layout=layout)


# returns top 5 lost opportunities
def top_lost_opportunities(df):
    df = df.sort_values("Amount", ascending=True)
    cols = ["CreatedDate", "Name", "Amount", "StageName"]
    df = df[cols].iloc[:5]
    df["Name"] = df["Name"].apply(lambda x: x[:30])  # only display 21 characters
    return df_to_table(df)


# returns top 5 lost opportunities
def top_lost_opportunities(df):
    df = df[df["StageName"] == 'Closed Lost']
    cols = ["CreatedDate", "Name", "Amount", "StageName"]
    df = df[cols].sort_values("Amount", ascending=False).iloc[:5]
    df["Name"] = df["Name"].apply(lambda x: x[:30])  # only display 21 characters
    return df_to_table(df)


# returns modal (hidden by default)
def modal():
    return html.Div(
        html.Div(
            [
                html.Div(
                    [

                        # modal header
                        html.Div(
                            [
                                html.Span(
                                    "New Opportunity",
                                    style={
                                        "color": "#506784",
                                        "fontWeight": "bold",
                                        "fontSize": "20",
                                    },
                                ),
                                html.Span(
                                    "×",
                                    id="opportunities_modal_close",
                                    n_clicks=0,
                                    style={
                                        "float": "right",
                                        "cursor": "pointer",
                                        "marginTop": "0",
                                        "marginBottom": "17",
                                    },
                                ),
                            ],
                            className="row",
                            style={"borderBottom": "1px solid #C8D4E3"},
                        ),

                        # modal form
                        html.Div(
                            [

                                # left div
                                html.Div(
                                    [
                                        html.P(
                                            [
                                                "Name"
                                            ],
                                            style={
                                                "float": "left",
                                                "marginTop": "4",
                                                "marginBottom": "2",
                                            },
                                            className="row",
                                        ),
                                        dcc.Input(
                                            id="new_opportunity_name",
                                            placeholder="Name of the opportunity",
                                            type="text",
                                            value="",
                                            style={"width": "100%"},
                                        ),

                                        html.P(
                                            [
                                                "StageName"
                                            ],
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_opportunity_stage",
                                            options=[
                                                {
                                                    "label": "Prospecting",
                                                    "value": "Prospecting",
                                                },
                                                {
                                                    "label": "Qualification",
                                                    "value": "Qualification",
                                                },
                                                {
                                                    "label": "Needs Analysis",
                                                    "value": "Needs Analysis",
                                                },
                                                {
                                                    "label": "Value Proposition",
                                                    "value": "Value Proposition",
                                                },
                                                {
                                                    "label": "Id. Decision Makers",
                                                    "value": "Closed",
                                                },
                                                {
                                                    "label": "Perception Analysis",
                                                    "value": "Perception Analysis",
                                                },
                                                {
                                                    "label": "Proposal/Price Quote",
                                                    "value": "Proposal/Price Quote",
                                                },
                                                {
                                                    "label": "Negotiation/Review",
                                                    "value": "Negotiation/Review",
                                                },
                                                {
                                                    "label": "Closed/Won",
                                                    "value": "Closed Won",
                                                },
                                                {
                                                    "label": "Closed/Lost",
                                                    "value": "Closed Lost",
                                                },
                                            ],
                                            clearable=False,
                                            value="Prospecting",
                                        ),

                                        html.P(
                                            "Source",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_opportunity_source",
                                            options=[
                                                {"label": "Web", "value": "Web"},
                                                {
                                                    "label": "Phone Inquiry",
                                                    "value": "Phone Inquiry",
                                                },
                                                {
                                                    "label": "Partner Referral",
                                                    "value": "Partner Referral",
                                                },
                                                {
                                                    "label": "Purchased List",
                                                    "value": "Purchased List",
                                                },
                                                {"label": "Other", "value": "Other"},
                                            ],
                                            value="Web",
                                        ),

                                        html.P(
                                            [
                                                "Close Date"
                                            ],
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        html.Div(
                                            dcc.DatePickerSingle(
                                                id="new_opportunity_date",
                                                min_date_allowed=date.today(),
                                                # max_date_allowed=dt(2017, 9, 19),
                                                initial_visible_month=date.today(),
                                                date=date.today(),
                                            ),
                                            style={"textAlign": "left"},
                                        ),

                                    ],
                                    className="six columns",
                                    style={"paddingRight": "15"},
                                ),

                                # right div
                                html.Div(
                                    [
                                        html.P(
                                            "Type",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Dropdown(
                                            id="new_opportunity_type",
                                            options=[
                                                {
                                                    "label": "Existing Customer - Replacement",
                                                    "value": "Existing Customer - Replacement",
                                                },
                                                {
                                                    "label": "New Customer",
                                                    "value": "New Customer",
                                                },
                                                {
                                                    "label": "Existing Customer - Upgrade",
                                                    "value": "Existing Customer - Upgrade",
                                                },
                                                {
                                                    "label": "Existing Customer - Downgrade",
                                                    "value": "Existing Customer - Downgrade",
                                                },
                                            ],
                                            value="New Customer",
                                        ),

                                        html.P(
                                            "Amount",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Input(
                                            id="new_opportunity_amount",
                                            placeholder="0",
                                            type="number",
                                            value="",
                                            style={"width": "100%"},
                                        ),

                                        html.P(
                                            "Probability",
                                            style={
                                                "textAlign": "left",
                                                "marginBottom": "2",
                                                "marginTop": "4",
                                            },
                                        ),
                                        dcc.Input(
                                            id="new_opportunity_probability",
                                            placeholder="0",
                                            type="number",
                                            max=100,
                                            step=1,
                                            value="",
                                            style={"width": "100%"},
                                        ),

                                    ],
                                    className="six columns",
                                    style={"paddingLeft": "15"},
                                ),
                            ],
                            className="row",
                            style={"paddingTop": "2%"},
                        ),

                        # submit button
                        html.Span(
                            "Submit",
                            id="submit_new_opportunity",
                            n_clicks=0,
                            className="button button--primary add"
                        ),
                    ],
                    className="modal-content",
                    style={"textAlign": "center"},
                )
            ],
            className="modal",
        ),
        id="opportunities_modal",
        style={"display": "none"},
    )


layout = [

    # top controls
    html.Div(
        [
            # html.Div(
            #     dcc.Dropdown(
            #         id="converted_opportunities_dropdown",
            #         options=[
            #             {"label": "By day", "value": "D"},
            #             {"label": "By week", "value": "W-MON"},
            #             {"label": "By month", "value": "M"},
            #         ],
            #         value="D",
            #         clearable=False,
            #     ),
            #     className="two columns",
            # ),

            html.Div(
                dcc.Dropdown(
                    id="heatmap_dropdown",
                    options=[
                        {"label": "All stages", "value": "all_s"},
                        {"label": "Cold stages", "value": "cold"},
                        {"label": "Warm stages", "value": "warm"},
                        {"label": "Hot stages", "value": "hot"},
                    ],
                    value="all_s",
                    clearable=False,
                ),
                className="two columns",
            ),
            html.Div(
                dcc.Dropdown(
                    id="source_dropdown",
                    options=[
                        {"label": "All sources", "value": "all_s"},
                        {"label": "Web", "value": "Web"},
                        {"label": "Word of Mouth", "value": "Word of mouth"},
                        {"label": "Phone Inquiry", "value": "Phone Inquiry"},
                        {"label": "Partner Referral", "value": "Partner Referral"},
                        {"label": "Purchased List", "value": "Purchased List"},
                        {"label": "Other", "value": "Other"},
                    ],
                    value="all_s",
                    clearable=False,
                ),
                className="two columns",
            ),

            # add button
            html.Div(
                html.Span(
                    "Add new",
                    id="new_opportunity",
                    n_clicks=0,
                    className="button button--primary add"
                ),
                className="two columns",
                style={"float": "right"},
            ),
        ],
        className="row",
        style={"marginBottom": "10"},
    ),

    # indicators row
    html.Div(
        [
            indicator(
                "#00cc96",
                "Won opportunities",
                "left_opportunities_indicator",
            ),
            indicator(
                "#119DFF",
                "Open opportunities",
                "middle_opportunities_indicator",
            ),
            indicator(
                "#EF553B",
                "Lost opportunities",
                "right_opportunities_indicator",
            ),
        ],
        className="row",
    ),

    # charts row div
    html.Div(
        [
            html.Div(
                [
                    html.P("Converted Opportunities count"),
                    dcc.Graph(
                        id='Iris_left_Viz',

                    ),
                ],
                className="four columns chart_div",
            ),

            html.Div(
                [
                    html.P("Probabilty heatmap per Stage and Type"),
                    dcc.Graph(
                        id='Iris Viz',
                    ),
                ],
                className="eight columns chart_div"
            ),
        ],
        className="row",
        style={"marginTop": "5px"}
    ),

    # tables row div
    html.Div(
        [
            html.Div(
                [
                    # html.P(
                    #     "Top Open opportunities",
                    #     style={
                    #         "color": "#2a3f5f",
                    #         "fontSize": "13px",
                    #         "textAlign": "center",
                    #         "marginBottom": "0",
                    #     },
                    # ),
                    # html.Div(
                    #     id="top_open_opportunities",
                    #     style={"padding": "0px 13px 5px 13px", "marginBottom": "5"},
                    # ),

                ],
                className="six columns",
                style={
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px",
                    "height": "100%",
                    "overflowY": "scroll",
                },
            ),
            html.Div(
                [
                    # html.P(
                    #     "Top Lost opportunities",
                    #     style={
                    #         "color": "#2a3f5f",
                    #         "fontSize": "13px",
                    #         "textAlign": "center",
                    #         "marginBottom": "0",
                    #     },
                    # ),
                    # html.Div(
                    #     id="top_lost_opportunities",
                    #     style={"padding": "0px 13px 5px 13px", "marginBottom": "5"},
                    # )
                ],
                className="six columns",
                style={
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px",
                    "height": "100%",
                    "overflowY": "scroll",
                },
            ),

            modal(),
        ],
        className="row",
        style={"marginTop": "5px", "max height": "200px"},
    ),
]

#
# # updates heatmap figure based on dropdowns values or df updates
@app.callback(
    Output("Iris_left_Viz", "figure")
    # [Input("heatmap_dropdown", "value"), Input("opportunities_df", "children")],
)
# def heat_map_callback(stage, df):
def heat_map_callback(df):
    # df = pd.read_json(df, orient="split")
    # df = df[pd.notnull(df["Type"])]
    # x = []
    # y = df["Type"].unique()
    # if stage == "all_s":
    #     x = df["StageName"].unique()
    # elif stage == "cold":
    #     x = ["Needs Analysis", "Prospecting", "Qualification"]
    # elif stage == "warm":
    #     x = ["Value Proposition", "Id. Decision Makers", "Perception Analysis"]
    # else:
    #     x = ["Proposal/Price Quote", "Negotiation/Review", "Closed Won"]
    return heat_map_fig(df)


# # updates converted opportunity count graph based on dropdowns values or df updates
# @app.callback(
#     Output("converted_count", "figure"),
#     [
#         Input("converted_opportunities_dropdown", "value"),
#         Input("source_dropdown", "value"),
#         Input("opportunities_df", "children"),
#     ],
# )
# def converted_opportunity_callback(period, source, df):
#     df = pd.read_json(df, orient="split")
#     return converted_opportunities(period, source, df)
#
#
# # updates left indicator value based on df updates
# @app.callback(
#     Output("left_opportunities_indicator", "children"),
#     [Input("opportunities_df", "children")],
# )
# def left_opportunities_indicator_callback(df):
#     df = pd.read_json(df, orient="split")
#     won = millify(str(df[df["IsWon"] == 1]["Amount"].sum()))
#     return won
#
#
# # updates middle indicator value based on df updates
# @app.callback(
#     Output("middle_opportunities_indicator", "children"),
#     [Input("opportunities_df", "children")],
# )
# def middle_opportunities_indicator_callback(df):
#     df = pd.read_json(df, orient="split")
#     active = millify(
#         str(df[(df["IsClosed"] == 0)]["Amount"].sum())
#     )
#     return active
#
#
# # updates right indicator value based on df updates
# @app.callback(
#     Output("right_opportunities_indicator", "children"),
#     [Input("opportunities_df", "children")],
# )
# def right_opportunities_indicator_callback(df):
#     df = pd.read_json(df, orient="split")
#     lost = millify(
#         str(
#             df[
#                 (df["IsWon"] == 0) & (df["IsClosed"] == 1)
#                 ]["Amount"].sum()
#         )
#     )
#     return lost
#
#
# # hide/show modal
# @app.callback(
#     Output("opportunities_modal", "style"), [Input("new_opportunity", "n_clicks")]
# )
# def display_opportunities_modal_callback(n):
#     if n > 0:
#         return {"display": "block"}
#     return {"display": "none"}
#
#
# # reset to 0 add button n_clicks property
# @app.callback(
#     Output("new_opportunity", "n_clicks"),
#     [
#         Input("opportunities_modal_close", "n_clicks"),
#         Input("submit_new_opportunity", "n_clicks"),
#     ],
# )
# def close_modal_callback(n, n2):
#     return 0
#
#
# # add new opportunity to salesforce and stores new df in hidden div
# @app.callback(
#     Output("opportunities_df", "children"),
#     [Input("submit_new_opportunity", "n_clicks")],
#     [
#         State("new_opportunity_name", "value"),
#         State("new_opportunity_stage", "value"),
#         State("new_opportunity_amount", "value"),
#         State("new_opportunity_probability", "value"),
#         State("new_opportunity_date", "date"),
#         State("new_opportunity_type", "value"),
#         State("new_opportunity_source", "value"),
#         State("opportunities_df", "children"),
#     ],
# )
# def add_opportunity_callback(
#         n_clicks, name, stage, amount, probability, date, o_type, source, current_df
# ):
#     if n_clicks > 0:
#         if name == "":
#             name = "Not named yet"
#         query = {
#             "Name": name,
#             "StageName": stage,
#             "Amount": amount,
#             "Probability": probability,
#             "CloseDate": date,
#             "Type": o_type,
#             "LeadSource": source,
#         }
#
#         sf_manager.add_opportunity(query)
#
#         df = sf_manager.get_opportunities()
#
#         return df.to_json(orient="split")
#
#     return current_df
#
#
# # updates top open opportunities based on df updates
# @app.callback(
#     Output("top_open_opportunities", "children"),
#     [Input("opportunities_df", "children")],
# )
# def top_open_opportunities_callback(df):
#     df = pd.read_json(df, orient="split")
#     return top_open_opportunities(df)
#
#
# # updates top lost opportunities based on df updates
# @app.callback(
#     Output("top_lost_opportunities", "children"),
#     [Input("opportunities_df", "children")],
# )
# def top_lost_opportunities_callback(df):
#     df = pd.read_json(df, orient="split")
#     return top_lost_opportunities(df)