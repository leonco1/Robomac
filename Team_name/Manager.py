import os
import numpy as np
import time
import math
from math import atan2
# Choose names for your players and team
    # Choose a funny name for each player and your team
    # Use names written only in cyrillic
    # Make sure that the name is less than 11 characters
    # Don't use profanity!!!

lower_wall = 718
upper_wall = 204
# Goal posts coordinates
left_goal_upper = (50, 383) # not actual value, but place to shoot.
left_goal_lower = (50, 538)
right_goal_upper = (1316, 383)
right_goal_lower = (1316, 538)
middle_of_playground = 460.5
left_goal_area = [350, 150, 560, 50] # North East South West

def team_properties():
    properties = dict()
    player_names = ["Илија Мижимакоски", "Л", "Г"]
    properties['team_name'] = "Мак Челзи"
    properties['player_names'] = player_names
    properties['image_name'] = 'Red.png' # use image resolution 153x153
    properties['weight_points'] = (15, 40, 15)
    properties['radius_points'] = (5, 11, 0)
    properties['max_acceleration_points'] = (40, 40, 15)
    properties['max_speed_points'] = (40, 10, 25)
    properties['shot_power_points'] = (18, 55, 13)
    return properties

def divide_allies(player1, player2, manager_decision):
    manager_decision[0]['force'] = player1['a_max'] * player1["mass"]
    manager_decision[2]['force'] = player2['a_max'] * player2["mass"]
    if player1['y'] > player2['y']:
        manager_decision[0]['alpha'] = (np.pi/2) 
        manager_decision[2]['alpha'] = -(np.pi/2) 
    else:
        manager_decision[0]['alpha'] = -(np.pi/2) 
        manager_decision[2]['alpha'] = (np.pi/2) 

        

def check_if_two_players_collide(player1, player2):
    d = calculate_eucledian_distance_for_circle(player1['x'], player1['y'], player2['x'], player2['y'])
    if d <= player1['radius'] * 1.5 + player2['radius']:
        return True
    return False

def get_proximity_to_wall(wall, radius_player):
    return abs(wall - radius_player)


def check_if_collision_with_opponents(player, their_team, ball):
    their_players = (their_team[0], their_team[1], their_team[2])
    opp1 = their_players[0]
    opp2 = their_players[1]
    opp3 = their_players[2]
    if check_if_any_side_collides(player, opp1, ball):
        return opp1
    if check_if_any_side_collides(player, opp2, ball):
        return opp2
    if check_if_any_side_collides(player, opp3, ball):
        return opp3
    return False

def calculate_eucledian_distance_for_circle(x, y, x1, y1):
    return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5

def check_if_any_side_collides(player, opponent, ball):
    d = calculate_eucledian_distance_for_circle(player['x'], player['y'], opponent['x'], opponent['y'])
    d_ball = calculate_eucledian_distance_for_circle(ball['x'], ball['y'], player['x'], player['y'])

    if d - d_ball <= player['radius'] * 1.5 + opponent['radius'] * 1.5 + 20:
        return True
    return False


def distance_between(obj1, obj2):
    return ((obj2['x'] - obj1['x']) ** 2 + (obj2['y'] - obj1['y']) ** 2) ** 0.5


def get_direction_to_opponent(player, opponent):
    return opponent['y'] - player['y'], opponent['x'] - player['x']

def change_direction_of_ball(player, ball):
    direction_to_ball = get_direction_to_opponent(player, ball)
    angle_to_ball = atan2(direction_to_ball[1], direction_to_ball[0])
    return angle_to_ball if angle_to_ball >= 0 else angle_to_ball + 2 * np.pi


def dribble(player, opponent):

    direction_to_opponent = opponent['y'] - player['y'], opponent['x'] - player['x']
    angle_to_opponent = atan2(direction_to_opponent[1], direction_to_opponent[0])

    return angle_to_opponent

def has_ball(player, ball):
    distance_to_ball = distance_between(player, ball)
    ball_pickup_threshold = 15
    return distance_to_ball < ball_pickup_threshold + player['radius']

def check_if_ball_is_correct_side(ball, player, your_side):
    if your_side == 'left':
        if player['x'] >= ball['x']:
            if player['y'] - upper_wall * 1.5 <= 10:
                return np.pi
            elif lower_wall - player['y'] * 1.5 <= 10:
                return -np.pi
            else:
                return -np.pi
        else:
            return player['alpha']
    if your_side == 'right':
        if player['x'] <= ball['x']:
            if player['y'] - upper_wall * 1.5 <= 10:
                return np.pi
            elif lower_wall - player['y'] * 1.5 <= 10:
                return -np.pi
            return -np.pi
        else:
            return player['alpha']

