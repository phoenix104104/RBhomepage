from django.db import models

# Create your models here.
class Member(models.Model):
	id 		= models.AutoField(primary_key=True)
	name 	= models.CharField(max_length=100, default="")
	number  = models.IntegerField(default=0)
	title   = models.CharField(max_length=200, default="", blank=True)
	

	def __unicode__(self):
		return "%s(%d)" %(self.name, self.number)

	class Meta:
		ordering = ["number"]


class League(models.Model):
	id      = models.AutoField(primary_key=True)
	name    = models.CharField(max_length=200)
	def __unicode__(self):
		return self.name


class Game(models.Model):
	id				= models.AutoField(primary_key=True)
	league      	= models.ForeignKey(League)
	date        	= models.DateField()
	location    	= models.CharField(max_length=200, default="")
	away_name      	= models.CharField(max_length=200, default="")
	away_scores 	= models.CharField(max_length=200, default="")
	away_R      	= models.IntegerField(default=0)
	away_H      	= models.IntegerField(default=0)
	away_E      	= models.IntegerField(default=0)
	home_name      	= models.CharField(max_length=200, default="")
	home_scores 	= models.CharField(max_length=200, default="")
	home_R      	= models.IntegerField(default=0)
	home_H      	= models.IntegerField(default=0)
	home_E      	= models.IntegerField(default=0)
	record 			= models.TextField(default="")

	def __unicode__(self):
		return str(self.date) + ' ' + self.away_name + ' vs ' + self.home_name

	class Meta:
		ordering = ["date"]


class Batting(models.Model):
	game    = models.ForeignKey(Game)
	member  = models.ForeignKey(Member)
	order   = models.CharField(max_length=10, default="")
	pa      = models.IntegerField(default=0)
	single  = models.IntegerField(default=0)
	double  = models.IntegerField(default=0)
	triple  = models.IntegerField(default=0)
	hr      = models.IntegerField(default=0)
	rbi     = models.IntegerField(default=0)
	run     = models.IntegerField(default=0)
	bb      = models.IntegerField(default=0)
	k       = models.IntegerField(default=0)
	sf      = models.IntegerField(default=0)
	field   = models.CharField(max_length=10, default="")


	def __unicode__(self):
		return self.member.name + ' ' + str(self.game.date) + ' ' + self.game.home_name + ' vs ' + self.game.away_name


class Pitching(models.Model):
	game    = models.ForeignKey(Game)
	member  = models.ForeignKey(Member)
	order   = models.IntegerField(default=0)
	outs    = models.IntegerField(default=0)
	pa      = models.IntegerField(default=0)
	hit     = models.IntegerField(default=0)
	hr      = models.IntegerField(default=0)
	bb      = models.IntegerField(default=0)
	k       = models.IntegerField(default=0)
	run     = models.IntegerField(default=0)
	er      = models.IntegerField(default=0)
	go      = models.IntegerField(default=0)
	fo      = models.IntegerField(default=0)
	win     = models.IntegerField(default=0)
	lose    = models.IntegerField(default=0)
	
	def __unicode__(self):
		return self.member.name + ' ' + str(self.game.date) + ' ' + self.game.home_name + ' vs ' + self.game.away_name

class Current(models.Model):
	year = models.IntegerField(default=0)

	def __unicode__(self):
		return "%d" %self.year
