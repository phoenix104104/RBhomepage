#!/usr/bin/python
# -*- coding: utf8 -*-

import sys, os
import argparse
from record_player import Game, Team, rdBatter, rdPitcher, PA
from dump_record import make_PTT_format, make_database_format, make_web_table

def extract_single_team_data(game, team_name):
    
    if( game.away.name == team_name ):
        game.away.pitchers[0].RUN = game.home.R
        if( game.away.R > game.home.R ):
            game.away.pitchers[0].WIN = 1;
        elif( game.away.R < game.home.R ):
            game.away.pitchers[0].LOSE = 1;

        ###### use self-team innings as pitching innings (not exactly correct)
        game.away.pitchers[0].OUT = game.away.col2inn[-1]*3
        team = game.away
        
    else:
        game.home.pitchers[0].RUN = game.away.R
        if( game.home.R > game.away.R ):
            game.home.pitchers[0].WIN = 1;
        elif( game.home.R < game.away.R ):
            game.home.pitchers[0].LOSE = 1;

        ###### use self-team innings as pitching innings (not exactly correct)
        game.home.pitchers[0].OUT = game.home.col2inn[-1]*3
        team = game.home
    
    # re-write web/PTT table
    if( game.away.hasRecord() ):
        game.away.compute_statistic()
        make_web_table(game.away)
    if( game.home.hasRecord() ):
        game.home.compute_statistic()
        make_web_table(game.home)

    isColor = True
    post_ptt = make_PTT_format(game, isColor)
    post_ptt = post_ptt.replace('\x1b', '\025')
    game.post_ptt = post_ptt
    game.post_db  = make_database_format(game)

    return game, team


def check_least_out(pa):
    out = 0
    one_out = ["G", "F", "K", "SF", "IF", "CB", "IB", "FO", "DO"]
    if( pa.result in one_out ):
        out = 1
    elif( pa.result == "DP" ):
        out = 2

    return out

def parse_base(pa, str):
    
    err = ""
    n = len(str)
    rbi   = 0
    run   = 0
    out   = 0
    isEnd = 0
    note  = 0
    for s in str:
        if( s == 'R' ):
            run += 1
        elif( s.isdigit() ):
            rbi += int(s)
        elif( s == 'X' ):
            out += 1
        elif( (s == '#') | (s == '!') ):
            isEnd = s
        elif( (s == '*') | (s == '?') ):
            note = s
        else:
            err = "Unknown base notation %s (%s)" %(s, pa.raw_str)
            break

    pa.rbi = rbi
    pa.run = run
    pa.out = out
    pa.endInning = isEnd
    pa.note = note
    return pa, err

def change_pitcher(pa_strs):
    if( pa_strs[0][0].upper() == 'P' ):
        return True
    else:
        return False

def change_batter(pa_strs):
    if( pa_strs[0][0].upper() == 'R' and len(pa_strs[0]) != 1 ): # s[0] = 'R + no', not only 'R'(Right)
        return True
    else:
        return False
        

def parse_PA(team, order, turn, inning, curr_order):
    
    err = ""
    pa_str = team.order_table[order][turn]
    s = pa_str.split('/')
    
    pa = PA()
    pa.inning = inning
    pa.raw_str = pa_str
    batter = curr_order[order] # pointer to current batter
    

    if( s[0].upper() == 'NP' ): # no play
        pa.isPlay = False
        pa.result = s[0].upper()
    else:
        pa.isPlay = True
        while( change_pitcher(s) or change_batter(s) ):

            if( change_pitcher(s) ):
                name = s[0][1:]
                pa.change_pitcher = name
                s = s[1:]

            if( change_batter(s)  ):  # change batter
                name = s[0][1:]
                idx = team.batters.index(batter) # current batter index

                batter = team.find_batter(name)
                if( batter == None or name == "OB" ): # may exist multiple OB
                    batter = rdBatter('R', name, 'R')
                    team.batters.insert(idx+1, batter)

                curr_order[order] = batter
                s = s[1:]

        s = [t.upper() for t in s]

        if( len(s) == 1 ):      # result
            pa.result = s[0]

        elif( len(s) == 2 ):

            if( s[0].isdigit() or (s[0] in ['L', 'R', 'C', 'l', 'r', 'c']) ):   # pos-res
                pa.pos    = s[0]
                pa.result = s[1]

            else:               # res-end
                pa.result = s[0]
                pa, err = parse_base(pa, s[1])

        elif( len(s) == 3 ):    # pos-res-end
            pa.pos    = s[0]
            pa.result = s[1]
            pa, err = parse_base(pa, s[2])

        else:
           err = "Incorrect PA format %s\n" %pa.raw_str
           return pa, err



    least_out = check_least_out(pa)
    if( pa.out < least_out ):
        pa.out = least_out

    err = batter.AddPA(pa)
    team.order_table[order][turn] = [batter, pa]
    return pa, err



