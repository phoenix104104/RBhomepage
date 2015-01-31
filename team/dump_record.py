#!/usr/bin/python
# -*- coding: utf8 -*-
import sys, os

def num_cjk(string):
    cnt = 0
    for x in string.decode('utf-8'):
        if 0x4e00 <= ord(x) <= 0x9fff:
            cnt += 1

    return cnt

def make_PTT_format(game, isAddColor=True):
    
    posts = ""
    posts += make_PTT_score_board(game)
    posts += "\n"
    if( game.away.hasRecord() ):
        posts += game.away.name + "\n"
        posts += make_team_PTTtable(game.away, isAddColor)
        posts += "\n\n"
        posts += make_pitcher_PTTtable(game.away.pitchers)
        posts += "\n"
    if( game.home.hasRecord() ):
        posts += game.home.name + "\n"
        posts += make_team_PTTtable(game.home, isAddColor)
        posts += "\n\n"
        posts += make_pitcher_PTTtable(game.home.pitchers)
        posts += '\n'

    return posts


def make_database_format(game):
    
    posts = make_score_board(game)
    posts += "\n"
    if( game.away.hasRecord() ):
        posts += dump_player_statistic(game.away)
        posts += "\n"
    if( game.home.hasRecord() ):
        posts += dump_player_statistic(game.home)
        posts += "\n"

    return posts

def make_score_board(game):

    posts = ""
    posts += "%s\t" %(game.away.name)
    for s in game.away.scores:
        posts += "%4d" %s
    posts += "\n"
    posts += "%s\t" %(game.home.name)
    for s in game.home.scores:
        posts += "%4d" %s
    posts += "\n"
    return posts

def make_PTT_score_board(game): 
    
    hh = "─"
    vv = "│"
    vh = "┼"
    posts  = "        %s一%s二%s三%s四%s五%s六%s七%s　%sＲ%sＨ%sＥ%s\n" %(vv, vv, vv, vv, vv, vv, vv, vv, vv, vv, vv, vv)
    for team in [game.away, game.home]:
        posts += "%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n" %(hh, hh, hh, hh, vh, hh, vh, hh, vh, hh, vh, hh, vh, hh, vh, hh, vh, hh, vh, hh, vh, hh, vh, hh, vh, hh, vh)
        
        space = 8 + num_cjk(team.name) 
        posts += "%s%s%2d%s%2d%s%2d%s%2d%s%2d%s%2d%s%2d%s　%s%2d%s%2d%s%2d%s\n" %(team.name.center(space), vv, team.scores[0], vv, team.scores[1], vv, team.scores[2], vv, team.scores[3], vv, team.scores[4], vv, team.scores[5], vv, team.scores[6], vv, vv, team.R, vv, team.H, vv, team.E, vv)
    
    return posts

def big5len(string):
    return len(string.decode('utf8').encode('big5') )


def make_web_table(team):

    team.batter_table  = make_batter_table(team)
    team.pitcher_table = make_pitcher_table(team)

def make_batter_table(team):

    col2inn = team.col2inn
    player  = team.batters

    # --- initialize table
    table = []

    # --- inning title
    offset = 2
    max_width = offset + len(col2inn)
    row = [""] * max_width

    row[offset] = (digit2FullWidth(1) + "局")
    for n in range(1, len(col2inn)):
        if( col2inn[n] != col2inn[n-1] ):
            row[offset+n] = (digit2FullWidth(col2inn[n]) + "局")

    table.append(row)

    for n in range(len(player)):
        row = [""] * max_width
        
        if( player[n].order == 'R' ):
            order = "代"
        else:
            order = player[n].order

        row[0] = order


        if( player[n].number == 'N' ):
            num = "新生"
        else:
            num = player[n].number

        row[1] = num

        for i in range(len(player[n].PAs) ):
            pa = player[n].PAs[i]
            word, word_len = PA2Character(pa)
            row[pa.column+2] = "%s" %word

        table.append(row)

    return table


def make_pitcher_table(team):

    table = []
    pitchers = team.pitchers

    row = ["投手", "投球局數", "面對打席", "被安打", "被全壘", "四壞", "三振", "失分", "自責", "滾地", "飛球", "ERA"]
    table.append(row)

    for pitcher in pitchers:
        row = []
        row.append(pitcher.number)
        row.append(pitcher.IP)
        row.append(pitcher.TBF)
        row.append(pitcher.H)
        row.append(pitcher.HR)
        row.append(pitcher.BB)
        row.append(pitcher.K)
        row.append(pitcher.Run)
        row.append(pitcher.ER)
        row.append(pitcher.GO)
        row.append(pitcher.FO)
        row.append("%.2f" %pitcher.ERA)
        
        table.append(row)

    return table


