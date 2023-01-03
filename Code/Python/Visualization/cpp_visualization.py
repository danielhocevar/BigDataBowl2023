import pandas as pd
from scipy.stats import multivariate_normal
import numpy as np
import os
import glob
from google.colab import files
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
from scipy.spatial import ConvexHull, convex_hull_plot_2d
import imageio


def get_player_color(row, default_color):
	# Assign a color based on the player's team
    if row['pff_beatenByDefender'] == 1 or row['pff_hitAllowed'] == 1 or row['pff_hurryAllowed'] == 1 or row['pff_sackAllowed'] == 1:
        # return 'black'
        return default_color
    else:
        return default_color


def processToVisualize(df1, df2, df3, df4, df5, playId, time, gameId):
	# Prepare the data for visualization
    testing = df1.loc[(df1['playId'] == playId) & (
        df1['time'] == time) & (df1['gameId'] == gameId)]
    testingNew = pd.merge(testing, df2, on='gameId', how='left')
    testingNew = pd.merge(testingNew, df3, on=['playId', 'gameId'], how='left')
    testingNew = pd.merge(testingNew, df4, on='nflId', how='left')

    # Merge pff scouting data
    testingNew = pd.merge(testingNew, df5, on=[
                          'playId', 'gameId', 'nflId'], how='left')
    testingNew['radiansDirection'] = testingNew['dir'].astype(
        float).apply(math.radians)  # Converts angle in degrees to radians
    testingNew['xComponent'] = testingNew['radiansDirection'].astype(
        float).apply(math.cos)  # Converts angle into an x and y component
    testingNew['yComponent'] = testingNew['radiansDirection'].astype(
        float).apply(math.sin)
    # Determines magnitude of speed by multiplying x and y component by magnitude of speed
    testingNew['xspeed'] = testingNew['xComponent']*testingNew['s']
    testingNew['yspeed'] = testingNew['yComponent']*testingNew['s']
    return testingNew


def determiningMaxXAndYs(tab, timeSnap, dictionaryValidPos):
	# Get the maximum player x and y coordinates
    oLinePlayers = tab.loc[tab['pff_role'] == 'Pass Block']
    print(int(oLinePlayers.quarter.unique()[0]))
    if oLinePlayers['team'].unique()[0] == oLinePlayers['homeTeamAbbr'].unique()[0] or int(oLinePlayers.quarter.unique()[0]) % 2 == 0:
        maxY = max(oLinePlayers['y'].values)+2
        minY = min(oLinePlayers['y'].values)-2
        maxX = max(oLinePlayers['x'].values)+1
        minX = 0
    else:
        maxY = max(oLinePlayers['y'].values)+2
        minY = min(oLinePlayers['y'].values)-2
        maxX = 120
        minX = min(oLinePlayers['x'].values)-1
    return [minX, maxX, minY, maxY]


def determiningDistancesAtTimeOfSnap(tab, timeSnap, dictionaryValidPos):

    xCoordinateQB = tab.loc[(tab['pff_positionLinedUp']
                             == 'QB')]['x'].unique()[0]
    yCoordinateQB = tab.loc[(tab['pff_positionLinedUp']
                             == 'QB')]['y'].unique()[0]
    teamQB = tab.loc[(tab['pff_positionLinedUp'] == 'QB')]['team'].unique()[0]
    tab['distanceFromQB'] = ((tab['x']-xCoordinateQB)
                             ** 2 + (tab['y']-yCoordinateQB)**2)**(1/2)
    oLinePlayers = tab.loc[tab['pff_role'] == 'Pass Block']
    dictPlayerDistances = {}
    for index, row in oLinePlayers.iterrows():
        dictPlayerDistances[row['nflId']] = row['distanceFromQB']
    return dictPlayerDistances


