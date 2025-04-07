from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Position, Candidate, Vote, Student

@login_required(login_url='admin_login')
def admin_dashboard(request):
    """Admin dashboard showing all positions and voting statistics"""
    positions = Position.objects.all()
    total_students = Student.objects.count()
    voted_students = Student.objects.filter(has_voted=True).count()
    
    # Calculate voting percentage
    voting_percentage = (voted_students / total_students * 100) if total_students > 0 else 0
    
    context = {
        'positions': positions,
        'total_students': total_students,
        'voted_students': voted_students,
        'voting_percentage': voting_percentage,
    }
    return render(request, 'polls/admin/dashboard.html', context)

@login_required(login_url='admin_login')
def position_details(request, position_id):
    """Detailed view for a specific position"""
    position = get_object_or_404(Position, id=position_id)
    candidates = Candidate.objects.filter(position=position)
    votes = Vote.objects.filter(position=position)
    
    # Get students who voted for this position
    students_voted = Student.objects.filter(vote__position=position).distinct()
    
    context = {
        'position': position,
        'candidates': candidates,
        'votes': votes,
        'students_voted': students_voted,
    }
    
    return render(request, 'polls/admin/position_details.html', context)

def admin_login(request):
    """Admin login view"""
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'polls/admin/login.html')

@login_required(login_url='admin_login')
def admin_logout(request):
    """Admin logout view"""
    logout(request)
    return redirect('admin_login')