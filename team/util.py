# -*- coding: utf-8 -*-
import math
from decimal import Decimal

def CommaSeparatedString_to_IntegerArray(input):
    
    output = input.split(',')
    output = [int(i) for i in output]
    
    return output

def IntegerArray_to_CommaSeparatedString(input):
    
    output = ""
    for x in input:
        output += str(x) + ","

    output = output[:-1] # delete last comma

    return output

def table_to_text(table):
    lines = ""
    for row in table:
        for col in row:
            lines += "%s\t" %col
        lines += "\n"
    
    return lines

def text_to_table(text):
    
    table = []
    lines = text.split('\n')
    for line in lines:
        data = line.split()
        data = filter(None, data)
        if len(data) != 0:
            table.append(data)
    
    return table

def gather_team_info_from_web(request, HA):

    team_name  = request.POST[HA + "_name"].encode('utf8')
    scores = []
    for i in range(1, 8):
        score = request.POST[HA + "_score_" + str(i)]
        if( not score ):
            break
        scores.append(int(score))

    return (team_name, scores)

# collect all statistic for webpage
class statBatting():
	game    = None
	member  = None
	order   = 0
	gp		= 0 # total game played (for accumulating statistic)
	pa      = 0
	single  = 0
	double  = 0
	triple  = 0
	hr      = 0
	rbi     = 0
	run     = 0
	bb      = 0
	k       = 0
	sf      = 0
	ab   	= 0
	hit  	= 0
	avg  	= 0
	slg  	= 0
	obp  	= 0
	ops  	= 0

	avg_s	= ''
	slg_s	= ''
	obp_s	= ''
	ops_s	= ''

	def stat(self):
		self.hit    = self.single + self.double + self.triple + self.hr
		self.ab     = self.pa - self.bb - self.sf
		bases       = self.single + 2*self.double + 3*self.triple + 4*self.hr
		
		if self.ab != 0:
			self.avg = self.hit / float(self.ab)
			self.slg = bases / float(self.ab)
		
		if self.pa != 0: 
			self.obp = (self.hit + self.bb) / float(self.pa)
			self.ops = self.obp + self.slg 

		# map to fix-decimal string
		self.avg_s = format(self.avg, '.3f')
		self.slg_s = format(self.slg, '.3f')
		self.obp_s = format(self.obp, '.3f')
		self.ops_s = format(self.ops, '.3f')

	# copy data from database
	def copy(self, batting):
		self.game 	= batting.game
		self.member = batting.member
		self.pa     = batting.pa
		self.single = batting.single
		self.double = batting.double
		self.triple = batting.triple
		self.hr     = batting.hr
		self.rbi    = batting.rbi
		self.run    = batting.run
		self.bb     = batting.bb
		self.k      = batting.k
		self.sf     = batting.sf
		self.gp 	= 1

	# accumulate statistic
	def add(self, player):
		self.pa     += player.pa
		self.single += player.single
		self.double += player.double
		self.triple += player.triple
		self.hr     += player.hr
		self.rbi    += player.rbi
		self.run    += player.run
		self.bb     += player.bb
		self.k      += player.k
		self.sf     += player.sf
		self.gp     += player.gp


class statPitching():
	game    = None
	member  = None
	gp     	= 0
	order   = 0
	outs    = 0
	pa      = 0
	hit     = 0
	hr      = 0
	bb      = 0
	so      = 0
	r       = 0
	er      = 0
	go      = 0
	fo      = 0
	win     = 0
	lose    = 0
	era    	= 0
	whip   	= 0
	IP  	= ''
	wl 		= ''
	era_s  	= ''
	whip_s 	= ''

	def stat(self):
		self.inning = 0.1 * (self.outs % 3) + math.floor(self.outs / 3)
		if self.inning !=0 :
			self.era  = ( self.er / (self.outs / 3.0) ) * 7.0
			self.whip = ( self.hit + self.bb ) / ( self.outs / 3.0 )
		else :
			self.era  = 99
			self.whip = 99

		# map to fix-decimal string
		self.era_s       = format(self.era, '.3f')
		self.whip_s      = format(self.whip, '.3f')

		# calculate IP
		if( self.outs == 0 ):
			self.IP = '0.0'
		else:
			N = int(self.outs / 3)
			m = self.outs % 3
			self.IP = '%d.%d' %(N, m)

		# win or lose
		if( self.win == 1 ):
			self.wl = "勝"
		elif( self.lose == 1 ):
			self.wl = "敗"


	def copy(self, pitching):
		self.game 	= pitching.game
		self.member = pitching.member
		self.outs   = pitching.outs
		self.pa     = pitching.pa
		self.so     = pitching.so
		self.bb     = pitching.bb
		self.hit    = pitching.hit
		self.hr     = pitching.hr
		self.r      = pitching.r
		self.er     = pitching.er
		self.go     = pitching.go
		self.fo     = pitching.fo
		self.win    = pitching.win
		self.lose   = pitching.lose

	# accumulate statistic
	def add(self, player):
		self.outs   += player.outs
		self.pa     += player.pa
		self.so     += player.so
		self.bb     += player.bb
		self.hit    += player.hit
		self.hr     += player.hr
		self.r      += player.r
		self.er     += player.er
		self.go     += player.go
		self.fo     += player.fo
		self.win    += player.win
		self.lose   += player.lose
		self.gp     += player.gp