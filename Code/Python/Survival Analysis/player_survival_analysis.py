# -*- coding: utf-8 -*-
"""player_survival_analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RHcvFSdqE8mZzCwvyg3HyNqDZthbuAWR
"""

#create_survival_analysis function
#Completes a survival analysis using the dataframe which includes the pressure array for each play

def create_survival_analysis(df):
    frames = []
    pressure_values = []

    for _, row in df.iterrows():
        cur_frames = []
        cur_pressure_values = []
        #Applies a 35 frame restriction
        for frame in range(35):
            if not math.isnan(row[frame]):
                cur_frames.append(frame)
                cur_pressure_values.append(row[frame])
        pressure_values.extend(cur_pressure_values)
        frames.extend(cur_frames)


    survival_values = pd.DataFrame({'Frame': frames, 'Pressure': pressure_values})
    #Determines whether the pressure value is greater than 0.915 at a particular frame
    survival_values['g90'] = np.where(survival_values['Pressure'] >= 0.915, True, False)
    #For each frame, plot the survival probability for each play associated with a particular player
    pred_frame, pred_survival_prob = kaplan_meier_estimator(survival_values["g90"], survival_values["Frame"])
    plt.plot(pred_frame, pred_survival_prob)
    plt.ylabel("Survival Probability")
    plt.xlabel("Elapsed Frames")
    plt.show()
    return [pred_frame, pred_survival_prob]

#Working with the final dataset provided in the github
updatedFinalDataset=pd.read_csv("finalDataset.csv")
scout=pd.read_csv("pffScoutingData.csv")
#Converting array to array of integers as opposed to a string
float_df = updatedFinalDataset["Pressure Array"].apply(lambda x: [float(el) for el in x.strip("[]").split(",")])
updatedFinalDataset["Pressure Array"] = float_df
#Extracts which pass rushers were involved in each play
pass_rushers=scout.loc[scout['pff_role']=="Pass Rush"]
pass_rushers['nflIdList']=pass_rushers['nflId'].apply(funcList)
pass_rushers['positions']=pass_rushers['pff_positionLinedUp'].apply(funcList)
pass_rushers['count']=1

bingpot1=pd.DataFrame(pass_rushers.groupby(['gameId','playId'])['count'].sum())#Count the number of pass rushers for a particular play
bingpot2=pd.DataFrame(pass_rushers.groupby(['gameId','playId'])['nflIdList'].sum()) #Extract a list with the players involved in the play
bingpot3=pd.DataFrame(pass_rushers.groupby(['gameId','playId'])['positions'].sum()) #Determining which player was involved in which role for the play
bingpot=pd.merge(bingpot1, bingpot2, on = ['gameId','playId']) #For each play, the number of pass rushers, players involved in the play, as well as positions involved in the play
bingpot=pd.merge(bingpot, bingpot3, on = ['gameId','playId'])
passRushers=pd.merge(updatedFinalDataset, bingpot,on=['gameId','playId'])
fourManPassRush=passRushers.loc[passRushers['count']==4] #Locate plays with four pass rushers
fourManPassRush['lGame']=fourManPassRush['gameId'].apply(funcList) #For each player, turn the game involved into a list so they can be added
fourManPassRush['lPlay']=fourManPassRush['playId'].apply(funcList) #Repeated for player
fourManPassRush['tup']=fourManPassRush['lGame']+fourManPassRush['lPlay'] #Create a list from these lists which includes the gameId and playId

dictPlayer={}
onField=[]
dictTeam={}
#Analyzes on a team-by-team basis for each player since the surplus pressure metric is defined on a team level by player
teams = fourManPassRush["defensiveTeam"].unique()
for team in teams:
  dictTeam={}
  team_df = fourManPassRush.loc[fourManPassRush["defensiveTeam"]==team]
  for index, row in team_df.iterrows():
    #Goes through each player from the team dataframe
    for i in row['nflIdList']:
      if i in dictTeam.keys():
        dictTeam[i].append([row['gameId'],row['playId']])
      else:
        dictTeam[i]=[[row['gameId'],row['playId']]]
  for i in dictTeam:
    if len(dictTeam[i])>=0:
      try:
        lst=[]
        #Seperates the plays into the ones where the player was involved versus not
        onField=team_df.loc[team_df['tup'].isin(dictTeam[i])]
        offField=team_df.loc[~(team_df['tup'].isin(dictTeam[i]))]
        for index, row in onField.iterrows():
          lst.append(row['Pressure Array'])
        lst_df = pd.DataFrame(lst)
        survival_curve = create_survival_analysis(lst_df)
        #Converts frame to time
        survival_curve [0] = 0.1 * survival_curve[0]
        #Simpson's integration for survival curve to extract AUC
        on_field_survival_auc = integrate.simpson(survival_curve[1], survival_curve[0], axis=0)
        lst=[]
        #Repeats process for off the field
        for index, row in offField.iterrows():
          lst.append(row['Pressure Array'])
        lst_df = pd.DataFrame(lst)
        survival_curve = create_survival_analysis(lst_df)
        survival_curve [0] = 0.1 * survival_curve[0]
        off_field_survival_auc = integrate.simpson(survival_curve[1], survival_curve[0], axis=0)
        dictPlayer[i]=[on_field_survival_auc,off_field_survival_auc, len(dictTeam[i])]
      except:
        pass

#Determines DPLE when on the field versus off the field and the surplus value for each player
listSurplusValue=[]
for i in dictPlayer:
  listSurplusValue.append([i,dictPlayer[i][2]*(dictPlayer[i][1]-dictPlayer[i][0]),dictPlayer[i][2], dictPlayer[i][1]-dictPlayer[i][0], dictPlayer[i][0], dictPlayer[i][1]])

playerSurplusValue=pd.DataFrame(Sort(listSurplusValue))
playerSurplusValue.columns=['nflId','TotalSurplusPressure','Number of Plays','surplusValuePerPlay','On-Field Expectancy (35 Frames)','Off-Field Expectancy (35 Frames)']
#Ranks players by total surplus pressure
playerSurplusTable=pd.merge(playerSurplusValue, players, on='nflId')
orderedRankings=playerSurplusTable.sort_values('TotalSurplusPressure', ascending=False)
#Seperates rankings by pass rush position
defensiveEndRankings=orderedRankings.loc[orderedRankings['officialPosition']=="DE"]
OLBRankings=orderedRankings.loc[orderedRankings['officialPosition']=="OLB"]
NTRankings=orderedRankings.loc[orderedRankings['officialPosition']=="NT"]
DTRankings=orderedRankings.loc[orderedRankings['officialPosition']=="DT"]

#Converts value within the dataframe into a list
def funcList(val):
  return [val]