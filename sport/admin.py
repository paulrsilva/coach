from django.contrib import admin
from models import *

class SportDayAdmin(admin.TabularInline):
  model = SportDay
  max_num = 7

class RaceCategoryAdmin(admin.ModelAdmin):
  model = RaceCategory
admin.site.register(RaceCategory, RaceCategoryAdmin)

class SportWeekAdmin(admin.ModelAdmin):
  list_display = ('user', 'week', 'updated')
  list_filter = ('user', )
  inlines = [SportDayAdmin, ]
admin.site.register(SportWeek, SportWeekAdmin)

class GarminActivityAdmin(admin.ModelAdmin):
  list_display = ('name', 'user', 'date', 'sport', 'distance', 'time', 'speed')
  list_filter = ('user', )
admin.site.register(GarminActivity, GarminActivityAdmin)

class SportAdmin(admin.ModelAdmin):
  model = Sport
  list_display = ('name', 'slug', 'parent')
admin.site.register(Sport, SportAdmin)
