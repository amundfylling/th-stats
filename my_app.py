import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np


# Load the DataFrame
df = pd.read_csv('all_matches_df.csv')

# Drop rows with errors in player columns
df.dropna(subset=['Player1', 'Player2'], inplace=True)

# Convert to datetime
df['Date'] = pd.to_datetime(df['Date'])


# Get a list of unique player names
player_names = pd.concat([df['Player1'], df['Player2']]).unique()

def generate_player_stats(selected_player, selected_stage):
    # Filter the DataFrame to include only games played by the selected player
    df_player = df[(df['Player1'] == selected_player) | (df['Player2'] == selected_player)]
    df_stage = df_player[df_player['Stage'] == selected_stage]

    total_games = len(df_stage)
    games_won = len(df_stage[(df_stage['Player1'] == selected_player) & (df_stage['GoalsPlayer1'] > df_stage['GoalsPlayer2'])]) \
        + len(df_stage[(df_stage['Player2'] == selected_player) & (df_stage['GoalsPlayer2'] > df_stage['GoalsPlayer1'])])
    games_lost = len(df_stage[(df_stage['Player1'] == selected_player) & (df_stage['GoalsPlayer1'] < df_stage['GoalsPlayer2'])]) \
        + len(df_stage[(df_stage['Player2'] == selected_player) & (df_stage['GoalsPlayer2'] < df_stage['GoalsPlayer1'])])
    games_drawn = len(df_stage[df_stage['GoalsPlayer1'] == df_stage['GoalsPlayer2']])
    total_goals_scored = df_stage[df_stage['Player1'] == selected_player]['GoalsPlayer1'].sum() + df_stage[df_stage['Player2'] == selected_player]['GoalsPlayer2'].sum()
    total_goals_conceded = df_stage[df_stage['Player1'] == selected_player]['GoalsPlayer2'].sum() + df_stage[df_stage['Player2'] == selected_player]['GoalsPlayer1'].sum()
    avg_goals_scored = round(total_goals_scored / total_games, 2) if total_games > 0 else 0
    avg_goals_conceded = round(total_goals_conceded / total_games, 2) if total_games > 0 else 0

    stats_data = [
        {
            'Statistic': 'Total games played',
            selected_stage: total_games,
        },
        {
            'Statistic': 'Games won',
            selected_stage: games_won,
        },
        {
            'Statistic': 'Games lost',
            selected_stage: games_lost,
        },
        {
            'Statistic': 'Games drawn',
            selected_stage: games_drawn,
        },
        {
            'Statistic': 'Total goals scored',
            selected_stage: total_goals_scored,
        },
        {
            'Statistic': 'Total goals conceded',
            selected_stage: total_goals_conceded,
        },
        {
            'Statistic': 'Average goals scored per game',
            selected_stage: avg_goals_scored,
        },
        {
            'Statistic': 'Average goals conceded per game',
            selected_stage: avg_goals_conceded,
        },
    ]
    
    stats_table = dash_table.DataTable(
        data=stats_data,
        columns=[{'name': col, 'id': col} for col in stats_data[0].keys()],
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left'},
        style_data_conditional=[
            {'if': {'column_id': 'Round Robin'}, 'textAlign': 'right'},
            {'if': {'column_id': 'Playoff'}, 'textAlign': 'right'}
        ],
        style_table={'maxWidth': '500px', 'margin': 'auto'},
        style_cell_conditional=[
            {'if': {'column_id': 'Statistic'}, 'width': '40%'},
            {'if': {'column_id': 'Round Robin'}, 'width': '30%'},
            {'if': {'column_id': 'Playoff'}, 'width': '30%'}
        ]
    )

    return [
        stats_table
    ]
    
external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/lux/bootstrap.min.css']
dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
app = dash_app.server

dash_app.layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dcc.Link('Player Statistics', href='/page-1', className='nav-link')),
            dbc.NavItem(dcc.Link('Head-to-Head Analysis', href='/page-2', className='nav-link')),
        ],
        brand='Table Hockey Statistics',
        color='primary',
        dark=True,
        expand='lg'
    ),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    dcc.Link('Go to Statistics', href='/page-1'),
    html.Br(),
    dcc.Link('Go to Head-to-Head Analysis', href='/page-2'),
])

