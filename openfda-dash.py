import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
import plotly.graph_objs as go
from datetime import datetime
import dash_table_experiments as dt
import pandas as pd
import requests
import json

openfdakey = 'NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H'
initial_rows = []

external_css = [
    # dash stylesheet
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://fonts.googleapis.com/css?family=Lobster|Raleway",
]
#Conversion arrays for 'term' int values
primarysources = {1:'Physician',2:'Pharmacist',3:'Health Professional',4:'Lawyer',5:'Non-health Professional'}
gender = {0:'Unknown',1:'Male',2:'Female'}
theme = {
    "font-family": "Raleway",
    # 'background-color': '#787878',
    "background-color": "#e0e0e0",
}

def get_results(url):
    response = requests.get(url)
    if response.ok:
        d = json.loads(response.text)
        results = d["results"]
    else:
        results = []
    return results


app = dash.Dash()

colors = {
    #'background': '#111111',
    'text': '#0040ff'  #'#7FDBFF'
}

app.layout = html.Div([
                html.H1(
                    children='OPEN FDA Adverse Effects',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    }
                ),
                html.Div([html.H3('Drug Selection:',style={'paddingRight':'30px'}),
                   dcc.Input(id='my_drug_picker',
                             value='VICTOZA',
                             style={'fontSize':24,'width':150})
               ],style={'display':'inline-block','verticalAlign':'top'}),

               html.Div([
                        html.Button(id='submit-button',
                                   n_clicks=0,
                                   children='Submit',
                                   style={'fontSize':24,'marginLeft':'70px'}
                        )
                ],style={'display':'inline-block','verticalAlign':'top'}),

               # Date picker not used yet
               # html.Div([html.H3('Select a start and end date:'),
               #            dcc.DatePickerRange(id ='my_date_picker',
               #                    min_date_allowed = datetime(2013,1,1),
               #                    max_date_allowed = datetime.today(),
               #                    start_date = datetime(2018,1,1),
               #                    end_date = datetime.today()
               #            )
               #   ],style={'display':'inline-block'}),


               html.Div([
                       dcc.Graph(id='my_graph',
                                 figure={'data':[
                                     {'x':[1,2],'y':[3,1]}
                                 ],
                                 'layout':{'Title': 'Primary Sources'}},
                                  className="six columns"
                       )
              ], style={'width': '54%', 'display': 'inline-block'}),
              html.Div(
                children=[
                   #html.Div(dcc.Graph(id="pie-primarysources"), className="six columns"),
                   html.Div(dcc.Graph(id="pie-primarysources"),  className="six columns")
                ],
               # className="row",
               style={'width': '44%', 'display': 'inline-block','margin-bottom': 20},
               ),
               html.Div([
                        dcc.Graph(id='graph2',
                                  figure={'data':[
                                      {'x':[1,2],'y':[3,1]}
                                  ],
                                  'layout':{'Title': 'Gender'}},
                                   className="four columns"
                        )
               ], style={'width': '54%', 'display': 'inline-block'}),
               html.Div(
                 children=[
                    html.Div(dcc.Graph(id="pie-gender"))
                 ],
                # className="row",
                style={'width': '44%', 'display': 'inline-block','margin-bottom': 20}
                ),
                html.Div([
                         dcc.Graph(id='scatter-serious',
                                   figure={'data':[
                                       {'x':[1,2],'y':[3,1]}
                                   ],
                                   'layout':{'Title': 'Seriousness'}},
                                    className="four columns"
                         )
                ], style={'width': '48%', 'display': 'inline-block'}),
                html.Div(
                   children=[
                       html.Div(dcc.Graph(id="pie-serious"))
                   ],
                  # className="row",
                  style={'width': '44%', 'display': 'inline-block','margin-bottom': 20},
                ),
                html.Hr(),
                html.Div([
                    html.H2(
                        children='Adverse Effects',
                        style={
                            'textAlign': 'center',
                            'color': colors['text']
                        }
                    )
                ]),
                html.Div([
                    dt.DataTable(
                        # table with dash_table_experiments
                        id="table-fda",
                        rows=[{}],
                        filterable=True,
                        sortable=True,
                    )

                ])

])


@app.callback(Output('my_graph', 'figure'),
              [Input('submit-button','n_clicks')],
              [State('my_drug_picker', 'value')])
def update_primarysource_plot(n_clicks,selected_drug):

    if (selected_drug):
        #url = 'https://api.fda.gov/drug/event.json?count=primarysource.qualification'
        url = 'https://api.fda.gov/drug/event.json?search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=primarysource.qualification'.format(selected_drug)
    else:
        url = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=primarysource.qualification'

    results = get_results(url)
    print('Primary Sources',results)
    df = pd.DataFrame(results, columns=['term', 'count'])

    df['titles'] = df['term'].map(primarysources)
    df = df.sort_values('term', ascending=False)

    print(df)

    fig = {'data':[go.Scatter(x=df['count'],
                              y=df['titles'],
                              mode='markers',
                              opacity=0.7,
                              marker=dict(
                                 size=16,
                                 color='rgba(0, 0, 152, .8)'
                  ))]
        ,'layout':go.Layout(title='Primary Sources')
         }
    return fig

