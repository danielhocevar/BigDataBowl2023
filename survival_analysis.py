# hello
import pandas as pd
import matplotlib.pyplot as plt
from sksurv.nonparametric import kaplan_meier_estimator
import numpy as np
import math

def create_survival_analysis():
    df = pd.read_csv('playArrays.csv', header=None)

    frames = []
    pressure_values = []

    for _, row in df.iterrows():
        cur_frames = []
        cur_pressure_values = []
        for frame in range(59):
            if not math.isnan(row[frame]):
                cur_frames.append(frame)
                cur_pressure_values.append(row[frame])
        pressure_values.extend(cur_pressure_values)
        frames.extend(cur_frames)

        # for i in range(len(cur_frames), 59):
        #     cur_frames.append(i)
        #     cur_pressure_values.append(cur_pressure_values[len(cur_pressure_values)-1])
        # plt.plot(cur_frames, cur_pressure_values)
        
        
        
    survival_values = pd.DataFrame({'Frame': frames, 'Pressure': pressure_values})
    survival_values['g100'] = np.where(survival_values['Pressure'] >= 1, True, False)
    print(survival_values)

    pred_frame, pred_survival_prob = kaplan_meier_estimator(survival_values["g100"], survival_values["Frame"])
    plt.plot(pred_frame, pred_survival_prob)
    plt.ylabel("Survival Probability")
    plt.xlabel("Elapsed Frames")
    plt.show()

if __name__ == "__main__":
    create_survival_analysis()