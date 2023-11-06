import os
import sys
import random 
import json
import math
import utils
import time
import config
import numpy
random.seed(73)


class Agent:
    def __init__(self, table_config) -> None:
        self.table_config = table_config
        self.prev_action = None
        self.curr_iter = 0
        self.state_dict = {}
        self.holes =[]
        self.ns = utils.NextState()
        self.curr_ball = 1          # ball to hit
        self.hitting_hole = 0       # hole to aim chosen ball


    def set_holes(self, holes_x, holes_y, radius):
        for x in holes_x:
            for y in holes_y:
                self.holes.append((x[0], y[0]))
        self.ball_radius = radius

    def get_angle(self,b1,b2):      # first arguement is the ball, which is reference of the angle measured
        return (-1 * math.atan2(b2[0]-b1[0],b1[1]-b2[1]))/math.pi
    
    def get_dist(self,b1,b2):       # distance between two points
        return math.sqrt((b1[0]-b2[0])**2 + (b1[1]-b2[1])**2)
    
    def choose_ball1(self, ball_pos):       # choose ball to hit by 1st method
        d2 = 5000
        cue = ball_pos[0]
        for i in ball_pos.keys():
            if i == 0 or i == 'white':
                continue
            for j in self.holes:
                if self.get_dist(ball_pos[i],j) + self.get_dist(cue,ball_pos[i]) < d2:
                    self.curr_ball = i
                    d2 = self.get_dist(ball_pos[i],j) + self.get_dist(cue,ball_pos[i])     

    def choose_ball2(self, ball_pos):       # choose ball to hit by 2nd method
        d2 = 5000
        cue = ball_pos[0]
        for i in ball_pos.keys():
            if i == 0 or i == 'white':
                continue
            for j in self.holes:
                if self.get_dist(ball_pos[i],j) < d2:
                    self.curr_ball = i
                    d2 = self.get_dist(ball_pos[i],j)

    def check(self,ns,ball_pos):            # check if the ball is pocketed or not by get_next_state()
        l1 = []
        l2 = []
        for i in ball_pos.keys():
            if i == 0 or i == 'white':
                continue
            l1.append(i)
        for j in ns.keys():
            if j == 0 or j == 'white':
                continue
            l2.append(j)
        if len(l2) < len(l1):
            return True
        return False

    def choose_ball3(self, ball_pos):       # choose ball to hit by 3rd method
        d2 = 5000
        cue = ball_pos[0]
        for i in ball_pos.keys():
            if i == 0 or i == 'white':
                continue
            b_cue = (cue[0] - ball_pos[i][0], cue[1] - ball_pos[i][1])
            for j in self.holes:
                h_ball = (ball_pos[i][0] - j[0], ball_pos[i][1] - j[1])
                cos_theta = (h_ball[0]*b_cue[0] + h_ball[1]*b_cue[1])/(numpy.linalg.norm(h_ball) * numpy.linalg.norm(b_cue))
                angle_ = math.acos(cos_theta)
                if angle_ <= d2:
                    angle_ = d2
                    self.curr_ball = i
    
    def choose_hole(self, ball_pos):        # choose hole to hit by default method
        h_dist = 5000
        for h in range(len(self.holes)):
            if self.get_dist(ball_pos[self.curr_ball],self.holes[h]) < h_dist:
                self.hitting_hole = h
                h_dist = self.get_dist(ball_pos[self.curr_ball],self.holes[h])

    def choose_hole1(self, ball_pos):       # choose hole to hit by another method
        d2 = 5000
        cue = ball_pos[0]
        b_cue = (cue[0] - ball_pos[self.curr_ball][0], cue[1] - ball_pos[self.curr_ball][1])
        for j in range(len(self.holes)):
            h_ball = (ball_pos[self.curr_ball][0] - self.holes[j][0], ball_pos[self.curr_ball][1] - self.holes[j][1])
            cos_theta = (h_ball[0]*b_cue[0] + h_ball[1]*b_cue[1])/(numpy.linalg.norm(h_ball) * numpy.linalg.norm(b_cue))
            angle_ = math.acos(cos_theta)
            if angle_ <= d2:
                angle_ = d2
                self.hitting_hole = j

    def action(self, ball_pos=None):
        ## Code you agent here ##
        ## You can access data from config.py for geometry of the table, configuration of the levels, etc.
        ## You are NOT allowed to change the variables of config.py (we will fetch variables from a different file during evaluation)
        ## Do not use any library other than those that are already imported.
        ## Try out different ideas and have fun!
        self.curr_iter += 1
        cue = ball_pos[0]
        ball_dirns = {}         # dictionary of ball directions
        for i in ball_pos.keys():
            if i == 0 or i == 'white':
                continue
            ball_dirns[i] = []
        for i in ball_pos.keys():
            if i == 0 or i == 'white':
                continue
            ball = ball_pos[i]
            for h in self.holes:
                ang = self.get_angle(h,ball)        
                ball_dirns[i].append((ang, (-1.85*self.ball_radius*math.sin(ang*math.pi),-1.85*self.ball_radius*math.cos(ang*math.pi))))
        f_angle = -1
        f_force = -1
        max_d = 920
        for i in range(3):
            if i == 0:
                self.choose_ball1(ball_pos)
            elif i == 1:
                self.choose_ball2(ball_pos)
            else:
                self.choose_ball3(ball_pos)
            self.choose_hole(ball_pos)
            angle = self.get_angle(cue, (ball_pos[self.curr_ball][0]+ball_dirns[self.curr_ball][self.hitting_hole][1][0],ball_pos[self.curr_ball][1]+ball_dirns[self.curr_ball][self.hitting_hole][1][1]))
            dist = self.get_dist(cue, ball_pos[self.curr_ball])
            d1 = self.get_dist(ball_pos[self.curr_ball], self.holes[self.hitting_hole])
            c_hole = self.get_dist(cue, self.holes[self.hitting_hole])
            force = max(dist/(dist+d1), d1/(d1+dist))
            #force = max(max(dist/max_d, d1/max_d), c_hole/max_d)
            #force = min(1,force)
            ns = self.ns.get_next_state(ball_pos, (angle, force), 0)
            if self.check(ns, ball_pos):
                f_angle = angle
                f_force = force
                break
        if f_angle == -1 and f_force == -1:
            self.choose_ball3(ball_pos)
            self.choose_hole(ball_pos)
            angle = self.get_angle(cue, (ball_pos[self.curr_ball][0]+ball_dirns[self.curr_ball][self.hitting_hole][1][0],ball_pos[self.curr_ball][1]+ball_dirns[self.curr_ball][self.hitting_hole][1][1]))
            dist = self.get_dist(cue, ball_pos[self.curr_ball])
            d1 = self.get_dist(ball_pos[self.curr_ball], self.holes[self.hitting_hole])
            c_hole = self.get_dist(cue, self.holes[self.hitting_hole])
            force = max(dist/(dist+d1), d1/(d1+dist))
            #force = max(max(dist/max_d, d1/max_d), c_hole/max_d)
            #force = min(1,force)
            f_angle = angle
            f_force = force
        return (f_angle, f_force)

