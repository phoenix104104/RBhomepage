# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from models import Member, Game

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
