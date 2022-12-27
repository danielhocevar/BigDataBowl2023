# -*- coding: utf-8 -*-
"""Team_Survival_Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1peA65vCAGkpQ3g94RbibUO2njBr9fPEQ
"""

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
    plt.plot(pred_frame, pred_survival_prob)
    plt.ylabel("Survival Probability")
    plt.xlabel("Elapsed Frames")
    plt.show()
    return [pred_frame, pred_survival_prob]

def extract_auc_array_defence(df):   
  all_team_pressures = []
  all_team_survival_auc_defence = []
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
    all_team_survival_auc_defence.append(team_survival_auc)
    return all_team_survival_auc_defence

def extract_auc_array_offence(df):  
  all_team_pressures = []
  all_team_survival_auc = []
  teams = df["possessionTeam"].unique()
  for team in teams:
    team_pressure_array = [team]
    team_survival_auc = [team]
    team_df = df.loc[df["possessionTeam"]==team]
    team_pressure = team_df['Pressure Array']
    lst = []
    for index, row in team_df.iterrows():
      lst.append(row['Pressure Array'])
    lst_df = pd.DataFrame(lst)
    survival_curve = create_survival_analysis(lst_df)
    survival_curve [0] = 0.1 * survival_curve[0]
    survival_auc = integrate.simpson(survival_curve[1], survival_curve[0], axis=0)
    team_survival_auc.append(survival_auc)
    all_team_survival_auc.append(team_survival_auc)