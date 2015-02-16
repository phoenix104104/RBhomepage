# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from models import League, Member, Game, Batting, Pitching, Current
import mimetypes, os
from operator import attrgetter
from django.core.servers.basehttp import FileWrapper
from parse_record import parse_game_record, extract_single_team_data
from util import statBatting, statPitching, CommaSeparatedString_to_IntegerArray, IntegerArray_to_CommaSeparatedString, gather_team_scores_from_web, text_to_table, table_to_text, calculate_batting_rank


def index(request, warning=""):
	
	context = {'warning': warning}
	return render(request, 'team/index.html', context)


def show_all_game(request):

	if not request.user.is_authenticated():
		print "user not login!"
		return render(request, 'team/show_all_game.html') 

	game_list = Game.objects.all().order_by('date')
	
	# calculate years
	y1 = int(game_list[0].date.year)
	y2 = int(game_list[len(game_list)-1].date.year)
	years = [y for y in range(y1, y2+1)]
	
	months = range(1, 13)
	leagues = League.objects.all()
	
	selected_year  	= Current.objects.all()[0].year
	selected_month 	= 0
	selected_league	= 0
	
	if request.method == "POST":
		selected_year  	= int(request.POST.get("selected-year"))
		selected_month 	= int(request.POST.get("selected-month"))
		selected_league	= int(request.POST.get("selected-league"))

	if( selected_year != 0 ):
		game_list = game_list.filter(date__year = selected_year)
	if( selected_month != 0 ):
		game_list = game_list.filter(date__month = selected_month)
	if( selected_league != 0 ):
		game_list = game_list.filter(league__id = selected_league)

	for game in game_list:
		game.scores = str(game.away_R) + ' : ' + str(game.home_R)

	context = {'years': years, 'months': months, 'leagues': leagues, 'selected_year': selected_year, 'selected_month': selected_month, 'selected_league': selected_league, 'game_list': game_list}
	return render(request, 'team/show_all_game.html', context)


def show_game(request, game_id) :

	if not request.user.is_authenticated():
		print "user not login!"
		return render(request, 'team/show_game.html') 

	game = Game.objects.get(id = game_id)
	
	away_name  	= game.away_name.encode('utf8')
	home_name  	= game.home_name.encode('utf8')
	game.away_scores = CommaSeparatedString_to_IntegerArray(game.away_scores)
	game.home_scores = CommaSeparatedString_to_IntegerArray(game.home_scores)

	record_table = text_to_table(game.record.encode('utf8'))

	if( away_name.upper() == 'RB' ):
		away_table = record_table
		home_table = []
	else:
		away_table = []
		home_table = record_table

	game_record, warning = parse_game_record(away_name, game.away_scores, away_table, \
	           	             	         	 home_name, game.home_scores, home_table)

	game_record, team = extract_single_team_data(game_record, 'RB')

	if request.method != "POST":
		
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
		
		context = {'game': game, 'team': team, 'batting_list': batting_list, 'pitching_list': pitching_list}

		return render(request, 'team/show_game.html', context)	

	else:
		# download PTT format
		if 'download-btn' in request.POST:
			print ("download game %d PTT format" %game.id)
			
			filename = '%s-%s-%s.txt' %(str(game.date), game.away, game.home)
			filepath = 'team/static/txt/%s' %filename

			with open(filepath, 'w') as f:
				f.write(rd_game.post_ptt)
				print ("save %s" %filepath)

			response = HttpResponse(FileWrapper( file(filepath) ), content_type=mimetypes.guess_type(filepath)[0] )
			response['Content-Disposition'] = 'attachment; filename=%s' %filename
			response['Content-Length'] = os.path.getsize(filepath)
			
			return response

		elif 'edit-btn' in request.POST:

			return redirect("/editgame/"+str(game_id))
			


def show_all_member(request):

	if not request.user.is_authenticated():
		print "user not login!"
		return render(request, 'team/show_all_member.html') 

	member_list = Member.objects.filter(title = '')
	captain  = Member.objects.get(title = '隊長')
	coach 	 = Member.objects.get(title = '教練')
	finance  = Member.objects.get(title = '預財')
	chairman = Member.objects.get(title = '董事')

	context = {'member_list': member_list, 'captain': captain, 'coach': coach, 'finance': finance, 'chairman': chairman}

	return render(request, 'team/show_all_member.html', context)

