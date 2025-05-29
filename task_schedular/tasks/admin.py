from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'due_date', 'completed')
    list_filter = ('priority', 'completed', 'user')
    search_fields = ('title', 'description')
    date_hierarchy = 'due_date'