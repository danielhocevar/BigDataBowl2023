import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

full_auc_df = pd.read_csv('figure6.csv')
team_dict = {'SF': '49ers', 'CHI': 'bears', 'CIN': 'bengals', 'CIN': 'bengals', 'BUF': 'bills', 'DEN': 'broncos', 'CLE': 'browns', 'TB': 'buccaneers', 'ARI': 'cardinals', 'LAC': 'chargers', 'KC': 'chiefs', 'IND': 'colts', 'DAL': 'cowboys', 'MIA': 'dolphins', 'PHI': 'eagles', 'ATL': 'falcons', 'NYG': 'giants', 'JAX': 'jaguars', 'NYJ': 'jets', 'DET': 'lions', 'GB': 'packers', 'CAR': 'panthers', 'NE': 'patriots', 'LV': 'raiders', 'LA': 'rams', 'BAL': 'ravens', 'WAS': 'commanders', 'NO': 'saints', 'SEA': 'seahawks', 'PIT': 'steelers', 'HOU': 'texans', 'TEN': 'titans', 'MIN': 'vikings'}

fig = go.Figure(data=go.Scatter(x=full_auc_df['off_auc_above_median'], y=full_auc_df['def_auc_above_median'], mode='markers', customdata=full_auc_df, fill='none'))

fig.update_traces(
    hovertemplate="<br> Team: %{customdata[1]} <br> OPLE: %{customdata[2]:.2f} <br> DPLE: %{customdata[4]:.2f}",
    marker=dict(size=1)
)

fig.add_hline(y=0, line_color="black", opacity=0.3)
fig.add_vline(x=0, line_color="black", opacity=0.3)
fig.update_xaxes(range = [-0.45,0.45])
fig.update_yaxes(range = [-0.45,0.45])

fig.update_layout(
    autosize=False,
    width=800,
    height=800,
    xaxis_title="Offensive Line Performance Above Average",
    yaxis_title="Defensive Line Performance Above Average",)

fig.add_annotation(dict(font=dict(color='black',size=15),
                        x=0.70,
                        y=0.95,
                        text="High OPLE, High DPLE",
                        showarrow=False,
                        textangle=0,
                        xanchor='left',
                        xref="paper",
                        yref="paper"))

fig.add_annotation(dict(font=dict(color='black',size=15),
                            x=0.70,
                            y=0.1,
                            text="High OPLE, Low DPLE",
                            showarrow=False,
                            textangle=0,
                            xanchor='left',
                            xref="paper",
                            yref="paper"))

fig.add_annotation(dict(font=dict(color='black',size=15),
                        x=0.02,
                        y=0.1,
                        text="Low OPLE, Low DPLE",
                        showarrow=False,
                        textangle=0,
                        xanchor='left',
                        xref="paper",
                        yref="paper"))       

fig.add_annotation(dict(font=dict(color='black',size=15),
                        x=0.02,
                        y=0.95,
                        text="Low OPLE, High DPLE",
                        showarrow=False,
                        textangle=0,
                        xanchor='left',
                        xref="paper",
                        yref="paper"))                                  


for _, row in full_auc_df.iterrows():
    cur_image = 'NFL/' + team_dict[row['team']] + '.png'
    fig.add_layout_image(
        x=row['off_auc_above_median'],
        y=row['def_auc_above_median'],
        source=Image.open(cur_image),
        xref="x",
        yref="y",
        sizex=0.045,
        sizey=0.045,
        xanchor="center",
        yanchor="middle",
    )
fig.data = fig.data[::-1]
fig.update_layout(hovermode='closest')
fig.show()