def show_member(request, member_id):

	if not request.user.is_authenticated():
		print "user not login!"
		return render(request, 'team/show_member.html') 

	member = Member.objects.get(id = member_id)
	game_all = Game.objects.all().order_by("date")
	
	# calculate years
	y1 = int(game_all[0].date.year)
	y2 = int(game_all[len(game_all)-1].date.year)
	years = [y for y in range(y1, y2+1)]
	
	months = range(1, 13)
	leagues = League.objects.all()
	

	########## per game log ##########
	log_selected_year  	= Current.objects.all()[0].year
	log_selected_month 	= 0
	log_selected_league	= 0

	if request.method == "POST":
		log_selected_year  	= int(request.POST.get("log-selected-year"))
		log_selected_month 	= int(request.POST.get("log-selected-month"))
		log_selected_league	= int(request.POST.get("log-selected-league"))
		
	# --- batting
	batting_all  = Batting.objects.filter(member__id = member_id)
	if( log_selected_year != 0 ):
		batting_all  = batting_all.filter(game__date__year = log_selected_year)
	if( log_selected_month != 0 ):
		batting_all  = batting_all.filter(game__date__month = log_selected_month)
	if( log_selected_league != 0 ):
		batting_all  = batting_all.filter(game__league__id = log_selected_league)
	batting_all  = batting_all.order_by("game__date")


	batting_sum  = statBatting()
	log_batting_list = []

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
			if( player.game.home_name == 'RB' ):
				player.opp = player.game.away_name
			else:
				player.opp = player.game.home_name

			log_batting_list.append(player)

	# --- pitching
	pitching_all  = Pitching.objects.filter(member__id = member_id)
	if( log_selected_year != 0 ):
		pitching_all  = pitching_all.filter(game__date__year = log_selected_year)
	if( log_selected_month != 0 ):
		pitching_all  = pitching_all.filter(game__date__month = log_selected_month)
	if( log_selected_league != 0 ):
		pitching_all  = pitching_all.filter(game__league__id = log_selected_league)
	pitching_all  = pitching_all.order_by("game__date")


	pitching_sum  = statPitching()
	log_pitching_list = []
	
	if pitching_all.exists() :
		for pitching in pitching_all:
			player = statPitching()
			player.copy(pitching)
			player.stat()

			pitching_sum.add(player)
			pitching_sum.stat()

			# accumulated statistic
			player.ra_s   = pitching_sum.ra_s
			player.era_s  = pitching_sum.era_s
			player.whip_s = pitching_sum.whip_s
			
			# opponent team
			if( player.game.home_name == 'RB' ):
				player.opp = player.game.away_name
			else:
				player.opp = player.game.home_name

			log_pitching_list.append(player)


	########## career ##########

	career_selected_year  	= 0
	career_selected_league	= 0

	if request.method == "POST":
		career_selected_year  	= int(request.POST.get("career-selected-year"))
		career_selected_league	= int(request.POST.get("career-selected-league"))
		
	# --- batting
	batting_all  = Batting.objects.filter(member__id = member_id)
	if( career_selected_year != 0 ):
		batting_all  = batting_all.filter(game__date__year = career_selected_year)
	if( career_selected_league != 0 ):
		batting_all  = batting_all.filter(game__league__id = career_selected_league)
	batting_all  = batting_all.order_by("game__date")

	career_batting_list = []

	if batting_all.exists():

		# calculate data per year
		if( career_selected_year == 0 ):

			for year in years:
				batting_year = batting_all.filter(game__date__year = year)
				batting_sum  = statBatting()

				for batting in batting_year:
					player = statBatting()
					player.copy(batting)
					
					batting_sum.add(player)
					
				batting_sum.stat()
				batting_sum.year = year
				career_batting_list.append(batting_sum)

		# calculate data per month in selected year
		else:

			for month in months:
				batting_month = batting_all.filter(game__date__month = month)
				batting_sum  = statBatting()

				for batting in batting_month:
					player = statBatting()
					player.copy(batting)
					
					batting_sum.add(player)
					
				batting_sum.stat()
				batting_sum.month = month
				career_batting_list.append(batting_sum)


	# --- pitching
	pitching_all  = Pitching.objects.filter(member__id = member_id)
	if( career_selected_year != 0 ):
		pitching_all  = pitching_all.filter(game__date__year = career_selected_year)
	if( career_selected_league != 0 ):
		pitching_all  = pitching_all.filter(game__league__id = career_selected_league)
	pitching_all  = pitching_all.order_by("game__date")

	career_pitching_list = []
	
	if pitching_all.exists():

		# calculate data per year
		if( career_selected_year == 0 ):

			for year in years:
				pitching_year = pitching_all.filter(game__date__year = year)
				pitching_sum  = statPitching()

				for pitching in pitching_year:
					player = statPitching()
					player.copy(pitching)
					
					pitching_sum.add(player)

				pitching_sum.stat()
				pitching_sum.year = year
				career_pitching_list.append(pitching_sum)

		# calculate data per month in selected year
		else:

			for month in months:
				pitching_month = pitching_all.filter(game__date__month = month)
				pitching_sum  = statPitching()
	
				for pitching in pitching_month:
					player = statPitching()
					player.copy(pitching)
					
					pitching_sum.add(player)
					
				pitching_sum.stat()
				pitching_sum.month = month
				career_pitching_list.append(pitching_sum)
	

	context = {'member': member, 'years': years, 'months': months, 'leagues': leagues, 'log_selected_year': log_selected_year, 'log_selected_month': log_selected_month, 'log_selected_league': log_selected_league, 'log_batting_list': log_batting_list, 'log_pitching_list': log_pitching_list, 'career_selected_year': career_selected_year, 'career_selected_league': career_selected_league, 'career_batting_list': career_batting_list, 'career_pitching_list': career_pitching_list}

	return render(request, 'team/show_member.html', context)


  
