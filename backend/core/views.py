from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User , Profile
from .serializers import UserSignupSerializer , ProfileSerializer

# 1. 회원가입 API
class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "회원가입이 성공적으로 완료되었습니다.",
                "user_id": user.user_id,
                "email": user.user_email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2. 로그인 API (JWT 토큰 발급)
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('user_email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "이메일과 비밀번호를 모두 입력해 주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_email=email)
        except User.DoesNotExist:
            return Response({"error": "존재하지 않는 이메일 계정입니다."}, status=status.HTTP_401_UNAUTHORIZED)

        # 비밀번호 검증
        if not check_password(password, user.password_hash):
            return Response({"error": "비밀번호가 일치하지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        # JWT 토큰 생성 (USER_ID_FIELD 설정 반영)
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.user_email

        return Response({
            "message": "로그인 성공",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "user_id": user.user_id,
                "email": user.user_email,
                "name": user.name
            }
        }, status=status.HTTP_200_OK)

# 3. 프로필 목록 조회 및 생성 (GET / POST)
class ProfileListCreateView(ListCreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]  # JWT 토큰 인증 필수

    def get_queryset(self):
        # 현재 로그인된 사용자의 프로필만 반환
        return Profile.objects.filter(user=self.request.user).order_by('-is_main', 'profile_id')


# 4. 프로필 상세 조회, 수정, 삭제 (GET / PUT / PATCH / DELETE)
class ProfileDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'profile_id'

    def get_queryset(self):
        # 본인의 프로필에만 접근 가능
        return Profile.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # 대표 프로필은 삭제 불가능하도록 검증
        if instance.is_main:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"error": "대표 프로필은 삭제할 수 없습니다. 다른 프로필을 대표로 지정 후 삭제해 주세요."})
        instance.delete()