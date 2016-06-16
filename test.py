from Model import Model
import numpy as np
import json

np.random.seed(1)

model = Model.create_realistic_network(50, 
              {"SCI,1":lambda:np.random.poisson(5), 
              "SCI,2":lambda: np.random.poisson(5), 
              "HUM,1":lambda:np.random.poisson(5), 
              "HUM,2":lambda:np.random.poisson(5)}, 
              {"SCI,1":0.40, "SCI,2":0.1, "HUM,1":0.40, "HUM,2":0.1}, 
              {("SCI,1","SCI,1"):0.9,
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


# model = Model.random_network(10,4,["ZAF","ARAM"])
print len(model.individuals)
print model.individuals[:10]
print 'number of individuals per property:'
print model.partition_summary()
print 'number of friends of property per class:'
print { k:map(lambda i: i.describe_friends(model.individuals), model.partitioning[k]) for k in model.partitioning.keys() }
model.introduce_infection()
model.simulate()

json.dump(model.export_network(), open('data.json','w'))