def show_all_batting(request):

	if not request.user.is_authenticated():
		print "user not login!"
		return render(request, 'team/show_all_batting.html') 

	game_all = Game.objects.all().order_by("date")
	# calculate years
	y1 = int(game_all[0].date.year)
	y2 = int(game_all[len(game_all)-1].date.year)
	years = [y for y in range(y1, y2+1)]
	
	months = range(1, 13)
	leagues = League.objects.all()
	
	
	selected_year  	= Current.objects.all()[0].year
	selected_month 	= 0
	selected_league	= 0
	
	if request.method == "POST":
		selected_year  	= int(request.POST.get("selected-year"))
		selected_month 	= int(request.POST.get("selected-month"))
		selected_league	= int(request.POST.get("selected-league"))

	batting_all = Batting.objects.all()
	if( selected_year != 0 ):
		batting_all  = batting_all.filter(game__date__year = selected_year)
	if( selected_month != 0 ):
		batting_all  = batting_all.filter(game__date__month = selected_month)
	if( selected_league != 0 ):
		batting_all  = batting_all.filter(game__league__id = selected_league)


	##### calculate rank
	player_map = {}
	for batting in batting_all:
		player = statBatting()
		player.copy(batting)
		
		id = batting.member.id
		
		if( not player_map.has_key(id) ):
			player_map[id] = player
		else:
			player_map[id].add(player)
		
	for player in player_map.values():
		player.stat()

	batting_list = sorted(player_map.values(), key=attrgetter("avg"), reverse=True)

	context = {'years': years, 'months': months, 'leagues': leagues, 'selected_year': selected_year, 'selected_month': selected_month, 'selected_league': selected_league, 'batting_list': batting_list}

	return render(request, 'team/show_all_batting.html', context)

