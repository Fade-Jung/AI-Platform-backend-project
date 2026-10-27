from django.urls import path
from .views import (
    SignupView, LoginView, #KakaoLoginView,
    ProfileListCreateView, ProfileDetailView
)

urlpatterns = [
# 로그인 인증
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    #path('auth/kakao/', KakaoLoginView.as_view(), name='kakao-login'),

# 프로필 CRUD
    path('profiles/', ProfileListCreateView.as_view(), name='profile-list-create'),
    path('profiles/<int:profile_id>/', ProfileDetailView.as_view(), name='profile-detail')
]