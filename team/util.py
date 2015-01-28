

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

# collect all statistic for webpage
class statBatter:
	def __init__ (self): 
		self.games    = 0
		self.pa       = 0
		self.single   = 0
		self.id       = 0
		self.double   = 0
		self.triple   = 0
		self.hr       = 0
		self.rbi      = 0
		self.r        = 0
		self.bb       = 0
		self.so       = 0
		self.sf       = 0
		self.bb       = 0
		self.k        = 0
		self.ab       = 0
		self.hit      = 0
		self.avg      = 0
		self.slg      = 0
		self.obp      = 0
		self.ops      = 0
		self.avg_s    = ''
		self.slg_s    = ''
		self.obp_s    = ''
		self.ops_s    = ''
		self.name 	  = ''
		self.date 	  = ''
		self.opp 	  = ''
		self.gameID	  = 0
		self.memberID = 0
	
	def stat(self):
		self.hit = self.single+self.double+self.triple+self.hr
		self.bases = self.single+2*self.double+3*self.triple+4*self.hr
		self.ab = self.pa-self.bb-self.sf
		if self.ab!=0 :
			self.avg = self.hit / self.ab 
			self.slg = self.bases / self.ab 
		if self.pa!=0 : 
			self.obp = (self.hit + self.bb) /self.pa 
		self.ops = self.obp + self.slg 

		# map to fix-decimal string
		self.avg_s = format(self.avg, '.3f')
		self.slg_s = format(self.slg, '.3f')
		self.obp_s = format(self.obp, '.3f')
		self.ops_s = format(self.ops, '.3f')

	def add(self, hitter):
		self.pa += hitter.pa
		self.single +=hitter.single
		self.double +=hitter.double
		self.triple +=hitter.triple
		self.hr +=hitter.hr
		self.rbi +=hitter.rbi
		self.r +=hitter.r
		self.bb +=hitter.bb
		self.so +=hitter.so
		self.sf +=hitter.sf
		self.games_played += hitter.games_played