def run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side):
    if has_ball(player, ball):
        manager_decision[i]['force'] = player['a_max'] * player["mass"]  # Maximum acceleration to move quickly
        manager_decision[i]['alpha'] = 2 * np.pi - check_if_ball_is_correct_side(ball, player, your_side)
        opponent = check_if_collision_with_opponents(player, their_team, ball)
        if check_if_collision_with_opponents(player, their_team, ball):
            manager_decision[i]['alpha'] = 2*np.pi + dribble(player, opponent)
            manager_decision[i]['alpha'] = 2 * np.pi - check_if_ball_is_correct_side(ball, player, your_side)
        else:
            manager_decision[i]['alpha'] = check_if_ball_is_correct_side(ball, player, your_side)

    else:
        #make_striker(ball, i, manager_decision, player)
        manager_decision[i]['alpha'] = 2 * np.pi - check_if_ball_is_correct_side(ball, player, your_side)
        dist_target = ((player['x'] - target_x) ** 2 + (player['y'] - target_y) ** 2) ** 0.5
        if dist_target > 15:
            target_angle = math.atan2(target_y - player['y'], target_x - player['x'])
            manager_decision[i]['alpha'] = target_angle
            manager_decision[i]['force'] = player['a_max'] * player["mass"]  # Maximum acceleration to move quickly
        else:
            manager_decision[i]['force'] = 0
            manager_decision[i]['alpha'] = np.pi
        # manager_decision[i]['alpha'] = check_if_ball_is_correct_side(ball, player, your_side)






# def run_player_to_target(player, i, manager_decision, target_x, target_y, ball):
#     # Calculate the distance to the target position
#     dist_target = ((player['x'] - target_x)**2 + (player['y'] - target_y)**2)**0.5
    
#     # Calculate the angle to the target position using arctangent function
#     target_angle = math.atan2(target_y - player['y'], target_x - player['x'])
  
#     # Set the direction (alpha) and force for the player in the manager_decision dictionary
#     manager_decision[i]['alpha'] = target_angle
#     manager_decision[i]['force'] = player['a_max'] * player["mass"]   # Maximum acceleration to move quickly and leave room for 15 pixels.




def run_keeper_to_ball_and_shoot(player,i,manager_decision,dist_ball,ball,your_side):
    # Move goalkeeper more vertically towards the ball
    target_angle = math.atan2(ball['y'] - player['y'], ball['x'] - player['x'])

    if(your_side == 'left'):
        vertical_angle = math.atan2(ball['y'] - player['y'], 75 - player['x'])  # Angle towards vertical
    else:
        vertical_angle = math.atan2(ball['y'] - player['y'], 1290 - player['x'])  # Angle towards vertical

    weighted_angle = 0.5 * target_angle + 0.5 * vertical_angle  # Weighted average of target and vertical angles
    manager_decision[i]['alpha'] = weighted_angle
    manager_decision[i]['force'] = player['a_max'] * player["mass"]

    if player['x']<ball['x'] and your_side == 'left': 
        manager_decision[i]['shot_request'] = True
    if player['x']>ball['x'] and your_side == 'right':
        manager_decision[i]['shot_request'] = True

def manage_goalkeeper_left(ball, your_side, manager_decision, i, player, dist_ball, their_team):
    if ball['x'] < 300 and (ball['y'] >= 303 and ball['y'] <= 613):
        # If the ball is under certain other coordinates and the player is in a specific area
        run_keeper_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side)
    elif ball['x'] < 400 and ball['y'] < middle_of_playground:
        # If the ball is under certain coordinates
        target_x, target_y = 75, middle_of_playground - 50
        run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
    elif ball['x'] < 400 and ball['y'] > middle_of_playground:
        # If the ball is under certain coordinates
        target_x, target_y = 75, middle_of_playground + 50
        run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
    else:
        # Default behavior if ball is not in specific ranges
        target_x, target_y = 75, middle_of_playground
        run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)

def manage_goalkeeper_right(ball, your_side, manager_decision, i, player, dist_ball, their_team):
    if ball['x'] > 950 and (ball['y'] >= 303 and ball['y'] <= 613):
        # If the ball is under certain other coordinates and the player is in a specific area
        run_keeper_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side)
    elif ball['x'] > 1050 and ball['y'] < middle_of_playground:
        # If the ball is under certain coordinates
        target_x, target_y = 1316, middle_of_playground - 50
        run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
    elif ball['x'] > 1050 and ball['y'] > middle_of_playground:
        # If the ball is under certain coordinates
        target_x, target_y = 1316, middle_of_playground + 50
        run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
    else:
        # Default behavior if ball is not in specific ranges
        target_x, target_y = 1316, middle_of_playground
        run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
        
