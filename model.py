
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import pickle

dataset = pd.read_csv('diabetes1.csv')

dataset_X = dataset.iloc[:,[0, 1, 2, 3]].values
dataset_Y = dataset.iloc[:,4].values

#dataset scaled between 0 and 1
sc = MinMaxScaler(feature_range = (0,1))
# print(sc)
dataset_scaled = sc.fit_transform(dataset_X)
print(dataset_scaled)

dataset_scaled = pd.DataFrame(dataset_scaled)

X = dataset_scaled
Y = dataset_Y


X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.20, random_state = 42)

svc = SVC(kernel = 'linear', random_state = 42)
svc.fit(X_train, Y_train)

svc.score(X_test, Y_test)

Y_pred = svc.predict(X_test)
print(accuracy_score(Y_test, Y_pred))

# plt.scatter(X_train[:,0] , X_train[:,1] , c=Y_train , cmap='winter')

pickle.dump(svc, open('model.pkl','wb'))