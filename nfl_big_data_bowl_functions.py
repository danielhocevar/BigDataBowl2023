# -*- coding: utf-8 -*-
"""NFL_Big_Data_Bowl_Functions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oE4w7wV3vKwvo8qUTFox2FM0Zwo2DZrE
"""

import pandas as pd
import os
import glob
from google.colab import files
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math 
from scipy.spatial import ConvexHull, convex_hull_plot_2d
import imageio

#create_football_field Function
#Author: Hassaan Inayatali
#imgSize parameter determines how large you want the football field to be sized
#playerCoordinatesProvided allows you to specify whether or not you want to include player coordinates in the field visualization
#playerCoordinates includes the table of data with the associated players
#labelNumbers specifies whether you want the player numbers to be on the visualization
#showArrow specifies whether you want the direction of the player to be shown on the viz
#fieldColor and endZoneColor specifies the color of each. Note the endzone color will be a blend of the field color and the endZoneColor

def create_football_field(imgSize=(12.66, 24),
                          playerCoordinatesProvided=False,
                          playerCoordinates=[],
                          labelNumbers=True,
                          showArrow=True,
                          fieldColor='gray',
                          endZoneColor='yellow',
                          bounds=False):
  rect = patches.Rectangle((0, 0), 53.3, 120, linewidth=0.1,
                             edgecolor='r', facecolor=fieldColor, zorder=0) #Creates the rectangle of coordinates for the field
  fig, ax = plt.subplots(1, figsize=imgSize)
  plt.plot([0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3,
              53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 53.3, 0, 0, 53.3],
           [10, 10, 10, 20, 20, 30, 30, 40, 40, 50, 50, 60, 60, 70, 70, 80,
              80, 90, 90, 100, 100, 110, 110, 120, 0, 0, 120, 120],
             color='white') # plots the location of the field lines
  homeEndzone = patches.Rectangle((0, 0), 53.3, 10,
                                linewidth=0.1,
                                edgecolor='r',
                                facecolor=endZoneColor,
                                alpha=0.2,
                                zorder=10) #Plots the endzone for the home team
  awayEndzone = patches.Rectangle((0, 110), 53.3, 10,
                                linewidth=0.1,
                                edgecolor='r',
                                facecolor=endZoneColor,
                                alpha=0.2,
                                zorder=10) #Plots the endzone for the away team
  ax.add_patch(homeEndzone)
  ax.add_patch(awayEndzone)
  for y in range(20, 110, 10): #Adds the field marker numbers
            numb = y
            if y > 50:
                numb = 120 - y
            plt.text(5, y-1.5, str(numb - 10),
                     horizontalalignment='center',
                     fontsize=20,  # fontname='Arial',
                     color='white', rotation=270)
            plt.text(53.3 - 5, y - 0.95, str(numb - 10),
                     horizontalalignment='center',
                     fontsize=20,  # fontname='Arial',
                     color='white', rotation=90) # 
  
  for y in range(11,110): #Adds all of the  hash lines
        ax.plot([0.7, 0.4],[y, y], color='white')
        ax.plot([53.0, 52.5],[y, y], color='white')
        ax.plot([22.91, 23.57],[y, y], color='white')
        ax.plot([29.73, 30.39],[y, y],  color='white')
  
  if playerCoordinatesProvided: #Plots player coordinates
    dictionaryValidPos={'SHOTGUN':['HB','HB-R','HB-L','TE','TE-L','TE-R','LT','RT','C','LG','RG','QB'],
                    'EMPTY':['LT','LG','C','RG','RT','QB'],
                    'SINGLEBACK':['HB','QB','LT','LG','C','TE','RG','RT','QB'],
                    'I_Form':['HB','FB','LT','LG','C','RG','RT','TE','TE-L','TE-R'],
                    'Jumbo':['HB','HB-R','HB-L', 'FB','FB-L','FB-R','LT','LG','C','RG','RT','TE','TE-L','TE-R','TE-oR','TE-iR','TE-oL','TE-oL'],
                    'Pistol':['LT','LG','C','RG','RT','TE','TE-R','TE-L','HB','HB-R','HB-L','QB'],
                    'Wildcat':['HB','QB','FB-R','FB-L','TE-L','TE-R','LG','C','RG','RT','LT','HB-R','HB-L']}
    listPoints=[]
    for index, row in playerCoordinates.iterrows():
      if row['team']==row['homeTeamAbbr']:
        plt.scatter(row['y'],row['x'], color=get_player_color(row, 'red'), s=300) #Given color red if home team, blue if away
        if showArrow==True:
          plt.arrow(row['y'],row['x'],row['xspeed'], row['yspeed']*0.1, color='green',width = 0.1) #if user wants direction arrow
        if labelNumbers:
          plt.annotate(int(row['jerseyNumber']), (row['y'], row['x']),xytext=(row['y']-0.5, row['x']-0.5), color='white') #if user wants jersey numbers
      elif row['team']=='football':
        plt.scatter(row['y'],row['x'], color='brown', s=100)
      else:
        plt.scatter(row['y'],row['x'], color = get_player_color(row, 'blue'), s=300)
        if showArrow==True:
          plt.arrow(row['y'],row['x'],row['xspeed'], row['yspeed']*0.1, color='orange', width = 0.1)
        if labelNumbers:
          plt.annotate(int(row['jerseyNumber']), (row['y'], row['x']),xytext=(row['y']-0.5, row['x']-0.5), color='white')
      # if row['team']==row['possessionTeam'] and row['officialPosition'] in positionsPocket:
      #   listAppend=[]
      #   listAppend.append(row['y'])
      #   listAppend.append(row['x'])
      #   listPoints.append(listAppend)
    xCoordinateQB=playerCoordinates.loc[(playerCoordinates['pff_positionLinedUp']=='QB')]['x'].unique()[0]
    yCoordinateQB=playerCoordinates.loc[(playerCoordinates['pff_positionLinedUp']=='QB')]['y'].unique()[0]
    teamQB=playerCoordinates.loc[(playerCoordinates['pff_positionLinedUp']=='QB')]['team'].unique()[0]
    playerCoordinates['distanceFromQB']=((playerCoordinates['x']-xCoordinateQB)**2 + (playerCoordinates['y']-yCoordinateQB)**2)**(1/2)
    minimumDistanceOpposingTeam=min(playerCoordinates.loc[(playerCoordinates['team']!=teamQB)&(playerCoordinates['team']!="football")]['distanceFromQB'])
    #dfOffensive=playerCoordinates.loc[(playerCoordinates['team']==teamQB)&(playerCoordinates['distanceFromQB']<=minimumDistanceOpposingTeam)]
    #print(playerCoordinates[['team','distanceFromQB']])
    #print(dictionaryValidPos[playerCoordinates['offenseFormation'].values[0]])
    dfOffensive=playerCoordinates.loc[(playerCoordinates['pff_positionLinedUp'].isin(dictionaryValidPos[playerCoordinates['offenseFormation'].values[0]]))]
    if bounds:
      dfOffensive=dfOffensive.loc[(dfOffensive['x']>=bounds[0])&(dfOffensive['x']<=bounds[1])&(dfOffensive['y']>=bounds[2])&(dfOffensive['y']<=bounds[3])]
        #dfOffensive=playerCoordinates.loc[(playerCoordinates['pff_positionLinedUp']=="QB")|(playerCoordinates['pff_positionLinedUp']=="G")|(playerCoordinates['pff_positionLinedUp']=="T")|(playerCoordinates['pff_positionLinedUp']=="C")]
    closerToQB=playerCoordinates.loc[(playerCoordinates['distanceFromQB']<=minimumDistanceOpposingTeam)&(playerCoordinates['pff_positionLinedUp'].isin(dictionaryValidPos[playerCoordinates['offenseFormation'].values[0]]))]['nflId'].nunique()
    points = dfOffensive[['y', 'x']].values
    if closerToQB>=2:
      hull = ConvexHull(dfOffensive[['y','x']])
      for simplex in hull.simplices:
            plt.plot(points[simplex, 0], points[simplex, 1], 'k-')
            plt.fill(points[hull.vertices,0], points[hull.vertices,1], 'red', alpha=0.05)
  ax.add_patch(rect)
  plt.ylim(0, 120)
  plt.xlim(-5, 58.3)
  plt.axis('off')