def run_player_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side):
    
    if player['x']<ball['x'] and your_side == 'left': 
        manager_decision[i]['shot_request'] = True
    if player['x']>ball['x'] and your_side == 'right':
        manager_decision[i]['shot_request'] = True

    target_angle = math.atan2(ball['y'] - player['y'], ball['x'] - player['x'])
    manager_decision[i]['alpha'] = target_angle
    manager_decision[i]['force'] = player['a_max'] * player["mass"]


def find_coordinates_for_straight_shot(ball, goal_post, player, your_side):
    
    if your_side == 'left':
        distance_to_go_from_ball = -(player['radius'] + 15)
        # Calculate the slope of the line between the ball and the left post
        dx = goal_post[0] - ball['x']
        dy = goal_post[1] - ball['y']
    else:
        distance_to_go_from_ball = (player['radius'] + 15)
        # Calculate the slope of the line between the ball and the right post
        dx = ball['x'] - goal_post[0]
        dy = ball['y'] - goal_post[1]
        
    if dx != 0:  # Avoid division by zero
        slope = dy / dx
    else:
        slope = float('inf')  # Vertical line
    
    # Determine the sign of the change in x and y based on the quadrant of the goal post relative to the ball
    if dx > 0:
        sign_x = 1
    else:
        sign_x = -1
    
    if dy > 0:
        sign_y = 1
    else:
        sign_y = -1
    
    # Calculate the new coordinates for the player
    new_x = ball['x'] + sign_x * distance_to_go_from_ball / math.sqrt(1 + slope**2)
    new_y = ball['y'] + sign_y * slope * distance_to_go_from_ball / math.sqrt(1 + slope**2)
    
    return new_x, new_y


def run_after_fastest(player, i, manager_decision, their_team, ball):
    target_angle = math.atan2(their_team[0]['y'] - player['y'], their_team[0]['x'] - player['x'])
    manager_decision[i]['alpha'] = target_angle
    manager_decision[i]['force'] = player['a_max'] * player["mass"]


