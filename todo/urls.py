from django.urls import path
from .views import AIAdvisorView 

urlpatterns = [
    # Khalli ken hadhi, ma3adech testa3mel 'index'
    path('ai-advisor/', AIAdvisorView.as_view(), name='ai_advisor_todo'),
]