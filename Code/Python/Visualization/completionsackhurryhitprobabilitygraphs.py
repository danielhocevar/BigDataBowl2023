# -*- coding: utf-8 -*-
"""CompletionSackHurryHitProbabilityGraphs

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_yCR_jL5tsy6eOUCnHas3S1bc9EPMOVq
"""

from google.colab import files
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

uploaded = files.upload()

final_dataset = pd.read_csv("finalDataset.csv")

def takeFloor(val):
  newVal=0
  if val<0.20:
    newVal=0
  elif val<0.40:
    newVal=0.2
  elif val<0.6:
    newVal=0.4
  elif val<0.8:
    newVal=0.6
  elif val<1.0:
    newVal=0.8
  elif val==1.0:
    newVal=1
  return newVal

final_dataset['maximas_rounded_off_single_decimal']= final_dataset['maximas'].apply(takeFloor)

passingPlays=final_dataset.loc[(final_dataset['passResult'] == "I")|(final_dataset['passResult'] == "C")]
passingPlays['completion'] = passingPlays['passResult'].apply(lambda x: 1 if x == "C" else 0)
passingPercentage = pd.DataFrame(passingPlays.groupby('maximas_rounded_off_single_decimal')['completion'].mean())
dfSack = pd.DataFrame(final_dataset.groupby('maximas_rounded_off_single_decimal')['pff_sack'].sum())
dfHurry = pd.DataFrame(final_dataset.groupby('maximas_rounded_off_single_decimal')['pff_hurryAllowed'].sum())
dfHit = pd.DataFrame(final_dataset.groupby('maximas_rounded_off_single_decimal')['pff_hitAllowed'].sum())

plt.style.use('fivethirtyeight')
fig, axs = plt.subplots(1, 2, figsize=(20, 10))
fig.patch.set_facecolor('#FFFFFF')
axs[0].set(facecolor='#FFFFFF')
axs[1].set(facecolor='#FFFFFF')
axs[0].plot(passingPercentage)
axs[0].set_title('Completion % vs Maximum CPP During Play')
axs[0].set_xlabel('Maximum CPP During Play')
axs[0].set_ylabel('Completion %')
axs[1].plot(dfSack)
axs[1].plot(dfHit)
axs[1].plot(dfHurry)
axs[1].legend(['Sacks', 'Hits', 'Hurries'], title='Pressure Type')
axs[1].set_title('Number of Pressures vs Maximum CPP During Play')
axs[1].set_xlabel('Maximum CPP During Play')
axs[1].set_ylabel('Number of Pressures')