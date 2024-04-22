import os
import numpy as np
import time
from math import atan2
# Choose names for your players and team
    # Choose a funny name for each player and your team
    # Use names written only in cyrillic
    # Make sure that the name is less than 11 characters
    # Don't use profanity!!!
def team_properties():
    properties = dict()
    player_names = ["Б", "Л", "Г"]
    properties['team_name'] = "Мак Челзи"
    properties['player_names'] = player_names
    properties['image_name'] = 'Red.png' # use image resolution 153x153
    properties['weight_points'] = (90, 1, 15)
    properties['radius_points'] = (5, 100, 20)
    properties['max_acceleration_points'] = (40, 1, 15)
    properties['max_speed_points'] = (40, 1, 25)
    properties['shot_power_points'] = (18, 2, 13)
    return properties

# This function gathers game information and controls each one of your three players
def decision(our_team, their_team, ball, your_side, half, time_left, our_score, their_score):
    manager_decision = [dict(), dict(), dict()]
    for i in range(3):
        player = our_team[i]
        # One player (Б) will chase the ball, while others will default to the base decision.
        if i == 0:

            # Determine the direction towards the ball
            direction_to_ball = (ball['x'] - player['x'], ball['y'] - player['y'])
            # Calculate the angle between the player and the ball
            angle_to_ball = atan2(direction_to_ball[1], direction_to_ball[0])
            manager_decision[i]['alpha'] = angle_to_ball

            manager_decision[i]['force'] = player['a_max']*player["mass"]
            
            manager_decision[i]['shot_request'] = True
            manager_decision[i]['shot_power'] = player['shot_power_max']

            #LEFT GOAL

                #Upper post 50, 343 
                #Lower post 50, 578

            #RIGHT GOAL

                #Upper post 718, 343
                #Lower post 718, 578

        
            
        else:
            # For other players, just use default behavior
            manager_decision[i]['alpha'] = player['alpha']
            manager_decision[i]['force'] = 0
            manager_decision[i]['shot_request'] = True
            manager_decision[i]['shot_power'] = player['shot_power_max']
            
    return manager_decision