def show_all_pitching(request, order="win"):
	
	if not request.user.is_authenticated():
		print "user not login!"
		return render(request, 'team/show_all_pitching.html') 

	game_all = Game.objects.all().order_by("date")
	# calculate years
	y1 = int(game_all[0].date.year)
	y2 = int(game_all[len(game_all)-1].date.year)
	years = [y for y in range(y1, y2+1)]
	
	months = range(1, 13)
	leagues = League.objects.all()
	
	
	selected_year  	= Current.objects.all()[0].year
	selected_month 	= 0
	selected_league	= 0
	
	if request.method == "POST":
		selected_year  	= int(request.POST.get("selected-year"))
		selected_month 	= int(request.POST.get("selected-month"))
		selected_league	= int(request.POST.get("selected-league"))

	pitching_all = Pitching.objects.all()
	if( selected_year != 0 ):
		pitching_all  = pitching_all.filter(game__date__year = selected_year)
	if( selected_month != 0 ):
		pitching_all  = pitching_all.filter(game__date__month = selected_month)
	if( selected_league != 0 ):
		pitching_all  = pitching_all.filter(game__league__id = selected_league)

	##### calculate rank
	player_map = {}
	for pitching in pitching_all:
		player = statPitching()
		player.copy(pitching)
		
		id = pitching.member.id
		
		if( not player_map.has_key(id) ):
			player_map[id] = player
		else:
			player_map[id].add(player)
		
	for player in player_map.values():
		player.stat()

	pitching_list = sorted(player_map.values(), key=attrgetter("win"), reverse=True)

	context = {'years': years, 'months': months, 'leagues': leagues, 'selected_year': selected_year, 'selected_month': selected_month, 'selected_league': selected_league, 'pitching_list': pitching_list}

	return render(request, 'team/show_all_pitching.html', context)


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
	game = Game()
	batting_list = []
	pitching_list = []

	if request.method != "POST":
		game.date        	= None
		game.location    	= ""
		game.away_name 		= ""
		game.away_scores 	= [0]*7
		game.home_name 		= ""
		game.home_scores 	= [0]*7
		game.record		 	= ""
		message 			= ""
		warning 			= ""

		context = {'league_list':league_list, 'game': game, 'warning': warning, 'message': message}

		return render(request, 'team/add_game.html', context)

	else:

		league_id 			= request.POST["league_id"]
		game.league	 		= League.objects.get(id=league_id)
		game.date      		= request.POST["date"]
		game.location  		= request.POST["location"]
		game.record			= request.POST["record_text"]
		game.away_name  	= request.POST["away_name"]
		game.home_name  	= request.POST["home_name"]
		game.away_scores 	= gather_team_scores_from_web(request, 'away')
		game.home_scores 	= gather_team_scores_from_web(request, 'home')
			
		message = ""
		warning = ""
		game_record = None
		team = None
		
		if 'add-new-league-btn' in request.POST:
			print ("add new league!")
			league_name = request.POST["new-league-name"]

			if league_name != None:

				league = League.objects.filter(name = league_name)
				if( league.exists() ):
					warning = "League name %s already exists." %league_name
				else:
					league = League(name=league_name)
					league.save()
					message = 'Add new league: %s' %league_name

			league_list = League.objects.all()
		
		if 'add-new-member-btn' in request.POST:
			print ("add new member!")
			member_name = request.POST["new-member-name"]
			member_number = int(request.POST["new-member-number"])

			if member_name != None:

				member = Member.objects.filter(name = member_name)
				if( member.exists() ):
					warning = "Member %s already exists." %member_name
				else:
					member = Member(name=member_name, number=member_number)
					member.save()
					message = 'Add new member: %s(%d)' %(member_name, member_number)

			member_list = Member.objects.all()

		
		if ('preview-btn' in request.POST) or ('save-game-btn' in request.POST):

			game.league	 = League.objects.get(id=league_id)
			record_table = text_to_table(game.record.encode('utf8'))

			away_name = game.away_name.encode('utf8')
			home_name = game.home_name.encode('utf8')

			if( away_name.upper() == 'RB' ):
				away_table = record_table
				home_table = []
			else:
				away_table = []
				home_table = record_table

			game_record, warning = parse_game_record(away_name, game.away_scores, away_table, \
	                        	                 	 home_name, game.home_scores, home_table)

			game.away_R	= game_record.away.R
			game.away_H	= game_record.away.H
			game.away_E	= game_record.away.E
			game.home_R	= game_record.home.R
			game.home_H	= game_record.home.H
			game.home_E	= game_record.home.E

			if( warning == "" ):
				message = "Preview record table!"

				game_record, team = extract_single_team_data(game_record, 'RB')

				# create and save new Batting object
				nBatter = len(team.batters)
				batting_list = []

				for i in range(nBatter):
					batting 		= Batting()
					batting.game 	= game
					batting.order 	= team.batters[i].order
					batting.pa     	= team.batters[i].PA
					batting.single	= team.batters[i].B1
					batting.double	= team.batters[i].B2
					batting.triple	= team.batters[i].B3
					batting.hr    	= team.batters[i].HR
					batting.rbi   	= team.batters[i].RBI
					batting.run   	= team.batters[i].RUN
					batting.bb    	= team.batters[i].BB
					batting.k     	= team.batters[i].K
					batting.sf    	= team.batters[i].SF
					batting.field 	= team.batters[i].pos
					try:
						batting.member  = Member.objects.get(name=team.batters[i].name.decode('utf8'))
					except Member.DoesNotExist:
						warning = "member name %s does not exist." %team.batters[i].name
						break

					batting_list.append(batting)
				

				# create and save new Batting object
				nPitcher = len(team.pitchers)
				pitching_list = []

				for i in range(nPitcher):
					pitching 		= Pitching()
					pitching.game 	= game
					pitching.order 	= i
					pitching.outs   = team.pitchers[i].OUT
					pitching.pa     = team.pitchers[i].TBF
					pitching.hit   	= team.pitchers[i].H
					pitching.hr    	= team.pitchers[i].HR
					pitching.bb    	= team.pitchers[i].BB
					pitching.k     	= team.pitchers[i].K
					pitching.run   	= team.pitchers[i].RUN
					pitching.er    	= team.pitchers[i].ER
					pitching.go    	= team.pitchers[i].GO
					pitching.fo    	= team.pitchers[i].FO
					pitching.win   	= team.pitchers[i].WIN
					pitching.lose  	= team.pitchers[i].LOSE
					try:
						pitching.member = Member.objects.get(name=team.pitchers[i].name.decode('utf8'))
					except Member.DoesNotExist:
						warning = "member name %s does not exist." %team.pitchers[i].name
						break

					pitching_list.append(pitching)

				# add rows for changing pitchers
				N = len(pitching_list)
				for i in range(5 - N):
					pitching_list.append(Pitching())

				if 'save-game-btn' in request.POST:
					
					# create and save new Game object
					game.away_scores = IntegerArray_to_CommaSeparatedString(game.away_scores)
					game.home_scores = IntegerArray_to_CommaSeparatedString(game.home_scores)
					game.save()

					nBatter = len(batting_list)
					for i in range(nBatter):
						batting = batting_list[i]
						member_id = int(request.POST.get("batting_%d_id" %(i+1), ""))

						if( member_id != 0 ):
							batting.member  = Member.objects.get(id = member_id)
							batting.game 	= game
							batting.save()

						
					nPitcher = len(pitching_list)
					for i in range(nPitcher):
						pitching = pitching_list[i]
						member_id = int(request.POST.get("pitching_%d_id" %(i+1), ""))

						if( member_id != 0 ):
							pitching.member = Member.objects.get(id = member_id)
							pitching.game 	= game
							pitching.outs	= int(request.POST.get("pitching_%d_outs"	%(i+1) , ""))
							pitching.pa		= int(request.POST.get("pitching_%d_pa"  	%(i+1) , ""))
							pitching.hit	= int(request.POST.get("pitching_%d_hit"	%(i+1) , ""))
							pitching.hr		= int(request.POST.get("pitching_%d_hr" 	%(i+1) , ""))
							pitching.bb		= int(request.POST.get("pitching_%d_bb" 	%(i+1) , ""))
							pitching.k		= int(request.POST.get("pitching_%d_k" 	 	%(i+1) , ""))
							pitching.run	= int(request.POST.get("pitching_%d_run" 	%(i+1) , ""))
							pitching.er		= int(request.POST.get("pitching_%d_er" 	%(i+1) , ""))
							pitching.go		= int(request.POST.get("pitching_%d_go" 	%(i+1) , ""))
							pitching.fo		= int(request.POST.get("pitching_%d_fo" 	%(i+1) , ""))
							
							win	 = request.POST.get("pitching_%d_win"  %(i+1) , "")
							lose = request.POST.get("pitching_%d_lose" %(i+1) , "")
							
							if( win != '' ):
								pitching.win = 1
							else:
								pitching.win = 0

							if( lose != '' ):
								pitching.lose = 1
							else:
								pitching.lose = 0
							 
							pitching.save()
				
					return redirect("/game/"+str(game.id))
				# end of add-game-btn
			# end of preview

					
		context = {'league_list':league_list, 'game': game, 'warning': warning, 'message': message, 'game_record': game_record, 'team': team, 'member_list': member_list, 'batting_list': batting_list, 'pitching_list': pitching_list}
			
		return render(request, 'team/add_game.html', context)