def pocketPressureVisualization(imgSize=(10.66, 24),
                   playerCoordinatesProvided=False,
                   playerCoordinates=[],
                   labelNumbers=True,
                   showArrow=True,
                   fieldColor='gray',
                   endZoneColor='yellow',
                   startingPlayerDistances=[]):
    # Draw the football field
    rect = patches.Rectangle((0, 0), 53.3, 120, linewidth=0.1,
                             edgecolor='r', facecolor=fieldColor, zorder=0)  # Creates the rectangle of coordinates for the field
    fig, ax = plt.subplots(1, figsize=imgSize)
    plt.plot([0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3,
              53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 53.3, 0, 0, 53.3],
             [10, 10, 10, 20, 20, 30, 30, 40, 40, 50, 50, 60, 60, 70, 70, 80,
              80, 90, 90, 100, 100, 110, 110, 120, 0, 0, 120, 120],
             color='black')  # plots the location of the field lines
    homeEndzone = patches.Rectangle((0, 0), 53.3, 10,
                                    linewidth=0.1,
                                    edgecolor='r',
                                    facecolor=endZoneColor,
                                    alpha=0.2,
                                    zorder=10)  # Plots the endzone for the home team
    awayEndzone = patches.Rectangle((0, 110), 53.3, 10,
                                    linewidth=0.1,
                                    edgecolor='r',
                                    facecolor=endZoneColor,
                                    alpha=0.2,
                                    zorder=10)  # Plots the endzone for the away team
    ax.add_patch(homeEndzone)
    ax.add_patch(awayEndzone)
    for y in range(20, 110, 10):  # Adds the field marker numbers
        numb = y
        if y > 50:
            numb = 120 - y
        plt.text(5, y-1.5, str(numb - 10),
                 horizontalalignment='center',
                 fontsize=20,  # fontname='Arial',
                 color='black', rotation=270)
        plt.text(53.3 - 5, y - 0.95, str(numb - 10),
                 horizontalalignment='center',
                 fontsize=20,  # fontname='Arial',
                 color='black', rotation=90)

    for y in range(11, 110):  # Adds all of the  hash lines
        ax.plot([0.7, 0.4], [y, y], color='black')
        ax.plot([53.0, 52.5], [y, y], color='black')
        ax.plot([22.91, 23.57], [y, y], color='black')
        ax.plot([29.73, 30.39], [y, y],  color='black')

    # The probability density function (pdf) for the defensive team is a sum of normal distributions
    offense_pdf_is_none = True
    defense_pdf_is_none = True
    pdf = None
    offense_pdf = None
    defense_pdf = None
    # The pdf for the qb is generated from a normal distribution over the region surrounding the qb
    qb_pdf = None

    b_off_pdf = None
    b_def_pdf = None

    # Define the domain of the pdf to be the football field
    x, y = np.mgrid[0:53.3:1, 0:120:1]
    locations = np.dstack((x, y))

    xCoordinateQB = playerCoordinates.loc[(
        playerCoordinates['pff_positionLinedUp'] == 'QB')]['x'].unique()[0]
    yCoordinateQB = playerCoordinates.loc[(
        playerCoordinates['pff_positionLinedUp'] == 'QB')]['y'].unique()[0]
    teamQB = playerCoordinates.loc[(
        playerCoordinates['pff_positionLinedUp'] == 'QB')]['team'].unique()[0]
    playerCoordinates['distanceFromQB'] = (
        (playerCoordinates['x']-xCoordinateQB)**2 + (playerCoordinates['y']-yCoordinateQB)**2)**(1/2)
    playerCoordinates['radiansDirection'] = playerCoordinates['dir'].astype(
        float).apply(math.radians)  # Converts angle in degrees to radians
    playerCoordinates['xComponent'] = playerCoordinates['radiansDirection'].astype(
        float).apply(math.cos)  # Converts angle into an x and y component
    playerCoordinates['yComponent'] = playerCoordinates['radiansDirection'].astype(
        float).apply(math.sin)

    # Determines magnitude of speed by multiplying x and y component by magnitude of speed
    playerCoordinates['xspeed'] = playerCoordinates['xComponent'] * \
        playerCoordinates['s']
    playerCoordinates['yspeed'] = playerCoordinates['yComponent'] * \
        playerCoordinates['s']
    tableOfDefensiveCoordinates = playerCoordinates.loc[(
        playerCoordinates['team'] != playerCoordinates['possessionTeam']) & (playerCoordinates['team'] != "football")]
    tableOfOffensiveCoordinates = playerCoordinates.loc[(
        playerCoordinates['team'] == playerCoordinates['possessionTeam'])]

    mu_val_x = 0
    mu_val_y = 0
    x, y = np.mgrid[0:53.3:1, 0:120:1]
    locations = np.dstack((x, y))
    total_gaussian_Influence_Defence = 0

    # Find the location of the qb and store it
    qb_pos_x = 0
    qb_pos_y = 0

	# Iterate through all the players and draw each player on the field
    for index, row in playerCoordinates.iterrows():
        if row['officialPosition'] == "QB":
            plt.scatter(row['y'], row['x'], color=get_player_color(
                row, 'limegreen'), s=300, zorder=2)
            if labelNumbers:
                plt.annotate(int(row['jerseyNumber']), (row['y'], row['x']), xytext=(
                    row['y']-0.5, row['x']-0.5), color='white')
        elif row['team'] == row['homeTeamAbbr']:
            plt.scatter(row['y'], row['x'], color=get_player_color(
                row, 'red'), s=300, zorder=2)  # Given color red if home team, blue if away
            if showArrow == True:
                plt.arrow(row['y'], row['x'], row['xspeed'], row['yspeed']*0.1,
                          color='green', width=0.1)  # if user wants direction arrow
            if labelNumbers:
                plt.annotate(int(row['jerseyNumber']), (row['y'], row['x']), xytext=(
                    row['y']-0.5, row['x']-0.5), color='white')  # if user wants jersey numbers
        elif row['team'] == 'football':
            plt.scatter(row['y'], row['x'], color='brown', s=100, zorder=2)
        else:
            plt.scatter(row['y'], row['x'], color=get_player_color(
                row, 'blue'), s=300, zorder=2)
            if showArrow == True:
                plt.arrow(row['y'], row['x'], row['xspeed'],
                          row['yspeed']*0.1, color='orange', width=0.1)
            if labelNumbers:
                plt.annotate(int(row['jerseyNumber']), (row['y'], row['x']), xytext=(
                    row['y']-0.5, row['x']-0.5), color='white')

    pass_rushers = playerCoordinates.loc[(
        playerCoordinates['pff_role'] == 'Pass Rush')]

    # Generate pdf's for each player
    for index, row in playerCoordinates.iterrows():
        if row['team'] == row['defensiveTeam']:
			# Generate the defensive player influence model
            speed_Ratio = (row['s']**2)/(100)
            topLeftSMatrix = (row['distanceFromQB'] +
                              row['distanceFromQB']*speed_Ratio)/2
            bottomRightSMatrix = (
                row['distanceFromQB']-row['distanceFromQB']*speed_Ratio)/2
            r_matrix = [(row['xComponent'], -row['yComponent']),
                        (row['yComponent'], row['xComponent'])]
            r_matrix = pd.DataFrame(data=r_matrix)
            s_matrix = [(topLeftSMatrix, 0), (0, bottomRightSMatrix)]
            s_matrix = pd.DataFrame(data=s_matrix)
            inverse_r_Matrix = np.linalg.inv(r_matrix)
            multiplyingTogetherFirstTwoMatrices = r_matrix.dot(s_matrix)
            nextMatrix = multiplyingTogetherFirstTwoMatrices.dot(s_matrix)
            covariance_matrix = nextMatrix.dot(inverse_r_Matrix)
            mu_val_x = row['y']+row['xspeed']*0.5
            mu_val_y = row['x']+row['yspeed']*0.5
            mu = [mu_val_x, mu_val_y]
            player_pdf = multivariate_normal(
                mu, covariance_matrix).pdf(locations)

            b_player_pdf = multivariate_normal(
                [row['y'], row['x']], [[4, 0], [0, 4]]).pdf(locations)
            if defense_pdf_is_none:
                # If this is the first defensive player, generate a new pdf
                defense_pdf = player_pdf
                defense_pdf_is_none = False
                b_def_pdf = b_player_pdf
            else:
                # Otherwise, update the existing pdf
                defense_pdf = defense_pdf + player_pdf
                b_def_pdf = b_def_pdf + b_player_pdf
        elif row['officialPosition'] == "QB":
            # Store the qb position
            qb_pos_x = row['y']
            qb_pos_y = row['x']
        elif row['team'] == row['possessionTeam'] and row['pff_role'] == 'Pass Block':
            # Create the offensive player influence model
            distance_from_QB = row['distanceFromQB']
            minDistancePassRusherToQB = min(pass_rushers['distanceFromQB'])
            minDistancePassRush = 1000
            for index, rowPass in pass_rushers.iterrows():
                totalDistance = ((rowPass['x']-row['x'])
                                 ** 2+(rowPass['y']-row['y'])**2)**(1/2)
                if totalDistance <= minDistancePassRush:
                    minDistancePassRush = totalDistance
                    xCoordinatePassRusher = rowPass['x']
                    yCoordinatePassRusher = rowPass['y']
                    speedPassRusher = rowPass['s']
                    dirPassRusher = rowPass['dir']
            p12 = ((xCoordinateQB-row['x'])**2 +
                   (yCoordinateQB-row['y'])**2)**(1/2)
            p23 = ((xCoordinateQB-xCoordinatePassRusher)**2 +
                   (yCoordinateQB-yCoordinatePassRusher)**2)**(1/2)
            p13 = (((row['x']-xCoordinatePassRusher)**2) +
                   ((row['y']-yCoordinatePassRusher)**2))**(1/2)
            angleBetweenThreePlayers = math.acos(
                ((p12**2) + (p13**2) - (p23**2)) / (2 * p12 * p13))
            degreesAngleBetweenThreePlayers = math.degrees(
                angleBetweenThreePlayers)
            angleFrom180 = abs(degreesAngleBetweenThreePlayers-180)
            normalizedDistance = minDistancePassRusherToQB / \
                (startingPlayerDistances[row['nflId']])

            speed_Ratio = (row['s']**2)/(100)
            topLeftSMatrix = (row['distanceFromQB'] +
                              row['distanceFromQB']*speed_Ratio)/2
            bottomRightSMatrix = (
                row['distanceFromQB']-row['distanceFromQB']*speed_Ratio)/2
            r_matrix = [(row['xComponent'], -row['yComponent']),
                        (row['yComponent'], row['xComponent'])]
            r_matrix = pd.DataFrame(data=r_matrix)
            s_matrix = [(topLeftSMatrix, 0), (0, bottomRightSMatrix)]
            s_matrix = pd.DataFrame(data=s_matrix)
            inverse_r_Matrix = np.linalg.inv(r_matrix)
            multiplyingTogetherFirstTwoMatrices = r_matrix.dot(s_matrix)
            nextMatrix = multiplyingTogetherFirstTwoMatrices.dot(s_matrix)
            covariance_matrix = nextMatrix.dot(inverse_r_Matrix)
            mu_val_x = row['y']+row['xspeed']*0.5
            mu_val_y = row['x']+row['yspeed']*0.5
            mu = [mu_val_x, mu_val_y]
            player_pdf = multivariate_normal(
                mu, covariance_matrix).pdf(locations)
            b_player_pdf = multivariate_normal(
                [row['y'], row['x']], [[4, 0], [0, 4]]).pdf(locations)
            if offense_pdf_is_none:
                # If this is the first defensive player, generate a new pdf
                offense_pdf = normalizedDistance * \
                    degreesAngleBetweenThreePlayers*(player_pdf/180)
                offense_pdf_is_none = False
                b_off_pdf = b_player_pdf
            else:
                # Otherwise, update the existing pdf
                offense_pdf = offense_pdf + normalizedDistance * \
                    degreesAngleBetweenThreePlayers*(player_pdf/180)
                b_off_pdf = b_off_pdf + b_player_pdf
        elif row['team'] == row['possessionTeam']:
            b_player_pdf = multivariate_normal(
                [row['y'], row['x']], [[4, 0], [0, 4]]).pdf(locations)
            if b_off_pdf is None:
                b_off_pdf = b_player_pdf
            else:
                b_off_pdf = b_off_pdf + b_player_pdf

    pdf = np.array(defense_pdf)/(np.array(defense_pdf)+np.array(offense_pdf))
    is_def = defense_pdf > 0.01
    display_pdf = is_def * pdf
    show_b = b_def_pdf - 0.7 * b_off_pdf
    # Generate a pdf for the qb
    qb_pdf = multivariate_normal([qb_pos_x, qb_pos_y], [
                                 [6, 0], [0, 6]]).pdf(locations)

    # Values of the defensive pdf get zeroed if they are not within the qb's pocket
    pressure_pdf = np.array(qb_pdf) * np.array(pdf)

    # Calculate the pressure percentage
    pressure_val = np.sum(np.sum(pressure_pdf, axis=1), axis=0) / \
        np.sum(np.sum(qb_pdf, axis=1), axis=0)  # 27 is the scaling factor
    pressure_val = (pressure_val-0.50)/(0.80-0.50)

    ax.contourf(x, y, display_pdf, cmap='Purples')

    # Calculate the pressure percentage
    im = plt.imread("../pressure_red.png")
    if pressure_val < 0.5:
        im = plt.imread("../pressure_green.png")
    elif pressure_val < 0.65:
        im = plt.imread("../pressure_yellow.png")
    elif pressure_val < 0.8:
        im = plt.imread("../pressure_orange.png")
    newax = fig.add_axes([0.56, 0.545, 0.3, 0.3], anchor='NE', zorder=1)
    newax.imshow(im)
    newax.axis('off')

    fontsize = 66
    if pressure_val >= 1:
        pressure_val = 1
        fontsize = 50
    elif pressure_val < 0:
        pressure_val = 0
    newax.text(200, 280, f"{int(pressure_val * 100)}%",
               fontSize=fontsize, fontWeight="bold", color='w', zorder=2)
    plt.axis('off')