def make_team_PTTtable(team, isAddColor=True):

    col2inn = team.col2inn
    nPlayer = team.nBatters
    player  = team.batters

    posts = " "*15
    posts += (digit2FullWidth(1) + "局    ")
        
    for n in range(1, len(col2inn)):
        if( col2inn[n] == col2inn[n-1] ):
            posts += (" "*8)
        else:
            posts += (digit2FullWidth(col2inn[n]) + "局    ")

    posts += '\n'
    
    for n in range(nPlayer):
        if( player[n].order == 'R' ):
            order = "代"
        else:
            order = player[n].order

        posts += "%2s. " %order

        if( player[n].number == 'N' ):
            num = "新生"
        else:
            num = player[n].number

        space = " " * (6 - big5len(num) ) 
        posts += "%s%s%3s  " %(num, space, player[n].pos)

        column = 0
        for i in range(len(player[n].PAs) ):
            
            pa = player[n].PAs[i]

            # append white space
            k = pa.column - column
            posts += ( " "*8*k )

            column = pa.column + 1
            word, word_len = PA2Character(pa, isAddColor)

            space = " " * (8 - word_len)
            posts += "%s%s" %(word, space)


        posts += '\n'

    return posts

def make_pitcher_PTTtable(pitchers):

    posts = ""
    posts += "  投    投局 面打  被   被   四  三  失  自  滾  飛   Ｅ\n"
    posts += "  手    球數 對席 安打 全壘  壞  振  分  責  地  球   RA\n"
    for pitcher in pitchers:
        posts += "  %-4s   %3s  %2d   %2d   %2d   %2d  %2d  %2d  %2d  %2d  %2d  %.2f\n" %(pitcher.number, pitcher.IP, pitcher.TBF, pitcher.H, pitcher.HR, pitcher.BB, pitcher.K, pitcher.Run, pitcher.ER, pitcher.GO, pitcher.FO, pitcher.getERA())
    
    return posts


def digit2FullWidth(n):
    if( n == 1 ):
        return "一"
    elif( n == 2 ):
        return "二"
    elif( n == 3 ):
        return "三"
    elif( n == 4 ):
        return "四"
    elif( n == 5 ):
        return "五"
    elif( n == 6 ):
        return "六"
    elif( n == 7 ):
        return "七"
    elif( n == 8 ):
        return "八"
    elif( n == 9 ):
        return "九"
    elif( n == 10 ):
        return "十"
    else:
        print "Error! Unsupported digit %d!" %n
        sys.exit(0)

def pos2word(pos, res):
    word = ""
    if( pos == "1" ):
        if( res == "1B" ):
            word = "內"
        else:
            word = "投"
    elif( pos == "2" ):
        if( res == "1B" ):
            word = "內"
        else:
            word = "補"
    elif( pos == "3" ):
        if( res == "1B" ):
            word = "右"
        else:
            word = "一"
    elif( pos == "4" ):
        if( res == "1B" ):
            word = "右"
        else:
            word = "二"
    elif( pos == "5" ):
        if( res == "1B" ):
            word = "左"
        else:
            word = "三"
    elif( pos == "6" ):
        word = "游"
    elif( (pos == "7") | (pos == "L") ):
        word = "左"
    elif( (pos == "8") | (pos == "C") ):
        word = "中"
    elif( (pos == "9") | (pos == "R") ):
        word = "右"
    elif( pos == "10" ):
        word = "自"
    
    return word

def res2word(pa, wordLen):
    res = pa.result
    if(wordLen == 1):
        if( res == "G" ):
            word = "滾"
        elif( res == "F" ):
            word = "飛"
        elif( res == "1B" ):
            word = "安"
        elif( res == "2B" ):
            word = "二"
        elif( res == "3B" ):
            word = "三"
        elif( res == "HR" ):
            word = "全"
        elif( res == "FC" ):
            word = "選"
        elif( res == "SF" ):
            word = "犧"
        elif( res == "E" ):
            word = "失"
        elif( res == "DP" ):
            word = "雙"
        else:
            print "Error! Unknown res notation %s" %res
            sys.exit(0)  
    else:   # wordLen = 2
        if( res == "BB" ):
            word = "四壞"
        elif( res == "K" ):
            word = "三振"
        elif( res == "G" ):
            word = "滾地"
        elif( res == "F" ):
            word = "飛球"
        elif( res == "DP" ):
            word = "雙殺"
        elif( res == "1B" ):
            word = "一安"
        elif( res == "2B" ):
            word = "二安"
        elif( res == "3B" ):
            word = "三安"
        elif( res == "HR" ):
            word = "全壘"
        elif( res == "SF" ):
            word = "犧牲"
        elif( res == "FC" ):
            word = "野選"
        elif( res == "IB" ):
            word = "違擊"
        elif( res == "E" ):
            word = "失誤"
        elif( res == "CB" ):
            word = "強襲"
        elif( res == "IF" ):
            word = "內飛"
        elif( res == "FO" ):
            word = "界飛"
        else:
            print "Error! Unknown res notation %s" %res
            sys.exit(0)  

    n = 0
    if( pa.rbi != 0 ):
        word += str(pa.rbi)
        n += 1
    if( pa.run != 0 ):
        word += "r"
        n += 1

    return word, n