#extractAllImagesForAPlay Function
#Author: Hassaan Inayatali
# df1 specifies the week of games dataframe
# df2 specifies the games dataframe
# playId specifies the playId from the week dataframe

def extractAllImagesForAPlay(df1,df2, df3,df4, df5, playId):
  dictionaryValidPos={'SHOTGUN':['HB','HB-R','HB-L','TE','TE-L','TE-R','LT','RT','C','LG','RG','QB'],
                    'EMPTY':['LT','LG','C','RG','RT','QB'],
                    'SINGLEBACK':['HB','QB','LT','LG','C','TE','RG','RT','QB'],
                    'I_Form':['HB','FB','LT','LG','C','RG','RT','TE','TE-L','TE-R'],
                    'Jumbo':['HB','HB-R','HB-L', 'FB','FB-L','FB-R','LT','LG','C','RG','RT','TE','TE-L','TE-R','TE-oR','TE-iR','TE-oL','TE-oL'],
                    'Pistol':['LT','LG','C','RG','RT','TE','TE-R','TE-L','HB','HB-R','HB-L','QB'],
                    'Wildcat':['HB','QB','FB-R','FB-L','TE-L','TE-R','LG','C','RG','RT','LT','HB-R','HB-L']}
  distinctTimes=df1.loc[(df1['playId'] == playId) ]
  distinctTimes=distinctTimes['time'].unique() #Extracts all times associated with a particular play
  
  df1['newTime']=pd.to_datetime(df1['time'])
  testing=df1.loc[(df1['playId'] == playId)]
  timeSnap=testing.loc[testing['event']=="ball_snap"]['newTime'].unique()[0]
  testing=testing.loc[(testing['newTime']==timeSnap)]
  testingNew=pd.merge(testing,df2, on='gameId', how='left')
  testingNew=pd.merge(testingNew,df3,on=['playId','gameId'], how='left')
  testingNew=pd.merge(testingNew,df4,on='nflId', how='left')
  testingNew=pd.merge(testingNew, df5, on=['playId','gameId','nflId'], how='left')

  lMaxCoordinates=determiningMaxXAndYs(testingNew, timeSnap,dictionaryValidPos)
  array_Of_Images=[]
  directory = "Play_"+str(playId)
  parent_dir = "/content/"
  path = os.path.join(parent_dir, directory)
  try:
    os.mkdir(path)
  except:
    pass
  os.chdir(path) 
  for i in distinctTimes: 
    dfForRunning=processToVisualize(df1,df2,df3,df4,df5, playId, i) #Goes through each time to process the data to visualize on the football field
    create_football_field(playerCoordinatesProvided=True,playerCoordinates=dfForRunning, labelNumbers=True ,showArrow=True, fieldColor='darkgreen', endZoneColor='purple', bounds=lMaxCoordinates) #Generate the field
    plt.savefig('imgTime:'+i +".png") #saves image into the folder
    array_Of_Images.append('imgTime:'+i +".png") #creates a list of the image names
    plt.close()
  files = []
  for filename in array_Of_Images:
    files.append(imageio.imread(filename)) #appends the image to the files
  imageio.mimsave('play'+str(playId) +'.gif', files) #Generates the gif of the play
  os.chdir('..')

