from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student, Position, Candidate, Vote
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.utils import timezone

def login_view(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        try:
            student = Student.objects.get(student_id=student_id)
            if student.has_voted:
                messages.error(request, "You have already voted!")
                return render(request, 'polls/login.html')
            
            request.session['student_id'] = student.id
            request.session['student_name'] = student.name
            return redirect('position_selection')
        except Student.DoesNotExist:
            messages.error(request, "Invalid Student ID")
    
    return render(request, 'polls/login.html')

def position_selection(request):
    if 'student_id' not in request.session:
        return redirect('login')
    
    student = Student.objects.get(id=request.session['student_id'])
    positions = Position.objects.all()
    
    # Get positions the student has already voted for
    voted_positions = Vote.objects.filter(student=student).values_list('position_id', flat=True)
    
    # Get the next position to vote for
    next_position = None
    for position in positions:
        if position.id not in voted_positions:
            next_position = position
            break
    
    # Check if student has voted for all positions
    all_voted = (len(voted_positions) == positions.count())
    
    context = {
        'student': student,
        'positions': positions,
        'next_position': next_position,
        'voted_positions': voted_positions,
        'all_voted': all_voted
    }
    
    return render(request, 'polls/position_selection.html', context)

def voting(request, position_id):
    if 'student_id' not in request.session:
        return redirect('login')
    
    student = Student.objects.get(id=request.session['student_id'])
    position = get_object_or_404(Position, id=position_id)
    candidates = Candidate.objects.filter(position=position)
    
    # Add position type class for styling
    position_class = f"position-{position.position_type}"
    
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        if candidate_id:
            candidate = Candidate.objects.get(id=candidate_id)
            
            # Check if student has already voted for this position
            if Vote.objects.filter(student=student, position=position).exists():
                messages.error(request, "You have already voted for this position!")
                return redirect('position_selection')
            
            # Create vote
            Vote.objects.create(student=student, position=position, candidate=candidate)
            
            # Increment candidate votes
            candidate.votes += 1
            candidate.save()
            
            messages.success(request, f"You have successfully voted for {candidate.name} as {position.title}")
            
            # Find next position to vote for
            positions = Position.objects.all()
            voted_positions = Vote.objects.filter(student=student).values_list('position_id', flat=True)
            
            next_position = None
            for pos in positions:
                if pos.id not in voted_positions:
                    next_position = pos
                    break
            
            if next_position:
                return redirect('voting', position_id=next_position.id)
            else:
                return redirect('position_selection')
    
    context = {
        'student': student,
        'position': position,
        'candidates': candidates,
        'position_class': position_class
    }
    
    return render(request, 'polls/voting.html', context)

def complete_voting(request):
    if 'student_id' not in request.session:
        return redirect('login')
    
    student = Student.objects.get(id=request.session['student_id'])
    positions = Position.objects.all()
    
    # Check if student has voted for all positions
    voted_positions = Vote.objects.filter(student=student).values_list('position_id', flat=True)
    if len(voted_positions) < positions.count():
        messages.error(request, "Please vote for all positions before completing.")
        return redirect('position_selection')
    
    # Mark student as having voted
    student.has_voted = True
    student.save()
    
    # Get all votes by this student for display
    votes = Vote.objects.filter(student=student).select_related('position', 'candidate')
    
    # Get current time for display
    from django.utils import timezone
    voting_time = timezone.now()
    
    # Clear session
    del request.session['student_id']
    if 'student_name' in request.session:
        del request.session['student_name']
    
    context = {
        'student': student,
        'votes': votes,
        'voting_time': voting_time
    }
    
    messages.success(request, "Thank you for voting!")
    return render(request, 'polls/thank_you.html', context)

def logout_view(request):
    if 'student_id' in request.session:
        del request.session['student_id']
    if 'student_name' in request.session:
        del request.session['student_name']
    
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@csrf_exempt
def get_results(request):
    positions = Position.objects.all()
    results = []
    
    for position in positions:
        candidates = Candidate.objects.filter(position=position)
        position_data = {
            'position': position.title,
            'position_type': position.position_type,
            'candidates': [{'name': c.name, 'votes': c.votes} for c in candidates]
        }
        results.append(position_data)
    
    return JsonResponse(results, safe=False)


@user_passes_test(lambda u: u.is_staff)
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


def voting_results_login(request):
    """Login page for viewing voting results"""
    if request.method == 'POST':
        password = request.POST.get('password')
        # Use a simple password check - in production, use a more secure approach
        if password == 'admin123':  # Replace with your desired password
            request.session['results_authorized'] = True
            return redirect('voting_results')
        else:
            messages.error(request, "Invalid password")
    
    return render(request, 'polls/results_login.html')

def voting_results(request):
    """Display voting results if authorized"""
    if not request.session.get('results_authorized', False):
        return redirect('voting_results_login')
    
    # Force database refresh by using select_related to optimize queries
    positions = Position.objects.all().order_by('order', 'title').select_related()
    results_data = []
    
    # Get fresh counts from database
    total_students = Student.objects.count()
    voted_students = Student.objects.filter(has_voted=True).count()
    voting_percentage = (voted_students / total_students * 100) if total_students > 0 else 0
    
    for position in positions:
        # Force refresh of candidates data
        candidates = Candidate.objects.filter(position=position).order_by('-votes')
        total_votes = sum(candidate.votes for candidate in candidates)
        
        candidates_data = []
        for candidate in candidates:
            vote_percentage = (candidate.votes / total_votes * 100) if total_votes > 0 else 0
            candidates_data.append({
                'name': candidate.name,
                'votes': candidate.votes,
                'percentage': vote_percentage,
            })
        
        results_data.append({
            'position': position,
            'candidates': candidates_data,
            'total_votes': total_votes,
        })
    
    context = {
        'results_data': results_data,
        'total_students': total_students,
        'voted_students': voted_students,
        'voting_percentage': voting_percentage,
    }
    
    # Add a timestamp to prevent browser caching
    from django.utils import timezone
    context['timestamp'] = timezone.now().timestamp()
    
    return render(request, 'polls/voting_results.html', context)

def logout_results(request):
    """Logout from results view"""
    if 'results_authorized' in request.session:
        del request.session['results_authorized']
    
    return redirect('voting_results_login')


@require_POST
@user_passes_test(lambda u: u.is_staff)
def reset_votes(request):
    """Reset all votes to zero"""
    try:
        with transaction.atomic():
            # Reset candidate votes
            Candidate.objects.all().update(votes=0)
            
            # Delete all vote records
            Vote.objects.all().delete()
            
            # Reset student voting status
            Student.objects.all().update(has_voted=False)
            
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def download_results_pdf(request):
    """Generate and download a PDF of voting results"""
    if not request.session.get('results_authorized', False):
        return redirect('voting_results_login')
    
    # Get the same data as in the voting_results view
    positions = Position.objects.all().order_by('order', 'title')
    results_data = []
    
    total_students = Student.objects.count()
    voted_students = Student.objects.filter(has_voted=True).count()
    voting_percentage = (voted_students / total_students * 100) if total_students > 0 else 0
    
    for position in positions:
        candidates = Candidate.objects.filter(position=position).order_by('-votes')
        total_votes = sum(candidate.votes for candidate in candidates)
        
        candidates_data = []
        for candidate in candidates:
            vote_percentage = (candidate.votes / total_votes * 100) if total_votes > 0 else 0
            candidates_data.append({
                'name': candidate.name,
                'votes': candidate.votes,
                'percentage': vote_percentage,
            })
        
        results_data.append({
            'position': position,
            'candidates': candidates_data,
            'total_votes': total_votes,
        })
    
    # Current date and time for the report
    now = timezone.now()
    
    # Prepare context for the template
    context = {
        'results_data': results_data,
        'total_students': total_students,
        'voted_students': voted_students,
        'voting_percentage': voting_percentage,
        'generated_date': now.strftime('%B %d, %Y'),
        'generated_time': now.strftime('%I:%M %p'),
    }
    
    # Render the template
    template = get_template('polls/pdf/results_pdf.html')
    html = template.render(context)
    
    # Create a PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    # Return the PDF as a download
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="voting_results_{now.strftime("%Y%m%d_%H%M")}.pdf"'
        return response
    
    return HttpResponse("Error generating PDF", status=400)
