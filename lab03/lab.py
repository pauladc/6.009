#!/usr/bin/env python3

from tkinter import E
import typing
from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_internal_representation(nodes_filename, ways_filename):
    """
    Create any internal representation you you want for the specified map, by
    reading the data from the given filenames (using read_osm_data)

    The internal representation returns three items: a dictionary of dictionaries
    containing the distance between the current node and its adjacent nodes,
    and the speed associated with the way. It also returns a dictionary with id of nodes
    as keys and tuples of latitutes and longitudes as values. The third item it returns is
    a set of valid nodes.
    """

    valid_nodes = set()
    nodes_rep = {}
    for ways in read_osm_data(ways_filename):
        if 'highway' in ways['tags'] and ways['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
            #calculating the maximum speed of the way
            try:
                max_speed = ways['tags']['maxspeed_mph']
            except:
                max_speed = DEFAULT_SPEED_LIMIT_MPH[ways['tags']['highway']]
            for node in ways['nodes']:
                valid_nodes.add(node)
            if 'oneway' in ways['tags'] and ways['tags']['oneway'] == 'yes':
                #if oneway only the next node can be added as an adjacent node.
                for i in range (len(ways['nodes'])):
                    if ways['nodes'][i] in valid_nodes:
                        if ways['nodes'][i] not in nodes_rep:
                            #creates a dictionary inside the dictionary with the node as a key and the coordinates (to be added) and adjacent nodes as values
                            nodes_rep[ways['nodes'][i]] = dict({1:(), 2:{}})
                        if i != len(ways['nodes'])-1: 
                            #assigns adjacent nodes to the dictionary as keys and the adjacent nodes between which distance will be calculated and speed between as values
                            nodes_rep[ways['nodes'][i]][2][ways['nodes'][i+1]]= (ways['nodes'][i], ways['nodes'][i+1], max_speed)
            else:
                #if not oneway both the next and the previous nodes can be added as adjacent nodes
                for i in range (len(ways['nodes'])):
                    if ways['nodes'][i] in valid_nodes:
                        if ways['nodes'][i] not in nodes_rep:
                            #creates a dictionary inside the dictionary with the node as a key and the coordinates and adjacent nodes as values
                            nodes_rep[ways['nodes'][i]] = dict({1:(), 2:{}})

                        if i != 0:
                            #assigns adjacent nodes to the dictionary as keys and the adjacent nodes between which distance will be calculated and speed between as values
                            nodes_rep[ways['nodes'][i]][2][ways['nodes'][i-1]]= (ways['nodes'][i], ways['nodes'][i-1], max_speed)
                        if i != len(ways['nodes'])-1: 
                            nodes_rep[ways['nodes'][i]][2][ways['nodes'][i+1]]= (ways['nodes'][i], ways['nodes'][i+1], max_speed)
    #assigns coordinates to the nodes
    for e in read_osm_data(nodes_filename):
        if e['id'] in valid_nodes:
            nodes_rep[e['id']][1] = (e['lat'], e['lon'])

    return nodes_rep
     

def find_short_path_nodes(map_rep, node1, node2, fast=False):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    if node1 == node2:
        return [node1]
    queue = [(node1, 0,)]
    visited = set()
    visited.add(node1)
    node2_coords = map_rep[node2][1]
    #creates a dictionary that will hold the previously visited nodes so they can be traced back
    before = {node:None for node in map_rep.keys()}
    #creates a dictionary with the current costs associated with visiting a node
    costs = {node: 1000000 for node in map_rep.keys()}

    while len(queue) != 0:
        zero_queue = queue.pop(0)
        #holds a value of (node, cost in terms of distance, cost in terms of time)
        possible_nodes = map_rep[zero_queue[0]]
        #dictionary of adjacent nodes in the form {node: distance, coordinates}
        current_node = zero_queue[0]
        visited.add(current_node)
        if current_node == node2:
            break
        for node, value in possible_nodes[2].items():
            if node not in visited:
                if fast:
                    #adjust cost based on past + current time
                    #great circle distance is used since distances aren't stored only adjacent nodes
                    cost = zero_queue[1] + great_circle_distance(map_rep[value[0]][1], map_rep[value[1]][1])/value[2]
                    if cost < costs[node]:
                        costs[node] = cost
                        before[node] = current_node    
                        queue.append((node, cost))
                else:
                    #adjusts costs based on past + currenet distance and predicted distance to goal
                    #great circle distance is used twice since distances aren't stored only adjacent nodes
                    cost = zero_queue[1] + great_circle_distance(map_rep[value[0]][1], map_rep[value[1]][1]) + great_circle_distance(map_rep[node][1], node2_coords)
                    if cost < costs[node]:
                        costs[node] = cost
                        before[node] = current_node    
                        queue.append((node, zero_queue[1] + great_circle_distance(map_rep[value[0]][1], map_rep[value[1]][1])))
            queue.sort(key = lambda x: x[1])

    node_path = []
    curr_node = node2
    #traces back the path
    while before[curr_node]!= None:
        node_path.append(curr_node)
        curr_node = before[curr_node]
    if node_path == []:
        return None
    node_path.append(curr_node)
    #reverses the path to return from starting to end node
    node_path.reverse()
    return node_path

       



def find_short_path(map_rep, loc1, loc2, fast=False):
    """
    Return the shortest path between the two locations

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """

    #minimum distances between coordinates given and coordinates guessed
    minlon1, minlon2 = 10000000000, 10000000000
    #guesses to be produced by algorithm
    for key in map_rep.keys():
        #checks to see if node is valid and the distance is less than the minimum
        if great_circle_distance(loc1, map_rep[key][1]) < minlon1:
            minlon1 = great_circle_distance(loc1, map_rep[key][1])
            #finds a possible coordinate
            best_guess1 = key  
        #checks to see if node is valid and the distance is less than the minimum      
        if great_circle_distance(loc2, map_rep[key][1]) < minlon2:
            minlon2 = great_circle_distance(loc2, map_rep[key][1])
            #finds a possible coordinate
            best_guess2 = key
    #checks if a path is found
    if find_short_path_nodes(map_rep, best_guess1, best_guess2, fast) != None:
        return [map_rep[e][1] for e in find_short_path_nodes(map_rep, best_guess1, best_guess2, fast)]
    return None





def find_fast_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    #accounts for the case where speed is prioritized
    return find_short_path(map_rep, loc1, loc2, True)



if __name__ == '__main__':
    wh = (41.4452463, -89.3161394)
    sa = (41.4452463, -89.32)
    map1 = build_internal_representation('resources/midwest.nodes', 'resources/midwest.ways')
    print(to_local_kml_url(find_short_path(map1, wh, sa)))
