import numpy as np
from collections import Counter
from BaseObjects import Individual

np.random.seed(1)

class Model(object):
    def __init__(self, 
        num_individuals, 
        num_connections, 
        partitioning, 
        friend_distribution, 
        states=[0,1], 
        symmetric=True,
        transmission_rate=1,
        recovery_time=4
        ):
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


        self.recovery_time = recovery_time
        self.transmission_rate = transmission_rate
        self.states = states

        #create a partitioning for easy access later.
        self.partitioning = { key: [] for key in partitioning.keys() }
        self.individuals = []
        self.infecteds = []

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
            
            self.individuals.append(created_individual)
            self.partitioning[selected_key].append(created_individual)
        
        # format the connections variable properly. 
        if type(num_connections) is int:
            num_connections = { key: num_connections for key in partitioning.keys()}
        
        # calculate the total number of connections in this network
        total_num_connections = 0
        try:
            for k,v in self.partition_summary():
                # check if the number is actualy a number or a function.
                total_num_connections += num_connections[k]() * v if hasattr(num_connections[k], '__call__') else num_connections[k] * v
        except KeyError as e:
            raise Exception("A key wasn't specified in num_connections: "+ str(e))
            

        # create some connections
        j = 0
        while j < total_num_connections:
            if j > total_num_connections * 5:
                raise Exception("Made too many connection attempts")
                
            # pick a random individual from the population
            individual_1 = self.individuals[np.random.randint(num_individuals)]
            individual_2 = self.individuals[np.random.randint(num_individuals)]
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

            j+=1 #increment

    def partition_summary(self, detailed=False):
        """

        """ 
        if detailed:
            raise NotImplemented("Not Implemented Yet")
        else:
            return map( lambda k,v: (k,len(v)), self.partitioning.items())

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
                "group":i.properties
                })

            for f,v in i.friends:
                links.append({
                    "source":i.id,
                    "target":f,
                    "value":v
                    })

        return {"links":links, "nodes":nodes}

    def introduce_infection(self, infected_id=False):
        """
            Turns an individual into an infected.
            @params:
                id: the ID of the individual to make infected.
                    By default this is random.
        """
        infected_id = infected_id if infected_id else np.random.randint(len(self.individuals)) 

        self.individuals[infected_id].state = self.states[1]
        self.infecteds.append(infected_id)

    def simulate(self, time=100, per_day_interaction_fraction=0.5):
        """ 
            Runs the simulation on the network
            @params:
                time[=100]: the amount of time that the simulation must be run
                per_day_interaction_fraction[=0.5]: the fraction of people that will interact per day
        """


        #N = len(self.individuals)
        #num_interactions_per_day = per_day_interaction_fraction * N

        # range through all time
        for t in xrange(time):
            # generate a list of selected individuals
            #selected_individuals = np.random.randint(N, size=num_interactions_per_day)
            stored_infecteds = []
            # loop through all individuals
            for i in self.infecteds:
                individual = self.individuals[i]
                for friendid, _ in individual.friends:
                    if individual.state == 0:
                        unif = np.random.random() 
                        if unif < self.transsmission_rate:
                            self.individuals[friendid].state = 1
                            self.individuals[friendid].time_since_infected = 0
                            stored_infecteds.append(friendid)
                                    #endif
                            #endif
                    #endfor
                if individual.time_since_infected < 4:
                    individual.time_since_infected += 1
                
                elif individual.time_since_infected == 4:
                    individual.state = 2
                    self.infecteds.remove(individual.id)
                    
            self.infecteds = self.infecteds + stored_infecteds   
             #endfor
             
                       
                # if you are infected, loop through all friends and
                # attempt to infect them with prob self.transmission_rate
                # if and only if they are in state[0]

                    
                
                # also increment individual.time_since_infected
                
                
                # so that you can check if they recover self.recovery
                # if recovered change their self.state to state[2]
        #end dayloop
