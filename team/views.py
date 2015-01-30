# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from models import League, Member, Game, Batting, Pitching
from util import statBatting, statPitching, CommaSeparatedString_to_IntegerArray

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

	game.away_scores = CommaSeparatedString_to_IntegerArray(game.away_scores)
	game.home_scores = CommaSeparatedString_to_IntegerArray(game.home_scores)

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
			player.avg_s	= batting_sum.avg_s
			player.slg_s	= batting_sum.slg_s
			player.obp_s	= batting_sum.obp_s
			player.ops_s	= batting_sum.ops_s
			
			# opponent team
			if( player.game.home == 'RB' ):
				player.opp = player.game.away
			else:
				player.opp = player.game.home

			batting_list.append(player)

		

	'''
	# --- pitching
	game_all  	  = Pitching.objects.filter(member__memberID = member_id).order_by("game")
	pitching_list = []
	pitching_sum  = Pitcher()
	
	if game_all.exists() :
		for game_detail in game_all:
			pitcher 		= Pitcher()
			pitcher.win 	= game_detail.win
			pitcher.lose 	= game_detail.lose
			pitcher.outs 	= game_detail.outs
			pitcher.pa 		= game_detail.pa
			pitcher.so 		= game_detail.so
			pitcher.bb 		= game_detail.bb
			pitcher.h		= game_detail.h
			pitcher.hr		= game_detail.hr
			pitcher.r 		= game_detail.r
			pitcher.er 		= game_detail.er
			pitcher.go 		= game_detail.go
			pitcher.fo 		= game_detail.fo

			pitcher.games_played = 1
			pitcher.stat()
			pitching_sum.add(pitcher)
			pitching_sum.stat()

			# accumulated statistic
			pitcher.bb_inning_s 	= pitching_sum.bb_inning_s
			pitcher.era_s 	= pitching_sum.era_s
			pitcher.whip_s 	= pitching_sum.whip_s
			
			# game information
			game 			= game_detail.game
			pitcher.date 	= str(game.date)
			pitcher.gameID 	= str(game.gameID)

			# opponent team
			if( game_detail.team == game.home ):
				opp = game.away	
			else:
				opp = game.home

			pitcher.opp 	= str(opp)
			pitcher.oppID 	= str(opp.teamID)

			pitching_list.append(pitcher)

	
	'''
	context = {'member': member, 'batting_list': batting_list, 'batting_sum': batting_sum}

	return render(request, 'team/show_member.html', context)


    
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