page_1_layout = html.Div([
    html.H1('Player Statistics'),
    dcc.Dropdown(
        id='player-dropdown',
        options=[{'label': i, 'value': i} for i in player_names],
        value=player_names[0],
        style={'width': '300px'},
    ),
    dcc.RadioItems(
        id='stage-radio-items',
        options=[{'label': i, 'value': i} for i in ['Round Robin', 'Playoff']],
        value='Round Robin',
        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
    ),
    html.Div(id='player-stats', style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'margin-top': '70px', 'margin-left': '20px'}),
    html.Div([
        dcc.Graph(id='win-draw-loss-plot', config={'displayModeBar': False}),
        dcc.RadioItems(
            id='win-loss-type',
            options=[{'label': 'Total', 'value': 'total'}, {'label': 'Overtime', 'value': 'overtime'}],
            value='total',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
            style={'display': 'none'}  # Initially hide the radio button
        )
    ], style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'top', 'float': 'right', 'margin-top': '10px', 'margin-right': '10px', 'margin_left': '10px'}),
])

page_2_layout = html.Div([
    html.H1('Head-to-Head Analysis'),
    dcc.Dropdown(
        id='player1-dropdown',
        options=[{'label': i, 'value': i} for i in player_names],
        placeholder='Select Player 1',
        style={'width': '300px'}
    ),
    dcc.Dropdown(
        id='player2-dropdown',
        options=[{'label': i, 'value': i} for i in player_names],
        placeholder='Select Player 2',
        style={'width': '300px'}
    ),
    dcc.Graph(id='head-to-head-plot', config={'displayModeBar': False}),
    html.Div(id='stage-info', style={'padding-top': '20px', 'padding-bottom': '20px', 'display': 'none'}),
    html.Div(id='matches-table', style={'padding-bottom': '20px'}),
], style={'margin': '5px'})



@dash_app.callback(Output('player-stats', 'children'),
              Output('win-draw-loss-plot', 'figure'),
              [Input('player-dropdown', 'value'),
               Input('stage-radio-items', 'value'),
               Input('win-loss-type', 'value')])
def update_graph_and_stats(selected_player, selected_stage, win_loss_type):
    df_player = df[(df['Player1'] == selected_player) | (df['Player2'] == selected_player)]
    df_selected = df_player[df_player['Stage'] == selected_stage]

    if win_loss_type == 'overtime':
        df_selected = df_selected[df_selected['Overtime'] == 'Yes']

    wins = len(df_selected[(df_selected['Player1'] == selected_player) & (df_selected['GoalsPlayer1'] > df_selected['GoalsPlayer2'])]) \
        + len(df_selected[(df_selected['Player2'] == selected_player) & (df_selected['GoalsPlayer2'] > df_selected['GoalsPlayer1'])])
    draws = len(df_selected[df_selected['GoalsPlayer1'] == df_selected['GoalsPlayer2']])
    losses = len(df_selected[(df_selected['Player1'] == selected_player) & (df_selected['GoalsPlayer1'] < df_selected['GoalsPlayer2'])]) \
        + len(df_selected[(df_selected['Player2'] == selected_player) & (df_selected['GoalsPlayer2'] < df_selected['GoalsPlayer1'])])

    data = go.Bar(x=['Wins', 'Draws', 'Losses'], y=[wins, draws, losses])

    layout = go.Layout(
        autosize=True,
        margin=dict(
            l=50,
            r=50,
            b=50,
            t=0,
            pad=10
        )
    )

    stats = generate_player_stats(selected_player, selected_stage)

    return stats, {'data': [data], 'layout': layout}

