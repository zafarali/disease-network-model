import numpy as np
from collections import Counter

class Individual(object):
    def __init__(self, id, state=0, friends=[], properties=""):
        """
            Creates an individual in the network.
            @params:
                id : the ID of this individual
                state: the state of this individual 
                friends: array of (individual_id, contact_strength) 
                        that describes this individuals connectsion
                properties: a comma separated string with characteristics
        """
        self.id = id
        self.friends = friends if len(friends) else [] # tuples containing (individual_id, contact_strength)
        self.state = state 
        self.properties = properties
    def add_connection(self, friend_id, contact_strength=1):
        """
            Adds a connection to this individual
            @params:
                friend_id: the ID of the friend
                contact_strength: the strength of the contact [=1]
        """
        self.friends.append((friend_id, contact_strength))
    def describe_friends(self, individuals):
        return Counter(map(lambda f: individuals[f[0]].properties, self.friends))
    def __repr__(self):
        return "<< INDIVIDUAL_ID:"+str(self.id)+", STATE:"+str(self.state)+", "+"PROPERTIES:"+str(self.properties)+">>"
    def __str__(self):
        return "<< INDIVIDUAL_ID:"+str(self.id)+", STATE:"+str(self.state)+", "+"PROPERTIES:"+str(self.properties)+"\n"+"FRIENDS:"+str(self.friends)+">>\n"