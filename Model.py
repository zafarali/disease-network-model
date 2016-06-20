import numpy as np
from collections import Counter
from BaseObjects import Individual
import random

# np.random.seed(1)

class Model(object):
    def __init__(self, transmission_rate, recovery_time, states=[0,1]):
        """
            Creates a model
        """
        np.random.seed(1)
        self.transmission_rate = transmission_rate
        self.recovery_time = recovery_time
        self.states = states
        self.infecteds = []
        self.individuals = []
        self.total_time = 0

    def deep_copy(self):

        new_model = Model(self.transmission_rate, self.recovery_time, states=self.states)
        new_model.infecteds = list(self.infecteds)
        new_model.individuals = []
        for individual in self.individuals:
            new_model.individuals.append(
                Individual(
                    individual.id, 
                    individual.state, 
                    [ (k,v) for k,v in individual.friends], 
                    individual.properties, 
                    individual.time_since_infected))
        new_model.partitioning = dict(self.partitioning)
        new_model.total_time = self.total_time
        return new_model

    @staticmethod
    def random_network(num_individuals,
        poisson_parameter, 
        partitioning, 
        states=[0,1],
        transmission_rate=1,
        recovery_time=4):
        """
            Creates a random poisson network of individuals
            @params:
                num_individuals: the number of individuals in the network
                poisson_parameter: the avergage number of connections
                states[=0,1]: the possible states of the network
        """
        model = Model(transmission_rate, recovery_time, states=states)
        model.partitioning = { p:[] for p in partitioning}
        # create all the new individuals        
        model.individuals = map(lambda i: Individual(i, properties=np.random.choice(partitioning), state=states[0]), xrange(num_individuals))

        # loop to generate add friends to individuals
        for individual in model.individuals:
            
            k = np.random.poisson(poisson_parameter) # number of connections

            for fid in np.random.randint(num_individuals, size=k):
                # add the connections between the two
                individual.add_connection(fid)
                model.individuals[fid].add_connection(individual.id)
            #endfor friends
        #endfor over all individuals

        return model

    @staticmethod
    def create_realistic_network(num_individuals, 
        num_connections, 
        partitioning, 
        friend_distribution, 
        states=[0,1], 
        symmetric=True,
        transmission_rate=1,
        recovery_time=4):
        """
            Creates a Network of individuals
            @params:
                num_individuals: the number of individuals in this network
                num_connections: the average number of connections in this network OR
                        a dict with the average number of connections for each partitioning.
                        note that the number can be a function that returns an integer.
                        eg: {"MALE,1": 5, "FEMALE,1":6, ... }
                        OR {"MALE,1": lambda : np.random.poisson(5) }
                partitioning: describes how the individuals should be partitioned. 
                        Must be a dictionary whose keys are comma separated according to characteristics.
                        (!) entries must add to 1
                        @example:
                            {"MALE,1":0.5, "MALE,2":0.25, "FEMALE,1":0, "FEMALE,2":0.25}
                friend_distribution: describes how the connections should be added in the network.
                        Must be a dictionary of tuples containing characteristics.
                    @example:
                        {("MALE,1","FEMALE,2"):0.5, ("MALE,1","MALE,2"):0.75,...}
                states: the states in this model (=[0,1]) (state[0] must be the default state)
                symmetric: if True it implies that if X is friends with Y, it automatically implies that Y is friends with X
                transmission_rate: the probability that a contact would result in a transmission
                recovery_time: the time taken to recover from the infected state into the recovered state.
                # (!) contact strenghts not yet supported.
        """
        assert np.sum(partitioning.values()) == 1, 'Partitioning must add to 1. Instead added to: '+str(np.sum(partitioning.values()))
        assert len(states) >= 1, 'Must have at least 1 state'
        assert type(num_connections) in [int, dict], 'number of connections is of unknown type.'

        model = Model(transmission_rate, recovery_time, states=states)

        # create a partitioning for easy access later.
        model.partitioning = { key: [] for key in partitioning.keys() }
        model.individuals = []
        model.infecteds = []


        #create our individuals
        for i in range(num_individuals):
            
            unif = np.random.random() #generate a uniform variable
            #determine the partition of this individual:

            prev_prob = 0 
            selected_key = ""
            for key, prob in partitioning.items():
                # just checks if a uniform is in a certain length
                if unif <= prev_prob+prob and unif > prev_prob:
                    selected_key = key
                    break
                else:
                    prev_prob += prob
            
            created_individual = Individual(i, properties=selected_key, state=states[0])
            
            model.individuals.append(created_individual)
            model.partitioning[selected_key].append(created_individual)
        print('Created '+str(num_individuals)+' individuals. Now creating network')
        # format the connections variable properly. 
        if type(num_connections) is int:
            num_connections = { key: num_connections for key in partitioning.keys()}
        
        # calculate the total number of connections in this network
        total_num_connections = 0
        try:
            for k,v in model.partition_summary():
                # check if the number is actualy a number or a function.
                total_num_connections += num_connections[k]() * v if hasattr(num_connections[k], '__call__') else num_connections[k] * v
        except KeyError as e:
            raise Exception("A key wasn't specified in num_connections: "+ str(e))
            
        print('Number of connections: '+str(total_num_connections)+'. Now creating...')
        # create some connections
        j = 0
        while j < total_num_connections:
            if j % 5000 == 0:
                print('Created '+str(j)+' connections')
            if j > total_num_connections * 5:
                raise Exception("Made too many connection attempts")
            j+=1 #increment
            # pick two random individuals from the population
            individual_1 = model.individuals[np.random.randint(num_individuals)]
            individual_2 = model.individuals[np.random.randint(num_individuals)]
            if individual_1.id == individual_2.id: #make sure they are not the same
                continue
            
            # determine the average number of connections for this individual:
            k = individual_1.properties # the property
            avg_num_connections = num_connections[k]() if hasattr(num_connections[k], '__call__') else num_connections[k] 

            if len(individual_1.friends) < avg_num_connections:
                # only add a new friend if the current num of connections is less than the avg.

                # get the probabilitiy of such a pair being friends.
                try:
                    prob_of_friendship = friend_distribution[(individual_1.properties, individual_2.properties)]
                except KeyError as e: # could not find the pair, try the reverse if symmetrical.
                    if symmetric:
                        prob_of_friendship = friend_distribution[(individual_2.properties, individual_1.properties)]
                    else:
                        raise KeyError('Could not find pair friendship probability.')

                # determine if the friend pair will exist
                unif = np.random.random()
                if unif < prob_of_friendship:
                    individual_1.add_connection(individual_2.id)
                    if symmetric:
                        individual_2.add_connection(individual_1.id)
                    #endif symmetric
                #endif unif
            #endif avg
        #endwhile
        
        return model

    def partition_summary(self, detailed=False):
        """

        """ 
        if detailed:
            raise NotImplemented("Not Implemented Yet")
        else:
            return map( lambda k: (k[0],len(k[1])), self.partitioning.items())

    def edge_list(self):
        """
            returns an array of edge-edge connections with 
            source_id,target_id,strength,class,state
        """
        to_return = ['source,target,strength,class,state']
        for i in self.individuals:

            for fid,c in i.friends:
                to_return.append(str(i.id)+','+str(fid)+','+str(c)+','+i.properties.replace(',','')+','+str(i.state))

        return to_return

    def export_network(self, format='JSON'):
        if not 'JSON':
            return self.edge_list()

        nodes = []
        links = []
        for i in self.individuals:
            nodes.append({
                "name":i.id,
                "group":i.properties,
                "state":i.state
                })

            for f,v in i.friends:
                links.append({
                    "source":i.id,
                    "target":f,
                    "value":v
                    })

        return {"links":links, "nodes":nodes}

    def introduce_infection(self, infected_id=False, infected_state=None):
        """
            Turns an individual into an infected.
            @params:
                id: the ID of the individual to make infected.
                    By default this is random.
        """
        infected_id = infected_id if infected_id else np.random.randint(len(self.individuals)) 
        
        if not self.infecteds:
            self.infecteds = []

        self.individuals[infected_id].state = infected_state if infected_state else self.states[1]
        self.infecteds.append(infected_id)

    def simulate(self, time=100, printer=False, return_data=False, until=None):
        """ 
            Runs the simulation on the network
            @params:
                time[=100]: the amount of time that the simulation must be run
                per_day_interaction_fraction[=0.5]: the fraction of people that will interact per day
        """


        #N = len(self.individuals)
        #num_interactions_per_day = per_day_interaction_fraction * N

        # range through all time
        to_return = [('time', 'num_infected')]
        backlog = []

        for t in xrange(time):
            # generate a list of selected individuals

            #selected_individuals = np.random.randint(N, size=num_interactions_per_day)
            stored_infecteds = []
            infecteds_count = Counter()
            # loop through all individuals
            # print self.infecteds
            for i in self.infecteds:
                
                individual = self.individuals[i]
                # if t == 0:
                #     print individual.time_since_infected
                # print('->checking individual:'+str(individual.id)+', #friends:'+str(len(individual.friends)))
                for friendid, _ in individual.friends:
                    unif = np.random.random() 
                    if self.individuals[friendid].state == 0:
                        if unif < self.transmission_rate: # person gets infected
                            # print 'friend added=',friendid
                            self.individuals[friendid].state = 1
                            self.individuals[friendid].time_since_infected = 0
                            stored_infecteds.append(friendid)
                            infecteds_count.update(self.individuals[friendid].properties)
                            #endif
                    #endfor
                if individual.time_since_infected > np.random.poisson(self.recovery_time)+np.random.randint(5):
                    individual.state = 2
                    self.infecteds.remove(individual.id)
                else:
                    individual.time_since_infected += 1
                
            # print 't=',self.total_time
            self.total_time += 1
            if self.total_time % 6 == 0 or self.total_time % 5 == 0:
                backlog.extend(stored_infecteds)
            else:
                if len(backlog) > 0:
                    # print 'extended:',backlog
                    self.infecteds.extend(backlog)
                    backlog = []
                self.infecteds.extend(stored_infecteds)
            #endfor
            if return_data:
                to_return.append((t, len(self.infecteds)))
            if printer:
                print(str(t)+','+str(len(self.infecteds)))
            else:
                # print('t='+str(t)+', # infected individuals='+str(len(self.infecteds)))
                pass
            if until and len(self.infecteds) > until:
                print until
                print('Reached '+str(len(self.infecteds))+' infected individuals at t='+str(t))
                break
        #end dayloop

        if return_data:
            return to_return


    def delete_random_edges(self, num_edges):
        
        deleted_edges = 0
        for individual in self.individuals:

            k = len(individual.friends)
            to_delete_proposed = np.random.poisson(num_edges)
            to_delete = to_delete_proposed if to_delete_proposed < k else k

            to_delete = random.sample(individual.friends, to_delete)
            for rem in to_delete:
                deleted_edges+=1
                self.individuals[rem[0]].friends.remove((individual.id,1))
                individual.friends.remove(rem)

        print('Deleted: '+str(deleted_edges)+' edges')
    def delete_preferential_edges(self, num_edges):
        """
            Deletes a random num of edges for non-self classes.
        """
        deleted_edges = 0
        for individual in self.individuals:
            k = len(individual.friends)

            to_delete = np.random.poisson(num_edges)
            to_delete = to_delete if to_delete < k else k
            to_delete = random.sample(individual.friends, to_delete)
            for rem in to_delete:
                if self.individuals[rem[0]].properties != individual.properties:
                    deleted_edges+=1
                    # only delete if we do not share properties.
                    self.individuals[rem[0]].friends.remove((individual.id,1))
                    individual.friends.remove(rem)
        print('Deleted: '+str(deleted_edges)+' edges')
