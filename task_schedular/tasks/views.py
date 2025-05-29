import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import render
from datetime import timedelta

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Task
import calendar
from .forms import TaskForm
from datetime import datetime
from django.contrib import messages

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def calendar_view(request,year=None, month=None):
    # Get current year and month
    now = timezone.now()
    year = int(year) if year else now.year
    month = int(month) if month else now.month
    

    #calculate previous nd next month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    # Create a calendar object
    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(year, month)
    
    # Get all tasks for the current month
    tasks = Task.objects.filter(
        user=request.user,
        due_date__year=year,
        due_date__month=month
    ).order_by('due_date')
    
    # Organize tasks by day
    tasks_by_day = {}
    for task in tasks:
        day = task.due_date.day
        if day not in tasks_by_day:
            tasks_by_day[day] = []
        tasks_by_day[day].append(task)
    
    # Prepare weekdays header
    weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    
    
    return render(request, 'tasks/calendar.html', {
        'month_days': month_days,
        'year': year,
        'month': month,
        'month_name': now.strftime("%B"),
        'tasks_by_day': tasks_by_day,
        'weekdays': weekdays,
        'today': now.day,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,

    })


@login_required
def week_view(request, year=None, month=None, day=None):
    now = timezone.now()
    year = int(year) if year else now.year
    month = int(month) if month else now.month
    day = int(day) if day else now.day
    
    date = datetime(year, month, day)
    week_days = [date + timedelta(days=i) for i in range(0 - date.weekday(), 7 - date.weekday())]
    
    tasks = Task.objects.filter(
        user=request.user,
        due_date__date__range=[week_days[0], week_days[-1]]
    ).order_by('due_date')
    
    return render(request, 'tasks/week.html', {
        'week_days': week_days,
        'tasks': tasks,
        'current_date': date
    })

@login_required
def day_view(request, year=None, month=None, day=None):
    now = timezone.now()
    year = int(year) if year else now.year
    month = int(month) if month else now.month
    day = int(day) if day else now.day
    
    date = datetime(year, month, day).date()
    
    tasks = Task.objects.filter(
        user=request.user,
        due_date__date=date
    ).order_by('due_date')
    
    return render(request, 'tasks/day.html', {
        'date': date,
        'tasks': tasks
    })



@login_required
@require_POST
def toggle_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    data = json.loads(request.body)
    task.completed = data.get('completed', False)
    task.save()
  
    return JsonResponse({'success': True, 'completed': task.completed})

@login_required
def statistics_view(request):
    tasks = Task.objects.filter(user=request.user)
    completed = tasks.filter(completed=True).count()
    pending = tasks.filter(completed=False).count()
    
    priorities = {
        'High': tasks.filter(priority='H').count(),
        'Medium': tasks.filter(priority='M').count(),
        'Low': tasks.filter(priority='L').count(),
    }
    
    return render(request, 'tasks/statistics.html', {
        'completed': completed,
        'pending': pending,
        'priorities': priorities,
    })

@login_required
def settings_view(request):
    return render(request, 'tasks/settings.html')

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            
            # Debug print to check data before save
            print(f"Creating task with data: {form.cleaned_data}")
            
            task.save()
            messages.success(request, "Task created successfully!")
            return redirect('tasks:task_list')
        else:
            # Print form errors for debugging
            print(f"Form errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")
    else:
        form = TaskForm()
    
    return render(request, 'tasks/create_task.html', {
        'form': form,
        'title': 'Create New Task'
    })

@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect('tasks:task_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/create_task.html', {
        'form': form,
        'title': 'Edit Task'
    })

@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task deleted successfully!")
        return redirect('tasks:task_list')
    return render(request, 'tasks/cornfirm_delete.html', {'task': task})

@login_required
def toggle_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    return redirect('tasks:task_list')