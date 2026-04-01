from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import UserProfile, QuizSession, Question, Task, JobRecommendation
from .serializers import UserSerializer, UserProfileSerializer, QuizSessionSerializer, QuestionSerializer, TaskSerializer, JobRecommendationSerializer
from .ai_service import generate_interview_questions, evaluate_interview_answer
from .job_service import get_job_recommendations

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class QuizSessionViewSet(viewsets.ModelViewSet):
    queryset = QuizSession.objects.all()
    serializer_class = QuizSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        round_number = int(request.data.get('round_number', 1))
        domain = request.data.get('domain', 'Full Stack')

        if round_number == 1:
            difficulty = 'Easy + Medium'
            count = 6
        elif round_number == 2:
            difficulty = 'Medium + Hard'
            count = 8
        else:
            difficulty = 'Hard'
            count = 10

        # Check unlock conditions
        if round_number == 2:
            prev_round = QuizSession.objects.filter(user=request.user, round_number=1, accuracy__gte=60).exists()
            if not prev_round:
                return Response({"error": "Round 2 is locked. Reach 60% accuracy in Round 1 to unlock."}, status=status.HTTP_403_FORBIDDEN)
        if round_number == 3:
            prev_round = QuizSession.objects.filter(user=request.user, round_number=2, accuracy__gte=70).exists()
            if not prev_round:
                return Response({"error": "Round 3 is locked. Reach 70% accuracy in Round 2 to unlock."}, status=status.HTTP_403_FORBIDDEN)

        # Generate questions via AI
        ai_questions = generate_interview_questions(domain, difficulty, count)
        if not ai_questions:
            return Response({"error": "Failed to generate questions. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        session = QuizSession.objects.create(
            user=request.user,
            round_number=round_number,
            domain=domain,
            difficulty=difficulty,
            total_questions=len(ai_questions)
        )

        for q in ai_questions:
            Question.objects.create(
                session=session,
                text=q.get('text'),
                options=q.get('options'),
                question_type=q.get('question_type'),
                correct_answer=q.get('correct_answer'),
                explanation=q.get('explanation')
            )

        serializer = self.get_serializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        session = self.get_object()
        answers = request.data.get('answers', []) # List of {question_id, user_answer}
        
        correct_count = 0
        for ans in answers:
            try:
                question = Question.objects.get(id=ans.get('question_id'), session=session)
                user_answer = ans.get('user_answer')
                
                # Evaluation logic
                evaluation = evaluate_interview_answer(question.text, question.correct_answer, user_answer)
                
                question.user_answer = user_answer
                question.is_correct = evaluation.get('is_correct', False)
                question.ai_feedback = evaluation.get('ai_feedback', '')
                question.save()

                if question.is_correct:
                    correct_count += 1
            except:
                continue
        
        session.correct_count = correct_count
        session.accuracy = (correct_count / session.total_questions) * 100 if session.total_questions > 0 else 0
        session.save()

        # Update job readiness score using average accuracy across completed sessions
        profile = request.user.profile
        avg_accuracy = QuizSession.objects.filter(user=request.user).aggregate(avg_accuracy=Avg('accuracy'))['avg_accuracy'] or 0
        profile.job_readiness_score = int(avg_accuracy)
        profile.save()

        serializer = self.get_serializer(session)
        return Response(serializer.data)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class JobRecommendationViewSet(viewsets.ModelViewSet):
    queryset = JobRecommendation.objects.all()
    serializer_class = JobRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def refresh(self, request):
        domain = request.query_params.get('domain') or request.user.profile.domain
        avg_accuracy = QuizSession.objects.filter(user=request.user).aggregate(avg_accuracy=Avg('accuracy'))['avg_accuracy'] or 0
        
        jobs = get_job_recommendations(domain, avg_accuracy)
        
        # Clear old and save new
        JobRecommendation.objects.filter(user=request.user).delete()
        for job in jobs:
            JobRecommendation.objects.create(
                user=request.user,
                title=job.get('title'),
                company=job.get('company'),
                link=job.get('link'),
                eligibility=job.get('eligibility'),
                skills_matched=job.get('skills_matched')
            )
            
        return Response(self.get_serializer(JobRecommendation.objects.filter(user=request.user), many=True).data)

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        sessions = QuizSession.objects.filter(user=request.user).order_by('completed_at')
        
        line_chart = [{"date": s.completed_at.strftime("%Y-%m-%d"), "accuracy": s.accuracy} for s in sessions]
        pie_chart = [
            {"name": "Easy", "value": sessions.filter(difficulty__icontains='Easy').count()},
            {"name": "Medium", "value": sessions.filter(difficulty__icontains='Medium').count()},
            {"name": "Hard", "value": sessions.filter(difficulty__icontains='Hard').count()},
        ]
        topic_accuracy = []
        for domain in sessions.values_list('domain', flat=True).distinct():
            avg_accuracy_by_domain = sessions.filter(domain=domain).aggregate(avg_accuracy=Avg('accuracy'))['avg_accuracy'] or 0
            topic_accuracy.append({"topic": domain, "accuracy": avg_accuracy_by_domain})

        return Response({
            "line_chart": line_chart,
            "pie_chart": pie_chart,
            "topic_accuracy": topic_accuracy,
            "total_attempted": sessions.count(),
            "avg_accuracy": sessions.aggregate(avg_accuracy=Avg('accuracy'))['avg_accuracy'] or 0
        })