@login_required(login_url='/admin')
def add_game(request):

	if request.method != 'POST':

		league_list = League.objects.all()
		context = {'league_list':league_list}

		return render(request, 'team/add_game.html', context)

	"""
	else :

		teams = Team.objects.all()

		home_teamID = request.POST.get("hometeamID", "")
		away_teamID = request.POST.get("awayteamID", "")
		
		hometeam = Team.objects.get(pk=home_teamID)
		awayteam = Team.objects.get(pk=away_teamID)

		homeplayer = Member.objects.filter(team = home_teamID).order_by("number")
		awayplayer = Member.objects.filter(team = away_teamID).order_by("number")

		date = request.POST.get("date", "")
		location = request.POST.get("location", "")		
		game_id  = request.POST.get("game_id", "")



#############################################################################
		away_record = request.POST.get("away_rd", "")
		home_record = request.POST.get("home_rd", "")

		record = None
		record_err = ""
		# ===== record parser
		if( len(away_record) and len(home_record) ):
			awayteam_name = awayteam.name.encode('utf8')[0:6]
			hometeam_name = hometeam.name.encode('utf8')[0:6]
			away_table = text_to_table(away_record.encode('utf8'))
			home_table = text_to_table(home_record.encode('utf8'))
			record, record_err = parse_game_record(awayteam_name, None, away_table, hometeam_name, None, home_table)
			
			record.game_type    = "台大慢壘聯盟"
			record.date         = date
			record.location     = location
			record.game_id      = game_id
			record.away.raw_record = away_record.encode('utf8')
			record.home.raw_record = home_record.encode('utf8')
		else:
			if( len(away_record) == 0 ):
				record_err = "Away 沒有記錄"
			else:
				record_err = "Home 沒有記錄"

#############################################################################
		


		if( date == u'' ):
			err_message = "請輸入日期"
			context = {'teams': teams, 'awayteam': awayteam, 'hometeam': hometeam, 'date': date, 'location': location, 'game_id': game_id, 'away_record': away_record, 'home_record': home_record, 'warning': err_message}
			
			return render(request, 'sbleague/newgame.html', context)
		

		if( game_id == u'' ):
			err_message = "請輸入場次編號"
			context = {'teams': teams, 'awayteam': awayteam, 'hometeam': hometeam, 'date': date, 'location': location, 'game_id': game_id, 'away_record': away_record, 'home_record': home_record, 'warning': err_message}

			return render(request, 'sbleague/newgame.html', context)


		game_exist = True
		try:
			new = Game.objects.get(gameID=game_id)

		except Game.DoesNotExist: # --- add new game

			game_exist = False

			max_batter_nums  = 25
			max_pitcher_nums = 5

			if( record != None and record_err == ""): 
				# --- append batter_num to 25 and pitcher_num to 5
				if( record.away.nBatters < max_batter_nums ):
					for i in range(max_batter_nums-record.away.nBatters):
						record.away.batters.append(rdBatter())

				if( record.home.nBatters < max_batter_nums ):
					for i in range(max_batter_nums-record.home.nBatters):
						record.home.batters.append(rdBatter())

				if( record.away.nPitchers < max_pitcher_nums ):
					for i in range(max_pitcher_nums-record.away.nPitchers):
						record.away.pitchers.append(rdPitcher())

				if( record.home.nPitchers < max_pitcher_nums ):
					for i in range(max_pitcher_nums-record.home.nPitchers):
						record.home.pitchers.append(rdPitcher())

		if( game_exist ):
			err_message = "重複的場次編號"
			context = {'teams': teams, 'awayteam': awayteam, 'hometeam': hometeam, 'date': date, 'location': location, 'game_id': game_id, 'away_record': away_record, 'home_record': home_record, 'warning': err_message}
			
			return render(request, 'sbleague/newgame.html', context)


		# === record error
		if( record_err != "" ):	
			err_message = record_err
			context = {'teams': teams, 'awayteam': awayteam, 'hometeam': hometeam, 'date': date, 'location': location, 'game_id': game_id, 'away_record': away_record, 'home_record': home_record, 'warning': err_message}
			
			return render(request, 'sbleague/newgame.html', context)

		# === success add new game
		if 'send' in request.POST: # --- send data
			context = {'hometeam': hometeam, 'awayteam': awayteam, 'homeplayer': homeplayer ,'awayplayer': awayplayer, 'date': date, 'location': location , 'game_id': game_id, 'home_away': range(2), 'max_batter_nums': max_batter_nums, 'max_pitcher_nums': max_pitcher_nums, 'record': record}

			return render(request, 'sbleague/newgame_detail.html', context)

		elif 'download' in request.POST:

			filename = '%d.txt' %int(game_id)
			filepath = 'sbleague/static/txt/%s' %filename
			with open(filepath, 'w') as f:
				f.write(record.post_ptt)
				print "save %s" %filepath

			response = HttpResponse(FileWrapper( file(filepath) ), content_type=mimetypes.guess_type(filepath)[0] )
			response['Content-Disposition'] = 'attachment; filename=%s' %filename
			response['Content-Length'] = os.path.getsize(filepath)
			
			return response

		else: # --- preview
			err_message = "preview"
			context = {'teams': teams, 'awayteam': awayteam, 'hometeam': hometeam, 'date': date, 'location': location, 'game_id': game_id, 'away_record': away_record, 'home_record': home_record, 'warning': err_message, 'record': record, 'preview': True}
			
			return render(request, 'sbleague/newgame.html', context)

	"""