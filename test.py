from Model import Model
import numpy as np
import json
import matplotlib.pyplot as plt
from collections import Counter

np.random.seed(1)

# model = Model.create_realistic_network(1000, 
#               {"SCI,1":lambda:np.random.poisson(5), 
#               "SCI,2":lambda: np.random.poisson(5), 
#               "HUM,1":lambda:np.random.poisson(6), 
#               "HUM,2":lambda:np.random.poisson(6)}, 
#               {"SCI,1":0.30, "SCI,2":0.2, "HUM,1":0.30, "HUM,2":0.2}, 
#               {("SCI,1","SCI,1"):0.9,
#                ("SCI,1","HUM,2"):0.1,
#                ("HUM,2","HUM,2"):0.9,
#                ("SCI,2","SCI,2"):0.9,
#                ("SCI,1","HUM,1"):0.5,
#                ("SCI,2", "HUM,2"):0.4,
#                ("HUM,1","HUM,1"):0.9,
#                ("HUM,1","SCI,2"):0,
#                ("SCI,1","SCI,2"):0.6,
#                ("HUM,1", "HUM,2"):0.6
#               }, transmission_rate=0.03, recovery_time=20)

model = Model.random_network(1000, 5, ["SCI,1", "HUM,1", "SCI,2", "HUM,2"], states=[0,1,2], transmission_rate=0.03, recovery_time=20)

model.introduce_infection()
model2 = model.deep_copy()
model3 = model.deep_copy()
model4 = model.deep_copy()



model2.transmission_rate = 0.03
model2.recovery_time = 4

model3.transmission_rate = 0.05
model3.recovery_time = 20

model4.transmission_rate = 0.05
model4.recovery_time = 4



print len(model.individuals)
print model.individuals[:10]
print 'number of individuals per property:'
print model.partition_summary()
print 'number of friends of property per class:'
# print { k:map(lambda i: i.describe_friends(model.individuals), model.partitioning[k]) for k in model.partitioning.keys() }

data = np.array(model.simulate(time=100, return_data=True)[1:])
data2 = np.array(model2.simulate(time=100, return_data=True)[1:])
data3 = np.array(model3.simulate(time=100, return_data=True)[1:])
data4 = np.array(model4.simulate(time=100, return_data=True)[1:])

json.dump(model.export_network(), open('data.json','w'))


plt.figure()
plt.subplot(2,2,1)
plt.plot(data[:,1])
plt.title('beta=0.03, gamma=20')
plt.ylabel('Infected Number of People')
plt.xlabel('Day')

plt.subplot(2,2,2)
plt.plot(data2[:,1])
plt.ylabel('Infected Number of People')
plt.title('beta=0.03, gamma=4')
plt.xlabel('Day')

plt.subplot(2,2,3)
plt.plot(data3[:,1])
plt.ylabel('Infected Number of People')
plt.title('beta=0.05, gamma=20')
plt.xlabel('Day')

plt.subplot(2,2,4)
plt.plot(data4[:,1])
plt.ylabel('Infected Number of People')
plt.title('beta=0.05, gamma=4')
plt.xlabel('Day')

plt.tight_layout()
plt.show()

# # reaction_model = model.deep_copy()
# reaction_model2 = model.deep_copy()
# # pre_reaction_data1 = reaction_model.simulate(until=50, time=1000, return_data=True)[1:]
# non_delete_data = reaction_model2.simulate(until=50, time=1000, return_data=True)[1:]

# # reaction_model.delete_random_edges(3)

# # pre_reaction_data1.extend(reaction_model.simulate(time=200, return_data=True)[1:])
# non_delete_data.extend(reaction_model2.simulate(time=200, return_data=True)[1:])


# # pre_reaction_data1 = np.array(pre_reaction_data1)
# non_delete_data = np.array(non_delete_data)

# plt.figure(3)
# # plt.subplot(2,1,1)
# plt.plot(non_delete_data[:,1])
# plt.ylabel('Infected number of people')
# plt.xlabel('Day')
# plt.title('beta=0.05, gamma=20 / no announcement')
# # plt.subplot(2,1,2)
# # plt.plot(non_delete_data[:,1])
# # plt.ylabel('Infected number of people')
# # plt.xlabel('Day')
# # plt.title('beta=0.05, gamma=20 / no announcement')

# plt.tight_layout()
# plt.show()

