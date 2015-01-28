from django.db import models

# Create your models here.
class Member(models.Model):
    id      = models.AutoField(primary_key=True)
    name    = models.CharField(max_length=100)
    number  = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

class League(models.Model):
    id      = models.AutoField(primary_key=True)
    name    = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Game(models.Model):
    id          = models.AutoField(primary_key=True)
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
    
    def __unicode__(self):
        return self.member.name + ' ' + str(self.game.date) + ' ' + self.game.home + ' vs ' + self.game.away

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

    def __unicode__(self):
        return self.member.name + ' ' + str(self.game.date) + ' ' + self.game.home + 'vs' + self.game.away