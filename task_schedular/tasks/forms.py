# forms.py
from django import forms
from .models import Task
from django.utils import timezone

class TaskForm(forms.ModelForm):
    PRIORITY_CHOICES = [
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    ]
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'priority-radio'}),
        initial='M'
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date', 
                 'notification_minutes_before', 'sync_with_google',
                 'ai_suggested_deadline']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter task description...'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter task title...'}),
            'notification_minutes_before': forms.NumberInput(attrs={'min': 5, 'max': 1440}),
        }
        labels = {
            'sync_with_google': 'Sync with Google Calendar',
            'ai_suggested_deadline': 'Suggest deadline with AI'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].input_formats = ['%Y-%m-%dT%H:%M']