@dash_app.callback(
    Output('head-to-head-plot', 'figure'),
    [Input('player1-dropdown', 'value'),
     Input('player2-dropdown', 'value')]
)
def update_head_to_head_plot(player1, player2):
    df_filtered = df[((df['Player1'] == player1) & (df['Player2'] == player2)) | ((df['Player1'] == player2) & (df['Player2'] == player1))]
    min_year = df_filtered['Date'].dt.year.min()
    max_year = df_filtered['Date'].dt.year.max()
    years = list(range(2010, pd.Timestamp.now().year + 1))

    win_rates_player1 = []
    win_rates_player2 = []
    draw_rates = []

    for year in years:
        matches_year = df_filtered[df_filtered['Date'].dt.year == year]
        total_matches = len(matches_year)
        wins_player1 = len(matches_year[(matches_year['Player1'] == player1) & (matches_year['GoalsPlayer1'] > matches_year['GoalsPlayer2'])]) \
            + len(matches_year[(matches_year['Player2'] == player1) & (matches_year['GoalsPlayer2'] > matches_year['GoalsPlayer1'])])
        wins_player2 = len(matches_year[(matches_year['Player1'] == player2) & (matches_year['GoalsPlayer1'] > matches_year['GoalsPlayer2'])]) \
            + len(matches_year[(matches_year['Player2'] == player2) & (matches_year['GoalsPlayer2'] > matches_year['GoalsPlayer1'])])
        draws = total_matches - wins_player1 - wins_player2

        if total_matches > 0:
            win_rate_player1 = (wins_player1 / total_matches) * 100
            win_rate_player2 = (wins_player2 / total_matches) * 100
            draw_rate = (draws / total_matches) * 100
        else:
            win_rate_player1 = 0
            win_rate_player2 = 0
            draw_rate = 0

        win_rates_player1.append(win_rate_player1)
        win_rates_player2.append(win_rate_player2)
        draw_rates.append(draw_rate)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years,
        y=win_rates_player1,
        name=player1,
        marker_color='lightskyblue'
    ))
    fig.add_trace(go.Bar(
        x=years,
        y=win_rates_player2,
        name=player2,
        marker_color='lightcoral'
    ))
    fig.add_trace(go.Bar(
        x=years,
        y=draw_rates,
        name='Draw',
        marker_color='lightgray'
    ))

    fig.update_layout(
        title='',
        xaxis={'title': 'Year', 'range': [min_year-1, max_year+1]},
        yaxis={'title': 'Win Rate (%)'},
        barmode='stack',
        legend={'x': 1, 'y': 1},
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return fig

@dash_app.callback(
    Output('matches-table', 'children'),
    [Input('head-to-head-plot', 'clickData'),
     Input('player1-dropdown', 'value'),
     Input('player2-dropdown', 'value')]
)
def display_match_data(clickData, player1, player2):
    if clickData:
        year = clickData['points'][0]['x']
        df_filtered_year = df[(df['Date'].dt.year == year) & (((df['Player1'] == player1) & (df['Player2'] == player2)) | ((df['Player1'] == player2) & (df['Player2'] == player1)))]
        
        df_filtered_year['Date'] = df_filtered_year['Date'].dt.strftime('%Y-%m-%d')

        return html.Div([
            dash_table.DataTable(
                data=df_filtered_year.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df_filtered_year.columns],
                style_table={'width': '80%', 'margin': 'auto'},
            )
        ])
    else:
        return 'Click on a bar to view match data'

@dash_app.callback(
    Output('stage-info', 'children'),
    Output('stage-info', 'style'),
    Input('head-to-head-plot', 'clickData'),
)
def show_stage_info(clickData):
    if clickData:
        return (
            [html.P('To see the matches of a specific tournament stage, insert the stage ID into the following URL:'),
            html.P(html.A('http://th.sportscorpion.com/eng/tournament/stage/{stageid}/matches/', 
                          href='http://th.sportscorpion.com/eng/tournament/stage/{stageid}/matches/', 
                          target="_blank"))],
            {'padding-top': '20px', 'padding-bottom': '20px'}
        )
    else:
        return None, {'display': 'none'}


@dash_app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return page_1_layout 

if __name__ == '__main__':
    dash_app.run_server(debug=False)