#processToVisualize Function
#Author: Hassaan Inayatali
# df1 specifies the week of games dataframe
# df2 specifies the games dataframe
# playId specifies the playId from the week dataframe
# time specifies a particular time to create the image


def processToVisualize(df1,df2,df3,df4,df5, playId, time):
  testing=df1.loc[(df1['playId'] == playId) & (df1['time']==time)]
  testingNew=pd.merge(testing,df2, on='gameId', how='left')
  testingNew=pd.merge(testingNew,df3,on=['playId','gameId'], how='left')
  testingNew=pd.merge(testingNew,df4,on='nflId', how='left')

  # Merge pff scouting data
  testingNew=pd.merge(testingNew, df5, on=['playId','gameId','nflId'], how='left')
  testingNew['radiansDirection'] = testingNew['dir'].astype(float).apply(math.radians) #Converts angle in degrees to radians
  testingNew['xComponent']=testingNew['radiansDirection'].astype(float).apply(math.cos) #Converts angle into an x and y component
  testingNew['yComponent']=testingNew['radiansDirection'].astype(float).apply(math.sin)
  testingNew['xspeed']=testingNew['xComponent']*testingNew['s'] #Determines magnitude of speed by multiplying x and y component by magnitude of speed
  testingNew['yspeed']=testingNew['yComponent']*testingNew['s']
  return testingNew

# Return black if the o-lineman was beaten by the defender
# Return default colour otherwise

def get_player_color(row, default_color):
  if row['pff_beatenByDefender'] == 1 or row['pff_hitAllowed'] == 1	or row['pff_hurryAllowed'] == 1 or row['pff_sackAllowed'] == 1:
    return 'black'
  else:
    return default_color

def determiningMaxXAndYs(tab, timeSnap, dictionaryValidPos):
  oLinePlayers=tab.loc[tab['pff_positionLinedUp'].isin(dictionaryValidPos[tab['offenseFormation'].values[0]])]
  if oLinePlayers['team'].unique()[0]==oLinePlayers['homeTeamAbbr'].unique()[0]:
    maxY=max(oLinePlayers['y'].values)+2
    minY=min(oLinePlayers['y'].values)-2
    maxX=max(oLinePlayers['x'].values)+1
    minX=0
  else:
    maxY=max(oLinePlayers['y'].values)+2
    minY=min(oLinePlayers['y'].values)-2
    maxX=120
    minX=min(oLinePlayers['x'].values)-1
  return [minX, maxX, minY, maxY]