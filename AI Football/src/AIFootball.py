import time
import random
import numpy as np
import pandas as pd
import pygame
from Team_name import Manager as team_1_script
from Test_team import Manager as team_2_script
import os

game_name = 'AI Football'
fps = 60
dt = 1 / fps

resolution = 1366, 768
resolution_rect = [0, 0, resolution[0], resolution[1]]
ground = [0, int(resolution[1]/5), resolution[0], resolution[1]]
ground_rect = [ground[0], ground[1], resolution[0], resolution[1]]
playground = [50, 50 + int(resolution[1]/5), resolution[0] - 50, resolution[1] - 50]
playground_rect = [playground[0], playground[1], playground[2] - playground[0], playground[3] - playground[1]]
half_playground_rect = [playground_rect[0], playground_rect[1], int(playground_rect[2]/2), playground_rect[3]]
center = [int((playground[2] - playground[0]) / 2) + playground[0],
          int((playground[3] - playground[1]) / 2) + playground[1]]

post_radius = 10
post_screen_top = 343
post_screen_bottom = 578
post_screen_left = playground[0]
post_screen_right = playground[2]

player_1_initial_position = [int((center[0] - playground[0])/2) + playground[0] - 10, post_screen_top]
player_2_initial_position = [int((center[0] - playground[0])/2) + playground[0] - 10, center[1]]
player_3_initial_position = [int((center[0] - playground[0])/2) + playground[0] - 10, post_screen_bottom]
player_4_initial_position = [player_1_initial_position[0] + half_playground_rect[2] + 10, post_screen_top]
player_5_initial_position = [player_2_initial_position[0] + half_playground_rect[2] + 10, center[1]]
player_6_initial_position = [player_3_initial_position[0] + half_playground_rect[2] + 10, post_screen_bottom]

initial_positions_team_left = [player_1_initial_position, player_2_initial_position, player_3_initial_position]
initial_positions_team_right = [player_4_initial_position, player_5_initial_position, player_6_initial_position]

# Colors:
black = [0, 0, 0]
white = [255, 255, 255]
red = [255, 0, 0]
yellow = [255, 255, 0]
green = [0, 255, 0]
sky_blue = [135, 206, 250]
blue = [0, 0, 255]
grass = [1, 142, 14]

cursor_width = 2

ball_restitution = 0.6
player_player_restitution = 0.5
ball_restitution_under_player_control = 0.4
player_post_restitution = 0.5
half_time_duration = 45
short_pause_countdown_time = 5
goal_pause_countdown_time = 5

shift = 230
team_left_logo_position = [22 + shift, 2, 153, 153]
team_right_logo_position = [527 + shift, 2, 153, 153]
team_left_color_position = [173 + shift, 0, 50, 153]
team_right_color_position = [477 + shift, 0, 50, 153]
post_mass = 1e99

# Player stats: Kylian Mbappé, Joshua Kimmich, Joško Gvardiol
weights = [73, 75, 80]
radiuses = [22, 23, 24]
accelerations = [100, 60, 70]
speeds = [100, 60, 85]
shot_powers = [65, 70, 50]

def get_weight(points):
    if points <= 10:
        return 60 + 1.5 * points
    elif points <= 20:
        return 65 + points
    elif points <= 50:
        return 75 + 0.5 * points
    else:
        return 100

def get_radius(points):
    if points <= 10:
        return 21 + 0.2 * points
    elif points <= 20:
        return 22 + 0.1 * points
    elif points <= 40:
        return 23 + 0.05 * points
    else:
        return 25

def get_acceleration(points):
    if points <= 10:
        return 30 + 3 * points
    elif points <= 20:
        return 40 + 2 * points
    elif points <= 40:
        return 60 + points
    else:
        return 100

def get_speed(points):
    if points <= 10:
        return 30 + 3 * points
    elif points <= 20:
        return 40 + 2 * points
    elif points <= 40:
        return 60 + points
    else:
        return 100

def get_shot_power(points):
    if points <= 20:
        return 10 + 3 * points
    elif points <= 30:
        return 20 + 2 * points
    elif points <= 40:
        return 50 + points
    else:
        return 90
        
