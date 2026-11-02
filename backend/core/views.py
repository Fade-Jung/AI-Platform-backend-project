from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from .models import Checkup, CheckupFile, CheckupDetail, User, Profile
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

class CheckupFileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        profile_id = request.data.get('profile_id')
        file_obj = request.FILES.get('file')

        if not profile_id or not file_obj:
            return Response({"error": "profile_id와 file을 모두 제공해 주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 프로필 소유권 확인
        try:
            profile = Profile.objects.get(profile_id=profile_id, user=request.user)
        except Profile.DoesNotExist:
            return Response({"error": "존재하지 않거나 접근 권한이 없는 프로필입니다."}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            # 2. Checkup (검진 마스터) 생성
            checkup = Checkup.objects.create(
                profile=profile,
                checkup_date="2026-01-01",  # OCR 인식 결과로 갱신 예정
                checkup_year=2026,
                checkup_type="일반검진",
                status="PENDING"
            )

            # 3. CheckupFile (업로드 파일) 저장
            # (실제 환경에 맞춰 MediaStorage나 S3 경로를 세팅 가능)
            checkup_file = CheckupFile.objects.create(
                profile=profile,
                checkup=checkup,
                original_filename=file_obj.name,
                file_path=f"uploads/{file_obj.name}",
                file_type=file_obj.name.split('.')[-1].lower(),
                file_size=file_obj.size,
                ocr_status="PROCESSING"
            )

            # 4. OCR 파싱 로직 실행 (실제 API 호출 함수 연결 지점)
            parsed_results = self.run_ocr_parser(file_obj)

            # 5. CheckupDetail (세부 결과) DB 저장
            detail_objects = []
            for item in parsed_results:
                detail_objects.append(
                    CheckupDetail(
                        checkup=checkup,
                        item_name=item['item_name'],
                        result_value=str(item['result_value']),
                        numeric_value=item.get('numeric_value'),
                        unit=item.get('unit', ''),
                        reference_range=item.get('reference_range', ''),
                        confidence_score=item.get('confidence_score', 95.00)
                    )
                )
            CheckupDetail.objects.bulk_create(detail_objects)

            # 6. OCR 상태 완료 처리
            checkup_file.ocr_status = "COMPLETED"
            checkup_file.save()

        return Response({
            "message": "검진표 파일 업로드 및 OCR 분석이 완료되었습니다.",
            "checkup_id": checkup.checkup_id,
            "file_id": checkup_file.file_id,
            "parsed_details_count": len(parsed_results)
        }, status=status.HTTP_201_CREATED)

    def run_ocr_parser(self, file_obj):
        """
        [OCR 파이프라인 지점]
        Google Cloud Vision 등에 파일 바이트를 전달하고
        파싱된 검사 항목과 수치를 리스트로 반환하는 메서드
        """
        # TODO: 실제 OCR SDK / REST API 연동 코드 위치
        # 테스트를 위한 Mock 데이터 예시
        return [
            {"item_name": "공복혈당", "result_value": "105", "numeric_value": 105.00, "unit": "mg/dL", "reference_range": "70~99"},
            {"item_name": "수축기혈압", "result_value": "128", "numeric_value": 128.00, "unit": "mmHg", "reference_range": "120 미만"},
            {"item_name": "이완기혈압", "result_value": "82", "numeric_value": 82.00, "unit": "mmHg", "reference_range": "80 미만"},
            {"item_name": "혈중 콜레스테롤", "result_value": "210", "numeric_value": 210.00, "unit": "mg/dL", "reference_range": "200 이하"},
        ]