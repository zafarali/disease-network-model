from Model import Model
import numpy as np

model = Model(10, 
              {"SCI,1": 5, "SCI,2":5, "HUM,1":lambda:5, "HUM,2":lambda:np.random.poisson(5)}, 
              {"SCI,1":0.30, "SCI,2":0.2, "HUM,1":0.30, "HUM,2":0.2}, 
              { ("SCI,1","SCI,1"):0.9,
               ("SCI,1","HUM,2"):0,
               ("HUM,2","HUM,2"):0.9,
               ("SCI,2","SCI,2"):0.9,
               ("SCI,1","HUM,1"):0.5,
               ("SCI,2", "HUM,2"):0.2,
               ("HUM,1","HUM,1"):0.9,
               ("HUM,1","SCI,2"):0,
               ("SCI,1","SCI,2"):0.6,
               ("HUM,1", "HUM,2"):0.6
              })


print 'number of individuals per property:'
print model.partition_summary()
print 'number of friends of property per class:'
print { k:map(lambda i: i.describe_friends(model.individuals), model.partitioning[k]) for k in model.partitioning.keys() }