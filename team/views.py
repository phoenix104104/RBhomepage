# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as log_account , logout as out_account
from django.contrib.auth.models import User
from models import Member, Game

def index(request):
	player = Member.objects.all()
	if request.user.is_authenticated:
		print "authenticated user"
	if request.user.username:
		print "username = " + request.user.username
	else:
		print "none"
	context = {'player': player}
	return render(request, 'team/index.html', context)


    
def login(request):
	
	if request.method != 'POST':
		return redirect("/")
	else:
		name = request.POST.get("id")
		password = request.POST.get("password")
		user = authenticate(username = name , password = password)
		if user is not None:
			if user.is_active:
				print name + " login!"
				log_account(request,user)
				return index(request)
			else:
				print "User not exist!"
		else:
			return redirect("/")


def logout(request):

	out_account(request)
	return index(request)
