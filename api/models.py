from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    domain = models.CharField(max_length=100, default='Full Stack')
    experience_level = models.CharField(max_length=50, default='Undergraduate') # Undergraduate, Postgraduate, PhD
    job_readiness_score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class QuizSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    round_number = models.IntegerField() # 1, 2, 3
    domain = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=50) # Easy, Medium, Hard
    accuracy = models.FloatField(default=0.0)
    correct_count = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Round {self.round_number} - {self.user.username}"

class Question(models.Model):
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    options = models.JSONField(blank=True, null=True) # For MCQs
    question_type = models.CharField(max_length=20, default='text') # mcq, text, code
    correct_answer = models.TextField()
    explanation = models.TextField(blank=True, null=True)
    user_answer = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    ai_feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Question for Session {self.session.id}"

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class JobRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_recommendations')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    link = models.URLField()
    eligibility = models.CharField(max_length=50, default='Needs Improvement') # Eligible, Needs Improvement
    skills_matched = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company}"
