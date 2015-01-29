# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from models import Member, Game, Batting, Pitching
from util import CommaSeparatedString_to_IntegerArray

def index(request, warning=None):
	player = Member.objects.all()
	if request.user.is_authenticated:
		print "authenticated user"
	if request.user.username:
		print "username = " + request.user.username
	else:
		print "none"
	context = {'player': player, 'warning': warning}
	return render(request, 'team/index.html', context)


def show_all_game(request):

	game_list = Game.objects.all().order_by('-date')

	for game in game_list:
		game.scores = str(game.away_R) + ' : ' + str(game.home_R)

	context = {'game_list': game_list}
	return render(request, 'team/show_all_game.html', context)


def show_game(request, game_id) :

	game = Game.objects.get(id = game_id)
	
	all_batting  = Batting.objects.filter(game = game).order_by("order")
	all_pitching = Pitching.objects.filter(game = game).order_by("order")
	
	for batter in all_batting:
		batter.stat()

	for pitcher in all_pitching:
		pitcher.stat()

	game.away_scores = CommaSeparatedString_to_IntegerArray(game.away_scores)
	game.home_scores = CommaSeparatedString_to_IntegerArray(game.home_scores)

	context = {'game': game, 'all_batting': all_batting, 'all_pitching': all_pitching}
	return render(request, 'team/show_game.html', context)	

    
def login_view(request):
	print "login view!"
	if request.method != 'POST':
		return redirect("/")
	else:
		username = request.POST.get("username")
		password = request.POST.get("password")
		print "username = %s" %username
		user = authenticate(username = username, password = password)
		if user is not None:
			if user.is_active:
				login(request, user)
				print "%s login!" %username
				return redirect("/")
				#return index(request)
			else:
				print "Inactive user!"
				return redirect("/")
		else:
			warning = "Invalid username or wrong password!"
			return index(request, warning)


def logout_view(request):

	logout(request)
	return redirect("/")