def end2word(pa):
    word = ""
    if( pa.endInning in ["#", "!"] ):
        word += "#"
    if( (pa.note != 0) & (pa.note != 'X') ):
        word += pa.note

    return word, len(word)

def PA2Character(pa, isAddColor=False):
    if( not pa.isPlay ):
        word = ("　　") # Full-Width white
        word_len = 4
    else:
        if( pa.pos == 0 or pa.pos == None ):
            word, n = res2word(pa, 2)
        else:
            pos_word = pos2word(pa.pos, pa.result)
            res_word, n = res2word(pa, 1)
            word = pos_word + res_word

        word_len = 4 + n
        if( isAddColor ):
            word = AddColor(pa.result, word)

        pa_word, n = end2word(pa)
        word += pa_word
        word_len += n

    return word, word_len

def AddColor(pa_result, word):
    if( (pa_result == "1B") | (pa_result == "2B") | (pa_result == "3B") ):
        word = "\x1b[1;31m%s\x1b[m" %word
    elif( pa_result == "HR" ):
        word = "\x1b[1;5;1;31m%s\x1b[m" %word
    elif( pa_result == "SF" ):
        word = "\x1b[1;35m%s\x1b[m" %word
    elif( pa_result == "BB" ):
        word = "\x1b[1;32m%s\x1b[m" %word
    elif( pa_result == "K" ):
        word = "\x1b[1;33m%s\x1b[m" %word
    
    return word



def dump_player_statistic(team):
    
    # Batter Statistic
    posts = "Team: %s\n" %team.name
    posts += "Batting:\n"
    posts += "          PA  AB  1B  2B  3B  HR  DP RBI RUN  BB   K  SF\n"
    for p in team.batters:
        space = " " * (6 - big5len(p.number) )
        line = "%2s. %s%s" %(p.order, p.number, space)
        line += "%2d  %2d  %2d  %2d  %2d  %2d  %2d %3d %3d  %2d   %d  %2d\n" %(p.PA, p.AB, p.B1, p.B2, p.B3, p.HR, p.DP, p.RBI, p.RUN, p.BB, p.K, p.SF)
        posts += line

    posts += '\nPitching:\n'
    posts += " No.    IP  PA   H  HR  BB   K  Run  ER  GO  FO\n" 
    # Pitcher Statistic
    for p in team.pitchers:
        posts += " %-8s%3s  %2d  %2d  %2d  %2d  %2d  %3d  %2d  %2d  %2d\n" %(p.number, p.IP, p.TBF, p.H, p.HR, p.BB, p.K, p.Run, p.ER, p.GO, p.FO)

    return posts


def PrintPlayer(player, n=-1):
    if n == -1:
        for p in player:
            print "Ord No. Inn Col Pos Res RBI Run out end note"
            print "%3s %2s." %(p.order, p.number)
            for pa in p.PAs:
                if not pa.isPlay:
                    print '\t-'
                else:
                    print "\t( %d,  %d,  %s,  %2s,  %d,  %d,  %d,  %s,  %s)" %(pa.inning, pa.column, pa.pos, pa.result, pa.rbi, pa.run, pa.out, pa.endInning, pa.note)
    else:
        p = player[n]
        print "Order No. Inn Col Pos Res RBI Run out end note"
        print " %s   %s." %(p.order, p.number)
        for pa in p.PAs:
            if not pa.isPlay:
                print "\t-"
            else:
                print "\t(%d, %d, %s, %s, %d, %d, %d, %s, %s)" %(pa.inning, pa.column, pa.pos, pa.result, pa.rbi, pa.run, pa.out, pa.endInning, pa.note)