def parse_column(team):
    # parse inning information
    inning   = 1
    turn     = 0
    order    = 0
    column   = 0
    pa_count = 0
    isER     = True
    nOrder   = len(team.order_table)
    nBatter  = team.num_of_batters()
    supp_out = 0    # supposed out
    col2inn  = []

    while(True):
        pa = team.order_table[order][turn][1]
        pa.column = column
        if( pa.endInning == '!'): # end of game
            col2inn.append(inning)
            break

        pa_count += 1
        if( pa_count % nOrder == 0 and pa.endInning != '#' ):
            col2inn.append(inning)
            column += 1

        if( pa.endInning == '#' ): # change inning
            pa_count = 0
            col2inn.append(inning)
            inning += 1
            column += 1

        order += 1
        if( order == nOrder ):
            order = 0
            turn += 1
    
    team.col2inn = col2inn



def parse_pitcher_info(team, pitchers):
    
    err = ""
    # parse inning information
    turn     = 0
    order    = 0
    isER     = True
    nOrder   = len(team.order_table)
    nBatter  = team.num_of_batters()
    supp_out = 0    # supposed out
    
    pitcher = pitchers[0]

    while(True):
        pa = team.order_table[order][turn][1]
        
        # change pitcher
        if( pa.change_pitcher != None ):
            name = pa.change_pitcher

            # find whether pitcher had been on field before
            is_new_pitcher = True
            for p in pitchers:
                if p.name == name:
                    pitcher = p
                    is_new_pitcher = False
                    break
                    
            if( is_new_pitcher ):
                pitcher = rdPitcher(no)
                pitchers.append( pitcher )

        err = pitcher.AddPa(pa, isER)
        if( err != "" ):
            break

        if( pa.endInning == '!'): # end of game
            break

        supp_out += pa.out
        if( pa.result == "E" ):
            supp_out += 1
        
        if( supp_out >= 3 ):
            isER = False

        if( pa.endInning == '#' ): # change inning
            supp_out = 0
            isER = True

        order += 1
        if( order == nOrder ):
            order = 0
            turn += 1
    
    return err

def print_order_table(table):
    for row in table:
        for col in row:
            batter  = col[0]
            pa      = col[1]
            sys.stdout.write("%2s  (%d)%-12s" %(batter.name, pa.out, pa.raw_str))
        sys.stdout.write('\n')

def print_batter(batters):
    for p in batters:
        sys.stdout.write("%2s  %2s " %(p.order, p.name) )
        for pa in p.PAs:
            sys.stdout.write("(%d)%-12s " %(pa.column, pa.raw_str) )
        sys.stdout.write('\n')


def parse_order_table(team):
    
    err = ""
    # parse inning information
    inning      = 1
    turn        = 0
    order       = 0
    out         = 0
    score       = 0    # score per inning
    nOrder      = len(team.batters)
    curr_order  = []
    for batter in team.batters:
        curr_order.append(batter)
    
    team_H = 0
    opp_E = 0
    while(True):
        pa, err = parse_PA(team, order, turn, inning, curr_order)
        if( err != "" ):
            err += " - row %d" %(order+1)
            break
        
        score += pa.run

        if( pa.result in ("1B", "2B", "3B", "HR") ):
            team_H += 1

        if( pa.result == "E" ):
            opp_E += 1

        if( pa.endInning in ('#', '!') ):  # change inning
            team.scores[inning-1] = score
            inning += 1
            score = 0

        if( pa.endInning == '!' ):
            break

        order += 1
        if( order == nOrder ):
            order = 0
            turn += 1

    team.H  = team_H
    if( err == "" ):
        parse_column(team)
    
    return opp_E, err



def make_team(team_name, scores, str_table):
    
    err = ""
    team = Team()
    team.name = team_name

    if( scores == None ):
        scores = [0] * 7
    if( len(scores) < 7 ):
        scores = scores + [0] * (7 - len(scores))

    team.scores = scores

    for r in range(len(str_table)):

        row = str_table[r]
        if( len(row) < 3 ):
            err = "format error(row %d): name position PA PA..." %(r+1)
            break

        order = str(r+1)
        name  = row[0]
        pos   = row[1].upper()
        PAs   = row[2:]
        team.batters.append( rdBatter(order, name, pos) )
        team.order_table.append( PAs )

        if( pos == 'P' ):
            team.pitchers.append( rdPitcher(name) )

    return team, err