# This function gathers game information and controls each one of your three players
def decision(our_team, their_team, ball, your_side, half, time_left, our_score, their_score):
    manager_decision = [dict(), dict(), dict()]


    for i in range(3):
        if(your_side == 'left'):
            player = our_team[i]
            manager_decision[i]['shot_power'] = player['shot_power_max']
            manager_decision[i]['shot_request'] = False

            
            if i == 0:
                dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                
                dist_to_teammate = ((player['x'] - our_team[2]['x'])**2 + (player['y'] - our_team[2]['y'])**2)**0.5 - our_team[2]['radius'] - player['radius']
                if dist_to_teammate<5:
                    divide_allies(player,our_team[2],manager_decision)
                    continue
               
                if(player['y']>middle_of_playground):
                    target_x, target_y = find_coordinates_for_straight_shot(ball, right_goal_upper, player, your_side)
                else:
                    target_x, target_y = find_coordinates_for_straight_shot(ball, right_goal_lower, player, your_side)
                run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                dist_target = ((player['x'] - target_x)**2 + (player['y'] - target_y)**2)**0.5 - player['radius']

                if dist_target <= 2 and player['x'] < ball['x']:
                    run_player_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side)

            elif i == 1:  # If player is the goalkeeper
                dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                manage_goalkeeper_left(ball, your_side, manager_decision, i, player, dist_ball, their_team)

            elif i == 2: 
                dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                striker_dist_to_ball = ((our_team[0]['x'] - ball['x'])**2 + (our_team[0]['y'] - ball['y'])**2)**0.5 - 15 - our_team[0]['radius']
                if ball['x'] < 100 and player['x'] < ball['x']:
                    # If the ball is under certain other coordinates and the player is in a specific area
                    run_keeper_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side)
                elif ball['x'] < 400 and ball['y'] < middle_of_playground:
                    # If the ball is under certain coordinates
                    target_x, target_y = 75, middle_of_playground + 50
                    run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                elif ball['x'] < 400 and ball['y'] > middle_of_playground:
                    # If the ball is under certain coordinates
                    target_x, target_y = 75, middle_of_playground - 50
                    run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                # While attacking, and striker is fighting for the ball on the bottom    
                elif ball['x'] > 1000 and ball['y'] > middle_of_playground and our_team[0]['y']>middle_of_playground and striker_dist_to_ball <= 100: 
                    dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                    target_x, target_y = 1100 , 300
                    run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                    if dist_ball <= 100:
                        run_player_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side) 
                # While attacking, and striker is fighting for the ball on the top 
                elif ball['x'] > 1000 and ball['y'] < middle_of_playground and our_team[0]['y']<middle_of_playground and striker_dist_to_ball <= 100: 
                    dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                    target_x, target_y = 1100 , 500
                    run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                    if dist_ball <= 100:
                        run_player_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side)   
                else:
                    
                    dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                    if(player['y']>middle_of_playground):
                        target_x, target_y = find_coordinates_for_straight_shot(ball, right_goal_upper, player, your_side)
                    else:
                        target_x, target_y = find_coordinates_for_straight_shot(ball, right_goal_lower, player, your_side)
                    run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                    dist_target = ((player['x'] - target_x)**2 + (player['y'] - target_y)**2)**0.5 - player['radius']

                    if dist_target <= 2 and player['x'] < ball['x']:
                        run_player_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side)
            else:
                manager_decision[i]['alpha'] = np.pi # player['alpha'] # choose direction for running (0, 2*pi)
                manager_decision[i]['force'] = 0 # accelerate or deaccelerate your player up to 'v_max' or 0: (-0.5 * 'a_max' * 'mass', 'a_max' * 'mass')
        
        # RIGHT        
        else:
            
            player = our_team[i]
            manager_decision[i]['shot_power'] = player['shot_power_max']
            manager_decision[i]['shot_request'] = False

            
            if i == 0:

                dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                
                dist_to_teammate = ((player['x'] - our_team[2]['x'])**2 + (player['y'] - our_team[2]['y'])**2)**0.5 - our_team[2]['radius'] - player['radius']
                if dist_to_teammate<5:
                    divide_allies(player,our_team[2],manager_decision)
                    continue

                if(player['y']>middle_of_playground):
                    target_x, target_y = find_coordinates_for_straight_shot(ball, left_goal_lower, player, your_side)
                else:
                    target_x, target_y = find_coordinates_for_straight_shot(ball, left_goal_upper, player, your_side)
                run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                dist_target = ((player['x'] - target_x)**2 + (player['y'] - target_y)**2)**0.5 - player['radius']

                if dist_target <= 2 and player['x'] > ball['x']:
                    run_player_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side)

            elif i == 1:  # If player is the goalkeeper
                dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                manage_goalkeeper_right(ball, your_side, manager_decision, i, player, dist_ball, their_team)

            elif i == 2: 

                dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                striker_dist_to_ball = ((our_team[0]['x'] - ball['x'])**2 + (our_team[0]['y'] - ball['y'])**2)**0.5 - 15 - our_team[0]['radius']
                if ball['x'] > 1266 and player['x'] > ball['x']:
                    # If the ball is under certain other coordinates and the player is in a specific area
                    run_keeper_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side)
                elif ball['x'] > 966 and ball['y'] < middle_of_playground:
                    # If the ball is under certain coordinates
                    target_x, target_y = 1316, middle_of_playground + 50
                    run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                elif ball['x'] > 966 and ball['y'] > middle_of_playground:
                    # If the ball is under certain coordinates
                    target_x, target_y = 1316, middle_of_playground - 50
                    run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                                # While attacking, and striker is fighting for the ball on the bottom    
                elif ball['x'] < 300 and ball['y'] > middle_of_playground and our_team[0]['y']>middle_of_playground and striker_dist_to_ball <= 100: 
                    dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                    target_x, target_y = 200 , 300
                    run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                    if dist_ball <= 100:
                        run_player_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side) 
                # While attacking, and striker is fighting for the ball on the top 
                elif ball['x'] < 300 and ball['y'] < middle_of_playground and our_team[0]['y']<middle_of_playground and striker_dist_to_ball <= 100: 
                    dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                    target_x, target_y = 200 , 500
                    run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                    if dist_ball <= 100:
                        run_player_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side)   
                else:
                    dist_ball = ((player['x'] - ball['x'])**2 + (player['y'] - ball['y'])**2)**0.5 - 15 - player['radius']
                    if(player['y']>middle_of_playground):
                        target_x, target_y = find_coordinates_for_straight_shot(ball, left_goal_lower, player, your_side)
                    else:
                        target_x, target_y = find_coordinates_for_straight_shot(ball, left_goal_upper, player, your_side)
                    run_player_to_target(player, i, manager_decision, target_x, target_y, ball, their_team, your_side)
                    dist_target = ((player['x'] - target_x)**2 + (player['y'] - target_y)**2)**0.5 - player['radius']

                    if dist_target <= 2 and player['x'] > ball['x']:
                        run_player_to_ball_and_shoot(player, i, manager_decision, dist_ball, ball, your_side)
            else:
                manager_decision[i]['alpha'] = np.pi # player['alpha'] # choose direction for running (0, 2*pi)
                manager_decision[i]['force'] = 0 # accelerate or deaccelerate your player up to 'v_max' or 0: (-0.5 * 'a_max' * 'mass', 'a_max' * 'mass')

        
                
    return manager_decision

