from Model import Model
import numpy as np
import json
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter



model = Model.create_realistic_network(2000, 
              {"SCI,1":lambda:np.random.poisson(5), 
              "SCI,2":lambda: np.random.poisson(5), 
              "HUM,1":lambda:np.random.poisson(6), 
              "HUM,2":lambda:np.random.poisson(6)}, 
              {"SCI,1":0.30, "SCI,2":0.2, "HUM,1":0.30, "HUM,2":0.2}, 
              {# within class
               ("SCI,1","SCI,1"):0.5,
               ("HUM,1","HUM,1"):0.5,
               ("HUM,2","HUM,2"):0.5,
               ("SCI,2","SCI,2"):0.5,
               ("SCI,1","HUM,1"):0.5,
               # cross class
               ("SCI,1","HUM,2"):0,
			   ("HUM,1","SCI,2"):0,
			   # in-cross terms
               ("SCI,2", "HUM,2"):0.25,
               ("SCI,1","SCI,2"):0.25,
               ("HUM,1", "HUM,2"):0.25
              }, transmission_rate=0.25, recovery_time=5)



# reaction_model = model.deep_copy()
model.introduce_infection()
reaction_model2 = model.deep_copy()
reaction_model3 = model.deep_copy()

until = 200
non_delete_data = model.simulate(time=100, return_data=True)[1:]
delete_data = reaction_model2.simulate(until=until, time=100, return_data=True)[1:]
delete_data2 = reaction_model3.simulate(until=until,time=100, return_data=True)[1:]

reaction_model2.delete_preferential_edges(2)
reaction_model3.delete_random_edges(2)

delete_data.extend(reaction_model2.simulate(time=100, return_data=True)[1:])
non_delete_data.extend(model.simulate(time=100,return_data=True)[1:])
delete_data2.extend(reaction_model3.simulate(time=100,return_data=True)[1:])

delete_data = np.array(delete_data)
non_delete_data = np.array(non_delete_data)
delete_data2 = np.array(delete_data2)

# np.save('delete_model.csv', non_delete_data)



plt.figure(3, figsize=(15,10))
# plt.subplot(2,1,1)
plt.plot(non_delete_data[:,1], label='w.o announcement')
plt.plot(delete_data[:,1], label='w preferential delete')
plt.plot(delete_data2[:,1], label='w random delete')
plt.xlim([0,80])
plt.ylabel('Infected number of people')
plt.xlabel('Day')
plt.legend()
plt.tight_layout()
plt.savefig('3models.png')

empirical_data = pd.read_csv('./empirica.csv', header=False, names=['t', 'i'])
plt.figure(4, figsize=(15,10))
plt.plot(delete_data[:,1], label='simulation data')
plt.plot(empirical_data['t'], empirical_data['i'], 'o-', label='empirical data')
plt.xlim([0,80])
plt.ylabel('Infected Number of People')
plt.xlabel('Time (Days)')
plt.legend()
plt.tight_layout()
plt.savefig('comparison.png')


import csv

with open('synthesized.csv', 'w') as f:
	writer = csv.writer(f)
	for t,i in delete_data.tolist():
		writer.writerow([t,i])


# print('END SIM 1')
# model2 = Model.random_network(2000,
#         5, 
#         ["SCI1", "HUM1","HUM2","SCI2"], 
#         states=[0,1,2],
#         transmission_rate=0.25,
#         recovery_time=7)

# # model2 = Model.create_realistic_network(2000, 
# #               {"SCI,1":lambda:np.random.poisson(5), 
# #               "SCI,2":lambda: np.random.poisson(5), 
# #               "HUM,1":lambda:np.random.poisson(6), 
# #               "HUM,2":lambda:np.random.poisson(6)}, 
# #               {"SCI,1":0.30, "SCI,2":0.2, "HUM,1":0.30, "HUM,2":0.2}, 
# #               {# within class
# #                ("SCI,1","SCI,1"):np.random.rand(),
# #                ("HUM,1","HUM,1"):np.random.rand(),
# #                ("HUM,2","HUM,2"):np.random.rand(),
# #                ("SCI,2","SCI,2"):np.random.rand(),
# #                ("SCI,1","HUM,1"):np.random.rand(),
# #                # cross class
# #                ("SCI,1","HUM,2"):np.random.rand(),
# # 			   ("HUM,1","SCI,2"):np.random.rand(),
# # 			   # in-cross terms
# #                ("SCI,2", "HUM,2"):np.random.rand(),
# #                ("SCI,1","SCI,2"):np.random.rand(),
# #                ("HUM,1", "HUM,2"):np.random.rand()
# #               }, transmission_rate=0.25, recovery_time=7)

# model2.introduce_infection()

# model3 = model2.deep_copy()
# model4 = model2.deep_copy()

# random_data = model2.simulate(until=until, return_data=True)[1:]
# random_data2 = model3.simulate(until=until, return_data=True)[1:]
# random_data3 = model4.simulate(until=until, return_data=True)[1:]

# model2.delete_preferential_edges(2)
# model4.delete_random_edges(2)

# random_data.extend(model2.simulate(time=100,return_data=True)[1:])
# random_data2.extend(model3.simulate(time=100,return_data=True)[1:])
# random_data3.extend(model4.simulate(time=100,return_data=True)[1:])

# random_data = np.array(random_data)
# random_data2 = np.array(random_data2)
# random_data3 = np.array(random_data3)

# plt.title('')
# plt.subplot(2,1,2)
# plt.plot(random_data2[:,1],label='w no delete')
# plt.plot(random_data[:,1], label='w preferential delete')
# plt.plot(random_data3[:,1], label='w random delete')
# plt.ylabel('Infected number of people')
# plt.xlabel('Day')
# plt.legend()
# # plt.title('beta=0.05, gamma=20 / no announcement')
# plt.tight_layout()


