import numpy as np
import pandas as pd
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn import metrics  # Import scikit-learn metrics module for accuracy calculation

# Build image
from sklearn.tree import export_graphviz
from sklearn.externals.six import StringIO
from IPython.display import Image
import pydotplus

dataset_name = 'oie.csv'

data = pd.read_csv('final_datasets/' + dataset_name)
data = data.drop(columns='Unnamed: 0')

# Best tree
best_hyperp = ''
best_acc = 0
best_tree = None

# Just bottom

data_bottom = data[data['Label'] != 3]

df_y = data_bottom['Label']
df_x = data_bottom.drop(columns='Label')

x_train, x_test, y_train, y_test = train_test_split(df_x, df_y, test_size=0.25, random_state=100)

for c in ['gini']:
	for max in [10]:
		for min in [25, 50, 100]:
			for w in [3, 5, 10, 15, 20, 25]:
				clf = tree.DecisionTreeClassifier(criterion=c, max_depth=max, min_samples_leaf=min,
												  class_weight={1: 1, 2: w})
				clf.fit(x_train, y_train)

				just_bottom = data_bottom[data_bottom['Label'] == 2]
				jb_y = just_bottom['Label']
				jb_x = just_bottom.drop(columns='Label')

				data_no_bottom = data_bottom[data_bottom['Label'] != 2]
				dnb_y = data_no_bottom['Label']
				dnb_x = data_no_bottom.drop(columns='Label')

				jb_pred = clf.predict(jb_x)
				dnb_pred = clf.predict(dnb_x)

				print(c, max, min, w)

				jb_acc = metrics.accuracy_score(jb_y, jb_pred)
				print("Just Bottom Accuracy:", jb_acc)

				dnb_acc = metrics.accuracy_score(dnb_y, dnb_pred)
				print("Data wout Bottoms Accuracy:", dnb_acc)

				total_acc = (w * dnb_acc + jb_acc) / (w + 1)
				print("Total Accuracy:", total_acc)

				if total_acc > best_acc:
					best_acc = total_acc
					best_hyperp = c, max, min, w
					best_tree = clf

print("\nBEST:")
print(best_hyperp)

dot_data = StringIO()
export_graphviz(best_tree, out_file=dot_data,
				filled=True, rounded=True,
				special_characters=True, feature_names=df_x.columns, class_names=['1', '3', '2'])
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
graph.write_png('oie_5_tree_bottom_gini.png')
Image(graph.create_png())