@app.callback(Output('pie-primarysources', 'figure'),
              [Input('submit-button','n_clicks')],
              [State('my_drug_picker', 'value')])
# @cache.memoize(timeout=30)  # in seconds (pickle.dump fails)
def update_primarysource_pie(n_clicks,selected_drug):
    if (selected_drug):
        url = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=primarysource.qualification'.format(selected_drug)
    else:
        url = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=primarysource.qualification'

    results = get_results(url)

    df = pd.DataFrame(results, columns=['term', 'count'])
    df['titles'] = df['term'].map(primarysources)

    data = [
        go.Pie(
            name="Primary Sources",
            values=df['count'],
            labels=df['titles'],
            hoverinfo="label + percent + name",
            hole=0.35,
            # showlegend=False,
        )
    ]
    layout = go.Layout(
        title="Primary Sources",
        autosize=True,
        hovermode="closest",
        font=dict(family=theme["font-family"], color="#777777", size=24)
        # 'height': 800,
        # 'margin': {'l': 10, 'b': 20, 't': 0, 'r': 0}

    )
    figure = go.Figure(data=data, layout=layout)
    return figure

@app.callback(Output('pie-gender', 'figure'),
              [Input('submit-button','n_clicks')],
              [State('my_drug_picker', 'value')])
    #output=Output("pie-gender", "figure"), inputs=[Input('my_drug_picker', 'value')]

# @cache.memoize(timeout=30)  # in seconds (pickle.dump fails)
def update_gender_pie(n_clicks,selected_drug):

    if (selected_drug):
        url = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=patient.patientsex'.format (selected_drug)
    else:
        url = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=patient.patientsex'

    results = get_results(url)
    df2 = pd.DataFrame(results, columns=['term', 'count'])
    df2['gender'] = df2['term'].map(gender)
    df2 = df2.sort_values('term', ascending=False)

    data = [
        go.Pie(
            name="Gender",
            values=df2['count'],
            labels=df2['gender'],
            hoverinfo="label + percent + name",
            hole=0.35,
            # showlegend=False,
        )
    ]
    layout = go.Layout(
        title="Gender",
        autosize=True,
        hovermode="closest",
        font=dict(family=theme["font-family"], color="#777777", size=24),
    )
    figure = go.Figure(data=data, layout=layout)
    return figure

@app.callback(Output('graph2', 'figure'),
                  [Input('submit-button','n_clicks')],
                  [State('my_drug_picker', 'value')])
def update_gender_plot(n_clicks,selected_drug):

    if (selected_drug):
        url = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=patient.patientsex'.format (selected_drug)
    else:
        url = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=patient.patientsex'
    results = get_results(url)
    print(results)
    df2 = pd.DataFrame(results, columns=['term', 'count'])
    df2['gender'] = df2['term'].map(gender)
    df2 = df2.sort_values('term', ascending=False)
    #data = resp.json()
    fig = {'data':[go.Scatter(x=df2['count'],
                              y=df2['gender'],
                              mode='markers',
                              opacity=0.7,
                              marker=dict(
                                 size=16,
                                 color='rgba(0, 152, 0, .8)'
                   ))]
        ,'layout':go.Layout(title='Gender',
                            hovermode="closest",
                            font=dict(family=theme["font-family"], color="#777777", size=24)
                            )
    }
    return fig

@app.callback(Output('scatter-serious', 'figure'),
                  [Input('submit-button','n_clicks')],
                  [State('my_drug_picker', 'value')])
