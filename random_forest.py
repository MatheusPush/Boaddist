import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

dataset_name = 'int_output_nocrossing_30k_12tb.csv'

data = pd.read_csv('final_datasets/' + dataset_name)
data = data.drop(columns='Unnamed: 0')

data_bottom = data[data['Label'] != 2]
df_x = data_bottom.iloc[:, :-1]
df_y = data_bottom.iloc[:, -1]

x_train, x_test, y_train, y_test = train_test_split(df_x, df_y, test_size=0.3, random_state=4)

rf = RandomForestClassifier(n_estimators=100, class_weight={0:1, 1:9})
rf.fit(x_train, y_train)

just_bottom = data_bottom[data_bottom['Label'] == 3]
jb_x = just_bottom.iloc[:, :-1]
jb_y = just_bottom.iloc[:, -1]

data_no_bottom = data_bottom[data_bottom['Label'] != 3]
dnb_x = data_no_bottom.iloc[:, :-1]
dnb_y = data_no_bottom.iloc[:, -1]

jb_acc = rf.score(jb_x, jb_y)
print("Just Bottom Accuracy:", jb_acc)

dnb_acc = rf.score(dnb_x, dnb_y)
print("Data wout Bottoms Accuracy:", dnb_acc)

total_acc = (2 * dnb_acc + jb_acc) / (2 + 1)
print("Total Accuracy:", total_acc)

feature_importances = pd.DataFrame(rf.feature_importances_,
								   index= x_train.columns,
								   columns=['importance']).sort_values('importance', ascending=False)
print(feature_importances)

'''
Bottom Importance:
Volume MA		(3) (9) (20) (14) (100) (200) (50)
Stoch			(9, 3) (14, 3) (5, 3) (EMA, WMA) (9, 5)
BBands			(20) (14) (9) (SMA)
RSI				(5) (3)

Top Importance:
BBands			(14, 2.0)


Close_OVER_UPPERBAND_TYPE0_14P_1.5DEV    0.002613
Close_OVER_UPPERBAND_TYPE0_9P_1.5DEV     0.002517
'''
