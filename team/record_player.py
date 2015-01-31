#!/usr/bin/python
# -*- coding: utf8 -*-
import sys, os

def check_pa_notation(pa):

    err = ""
    if( pa.result not in ["BB", "SF", "1B", "2B", "3B", "HR", "DP", "K", "CB", "IB", "IF", "FO", "F", "G", "FC", "E"] ):
        err = "Unknown notation %s (%s)" %(pa.result, pa.raw_str)

    return err

class Game:
    def __init__(self):
        self.home       = Team()
        self.away       = Team()
        self.game_id    = None
        self.date       = None
        self.location   = ""
        self.game_type  = ""    

    def save_game(self, filepath):
        dir_name = os.path.dirname(filepath)
        if( not os.path.isdir(dir_name) ):
                os.mkdir(dir_name)

        with open(filepath, 'w') as f:
            output = ""
            output += "type\t%s\n" %self.game_type
            output += "date\t%s\n" %str(self.date)
            output += "gameid\t%s\n" %self.game_id
            output += "location\t%s\n\n" %self.location
            
            output += "Away\t%s\n"  %self.away.name
            output += "Box"
            for score in self.away.scores:
                output += "\t%d" %score
            output += "\n"
            output += "%s\n" %self.away.raw_record.replace('\r', '')
            
            output += '\n'

            output += "Home\t%s\n" %self.home.name
            output += "Box"
            for score in self.home.scores:
                output += "\t%d" %score
            output += "\n"
            output += "%s\n" %self.home.raw_record.replace('\r', '')
            
            f.write(output)

        print "Save %s" %filepath

class Team:
    def __init__(self):
        self.name = ""
        self.batters        = []   # batter per PA record (in raw string format)
        self.pitchers       = []
        self.orders         = []
        self.order_table    = []
        self.scores         = [0]*7
        self.col2inn        = None
        self.H              = 0
        self.E              = 0
        self.R              = 0
        self.nBatters       = 0
        self.nPitchers      = 0
        self.batter_table   = []
        self.pitcher_table  = []
        self.raw_record     = ""

    def hasRecord(self):
        return len(self.order_table) != 0

    def order(self):
        return len(self.order_table)

    def num_of_batters(self):
        self.nBatters = len(self.batters)
        return self.nBatters

    def num_of_pitchers(self):
        self.nPitchers = len(self.pitchers)
        return self.nPitchers

    def get_Runs(self):
        self.R = sum(self.scores) 
        return self.R

    def find_batter(self, number):
        for batter in self.batters:
            if batter.number == number:
                return batter
        # not found
        return None
    
    def compute_statistic(self):
        self.num_of_batters()
        self.num_of_pitchers()
        self.get_Runs()
        for batter in self.batters:
            batter.compute_statistic()

        for pitcher in self.pitchers:
            pitcher.compute_statistic()


class PA:
    def __init__(self):
        self.isPlay         = False     # used for no-play batter
        self.pos            = None      # hit-ball direction
        self.result         = None      # result string
        self.rbi            = 0         # RBI
        self.run            = 0         # RUN
        self.out            = 0         # number of outs in this play
        self.endInning      = ""        # should be 0, '#' or '!'
        self.note           = ""        # 0 or *'
        self.inning         = -1        # inning
        self.column         = 0         # column in printed table
        self.raw_str        = ""        # pa code string
        self.change_pitcher = None

class rdBatter:
    def __init__(self, order="", number="", pos=""):
        self.order  = order
        self.number = number
        self.pos    = pos
        self.PAs    = []
        self.PA     = 0
        self.AB     = 0
        self.B1     = 0
        self.B2     = 0
        self.B3     = 0
        self.HR     = 0
        self.DP     = 0
        self.RBI    = 0
        self.RUN    = 0
        self.BB     = 0
        self.K      = 0
        self.SF     = 0    # sacrificed fly 高飛犧牲打
        self.CB     = 0    # combacker 投手強襲球
        self.IB     = 0    # illegal batted 違規擊球
        self.IF     = 0    # infield fly 內野高飛必死球
        self.FO     = 0    # foul out 界外飛球出局

    def AddPA(self, pa):

        err = check_pa_notation(pa)
        if( err != "" ):
            return err

        self.PAs.append(pa)
        if( pa.isPlay ):
            self.PA += 1
            if( pa.result == "BB" ):
                self.BB += 1
            elif( pa.result == "SF"):
                self.SF += 1
            else:
                self.AB += 1
                if( pa.result == "1B" ):
                    self.B1 += 1
                elif( pa.result == "2B" ):
                    self.B2 += 1
                elif( pa.result == "3B" ):
                    self.B3 += 1
                elif( pa.result == "HR" ):
                    self.HR += 1
                elif( pa.result == "DP" ):
                    self.DP += 1
                elif( pa.result == "K" ):
                    self.K += 1
                elif( pa.result == "CB" ):
                    self.CB += 1
                elif( pa.result == "IB" ):
                    self.IB += 1
                elif( pa.result == "IF" ):
                    self.IF += 1
                elif( pa.result == "FO" ):
                    self.FO += 1

            self.RBI += pa.rbi
            self.RUN += pa.run

        return err

    def compute_statistic(self):
        self.num_of_PA()

    def num_of_PA(self):
        n = 0
        for pa in self.PAs:
            if( pa.isPlay ):
                n += 1

        self.PA = n
        return self.PA

class rdPitcher:
    def __init__(self, number=""):
        self.number = number
        self.TBF = 0    # total batters faced 面對人次
        self.Out = 0
        self.H   = 0
        self.HR  = 0
        self.BB  = 0
        self.K   = 0
        self.Run = 0
        self.ER  = 0
        self.ERA = 0
        self.GO  = 0
        self.FO  = 0
        self.IP  = ''

    def getERA(self):
        if( self.ER == 0 ):
            self.ERA = 0
        else:
            if( self.Out == 0 ):
                self.ERA = float("inf")
            else:
                self.ERA = float(self.ER) / self.Out * (7*3)
        
        return self.ERA

    def calculate_IP(self):
        if( self.Out == 0 ):
            self.IP = '0.0'
        else:
            N = int(self.Out / 3)
            m = self.Out % 3
            self.IP = '%d.%d' %(N, m)

        return self.IP
            

    def AddPa(self, pa, isER=True):

        err = check_pa_notation(pa)
        if( err != "" ):
            return err

        if( pa.isPlay ):
            self.TBF += 1
            if( pa.result in ("1B", "2B", "3B", "HR") ):
                self.H  += 1
                if( pa.result == "HR" ):
                    self.HR += 1
            elif( pa.result == "BB" ):
                self.BB += 1
            elif( pa.result == "K" ):
                self.K += 1
            elif( pa.result == "G" ):
                self.GO += 1
            elif( pa.result in ("F", "SF", "IF", "FO") ):
                self.FO += 1
            elif( pa.result == "DP" ): # TODO: need to seperate G-DP or F-DP ?
                self.GO += 2
            elif( (pa.result == "FC") & (pa.out > 0) ):
                self.GO += 1
            
            #print "pitcher add PA(%s), out = %d" %(pa.raw_str, pa.out)
            self.Out += pa.out
            self.Run += pa.run
            if (isER and pa.result != "E"):
                self.ER += pa.run
        
        return err

    def compute_statistic(self):
        self.calculate_IP()
        self.getERA()
