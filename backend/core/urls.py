from django.urls import path
from .views import (
    SignupView, LoginView, #KakaoLoginView,
    ProfileListCreateView, ProfileDetailView,
    CheckupFileUploadView,
    TimeSeriesAnalysisView,
    StateChangesReceiveView,
    SensitiveSurveyHistoryView
)

urlpatterns = [
# 로그인 인증
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    #path('auth/kakao/', KakaoLoginView.as_view(), name='kakao-login'),

# 프로필 CRUD
    path('profiles/', ProfileListCreateView.as_view(), name='profile-list-create'),
    path('profiles/<int:profile_id>/', ProfileDetailView.as_view(), name='profile-detail'),

# OCR / 검진표 업로드 API 추가
    path('checkups/upload/', CheckupFileUploadView.as_view(), name='checkup-file-upload'),

# 시계열 분석 API 추가
    path('profiles/<int:profile_id>/trends/', TimeSeriesAnalysisView.as_view(), name='profile-trends'),

# state_changes 상태 연동 및 민감정보 보안 조회 API
    path('state-changes/', StateChangesReceiveView.as_view(), name='state-changes-receive'),
    path('surveys/<int:survey_id>/sensitive-history/', SensitiveSurveyHistoryView.as_view(), name='sensitive-survey-history'),
]