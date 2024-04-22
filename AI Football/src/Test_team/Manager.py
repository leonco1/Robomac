# Choose names for your players and team
    # Choose a funny name for each player and your team
    # Use names written only in cyrillic
    # Make sure that the name is less than 11 characters
    # Don't use profanity!!!
def team_properties():
    properties = dict()
    player_names = ["Пробалдо", "Панчевалдо", "Елмасалдо"]
    properties['team_name'] = "Проба UTD"
    properties['player_names'] = player_names
    properties['image_name'] = 'Blue.png' # use image resolution 153x153
    properties['weight_points'] = (20, 15, 15)
    properties['radius_points'] = (20, 15, 20)
    properties['max_acceleration_points'] = (40, 10, 15)
    properties['max_speed_points'] = (40, 15, 25)
    properties['shot_power_points'] = (30, 25, 18)
    return properties

# This function gathers game information and controls each one of your three players
def decision(our_team, their_team, ball, your_side, half, time_left, our_score, their_score):
    manager_decision = [dict(), dict(), dict()]
    for i in range(3):
        
        # python dictionary with the following keys: 'x', 'y', 'alpha', 'mass', 'radius', 'a_max', 'v_max', 'shot_power_max'
        player = our_team[i] # gather information about each one of your players eg. position
        manager_decision[i]['alpha'] = player['alpha'] # player['alpha'] # choose direction for running (0, 2*pi)
        manager_decision[i]['force'] = 0 # accelerate or deaccelerate your player up to 'v_max' or 0: (-0.5 * 'a_max' * 'mass', 'a_max' * 'mass')
        manager_decision[i]['shot_request'] = True # choose if you want to shoot
        manager_decision[i]['shot_power'] = 100 # use different shot power: (0, 'shot_power_max')
    # print(our_score, their_score)
    # print(our_team[0]['weight'], our_team[0]['radius'], our_team[0]['max_acceleration'], our_team[0]['max_speed'], our_team[0]['shot_power'])
    # print(their_team[0]['weight'], their_team[0]['radius'], their_team[0]['max_acceleration'], their_team[0]['max_speed'], their_team[0]['shot_power'])
    
    return manager_decision
