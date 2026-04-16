from urllib import request

from django.shortcuts import render, redirect
from MainApp.models import Topic
from .forms import EntryForm, TopicForm
from .models import Entry, Topic
from django.contrib.auth.decorators import login_required
from django.http import Http404

# Create your views here.

def index(request):
    """The home page for Learning Log."""
    return render(request, 'mainapp/index.html')

@login_required
def topics(request):
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'mainapp/topics.html', context)

@login_required
def topic(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    if topic.owner != request.user:
        raise Http404()
    
    entries = Entry.objects.filter(topic=topic).order_by('-date_added')
    context = {'topic': topic, 'entries': entries}

    return render(request, 'mainapp/topic.html', context)

@login_required
def new_topic(request):
    """Add a new topic."""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TopicForm()
    else:
        # POST data submitted; process data.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('mainapp:topics')

    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'mainapp/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Add a new entry for a particular topic."""
    topic = Topic.objects.get(id=topic_id)

    if topic.owner != request.user:
        raise Http404()
    
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = EntryForm()
    else:
        # POST data submitted; process data.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            form.save()
            return redirect('mainapp:topic', topic_id=topic_id)

    # Display a blank or invalid form.
    context = {'topic': topic, 'form': form}
    return render(request, 'mainapp/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry.
        form = EntryForm(instance=entry)
    else:
        # POST data submitted; process data.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('mainapp:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'mainapp/edit_entry.html', context)