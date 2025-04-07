from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    has_voted = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.student_id})"

class Position(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    position_type = models.CharField(max_length=50, choices=[
        ('school_prefect', 'School Prefect'),
        ('protocol_prefect', 'Protocol Prefect'),
        ('sports_prefect', 'Sports Prefect'),
        ('entertainment_prefect', 'Entertainment Prefect'),
        ('other', 'Other')
    ], default='other')
    order = models.IntegerField(default=0)  # For ordering positions in the voting process
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order', 'title']

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    # Replace ImageField with CharField for photo URL
    photo_url = models.CharField(max_length=255, blank=True, null=True)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} - {self.position.title}"

class Vote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'position')
        
    def __str__(self):
        return f"{self.student.name} voted for {self.candidate.name} as {self.position.title}"
