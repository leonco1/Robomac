import math
import os

import numpy
import numpy as np
import time
from math import atan2

# Choose names for your players and team
# Choose a funny name for each player and your team
# Use names written only in cyrillic
# Make sure that the name is less than 11 characters
# Don't use profanity!!!
# LEFT GOAL

# Upper post 50, 343
# Lower post 50, 578

# RIGHT GOAL

# Upper post 718, 343
# Lower post 718, 578
left_goal_upper = (50, 343)
left_goal_lower = (50, 578)

right_goal_upper = (718, 343)
right_goal_lower = (718, 578)


# class Square:
#
#     def __init__(self, x, y, radius):
#         self.East = x + radius + 10
#         self.North = y + radius - 10
#         self.West = x - radius - 10
#         self.South = y - radius + 10
#

def get_right_goal():
    # Extract coordinates
    x1, y1 = right_goal_upper
    x2, y2 = right_goal_lower

    # Calculate width and height
    width = x2 - x1
    height = y2 - y1

    # Return dimensions as a tuple
    return width, height


def get_left_goal():
    x1, y1 = left_goal_upper
    x2, y2 = left_goal_lower

    # Calculate width and height
    width = x2 - x1
    height = y2 - y1

    # Return dimensions as a tuple
    return width, height


def team_properties():
    properties = dict()
    player_names = ["Б", "Л", "Г"]
    properties['team_name'] = "Мак Челзи"
    properties['player_names'] = player_names
    properties['image_name'] = 'Red.png'  # use image resolution 153x153
    properties['weight_points'] = (90, 1, 15)
    properties['radius_points'] = (5, 100, 20)
    properties['max_acceleration_points'] = (400, 1, 15)
    properties['max_speed_points'] = (400, 1, 25)
    properties['shot_power_points'] = (18, 2, 13)
    return properties


def pass_ball():
    #TODO MAKE HIM PASS BALL
    return


def make_striker(ball, i, manager_decision, player):
    direction_to_ball = (ball['x'] - player['x'], ball['y'] - player['y'])
    # Calculate the angle between the player and the ball
    angle_to_ball = atan2(direction_to_ball[1], direction_to_ball[0])
    manager_decision[i]['alpha'] = angle_to_ball
    manager_decision[i]['force'] = player['a_max']
    manager_decision[i]['shot_request'] = False
    manager_decision[i]['shot_power'] = player['shot_power_max']


def check_if_collision_with_opponents(player, their_team):
    their_players = (their_team[0], their_team[1], their_team[2])
    opp1 = their_players[0]
    opp2 = their_players[1]
    opp3 = their_players[2]
    if (check_if_any_side_collides(player, opp1) or check_if_any_side_collides(player, opp2) or
            check_if_any_side_collides(player, opp3)):
        return True
    return False


def check_if_within_square(x, y, x1, y1):
    return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5


def check_if_any_side_collides(player, opponent):
    d = check_if_within_square(player['x'], player['y'], opponent['x'], opponent['y'])
    print(d, player['radius'], opponent['radius'])
    if d <= player['radius'] * 1.4 +opponent['radius']*1.4 + 15:
        return True
    return False


def distance_between(obj1, obj2):
    return ((obj2['x'] - obj1['x']) ** 2 + (obj2['y'] - obj1['y']) ** 2) ** 0.5


# def convert_radius_to_square(player):
#     player_as_square = Square(player['x'], player['y'], player['radius'])
#     return player_as_square
#

# This function gathers game information and controls each one of your three players
def decision(our_team, their_team, ball, your_side, half, time_left, our_score, their_score):
    manager_decision = [dict(), dict(), dict()]
    for i in range(3):
        player = our_team[i]
        # One player (Б) will chase the ball, while others will default to the base decision.
        if i == 2:

            # Determine the direction towards the ball
            make_striker(ball, i, manager_decision, player)
            if check_if_collision_with_opponents(player, their_team):
                print("Close")
                return
            else:
                print("Far")


        else:
            # For other players, just use default behavior
            manager_decision[i]['alpha'] = player['alpha']
            manager_decision[i]['force'] = 0
            manager_decision[i]['shot_request'] = True
            manager_decision[i]['shot_power'] = player['shot_power_max']

    return manager_decision
