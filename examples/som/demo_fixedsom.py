import sys
import os

# Fix python Path if run from terminal
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(curdir, "../../")))

import heat as ht
from heat.som.som import FixedSOM

# Load Dataset from hdf5 file
X = ht.load_hdf5("../../heat/datasets/data/iris.h5", dataset="data", split=0)

# Generate Keys for the iris.h5 dataset
keys = []
for i in range(50):
    keys.append(0)
for i in range(50, 100):
    keys.append(1)
for i in range(100, 150):
    keys.append(2)
Y = ht.array(keys, split=0)

som = FixedSOM(
    10,
    10,
    4,
    initial_learning_rate=0.1,
    target_learning_rate=0.01,
    initial_radius=2,
    target_radius=1,
    max_epoch=50,
    batch_size=75,
    seed=1,
    data_split=0,
)
som.fit(X)
print(som.network)