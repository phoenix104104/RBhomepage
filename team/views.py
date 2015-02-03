# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from models import League, Member, Game, Batting, Pitching
import mimetypes, os
from django.core.servers.basehttp import FileWrapper
from parse_record import parse_game_record
from util import statBatting, statPitching, CommaSeparatedString_to_IntegerArray, IntegerArray_to_CommaSeparatedString, gather_team_info_from_web, text_to_table, table_to_text


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
	
	batting_all  = Batting.objects.filter(game = game).order_by("order")
	pitching_all = Pitching.objects.filter(game = game).order_by("order")
	
	batting_list  = []
	pitching_list = []

	for batting in batting_all:
		player = statBatting()
		player.copy(batting)
		player.stat()

		batting_list.append(player)

	for pitching in pitching_all:
		player = statPitching()
		player.copy(pitching)
		player.stat()

		pitching_list.append(player)

	game.away_scores 	= CommaSeparatedString_to_IntegerArray(game.away_scores)
	game.home_scores 	= CommaSeparatedString_to_IntegerArray(game.home_scores)
	game.batter_table 	= text_to_table(game.batter_table)
	game.pitcher_table 	= text_to_table(game.pitcher_table)

	context = {'game': game, 'batting_list': batting_list, 'pitching_list': pitching_list}
	return render(request, 'team/show_game.html', context)	



def show_member(request, member_id) :

	member = Member.objects.get(id = member_id)

	# --- batting
	batting_all  = Batting.objects.filter(member__id = member_id).order_by("game")
	batting_sum  = statBatting()
	batting_list = []

	if batting_all.exists():
		for batting in batting_all:
			player = statBatting()
			player.copy(batting)
			player.stat()

			batting_sum.add(player)
			batting_sum.stat()

			# accumulated statistic
			player.avg_s = batting_sum.avg_s
			player.slg_s = batting_sum.slg_s
			player.obp_s = batting_sum.obp_s
			player.ops_s = batting_sum.ops_s
			
			# opponent team
			if( player.game.home == 'RB' ):
				player.opp = player.game.away
			else:
				player.opp = player.game.home

			batting_list.append(player)

		

	# --- pitching
	pitching_all  = Pitching.objects.filter(member__id = member_id).order_by("game")
	pitching_sum  = statPitching()
	pitching_list = []
	
	if pitching_all.exists() :
		for pitching in pitching_all:
			player = statPitcher()
			player.copy(pitching)
			player.stat()

			pitching_sum.add(player)
			pitching_sum.stat()

			# accumulated statistic
			player.era_s  = pitching_sum.era_s
			player.whip_s = pitching_sum.whip_s
			
			# opponent team
			if( player.game.home == 'RB' ):
				player.opp = player.game.away
			else:
				player.opp = player.game.home

			pitching_list.append(player)

	
	context = {'member': member, 'batting_list': batting_list, 'batting_sum': batting_sum, 'pitching_list': pitching_list, 'pitching_sum': pitching_sum}

	return render(request, 'team/show_member.html', context)


    
