from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse  # para respuestas http
# libreria con configuracion de login
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import Task
from django.utils import timezone 
from django.contrib.auth.decorators import login_required
# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            # register user
            try:
                # register user
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('/tasks')
            # si falla en registrar al usuario en la bbdd debido a condiciones de la bdd entonces capturamos el error para que no se caiga la app
            except:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Count already exists'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Password do not match'
        })

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull=False).order_by('-dateCompleted')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {'form': TaskForm})
    else: 
        try: 
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:            
            return render(request, 'create_task.html', {'form': TaskForm, 'error': 'Please provide a valid data'})

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk = task_id, user= request.user)
        form = TaskForm(instance=task)
        return render(request, 'task.detail.html', {'task': task, 'form': form})
    else: 
        try: 
            task = get_object_or_404(Task, pk= task_id, user=request.user)
            form = TaskForm(request.POST, instance = task) #usamos el mismo form para actualizar
            form.save()
            return redirect('tasks')
        except: 
            return render(request, 'task.detail.html', {'task': task, 'form': form ,'error': 'error updating taks'})
    
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk= task_id, user = request.user)
    if request.method == 'POST':
        task.dateCompleted = timezone.now()
        task.save()
        return redirect('tasks')
    
@login_required 
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk= task_id, user = request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


@login_required
def cerrarSesion(request):
    logout(request)
    return redirect('/')


def ingresar(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {'form': AuthenticationForm, 'error': 'Username or password is incorrect'})
        else:
            login(request, user)  # se genera el login
            return redirect('tasks')