def constructPressureGif(df1, df2, df3, df4, df5, playId, gameId):
	# For each image, construct the pressure visualization and then save these images to a gif
    dictionaryValidPos = {'SHOTGUN': ['HB', 'HB-R', 'HB-L', 'TE', 'TE-L', 'TE-R', 'LT', 'RT', 'C', 'LG', 'RG', 'QB'],
                          'EMPTY': ['LT', 'LG', 'C', 'RG', 'RT', 'QB'],
                          'SINGLEBACK': ['HB', 'QB', 'LT', 'LG', 'C', 'TE', 'RG', 'RT', 'QB'],
                          'I_Form': ['HB', 'FB', 'LT', 'LG', 'C', 'RG', 'RT', 'TE', 'TE-L', 'TE-R'],
                          'Jumbo': ['HB', 'HB-R', 'HB-L', 'FB', 'FB-L', 'FB-R', 'LT', 'LG', 'C', 'RG', 'RT', 'TE', 'TE-L', 'TE-R', 'TE-oR', 'TE-iR', 'TE-oL', 'TE-oL'],
                          'Pistol': ['LT', 'LG', 'C', 'RG', 'RT', 'TE', 'TE-R', 'TE-L', 'HB', 'HB-R', 'HB-L', 'QB'],
                          'Wildcat': ['HB', 'QB', 'FB-R', 'FB-L', 'TE-L', 'TE-R', 'LG', 'C', 'RG', 'RT', 'LT', 'HB-R', 'HB-L']}
    distinctTimes = df1.loc[(df1['playId'] == playId)
                            & (df1['gameId'] == gameId)]
    # Extracts all times associated with a particular play
    distinctTimes = distinctTimes['time'].unique()

    df1['newTime'] = pd.to_datetime(df1['time'])

	# Join all the dataframes together
    testing = df1.loc[(df1['playId'] == playId)]
    timeSnap = testing.loc[testing['event'] == "ball_snap"]['newTime'].unique()[
        0]
    testing = testing.loc[(testing['newTime'] == timeSnap)]
    testingNew = pd.merge(testing, df2, on='gameId', how='left')
    testingNew = pd.merge(testingNew, df3, on=['playId', 'gameId'], how='left')
    testingNew = pd.merge(testingNew, df4, on='nflId', how='left')
    testingNew = pd.merge(testingNew, df5, on=[
                          'playId', 'gameId', 'nflId'], how='left')

	# Determine start distances and max coordinates
    lMaxCoordinates = determiningMaxXAndYs(
        testingNew, timeSnap, dictionaryValidPos)
    startingPlayerDistances = determiningDistancesAtTimeOfSnap(
        testingNew, timeSnap, dictionaryValidPos)
    array_Of_Images = []
    directory = "Play_"+str(playId)
    parent_dir = "/content/"
    path = os.path.join(parent_dir, directory)
    try:
        os.mkdir(path)
    except:
        pass
    os.chdir(path)
    for i in distinctTimes:
        # Goes through each time to process the data to visualize on the football field
        dfForRunning = processToVisualize(
            df1, df2, df3, df4, df5, playId, i, gameId)

		# Create the pressure visulization and then save the plt figure to a file
        pocketPressureVisualization(playerCoordinates=dfForRunning, fieldColor='darkgreen',
                       endZoneColor='purple', startingPlayerDistances=startingPlayerDistances, showArrow=False)
        plt.savefig('imgTime:'+i + ".png")  # saves image into the folder
        # creates a list of the image names
        array_Of_Images.append('imgTime:'+i + ".png")
        plt.close()
    files = []
    for filename in array_Of_Images:
        # appends the image to the files
        files.append(imageio.imread(filename))
    # Generates the gif of the play
    imageio.mimsave('play'+str(playId) + '.gif', files)
    os.chdir('..')

# These are the plays used in visulization displayed in the kaggle notebook
# Low pressure: PlayID: 1909, GameID: 2021091202
# Medium pressure: PlayID: 2253, GameID: 2021091600
# High pressure: PlayID: 3149, GameID: 2021091209
