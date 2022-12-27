# -*- coding: utf-8 -*-
"""Team_CPP_Rankings

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aUmwl3xliHGnbCv_uw60tS2RSVNr8qtM
"""

!pip install scikit-survival
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sksurv.nonparametric import kaplan_meier_estimator
from scipy import integrate
import math
from google.colab import files

uploaded=files.upload()

df = pd.read_csv('passRushers.csv')
float_df = df["Pressure Array"].apply(lambda x: [float(el) for el in x.strip("[]").split(",")])
df["Pressure Array"] = float_df

four_rushers_df = df.loc[df['count'] == 4]

def create_survival_analysis(df):

    frames = []
    pressure_values = []

    for _, row in df.iterrows():
        cur_frames = []
        cur_pressure_values = []
        for frame in range(40):
            if not math.isnan(row[frame]):
                cur_frames.append(frame)
                cur_pressure_values.append(row[frame])
        pressure_values.extend(cur_pressure_values)
        frames.extend(cur_frames)

    survival_values = pd.DataFrame({'Frame': frames, 'Pressure': pressure_values})
    survival_values['g90'] = np.where(survival_values['Pressure'] >= 0.915, True, False)

    pred_frame, pred_survival_prob = kaplan_meier_estimator(survival_values["g90"], survival_values["Frame"])
    return [pred_frame, pred_survival_prob]

def extract_auc_defense_array(df):   
  all_team_pressures = []
  all_team_survival_defence_auc = []
  teams = df["defensiveTeam"].unique()
  for team in teams:
    team_pressure_array = [team]
    team_survival_auc = [team]
    team_df = df.loc[df["defensiveTeam"]==team]
    team_pressure = team_df['Pressure Array']
    lst = []
    for index, row in team_df.iterrows():
      lst.append(row['Pressure Array'])
    lst_df = pd.DataFrame(lst)
    survival_curve = create_survival_analysis(lst_df)
    survival_curve [0] = 0.1 * survival_curve[0]
    survival_auc = integrate.simpson(survival_curve[1], survival_curve[0], axis=0)
    team_survival_auc.append(survival_auc)
    all_team_survival_defence_auc.append(team_survival_auc)
  return all_team_survival_defence_auc

four_rush_df = pd.DataFrame(extract_auc_defense_array(four_rushers_df)).sort_values(by=[1]).nsmallest(10, 1)
four_rush_df['Rank'] = range(1, 11)
four_rush_df = four_rush_df.rename(columns={0: 'Team', 1: 'PocketLifetime'})
four_rush_df = four_rush_df[['Rank', 'Team', 'PocketLifetime']]
four_rush_df = four_rush_df.round(3)
sacks = four_rushers_df.groupby(['defensiveTeam'])['pff_sack'].sum()
hits = four_rushers_df.groupby(['defensiveTeam'])['pff_hitAllowed'].sum()
hurries = four_rushers_df.groupby(['defensiveTeam'])['pff_hurryAllowed'].sum()
four_rush_df