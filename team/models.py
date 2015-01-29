from django.db import models
import math

# Create your models here.
class Member(models.Model):
	id 		= models.AutoField(primary_key=True)
	name 	= models.CharField(max_length=100)
	number  = models.IntegerField(default=0)

	def __unicode__(self):
		return self.name


class League(models.Model):
	id      = models.AutoField(primary_key=True)
	name    = models.CharField(max_length=200)
	def __unicode__(self):
		return self.name


class Game(models.Model):
	id			= models.AutoField(primary_key=True)
	league      = models.ForeignKey(League)
	date        = models.DateField(blank=True)
	location    = models.CharField(max_length=200)
	away        = models.CharField(max_length=200)
	home        = models.CharField(max_length=200)
	away_scores = models.CharField(max_length=200)
	away_R      = models.IntegerField()
	away_H      = models.IntegerField()
	away_E      = models.IntegerField()
	home_scores = models.CharField(max_length=200)
	home_R      = models.IntegerField()
	home_H      = models.IntegerField()
	home_E      = models.IntegerField()

	def __unicode__(self):
		return self.away + ' vs ' + self.home + '  ' + str(self.date)

class Batting(models.Model):
	game    = models.ForeignKey(Game)
	member  = models.ForeignKey(Member)
	order   = models.IntegerField()
	pa      = models.IntegerField()
	single  = models.IntegerField()
	double  = models.IntegerField()
	triple  = models.IntegerField()
	hr      = models.IntegerField()
	rbi     = models.IntegerField()
	run     = models.IntegerField()
	bb      = models.IntegerField()
	k       = models.IntegerField()
	sf      = models.IntegerField()

	# statistic data (no need to store in database)
	gp		= 0 # total game played (for accumulating statistic)
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

	def __unicode__(self):
		return self.member.name + ' ' + str(self.game.date) + ' ' + self.game.home + ' vs ' + self.game.away

	def stat(self):
		self.hit    = self.single + self.double + self.triple + self.hr
		self.ab     = self.pa - self.bb - self.sf
		bases       = self.single + 2*self.double + 3*self.triple + 4*self.hr

		if self.ab != 0:
			self.avg = self.hit / self.ab 
			self.slg = bases / self.ab 

		if self.pa != 0: 
			self.obp = (self.hit + self.bb) /self.pa 
			self.ops = self.obp + self.slg 

		# map to fix-decimal string
		self.avg_s = format(self.avg, '.3f')
		self.slg_s = format(self.slg, '.3f')
		self.obp_s = format(self.obp, '.3f')
		self.ops_s = format(self.ops, '.3f')

	# accumulate statistic
	def add(self, player):
		self.pa     += player.pa
		self.single += player.single
		self.double += player.double
		self.triple += player.triple
		self.hr     += player.hr
		self.rbi    += player.rbi
		self.r      += player.r
		self.bb     += player.bb
		self.k      += player.k
		self.sf     += player.sf
		self.gp     += player.gp


class Pitching(models.Model):
	game    = models.ForeignKey(Game)
	member  = models.ForeignKey(Member)
	order   = models.IntegerField()
	outs    = models.IntegerField()
	pa      = models.IntegerField()
	hit     = models.IntegerField()
	hr      = models.IntegerField()
	bb      = models.IntegerField()
	so      = models.IntegerField()
	r       = models.IntegerField()
	er      = models.IntegerField()
	go      = models.IntegerField()
	fo      = models.IntegerField()
	win     = models.IntegerField()
	lose    = models.IntegerField()
	# statistic data (no need to store in database)
	gp     	= 0
	era    	= 0
	whip   	= 0
	era_s  	= ''
	whip_s 	= ''

	def __unicode__(self):
		return self.member.name + ' ' + str(self.game.date) + ' ' + self.game.home + 'vs' + self.game.away

	def stat(self):
		self.inning = 0.1 * (self.outs % 3) + math.floor(self.outs / 3)
		if self.inning !=0 :
			self.era  = ( self.er / (self.outs / 3) ) * 7 
			self.whip = ( self.hit + self.bb ) / ( self.outs / 3 )
		else :
			self.era  = 99
			self.whip = 99

		# map to fix-decimal string
		self.era_s       = format(self.era, '.3f')
		self.whip_s      = format(self.whip, '.3f')

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