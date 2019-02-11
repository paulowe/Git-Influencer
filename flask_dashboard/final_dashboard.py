#######
#The final dashboard for dash app
######
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import pymysql
import pymysql.cursors
import os
import flask
from flask import jsonify

#initial dash obj
app = dash.Dash()

#lanugages and tables are all named like this list
languages = ['C','Cplus','Csharp','Go','Java','JavaScript','Perl','PHP','Python','Python','Ruby','Scala','Shell']
#initial the app layout
app.layout = html.Div([


        html.Img(src='https://storage.googleapis.com/pics-insight/pagerankcats.png',
                 style={
                'maxWidth': '50%',
                'maxHeight': '50%',
                'marginLeft': 'auto',
                'marginRight': 'auto'
            }
        ),

        html.H1(
           children='Git Influencer',
           style={
               'textAlign': 'center',
               #'background':'rgb(240,255,255)',
               'color': 'Black'
               #'background': 'darkblue'
           }
        ),
        html.H3(
           children='Help you find people to follow on github for your interest language. ',
           style={
               'textAlign': 'center'
           }
        ),

        html.Label(' Select your interest Language'),
        html.Div([
            dcc.Dropdown(
                id='language',
                options=[{'label': i, 'value': i} for i in languages],
                value='Select your interest language'
            )
        ],
        style={'width': '30%', 'display': 'inline-block'}),

        html.Label('  Select top number of users'),
        html.Div([
            dcc.Dropdown(
                id='topN',
                options=[{'label': i, 'value': i} for i in range(5,26)],
                value='Select the top user number'
            )
        ],style={'width': '38%', 'display': 'inline-block'}),
        html.Div(
        ' ',
        style={'color':'blue', 'padding':10, 'width':600}
    ),

    dcc.Graph(id='barplot-pagerank'),
    html.Div(
    ' ',
    style={'color':'blue', 'padding':10, 'width':600}
),
    html.Div(id = 'github-link'),

    html.Div(
    ' ',
    style={'color':'blue', 'padding':10, 'width':1200}
)
],
    style={
            'border': 'lightblue',
            'padding':20,
            'width': '100%',
            'float': 'left'})

#call back function for updating the external link of user's github page
@app.callback(
    Output('github-link', 'children'),
    [Input('barplot-pagerank', 'hoverData')])
def callback_githublink(hoverData):

    githubusername = hoverData['points'][0]['text']
    #print(githubusername)

    redirect_url = 'https://github.com/'+ githubusername
    markdown = '[_______________________________________Follow {} on github]({})'.format(githubusername,redirect_url)
    #print('url',redirect_url )

    obj = dcc.Markdown(children = markdown)
    return obj


#call back function for updating the barplot
@app.callback(
    Output('barplot-pagerank', 'figure'),
    [Input('language', 'value'),
     Input('topN', 'value')])
def update_graph( xaxis_name, yaxis_name):
    mysql_host = os.environ['MYSQL_HOST']
    mysql_username = os.environ['MYSQL_USERNAME']
    mysql_password = os.environ['MYSQL_PASSWORD']

    # Get DATA from mysql db
    connection = pymysql.connect(host = mysql_host,
                                 user = mysql_username,
                                 password = mysql_password,
                                 db = 'detail',
                                 charset = 'utf8mb4',
                                 cursorclass = pymysql.cursors.DictCursor)

    cursor = connection.cursor()
    #select by input
    #select_table,topN = 'Scala', 20
    #select top 2 users by their pange rank rating
    cursor.execute("SELECT user_id, user_rank FROM {} ORDER BY user_rank  LIMIT {}".format(xaxis_name, yaxis_name))
    data = cursor.fetchall()
    #grab username and userrank from data list
    user_list = []
    user_detail_list = []
    normalize_num = int(data[0]['user_rank'])
    for i in range(len(data)):
        user_list.append(data[i]['user_id'])
        user_detail_list.append(float(normalize_num)/(data[i]['user_rank']))

    return {
        'data': [go.Bar(
            x=user_list,
            y=user_detail_list,
            text=user_list,
            opacity= 0.5

        )],
        'layout': go.Layout(
            title='{} User to follow based on pagerank score'.format(xaxis_name),
            xaxis={'title': 'Github Username'},
            yaxis={'title': 'Normalized Pagerank'},
            margin={'l': 60, 'b': 40, 't': 50, 'r': 60},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            paper_bgcolor='rgb(173,216,230)',
            plot_bgcolor='rgb(240,248,255)'

        )
    }

if __name__ == '__main__':
    app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
    app.run_server()
