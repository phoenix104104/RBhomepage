from django.contrib import admin
from team.models import Member, League, Game, Batting, Pitching

# Register your models here.

admin.site.register(Member)
admin.site.register(League)
admin.site.register(Game)
admin.site.register(Batting)
admin.site.register(Pitching)