@login_required(login_url='/admin')
def edit_game(request, game_id):

	game = Game.objects.get(id = game_id)
	league_list = League.objects.all()
	member_list = Member.objects.all()
	batting_query  = Batting.objects.filter(game = game)
	pitching_query = Pitching.objects.filter(game = game)

	if request.method != "POST":
		game.date   = unicode(game.date)
		away_name 	= game.away_name.encode('utf8')
		home_name 	= game.home_name.encode('utf8')
		game.away_scores = CommaSeparatedString_to_IntegerArray(game.away_scores)
		game.home_scores = CommaSeparatedString_to_IntegerArray(game.home_scores)
		message 	= ""
		warning 	= ""
		
		record_table = text_to_table(game.record.encode('utf8'))

		if( away_name.upper() == 'RB' ):
			away_table = record_table
			home_table = []
		else:
			away_table = []
			home_table = record_table

		game_record, warning = parse_game_record(away_name, game.away_scores, away_table, \
	                       	                 	 home_name, game.home_scores, home_table)
		
		if( away_name.upper() == 'RB' ):
			team = game_record.away
		else:
			team = game_record.home


		batting_list = []
		for batting in batting_query:
			batting_list.append(batting)

		pitching_list = []
		for pitching in pitching_query:
			pitching_list.append(pitching)

		# add rows for changing pitchers
		N = len(pitching_list)
		for i in range(5 - N):
			pitching_list.append(Pitching())

		context = {'league_list':league_list, 'game': game, 'warning': warning, 'message': message, 'game_record': game_record, 'team': team, 'member_list': member_list, 'batting_list': batting_list, 'pitching_list': pitching_list}
		

		return render(request, 'team/edit_game.html', context)

	else:
		league_id 			= request.POST["league_id"]
		game.league	 		= League.objects.get(id=league_id)
		game.date      		= request.POST["date"]
		game.location  		= request.POST["location"]
		game.record			= request.POST["record_text"]
		game.away_name  	= request.POST["away_name"]
		game.home_name  	= request.POST["home_name"]
		game.away_scores 	= gather_team_scores_from_web(request, 'away')
		game.home_scores 	= gather_team_scores_from_web(request, 'home')
			
		message = ""
		warning = ""
		game_record = None
		team = None
		
		if 'add-new-league-btn' in request.POST:
			print ("add new league!")
			league_name = request.POST["new-league-name"]

			if league_name != None:

				league = League.objects.filter(name = league_name)
				if( league.exists() ):
					warning = "League name %s already exists." %league_name
				else:
					league = League(name=league_name)
					league.save()
					message = 'Add new league: %s' %league_name

			league_list = League.objects.all()
		
		if 'add-new-member-btn' in request.POST:
			print ("add new member!")
			member_name = request.POST["new-member-name"]
			member_number = int(request.POST["new-member-number"])

			if member_name != None:

				member = Member.objects.filter(name = member_name)
				if( member.exists() ):
					warning = "Member %s already exists." %member_name
				else:
					member = Member(name=member_name, number=member_number)
					member.save()
					message = 'Add new member: %s(%d)' %(member_name, member_number)

			member_list = Member.objects.all()

		if ('preview-btn' in request.POST) or ('save-game-btn' in request.POST):

			game.league	 = League.objects.get(id=league_id)
			record_table = text_to_table(game.record.encode('utf8'))

			away_name = game.away_name.encode('utf8')
			home_name = game.home_name.encode('utf8')

			if( away_name.upper() == 'RB' ):
				away_table = record_table
				home_table = []
			else:
				away_table = []
				home_table = record_table

			game_record, warning = parse_game_record(away_name, game.away_scores, away_table, \
	                        	                 	 home_name, game.home_scores, home_table)

			game.away_R	= game_record.away.R
			game.away_H	= game_record.away.H
			game.away_E	= game_record.away.E
			game.home_R	= game_record.home.R
			game.home_H	= game_record.home.H
			game.home_E	= game_record.home.E

			if( warning == "" ):
				message = "Preview record table!"

				game_record, team = extract_single_team_data(game_record, 'RB')


				batting_list = []
				for batter in team.batters:
					batting = Batting()
					for play in batting_query:
						if batter.name.decode('utf8') == play.member.name:
							batting = play
							break

					batting.member  = Member.objects.get(name=batter.name.decode('utf8'))
					batting.game 	= game
					batting.order 	= batter.order
					batting.pa     	= batter.PA
					batting.single	= batter.B1
					batting.double	= batter.B2
					batting.triple	= batter.B3
					batting.hr    	= batter.HR
					batting.rbi   	= batter.RBI
					batting.run   	= batter.RUN
					batting.bb    	= batter.BB
					batting.k     	= batter.K
					batting.sf    	= batter.SF
					batting.field 	= batter.pos

					batting_list.append(batting)

				pitching_list = []
				i = 0
				for pitcher in team.pitchers:
					
					pitching = Pitching()
					for play in pitching_query:
						if pitcher.name.decode('utf8') == play.member.name:
							pitching = play
							break
					
					pitching.member = Member.objects.get(name=pitcher.name.decode('utf8'))
					pitching.game 	= game
					pitching.order 	= i
					pitching.outs   = pitcher.OUT
					pitching.pa     = pitcher.TBF
					pitching.hit   	= pitcher.H
					pitching.hr    	= pitcher.HR
					pitching.bb    	= pitcher.BB
					pitching.k     	= pitcher.K
					pitching.run   	= pitcher.RUN
					pitching.er    	= pitcher.ER
					pitching.go    	= pitcher.GO
					pitching.fo    	= pitcher.FO
					
					pitching_list.append(pitching)
					i += 1

				# add rows for changing pitchers
				N = len(pitching_list)
				for i in range(5 - N):
					pitching_list.append(Pitching())



				if 'save-game-btn' in request.POST:
					
					# create and save new Game object
					game.away_scores = IntegerArray_to_CommaSeparatedString(game.away_scores)
					game.home_scores = IntegerArray_to_CommaSeparatedString(game.home_scores)
					game.save()

					nBatter = len(batting_list)
					for i in range(nBatter):
						batting = batting_list[i]
						member_id = int(request.POST.get("batting_%d_id" %(i+1), ""))

						if( member_id != 0 ):
							batting.member  = Member.objects.get(id = member_id)
							batting.game 	= game
							batting.save()

						
					nPitcher = len(pitching_list)
					for i in range(nPitcher):
						pitching = pitching_list[i]
						member_id = int(request.POST.get("pitching_%d_id" %(i+1), ""))

						if( member_id != 0 ):
							pitching.member = Member.objects.get(id = member_id)
							pitching.game 	= game
							pitching.outs	= int(request.POST.get("pitching_%d_outs"	%(i+1) , ""))
							pitching.pa		= int(request.POST.get("pitching_%d_pa"  	%(i+1) , ""))
							pitching.hit	= int(request.POST.get("pitching_%d_hit"	%(i+1) , ""))
							pitching.hr		= int(request.POST.get("pitching_%d_hr" 	%(i+1) , ""))
							pitching.bb		= int(request.POST.get("pitching_%d_bb" 	%(i+1) , ""))
							pitching.k		= int(request.POST.get("pitching_%d_k" 	 	%(i+1) , ""))
							pitching.run	= int(request.POST.get("pitching_%d_run" 	%(i+1) , ""))
							pitching.er		= int(request.POST.get("pitching_%d_er" 	%(i+1) , ""))
							pitching.go		= int(request.POST.get("pitching_%d_go" 	%(i+1) , ""))
							pitching.fo		= int(request.POST.get("pitching_%d_fo" 	%(i+1) , ""))
							
							win	 = request.POST.get("pitching_%d_win"  %(i+1) , "")
							lose = request.POST.get("pitching_%d_lose" %(i+1) , "")
							
							if( win != '' ):
								pitching.win = 1
							else:
								pitching.win = 0

							if( lose != '' ):
								pitching.lose = 1
							else:
								pitching.lose = 0
							 
							pitching.save()
				
					return redirect("/game/"+str(game.id))

		context = {'league_list':league_list, 'game': game, 'warning': warning, 'message': message, 'game_record': game_record, 'team': team, 'member_list': member_list, 'batting_list': batting_list, 'pitching_list': pitching_list}
			

		return render(request, 'team/edit_game.html', context)