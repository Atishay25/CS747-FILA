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
# original seed was 73
# problem happening in seed 100

class Agent:
    def __init__(self, table_config) -> None:
        self.table_config = table_config
        self.prev_action = None
        self.curr_iter = 0
        self.state_dict = {}
        self.holes =[]
        self.ns = utils.NextState()
        # below are my changes
        self.curr_ball = 1
        self.hitting_hole = 0


    def set_holes(self, holes_x, holes_y, radius):
        for x in holes_x:
            for y in holes_y:
                self.holes.append((x[0], y[0]))
        self.ball_radius = radius

    def get_angle(self,b1,b2):      # first arguement is the ball, which is reference
        return (-1 * math.atan2(b2[0]-b1[0],b1[1]-b2[1]))/math.pi
    
    def get_dist(self,b1,b2):
        return math.sqrt((b1[0]-b2[0])**2 + (b1[1]-b2[1])**2)
    
    def angle_range(self,x):
        r_max = x+0.5
        r_min = x-0.5
        if r_max > 1:
            r_max = -1 * (1 - (r_max - 1))
        if r_min < -1:
            r_min = 1 - (-r_min - 1)
        return (r_min, r_max)
    
    def choose_ball1(self, ball_pos):
        d2 = 5000
        cue = ball_pos[0]
        for i in ball_pos.keys():
            if i == 0 or i == 'white':
                continue
            for j in self.holes:
                if self.get_dist(ball_pos[i],j) + self.get_dist(cue,ball_pos[i]) < d2:
                    self.curr_ball = i
                    d2 = self.get_dist(ball_pos[i],j) + self.get_dist(cue,ball_pos[i])     

    def choose_ball2(self, ball_pos):
        d2 = 5000
        cue = ball_pos[0]
        for i in ball_pos.keys():
            if i == 0 or i == 'white':
                continue
            for j in self.holes:
                if self.get_dist(ball_pos[i],j) < d2:
                    self.curr_ball = i
                    d2 = self.get_dist(ball_pos[i],j)

    def check(self,ns,ball_pos):
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
            #print(l1,l2)
            return True
        return False

    def choose_ball3(self, ball_pos):
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
    
    def choose_hole(self, ball_pos):
        #d2 = 5000
        #cue = ball_pos[0]
        #b_cue = (cue[0] - ball_pos[self.curr_ball][0], cue[1] - ball_pos[self.curr_ball][1])
        #for j in self.holes:
        #    h_ball = (ball_pos[self.curr_ball][0] - j[0], ball_pos[self.curr_ball][1] - j[1])
        #    cos_theta = (h_ball[0]*b_cue[0] + h_ball[1]*b_cue[1])/(numpy.linalg.norm(h_ball) * numpy.linalg.norm(b_cue))
        #    angle_ = math.acos(cos_theta)
        #    if angle_ <= d2:
        #        angle_ = d2
        #        self.hitting_hole = self.holes.index(j)
        h_dist = 5000
        for h in range(len(self.holes)):
            if self.get_dist(ball_pos[self.curr_ball],self.holes[h]) < h_dist:
                self.hitting_hole = h
                h_dist = self.get_dist(ball_pos[self.curr_ball],self.holes[h])

    def choose_hole1(self, ball_pos):
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
        #return (2*random.random() - 1, random.random())
        self.curr_iter += 1
        cue = ball_pos[0]
        angle = 0
        ball_dirns = {}
        for i in ball_pos.keys():
            if i == 0 or i == 'white':
                continue
            ball_dirns[i] = []
        for i in ball_pos.keys():
            if i == 0 or i == 'white':
                continue
            ball = ball_pos[i]
            for h in self.holes:
                ang = self.get_angle(ball,h)        # best at 1.8 abhi tak toh
                ball_dirns[i].append((ang, (1.85*self.ball_radius*math.sin(ang*math.pi),1.85*self.ball_radius*math.cos(ang*math.pi))))
        f_angle = -1
        f_force = -1
        chosen = 0
        max_d = 920
        for i in range(3):
            if chosen == 1:
                break
            if i == 0:
                self.choose_ball1(ball_pos)
            elif i == 1:
                self.choose_ball2(ball_pos)
            else:
                self.choose_ball3(ball_pos)
            for j in range(1):
                if j == 0:
                    self.choose_hole(ball_pos)
                #else:
                #    self.choose_hole1(ball_pos)
                angle = self.get_angle(cue, (ball_pos[self.curr_ball][0]+ball_dirns[self.curr_ball][self.hitting_hole][1][0],ball_pos[self.curr_ball][1]+ball_dirns[self.curr_ball][self.hitting_hole][1][1]))
                dist = self.get_dist(cue, ball_pos[self.curr_ball])
                d1 = self.get_dist(ball_pos[self.curr_ball], self.holes[self.hitting_hole])
                c_hole = self.get_dist(cue, self.holes[self.hitting_hole])
                force = max(dist/(dist+d1), d1/(d1+dist))
                #force = max(dist/max_d, d1/max_d)
                #force = max(force, c_hole/max_d)
                #force = min(force, 1)
                ns = self.ns.get_next_state(ball_pos, (angle, force), 75)
                if self.check(ns, ball_pos):
                    f_angle = angle
                    f_force = force
                    #print("CHOOSEN STRATEGY : ", i+1)
                    chosen = 1
                    break
        if f_angle == -1 and f_force == -1:
            #print("GOING DEFAULT", 3)
            self.choose_ball3(ball_pos)
            self.choose_hole(ball_pos)
            angle = self.get_angle(cue, (ball_pos[self.curr_ball][0]+ball_dirns[self.curr_ball][self.hitting_hole][1][0],ball_pos[self.curr_ball][1]+ball_dirns[self.curr_ball][self.hitting_hole][1][1]))
            dist = self.get_dist(cue, ball_pos[self.curr_ball])
            d1 = self.get_dist(ball_pos[self.curr_ball], self.holes[self.hitting_hole])
            c_hole = self.get_dist(cue, self.holes[self.hitting_hole])
            force = max(dist/(dist+d1), d1/(d1+dist))
            #force = max(dist/max_d, d1/max_d)
            #force = max(force, c_hole/max_d)
            #force = min(force, 1)
            f_angle = angle
            f_force = force
        return (f_angle, f_force)

'''
Things that I can change :
1. order of choosing balls to hit
2. order of choosing holes to hit
3. force parameters
4. angle parameters
5. Find a way to use the next state function
6. See, you can make 15-20 call to that function, so use it, ikuzo yarodomo

7. Change hole strategy
'''
