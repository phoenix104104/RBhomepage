# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from models import Member, Game
import sys

# Create your views here.
def index(request):
    player = Member.objects.all()
    for p in player:
        print p.name

    context = {'player': player}
    return render(request, 'team/index.html', context)

def show_all_member(request):

    members = Member.objects.all()
    """
    members_bat= []
    members_pit= []
    team_bat = Hitter()
    team_pit = Pitcher()

    for player in members:
		#batting data
		bat = Batting.objects.filter(member__memberID = player.memberID , team = thisteam.teamID)
		
		if bat.exists() :
			hitter = Hitter()
			for bat_detail in bat:
				hitter.name = player.name
				hitter.id = player.memberID
				hitter.games_played += 1
				hitter.pa += bat_detail.pa
				hitter.single +=bat_detail.single
				hitter.double +=bat_detail.double
				hitter.triple +=bat_detail.triple
				hitter.hr += bat_detail.hr
				hitter.rbi += bat_detail.rbi
				hitter.r += bat_detail.run
				hitter.bb+= bat_detail.bb
				hitter.so +=bat_detail.so
				hitter.sf +=bat_detail.sf
			hitter.stat()
			members_bat.append(hitter)
			team_bat.add(hitter)
			team_bat.stat()

		#pitching data
		pit = Pitching.objects.filter(member__memberID = player.memberID , team = thisteam.teamID)
		if pit.exists() :
			pitcher = Pitcher()

			for pit_detail in pit:
				pitcher.name = player.name
				pitcher.games_played +=1
				pitcher.id = player.memberID
				pitcher.win+=pit_detail.win
				pitcher.lose+=pit_detail.lose
				pitcher.outs+=pit_detail.outs
				pitcher.pa+=pit_detail.pa
				pitcher.so+=pit_detail.so
				pitcher.bb+=pit_detail.bb
				pitcher.h+=pit_detail.h
				pitcher.hr+=pit_detail.hr
				pitcher.r+=pit_detail.r
				pitcher.er+=pit_detail.er
				pitcher.go+=pit_detail.go
				pitcher.fo+=pit_detail.fo

			pitcher.stat()
			members_pit.append(pitcher)
			team_pit.add(pitcher)
			team_pit.stat()

	context = {'thisteam' : thisteam, 'team_info':team_info, 'game_list': game_list, 'members_bat': members_bat ,'members_pit':members_pit, 'team_bat' : team_bat, 'team_pit' : team_pit}

	return render(request , 'sbleague/team.html',context)
    """