def update_serious_plot(n_clicks,selected_drug):

     if (selected_drug):

         url1 = 'https://api.fda.gov/drug/event.json?search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=seriousnessdeath'.format(selected_drug)
         url2 = 'https://api.fda.gov/drug/event.json?search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=seriousnesshospitalization'.format(selected_drug)
         url3 = 'https://api.fda.gov/drug/event.json?search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=seriousnessdisabling'.format(selected_drug)
         url4 = 'https://api.fda.gov/drug/event.json?search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=seriousnesslifethreatening'.format(selected_drug)
         url5 = 'https://api.fda.gov/drug/event.json?search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=seriousnessother'.format(selected_drug)

     else:
         url1 = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=seriousnessdeath'
         url2 = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=seriousnesshospitalization'
         url3 = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=seriousnessdisabling'
         url4 = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=seriousnesslifethreatening'
         url5 = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=seriousnessother'

     results1 = get_results(url1)

     rows = list()
     for res in results1:
       row = {
           "Term": 'Death',
           "Count": res["count"]
       }
       rows.append(row)

     results2 = get_results(url2)
     for res in results2:
       row = {
           "Term": 'Hospitalization',
           "Count": res["count"]
       }
       rows.append(row)

     results3 = get_results(url3)
     for res in results3:
       row = {
           "Term": 'Disabling',
           "Count": res["count"]
       }
       rows.append(row)

     results4 = get_results(url4)
     for res in results4:
       row = {
           "Term": 'Life Threatening',
           "Count": res["count"]
       }
       rows.append(row)

     results5 = get_results(url5)
     for res in results5:
       row = {
           "Term": 'Other',
           "Count": res["count"]
       }
       rows.append(row)

     print(rows)

     df3 = pd.DataFrame(rows, columns=['Term', 'Count'])


     fig = {'data':[go.Scatter(x=df3['Term'],
                                  y=df3['Count'],
                                  mode='markers',
                                  opacity=0.7,
                                  marker=dict(
                                     size=16,
                                     color='rgba(152, 0, 0, .8)'
                       ))]
            ,'layout':go.Layout(title='Seriousness',
                                hovermode="closest",
                                font=dict(family=theme["font-family"], color="#777777", size=24)
                                )
     }
     return fig

@app.callback(Output('pie-serious', 'figure'),
                  [Input('submit-button','n_clicks')],
                  [State('my_drug_picker', 'value')])
    #output=Output("pie-serious", "figure"), inputs=[Input('my_drug_picker', 'value')]

# @cache.memoize(timeout=30)  # in seconds (pickle.dump fails)
def update_serious_pie(n_clicks,selected_drug):

    if (selected_drug):

        url1 = 'https://api.fda.gov/drug/event.json?search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=seriousnessdeath'.format(selected_drug)
        url2 = 'https://api.fda.gov/drug/event.json?search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=seriousnesshospitalization'.format(selected_drug)
        url3 = 'https://api.fda.gov/drug/event.json?search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=seriousnessdisabling'.format(selected_drug)
        url4 = 'https://api.fda.gov/drug/event.json?search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=seriousnesslifethreatening'.format(selected_drug)
        url5 = 'https://api.fda.gov/drug/event.json?search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=seriousnessother'.format(selected_drug)

    else:
        url1 = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=seriousnessdeath'
        url2 = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=seriousnesshospitalization'
        url3 = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=seriousnessdisabling'
        url4 = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=seriousnesslifethreatening'
        url5 = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&count=seriousnessother'

    results1 = get_results(url1)

    rows = list()
    for res in results1:
       row = {
           "Term": 'Death',
           "Count": res["count"]
       }
       rows.append(row)

    results2 = get_results(url2)
    for res in results2:
       row = {
           "Term": 'Hospitalization',
           "Count": res["count"]
       }
       rows.append(row)

    results3 = get_results(url3)
    for res in results3:
       row = {
           "Term": 'Disabling',
           "Count": res["count"]
       }
       rows.append(row)

    results4 = get_results(url4)
    for res in results4:
       row = {
           "Term": 'Life Threatening',
           "Count": res["count"]
       }
       rows.append(row)

    results5 = get_results(url5)
    for res in results5:
       row = {
           "Term": 'Other',
           "Count": res["count"]
       }
       rows.append(row)

    df3 = pd.DataFrame(rows, columns=['Term', 'Count'])

    data = [
        go.Pie(
            name="Seriousness",
            values=df3['Count'],
            labels=df3['Term'],
            hoverinfo="label + percent + name",
            hole=0.35,
            # showlegend=False,
        )
    ]
    layout = go.Layout(
        title="Seriousness",
        autosize=True,
        hovermode="closest",
        font=dict(family=theme["font-family"], color="#777777", size=24),
    )
    figure = go.Figure(data=data, layout=layout)
    return figure



@app.callback(Output('table-fda', 'rows'),
                  [Input('submit-button','n_clicks')],
                  [State('my_drug_picker', 'value')])

#@cache.memoize(timeout=30)  # in seconds
def update_table(n_clicks,selected_drug):

    if (selected_drug):
        url = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&search=_exists_:(patient.reaction.reactionmeddrapt.exact)+AND+patient.drug.openfda.brand_name:({})&count=patient.reaction.reactionmeddrapt.exact'.format (selected_drug)
    else:
        url = 'https://api.fda.gov/drug/event.json?api_key=NmPuF5e95qXX9gj59DGfG5g2EACkGnfzXP09Xb3H&search=_exists_:(patient.reaction.reactionmeddrapt.exact)&count=patient.reaction.reactionmeddrapt.exact'

    results = get_results(url)
    rows = list()
    for res in results:
        row = {
            "Preferred Term": res["term"],
            "Count": res["count"]
        }
        rows.append(row)
    return rows


if __name__ =='__main__':
    app.run_server(debug=True)