class Circle:
    def __init__(self, x=0, y=0, radius=0, mass=1, alpha=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        self.alpha = alpha
        self.v = 0


class Player(Circle):
    a_fifa = 0.75
    v_fifa = 0.88
    shot_power_fifa = 0.95
    a_max_coeff = 22
    v_max_coeff = 7
    shot_power_max_coeff = 200
    a_max = a_max_coeff * a_fifa
    v_max = v_max_coeff * v_fifa
    shot_power_max = shot_power_max_coeff * shot_power_fifa
    shot_power = shot_power_max
    shot_request = False

    def __init__(self, name, weight, radius, acceleration, speed, shot_power):
        self.name = name
        self.mass = int(weight)
        self.radius = int(radius)
        self.a_fifa = int(acceleration)
        self.v_fifa = int(speed)
        self.shot_power_fifa = int(shot_power)
        self.v_max = self.v_max_coeff * self.v_fifa
        self.a_max = self.a_max_coeff * self.a_fifa
        self.shot_power_max = self.shot_power_max_coeff * self.shot_power_fifa

    def move(self, manager_decision):
        force = np.clip(manager_decision['force'], -0.5 * self.a_max * self.mass, self.a_max * self.mass)
        self.alpha = manager_decision['alpha']
        self.shot_power = np.clip(manager_decision['shot_power'], 0, self.shot_power_max)
        self.shot_request = manager_decision['shot_request']
        self.v += force / self.mass * dt
        self.v = np.clip(self.v, 0, self.v_max)
        self.x += np.cos(self.alpha) * self.v * dt
        self.y += np.sin(self.alpha) * self.v * dt
        self.x = np.clip(self.x, ground_rect[0], ground_rect[2])
        self.y = np.clip(self.y, ground_rect[1], ground_rect[3])

    def draw(self, screen, color):
        pygame.draw.circle(screen, color, [int(self.x), int(self.y)], self.radius)
        new_x = self.x + self.radius * np.cos(self.alpha)
        new_y = self.y + self.radius * np.sin(self.alpha)
        pygame.draw.line(screen, black, [self.x, self.y], [new_x, new_y], cursor_width)

    def data(self):
        player_data = {'x': self.x, 'y': self.y, 'alpha': self.alpha, 
                       'mass': self.mass, 'radius': self.radius, 
                       'a_max': self.a_max, 'v_max': self.v_max, 'shot_power_max': self.shot_power_max,
                       }
        return player_data

    def snelius(self):
        if self.y + self.radius >= ground[3] and np.sin(self.alpha) > 0:
            self.alpha = -self.alpha
            self.v *= np.abs(np.cos(self.alpha))
        if self.y - self.radius <= ground[1] and np.sin(self.alpha) < 0:
            self.alpha = -self.alpha
            self.v *= np.abs(np.cos(self.alpha))
        if self.x + self.radius >= ground[2] and np.cos(self.alpha) > 0:
            self.alpha = np.pi - self.alpha
            self.v *= np.abs(np.sin(self.alpha))
        if self.x - self.radius <= ground[0] and np.cos(self.alpha) < 0:
            self.alpha = -np.pi - self.alpha
            self.v *= np.abs(np.sin(self.alpha))

    def reset(self, initial_position, alpha):
        self.x = initial_position[0]
        self.y = initial_position[1]
        self.alpha = alpha
        self.v = 0

    def clip_velocity(self):
        self.v = np.clip(self.v, 0, self.v_max)

class Ball(Circle):
    v_max = 850
    radius = 15
    mass = 0.5

    def move(self):
        self.x += np.cos(self.alpha) * self.v * dt
        self.y += np.sin(self.alpha) * self.v * dt
        self.v *= 0.99

    def draw(self, screen):
        pygame.draw.circle(screen, black, [int(self.x), int(self.y)], self.radius)
        pygame.draw.circle(screen, white, [int(self.x), int(self.y)], self.radius - 2)

    def snelius(self):
        goal = post_screen_top < self.y < post_screen_bottom
        if self.y + self.radius >= playground[3] and np.sin(self.alpha) > 0:
            self.alpha = -self.alpha
            self.y = playground[3] - self.radius
        if self.y - self.radius <= playground[1] and np.sin(self.alpha) < 0:
            self.alpha = -self.alpha
            self.y = playground[1] + self.radius
        if self.x + self.radius >= playground[2] and np.cos(self.alpha) > 0 and not goal:
            self.alpha = np.pi - self.alpha
            self.x = playground[2] - self.radius
        if self.x - self.radius <= playground[0] and np.cos(self.alpha) < 0 and not goal:
            self.alpha = -np.pi - self.alpha
            self.x = playground[0] + self.radius

    def reset(self):
        self.x = center[0]
        self.y = center[1]
        self.alpha = 0
        self.v = 0

    def data(self):
        ball_data = {'x': self.x, 'y': self.y, 'alpha': self.alpha, 'mass': self.mass, 'radius': self.radius}
        return ball_data

    def clip_velocity(self):
        self.v = np.clip(self.v, 0, self.v_max)


class Post(Circle):
    def draw(self, screen):
        pygame.draw.circle(screen, white, [int(self.x), int(self.y)], self.radius)


def collision(circle_1, circle_2):
    return (circle_1.x - circle_2.x)**2 + (circle_1.y - circle_2.y)**2 <= (circle_1.radius + circle_2.radius)**2


def resolve_collision(circle_1, circle_2):
    collision_angle = np.arctan2(circle_2.y - circle_1.y, circle_2.x - circle_1.x)

    new_x_speed_1 = circle_1.v * np.cos(circle_1.alpha - collision_angle)
    new_y_speed_1 = circle_1.v * np.sin(circle_1.alpha - collision_angle)
    new_x_speed_2 = circle_2.v * np.cos(circle_2.alpha - collision_angle)
    new_y_speed_2 = circle_2.v * np.sin(circle_2.alpha - collision_angle)

    final_x_speed_1 = ((circle_1.mass - circle_2.mass) * new_x_speed_1
                       + (circle_2.mass + circle_2.mass) * new_x_speed_2) / (circle_1.mass + circle_2.mass)
    final_x_speed_2 = ((circle_1.mass + circle_1.mass) * new_x_speed_1
                       + (circle_2.mass - circle_1.mass) * new_x_speed_2) / (circle_1.mass + circle_2.mass)
    final_y_speed_1 = new_y_speed_1
    final_y_speed_2 = new_y_speed_2

    cos_gamma = np.cos(collision_angle)
    sin_gamma = np.sin(collision_angle)
    circle_1.v_x = cos_gamma * final_x_speed_1 - sin_gamma * final_y_speed_1
    circle_1.v_y = sin_gamma * final_x_speed_1 + cos_gamma * final_y_speed_1
    circle_2.v_x = cos_gamma * final_x_speed_2 - sin_gamma * final_y_speed_2
    circle_2.v_y = sin_gamma * final_x_speed_2 + cos_gamma * final_y_speed_2

    x_difference = circle_1.x - circle_2.x
    y_difference = circle_1.y - circle_2.y
    d = np.linalg.norm([x_difference, y_difference])

    # minimum translation distance to push balls apart after intersecting
    mtd_x = x_difference * (((circle_1.radius + circle_2.radius) - d) / d)
    mtd_y = y_difference * (((circle_1.radius + circle_2.radius) - d) / d)
    im1 = 1 / circle_1.mass if circle_1.mass > 0 else 0
    im2 = 1 / circle_2.mass if circle_2.mass > 0 else 0

    # push-pull them apart based off their mass
    circle_1.x += mtd_x * (im1 / (im1 + im2))
    circle_1.y += mtd_y * (im1 / (im1 + im2))
    circle_2.x -= mtd_x * (im2 / (im1 + im2))
    circle_2.y -= mtd_y * (im2 / (im1 + im2))

    if isinstance(circle_1, Player) and isinstance(circle_2, Player):
        circle_1.v = player_player_restitution * np.sqrt(circle_1.v_x**2 + circle_1.v_y**2)
        circle_2.v = player_player_restitution * np.sqrt(circle_2.v_x**2 + circle_2.v_y**2)
    if isinstance(circle_1, Player) and isinstance(circle_2, Ball):
        circle_1.v = np.sqrt(circle_1.v_x**2 + circle_1.v_y**2)
        if circle_1.shot_request:
            circle_2.v = np.sqrt(circle_2.v_x**2 + circle_2.v_y**2)
            circle_2.v = circle_1.shot_power * circle_1.mass / (circle_1.mass + circle_2.mass) * (1 + ball_restitution)
        else:
            circle_2.v = ball_restitution_under_player_control * np.sqrt(circle_2.v_x**2 + circle_2.v_y**2)
    if isinstance(circle_1, Player) and isinstance(circle_2, Post):
        circle_1.v = player_post_restitution * np.sqrt(circle_1.v_x**2 + circle_1.v_y**2)
        circle_2.v = 0
    if isinstance(circle_1, Ball) and isinstance(circle_2, Post):
        circle_1.v = np.sqrt(circle_1.v_x**2 + circle_1.v_y**2)
        circle_2.v = 0

    circle_1.alpha = np.arctan2(circle_1.v_y, circle_1.v_x)
    circle_2.alpha = np.arctan2(circle_2.v_y, circle_2.v_x)

    for circle in [circle_1, circle_2]:
        if isinstance(circle, Player) or isinstance(circle, Ball):
            circle.clip_velocity()
            circle.snelius()

    return circle_1, circle_2

def render_goal_pause(start_goal, screen):
    myfont = pygame.font.SysFont("monospace", 350)
    message = "GOAL!"
    label = myfont.render(message, True, (0, 0, 0))
    while int(time.time() - start_goal) < goal_pause_countdown_time:
        screen.blit(label, (200, 250))
        pygame.display.flip()
        
def render(screen, team_1, team_2, ball, posts, team_1_score, team_2_score, time_to_play, start, half, countdown,
           team_1_name, team_2_name, team_1_color, team_2_color):

    pygame.draw.rect(screen, white, resolution_rect)
    pygame.draw.rect(screen, grass, ground_rect)
    pygame.draw.rect(screen, black, resolution_rect, 2)
    pygame.draw.rect(screen, black, ground_rect, 2)
    pygame.draw.rect(screen, white, playground_rect, 2)
    pygame.draw.rect(screen, white, half_playground_rect, 2)
    pygame.draw.circle(screen, white, center, 100, 2)
    pygame.draw.circle(screen, white, center, 5)

    if half == 1:
        team_left_logo = logos[team_1_name]
        team_right_logo = logos[team_2_name]
            
        font = pygame.font.SysFont("roboto", 50)
        img = font.render(team_1_name, True, (0, 0, 0))
        screen.blit(img, (10, 60))
        
        font = pygame.font.SysFont("roboto", 50)
        img = font.render(team_2_name, True, (0, 0, 0))
        screen.blit(img, (915, 60))
        
        team_left_color = team_1_color
        team_right_color = team_2_color
    else:
        team_left_logo = logos[team_2_name]
        team_right_logo = logos[team_1_name]
        
        font = pygame.font.SysFont("roboto", 45)
        img = font.render(team_1_name, True, (0, 0, 0))
        screen.blit(img, (915, 60))
        
        font = pygame.font.SysFont("roboto", 45)
        img = font.render(team_2_name, True, (0, 0, 0))
        screen.blit(img, (10, 60))
        
        team_left_color = team_2_color
        team_right_color = team_1_color

    screen.blit(team_left_logo, team_left_logo_position)
    screen.blit(team_right_logo, team_right_logo_position)

    pygame.draw.rect(screen, team_left_color, team_left_color_position)
    pygame.draw.rect(screen, team_right_color, team_right_color_position)

    for player in team_1:
        player.draw(screen, team_1_color)
        font = pygame.font.SysFont("roboto", 30)
    for player in team_2:
        player.draw(screen, team_2_color)
        font = pygame.font.SysFont("roboto", 30)
    for player in team_1 + team_2:
        img = font.render(player.name, True, (0, 0, 0))
        screen.blit(img, (player.x - 50, player.y - 50))
    ball.draw(screen)
    for post in posts:
        post.draw(screen)

    if countdown:
        myfont = pygame.font.SysFont("monospace", 750)
        short_pause_countdown = "{}".format(short_pause_countdown_time - int(time.time() - start))
        label = myfont.render(short_pause_countdown, 1, (0, 0, 0))
        screen.blit(label, (460, 85))

        myfont = pygame.font.SysFont("monospace", 120)
        message = "{}s".format(time_to_play)
        label = myfont.render(message, 1, (0, 0, 0))
        screen.blit(label, (1150, 0))
    else:
        myfont = pygame.font.SysFont("monospace", 120)
        time_screen_value = time_to_play - int(time.time() - start)
        if time_screen_value < 0:
            time_screen_value = 0
        message = "{}s".format(time_screen_value)
        label = myfont.render(message, 1, (0, 0, 0))
        screen.blit(label, (1150, 0))


    myfont = pygame.font.SysFont("roboto", 40)
    if half == 1:
        message = "полувреме: 1"
    else:
        message = "полувреме: 2"

    label = myfont.render(message, 1, (0, 0, 0))
    screen.blit(label, (1175, 125))


    myfont = pygame.font.SysFont("monospace", 150)
    if half == 1:
        message = "{}:{}".format(team_1_score, team_2_score)
    else:
        message = "{}:{}".format(team_2_score, team_1_score)

    label = myfont.render(message, 1, (0, 0, 0))
    screen.blit(label, (215 + shift, 0))

    pygame.display.flip()
    pygame.time.Clock().tick(fps)


def play(screen, team_1, team_2, ball, posts, time_to_play, team_1_score, team_2_score, half, team_1_name, team_2_name,
         team_1_color, team_2_color, team_1_script, team_2_script):

    start = time.time()
    while time.time() - start < short_pause_countdown_time:
        render(screen, team_1, team_2, ball, posts, team_1_score, team_2_score, time_to_play, start, half, True,
               team_1_name, team_2_name, team_1_color, team_2_color)

    start = time.time()
    velocity_step = 10000
    angle_step = 0.1
    angle_change = 0
    velocity_change = 0

    circles = [team_1[0], team_1[1], team_1[2], team_2[0], team_2[1], team_2[2], ball, posts[0], posts[1], posts[2],
               posts[3]]
    goal = False
    game_exit = False
    manager_1_last_decision = {}
    manager_2_last_decision = {}
    while not game_exit:
        if time.time() - start >= time_to_play:
            if ball.v <= 50:
                return False, 0, team_1_score, team_2_score

            if ball.x <= center[0] and np.cos(ball.alpha) >= 0:
                return False, 0, team_1_score, team_2_score

            if ball.x >= center[0] and np.cos(ball.alpha) <= 0:
                return False, 0, team_1_score, team_2_score

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_exit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    angle_change = -angle_step
                if event.key == pygame.K_RIGHT:
                    angle_change = angle_step
                if event.key == pygame.K_UP:
                    velocity_change = velocity_step
                if event.key == pygame.K_DOWN:
                    velocity_change = -velocity_step
                if event.key == pygame.K_ESCAPE:
                    game_exit = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    angle_change = 0
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    angle_change = 0
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    velocity_change = 0
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    velocity_change = 0

        if not goal:
            try:
                manager_1_decision = team_1_script.decision(
                    our_team = [team_1[0].data(), team_1[1].data(), team_1[2].data()],
                    their_team=[team_2[0].data(), team_2[1].data(), team_2[2].data()],
                    ball=ball.data(),
                    your_side='left' if half == 1 else 'right',
                    half=half,
                    time_left=time_to_play - int(time.time() - start),
                    our_score=team_1_score,
                    their_score=team_2_score)
            except:
                manager_1_decision = manager_1_last_decision
            manager_1_last_decision = manager_1_decision

            try:
                manager_2_decision = team_2_script.decision(
                    our_team=[team_2[0].data(), team_2[1].data(), team_2[2].data()],
                    their_team=[team_1[0].data(), team_1[1].data(), team_1[2].data()],
                    ball=ball.data(),
                    your_side='right' if half == 1 else 'left',
                    half=half,
                    time_left=time_to_play - int(time.time() - start),
                    our_score=team_2_score,
                    their_score=team_1_score)
            except:
                manager_2_decision = manager_2_last_decision
            manager_2_last_decision = manager_2_decision

        manager_decision = [manager_1_decision[0], manager_1_decision[1], manager_1_decision[2],
                            manager_2_decision[0], manager_2_decision[1], manager_2_decision[2]]

        manager_decision[0]['alpha'] += angle_change
        manager_decision[0]['force'] += velocity_change

        for i, player in enumerate(circles[:6]):
            player.move(manager_decision[i])
        ball.move()

        if not goal:
            goal_team_right = post_screen_top < ball.y < post_screen_bottom and ball.x < post_screen_left
            goal_team_left = post_screen_top < ball.y < post_screen_bottom and ball.x > post_screen_right
            if goal_team_left:
                if half == 1:
                    team_1_score += 1
                else:
                    team_2_score += 1
            if goal_team_right:
                if half == 1:
                    team_2_score += 1
                else:
                    team_1_score += 1
            goal = goal_team_left or goal_team_right
        else:
            render_goal_pause(time.time(), screen)
            start += goal_pause_countdown_time
            return True, time_to_play - int(time.time() - start), team_1_score, team_2_score

        if not goal:
            for i in range(len(circles[:-4])):
                circles[i].snelius()
                for j in range(i + 1, len(circles)):
                    if collision(circles[i], circles[j]):
                        circles[i], circles[j] = resolve_collision(circles[i], circles[j])

        render(screen, team_1, team_2, ball, posts, team_1_score, team_2_score, time_to_play, start, half, False,
               team_1_name, team_2_name, team_1_color, team_2_color)


def game(team_1, team_2, ball, posts, team_1_name, team_2_name, team_1_color, team_2_color, team_1_script,
         team_2_script):
    pygame.init()
    screen = pygame.display.set_mode(resolution, pygame.RESIZABLE)
    pygame.display.set_caption(game_name)
    team_1_score, team_2_score = 0, 0

    pygame.mixer.init(22050, -16, 2, 2048)
    crowd = pygame.mixer.music.load('football_crowd.ogg')
    pygame.mixer.music.play(10, 14)
    
    initial_positions_team_left, initial_positions_team_right = randomize_initial_positions()
    
    time_to_play = half_time_duration
    while time_to_play:
        for i, player in enumerate(team_1):
            player.reset(initial_positions_team_left[i], 0)
        for i, player in enumerate(team_2):
                player.reset(initial_positions_team_right[i], np.pi)
        ball.reset()
        goal, time_to_play, team_1_score, team_2_score = \
            play(screen, team_1, team_2, ball, posts, time_to_play, team_1_score, team_2_score, 1, team_1_name,
                 team_2_name, team_1_color, team_2_color, team_1_script, team_2_script)
        initial_positions_team_left, initial_positions_team_right = randomize_initial_positions()

    time_to_play = half_time_duration
    while time_to_play:
        for i, player in enumerate(team_2):
            player.reset(initial_positions_team_left[i], 0)
        for i, player in enumerate(team_1):
                player.reset(initial_positions_team_right[i], np.pi)
        ball.reset()
        goal, time_to_play, team_1_score, team_2_score = \
            play(screen, team_1, team_2, ball, posts, time_to_play, team_1_score, team_2_score, 2, team_1_name,
                 team_2_name, team_1_color, team_2_color, team_1_script, team_2_script)
        initial_positions_team_left, initial_positions_team_right = randomize_initial_positions()

    # print('{}  {}:{}  {} '.format(team_1_name, team_1_score, team_2_score, team_2_name))

    time.sleep(6)
    pygame.quit()


def randomize_initial_positions():
    displacement = random.randint(0, 10)
    player_1_initial_position = [int((center[0] - playground[0]) / 2) + playground[0] - displacement, post_screen_top]
    player_2_initial_position = [int((center[0] - playground[0]) / 2) + playground[0] - displacement, center[1]]
    player_3_initial_position = [int((center[0] - playground[0]) / 2) + playground[0] - displacement, post_screen_bottom]
    player_4_initial_position = [player_1_initial_position[0] + half_playground_rect[2] + displacement, post_screen_top]
    player_5_initial_position = [player_2_initial_position[0] + half_playground_rect[2] + displacement, center[1]]
    player_6_initial_position = [player_3_initial_position[0] + half_playground_rect[2] + displacement, post_screen_bottom]

    initial_positions_team_left = [player_1_initial_position, player_2_initial_position, player_3_initial_position]
    initial_positions_team_right = [player_4_initial_position, player_5_initial_position, player_6_initial_position]    
    return initial_positions_team_left, initial_positions_team_right
    

if __name__ == "__main__":
    team_1_properties = team_1_script.team_properties()
    team_2_properties = team_2_script.team_properties()

    team_1_total_points = [
        (
            team_1_properties['weight_points'][i] + 
            team_1_properties['radius_points'][i] + 
            team_1_properties['max_acceleration_points'][i] + 
            team_1_properties['max_speed_points'][i] +
            team_1_properties['shot_power_points'][i]
        ) for i in range(3)
    ]
    team_2_total_points = [
        (
            team_2_properties['weight_points'][i] + 
            team_2_properties['radius_points'][i] + 
            team_2_properties['max_acceleration_points'][i] + 
            team_2_properties['max_speed_points'][i] +
            team_2_properties['shot_power_points'][i]
        ) for i in range(3)
    ]

    team_1 = [
        Player(
            team_1_properties['player_names'][0], 
            get_weight(team_1_properties['weight_points'][0]), 
            get_radius(team_1_properties['radius_points'][0]), 
            get_acceleration(team_1_properties['max_acceleration_points'][0]), 
            get_speed(team_1_properties['max_speed_points'][0]), 
            get_shot_power(team_1_properties['shot_power_points'][0])
        ), 
        Player(
            team_1_properties['player_names'][1], 
            get_weight(team_1_properties['weight_points'][1]), 
            get_radius(team_1_properties['radius_points'][1]), 
            get_acceleration(team_1_properties['max_acceleration_points'][1]), 
            get_speed(team_1_properties['max_speed_points'][1]), 
            get_shot_power(team_1_properties['shot_power_points'][1])
        ), 
        Player(
            team_1_properties['player_names'][2], 
            get_weight(team_1_properties['weight_points'][2]), 
            get_radius(team_1_properties['radius_points'][2]), 
            get_acceleration(team_1_properties['max_acceleration_points'][2]), 
            get_speed(team_1_properties['max_speed_points'][2]), 
            get_shot_power(team_1_properties['shot_power_points'][2])
        )
    ]
    team_2 = [
        Player(
            team_2_properties['player_names'][0], 
            get_weight(team_2_properties['weight_points'][0]), 
            get_radius(team_2_properties['radius_points'][0]), 
            get_acceleration(team_2_properties['max_acceleration_points'][0]), 
            get_speed(team_2_properties['max_speed_points'][0]), 
            get_shot_power(team_2_properties['shot_power_points'][0])
        ), 
        Player(
            team_2_properties['player_names'][1], 
            get_weight(team_2_properties['weight_points'][1]), 
            get_radius(team_2_properties['radius_points'][1]), 
            get_acceleration(team_2_properties['max_acceleration_points'][1]), 
            get_speed(team_2_properties['max_speed_points'][1]), 
            get_shot_power(team_2_properties['shot_power_points'][1])
        ), 
        Player(
            team_2_properties['player_names'][2], 
            get_weight(team_2_properties['weight_points'][2]), 
            get_radius(team_2_properties['radius_points'][2]), 
            get_acceleration(team_2_properties['max_acceleration_points'][2]), 
            get_speed(team_2_properties['max_speed_points'][2]), 
            get_shot_power(team_2_properties['shot_power_points'][2])
        )
    ]
    
    the_ball = Ball(420, 250, 15, 0.5)
    the_posts = [Post(post_screen_left, post_screen_top, post_radius, post_mass),
                 Post(post_screen_left, post_screen_bottom, post_radius, post_mass),
                 Post(post_screen_right, post_screen_top, post_radius, post_mass),
                 Post(post_screen_right, post_screen_bottom, post_radius, post_mass)]

    red_logo = pygame.image.load(os.getcwd() + '\\Team_name\\' + team_1_properties['image_name'])
    blue_logo = pygame.image.load(os.getcwd() + '\\Test_team\\' + team_2_properties['image_name'])
    logos = {team_1_properties['team_name']: red_logo, team_2_properties['team_name']: blue_logo}
    game(team_1, team_2, the_ball, the_posts, team_1_properties['team_name'], team_2_properties['team_name'], red, blue, team_1_script, team_2_script)