def make_game(game):

    err = ""
    away = game.away
    home = game.home

    if( not away.hasRecord() and not home.hasRecord() ):
        err = "Both record not exist"
        return game, err

    ## handle 1 team case
    if( not away.hasRecord() and home.hasRecord() ):
        away.pitchers.append( rdPitcher('00') )
    if( away.hasRecord() and not home.hasRecord() ):
        home.pitchers.append( rdPitcher('00') )


    if( away.hasRecord() ):
        if( len(away.pitchers) == 0 ):
            err = away.name + u"沒有先發投手"
            return game, err

        home.E, err = parse_order_table(away)
        if( err != "" ):
            err += " in Away Record"
            return game, err

        err = parse_pitcher_info(away, home.pitchers)  
        if( err != "" ):
            err += " in Away Record"
            return game, err
        

    if( home.hasRecord() ):
        if( len(home.pitchers) == 0 ):
            err = home.name + u"沒有先發投手"
            return game, err

        away.E, err = parse_order_table(home)

        if( err != "" ):
            err += " in Home Record"
            return game, err

        err = parse_pitcher_info(home, away.pitchers)  
        if( err != "" ):
            err += " in Home Record"
            return game, err

        
    # calculate total scores
    away.compute_statistic()
    home.compute_statistic()

    game.away = away
    game.home = home

    return game, err





def load_record_file(recordFileName):
    
    game_type   = ""
    date        = ""
    game_id     = ""
    location    = ""
    away_scores = []
    away_table  = []
    home_scores = []
    home_table  = []

    with open(recordFileName) as f:
        print "Load " + recordFileName
        for line in f:
            data = list(line.split())
            if len(data) != 0:
                if( data[0].upper() == 'TYPE' ):
                    game_type = data[1]
                elif( data[0].upper() == 'DATE' ):
                    date = data[1]
                elif( data[0].upper() == 'GAMEID' ):
                    game_id = data[1]
                elif( data[0].upper() == 'LOCATION' ):
                    location = data[1]
                elif( data[0].upper() == 'AWAY' ):
                    away_team_name = data[1]
                    scores = away_scores
                    table  = away_table
                elif( data[0].upper() == 'HOME' ):
                    home_team_name = data[1]
                    scores = home_scores
                    table  = home_table
                elif( data[0].upper() == 'BOX' ):
                    for s in data[1:]:
                        scores.append(int(s))
                else:
                    table.append(data)

    return game_type, date, game_id, location, away_team_name, away_scores, away_table, home_team_name, home_scores, home_table

## main calling function
def parse_game_record(away_team_name, away_scores, away_table, home_team_name, home_scores, home_table):
    
    err = ""
    game = Game()
     
    game.away, err = make_team(away_team_name, away_scores, away_table)
    if( err != "" ):
        err += " in Away record"
        return game, err

    game.home , err = make_team(home_team_name, home_scores, home_table)
    if( err != "" ):
        err += " in Home record"
        return game, err

    game, err = make_game(game)
    
    if( err != "" ):
        return game, err

    if( game.away.hasRecord() ):
        game.away.compute_statistic()
        make_web_table(game.away)
    if( game.home.hasRecord() ):
        game.home.compute_statistic()
        make_web_table(game.home)

    isColor = True
    post_ptt = make_PTT_format(game, isColor)
    post_ptt = post_ptt.replace('\x1b', '\025')
    game.post_ptt = post_ptt
    game.post_db  = make_database_format(game)
    
    return game, err
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i" , dest="input_file_name" , required=True, help="Specify input file name")
    parser.add_argument("-o" , dest="output_file_name", help="Specify output file name [default: print to screen]")
    parser.add_argument("-nc", dest="no_color", default=False, action="store_true", help="Close color mode [default: on]")

    opts = parser.parse_args(sys.argv[1:])
    
    recordFileName = opts.input_file_name
    outputFileName = opts.output_file_name
    isColor = not opts.no_color

    game_type, date, game_id, location, \
    away_team_name, away_scores, away_record, \
    home_team_name, home_scores, home_record = load_record_file(recordFileName)

    game, err = parse_game_record(away_team_name, away_scores, away_record, \
                                  home_team_name, home_scores, home_record)
    """
    if( game.team2 == None ):
        isOneTeam = True
    else:
        isOneTeam = False

    post_ptt = make_PTT_format(game, isOneTeam, isColor)
    post_db  = make_database_format(game, isOneTeam)
    if( outputFileName == None ):
        print post_ptt
        print post_db
    else:
        with open(outputFileName, 'w') as f:
            print "Dump %s" %outputFileName
            # replace ESC to ^U
            post_ptt = post_ptt.replace('\x1b', '\025')
            f.write(post_ptt)

        with open(outputFileName + '.db', 'w') as f:
            print "Dump %s" %(outputFileName + '.db')
            f.write(post_db)
    """