def login_view(request):
	
	if request.method != 'POST':
		return redirect("/")
	else:
		username = request.POST.get("username")
		password = request.POST.get("password")
		user = authenticate(username = username, password = password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect("/")
			else:
				return redirect("/")
		else:
			warning = "Invalid username or wrong password!"
			return index(request, warning)


def logout_view(request):

	logout(request)
	return redirect("/")


@login_required(login_url='/admin')
def add_game(request):

	league_list = League.objects.all()
	member_list = Member.objects.all()

	if request.method != "POST":
		league_id 	= -1
		date        = None
		location    = ""
		record 	 	= ""
		away_name 	= ""
		away_scores = [0]*7
		home_name 	= ""
		home_scores = [0]*7
		record_text = ""
		message 	= ""
		warning 	= ""


		context = {'league_list':league_list, 'league_id': league_id, 'date': date, 'location': location, 'away_name': away_name, 'away_scores': away_scores, 'home_name': home_name, 'home_scores': home_scores, 'record_text': record_text, 'warning': warning, 'message': message}

		return render(request, 'team/add_game.html', context)

	else:

		league_id 		= request.POST["league_id"]
		date        	= request.POST["date"]
		location    	= request.POST["location"].encode('utf8')
		record_text		= request.POST["record_text"]
		batting_table 	= []
		pitching_table 	= []

		away_name, away_scores = gather_team_info_from_web(request, 'away')
		home_name, home_scores = gather_team_info_from_web(request, 'home')
			
		message = ""
		warning = ""
		rd_game = None
		team 	= None
		
		if 'add-new-league-btn' in request.POST:
			print "add new league!"
			league_name = request.POST["new-league-name"]

			if league_name != None:

				league = League.objects.filter(name = league_name)
				if( league.exists() ):
					warning = "League name %s already exists." %league_name
				else:
					league = League(name=league_name)
					league.save()
					message = 'Add new league: %s' %league_name
		
		if ('preview-btn' in request.POST) or ('save-game-btn' in request.POST):

			league 		 = League.objects.get(id=league_id)
			record_table = text_to_table(record_text.encode('utf8'))

			
			if( away_name.upper() == 'RB' ):
				away_table = record_table
				home_table = []
			else:
				away_table = []
				home_table = record_table

			rd_game, warning = parse_game_record(away_name, away_scores, away_table, \
	                        	                 home_name, home_scores, home_table)


			if( warning == "" ):
				message = "Preview record table!"

				if( away_name.upper() == 'RB' ):
					team = rd_game.away
				else:
					team = rd_game.home

				for P in team.batters:
					P.name = (P.name).decode('utf8')

				for P in team.pitchers:
					P.name = (P.name).decode('utf8')

				# add rows for changing pitchers
				team.pitchers.append([])
				team.pitchers.append([])
				team.pitchers.append([])

				
				# download PTT format
				"""
				if 'download-btn' in request.POST:

					filename = '%s-%s-%s.txt' %(str(date), away_name, home_name)
					filepath = 'team/static/txt/%s' %filename

					with open(filepath, 'w') as f:
						f.write(rd_game.post_ptt)
						print "save %s" %filepath

					response = HttpResponse(FileWrapper( file(filepath) ), content_type=mimetypes.guess_type(filepath)[0] )
					response['Content-Disposition'] = 'attachment; filename=%s' %filename
					response['Content-Length'] = os.path.getsize(filepath)
					
					return response
				"""

				if 'save-game-btn' in request.POST:
					
					# create and save new Game object
					game = Game(league=league)
					game.date 			= date
					game.location		= location
					game.away			= away_name
					game.away_scores	= IntegerArray_to_CommaSeparatedString(away_scores)
					game.away_R			= rd_game.away.R
					game.away_H			= rd_game.away.H
					game.away_E			= rd_game.away.E
					game.home			= home_name
					game.home_scores	= IntegerArray_to_CommaSeparatedString(home_scores)
					game.home_R			= rd_game.home.R
					game.home_H			= rd_game.home.H
					game.home_E			= rd_game.home.E
					game.record 		= record_text
					game.batter_table 	= table_to_text(team.batter_table)
					game.pitcher_table 	= table_to_text(team.pitcher_table)

					game.save()

					# create and save new Batting object
					nBatter = len(team.batters)
					for i in range(1, nBatter):
						member_id = int(request.POST.get("batter_%d_id"%i, ""))

						if( member_id != 0 ):
							member  = Member.objects.get(id = member_id)

							pa		= int(request.POST.get("batter_%d_pa" 	 %i , ""))
							single	= int(request.POST.get("batter_%d_single"%i , ""))
							double	= int(request.POST.get("batter_%d_double"%i , ""))
							triple	= int(request.POST.get("batter_%d_triple"%i , ""))
							hr		= int(request.POST.get("batter_%d_hr" 	 %i , ""))
							bb		= int(request.POST.get("batter_%d_bb" 	 %i , ""))
							rbi		= int(request.POST.get("batter_%d_rbi" 	 %i , ""))
							run		= int(request.POST.get("batter_%d_run" 	 %i , ""))
							k		= int(request.POST.get("batter_%d_k" 	 %i , ""))
							sf		= int(request.POST.get("batter_%d_sf" 	 %i , ""))
							field	=     request.POST.get("batter_%d_field" %i , "")
							
							batting 		= Batting()
							batting.game 	= game
							batting.member	= member
							batting.order 	= i
							batting.pa     	= pa
							batting.single	= single 
							batting.double	= double 
							batting.triple	= triple 
							batting.hr    	= hr     
							batting.rbi   	= rbi    
							batting.run   	= run    
							batting.bb    	= bb     
							batting.k     	= k      
							batting.sf    	= sf     
							batting.field 	= field  
							 
							batting.save()

						
					# create and save new Batting object
					nPitcher = len(team.pitchers)
					for i in range(1, nPitcher):
						member_id = int(request.POST.get("pitcher_%d_id"%i, ""))

						if( member_id != 0 ):
							member  = Member.objects.get(id = member_id)
							outs	= int(request.POST.get("pitcher_%d_outs" %i , ""))
							pa		= int(request.POST.get("pitcher_%d_pa" 	 %i , ""))
							hit		= int(request.POST.get("pitcher_%d_hit"	 %i , ""))
							hr		= int(request.POST.get("pitcher_%d_hr" 	 %i , ""))
							bb		= int(request.POST.get("pitcher_%d_bb" 	 %i , ""))
							k		= int(request.POST.get("pitcher_%d_k" 	 %i , ""))
							run		= int(request.POST.get("pitcher_%d_run"  %i , ""))
							er		= int(request.POST.get("pitcher_%d_er" 	 %i , ""))
							go		= int(request.POST.get("pitcher_%d_go" 	 %i , ""))
							fo		= int(request.POST.get("pitcher_%d_fo" 	 %i , ""))
							win		= 	  request.POST.get("pitcher_%d_win"  %i , "")
							lose	= 	  request.POST.get("pitcher_%d_lose" %i , "")
							
							if( win != '' ):
								win = 1
							else:
								win = 0

							if( lose != '' ):
								lose = 1
							else:
								lose = 0
							

							pitching 		= Pitching()
							pitching.game 	= game
							pitching.member	= member
							pitching.order 	= i
							pitching.outs   = outs
							pitching.pa     = pa
							pitching.hit   	= hit
							pitching.hr    	= hr
							pitching.bb    	= bb     
							pitching.k     	= k      
							pitching.run   	= run
							pitching.er    	= er
							pitching.go    	= go
							pitching.fo    	= fo
							pitching.win   	= win
							pitching.lose  	= lose
							 
							pitching.save()
				

				return redirect("/game/"+str(game.id))

					

		context = {'league_list':league_list, 'league_id': league_id, 'date': date, 'location': location, 'away_name': away_name, 'away_scores': away_scores, 'home_name': home_name, 'home_scores': home_scores, 'record_text': record_text, 'warning': warning, 'message': message, 'record_game': rd_game, 'team': team, 'member_list': member_list}
			
		return render(request, 'team/add_game.html', context)
	