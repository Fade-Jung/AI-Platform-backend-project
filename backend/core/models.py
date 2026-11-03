from django.db import models


# 1. 사용자 테이블 (USERS)
class User(models.Model):
    user_id = models.BigAutoField(primary_key=True, verbose_name="사용자 ID")
    user_email = models.CharField(max_length=255, unique=True, verbose_name="사용자 이메일")
    password_hash = models.CharField(max_length=255, null=True, blank=True, verbose_name="비밀번호 해시")
    name = models.CharField(max_length=100, verbose_name="사용자 이름")
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="전화번호")
    provider = models.CharField(max_length=20, default="email", verbose_name="가입 경로")
    status = models.CharField(max_length=20, default="ACTIVE", verbose_name="계정 상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="계정 생성 일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="계정 수정 일시")

    class Meta:
        db_table = "users"
        verbose_name = "사용자"
        verbose_name_plural = "사용자"

    def __str__(self):
        return f"{self.name} ({self.user_email})"


# 2. 프로필 테이블 (PROFILES)
class Profile(models.Model):
    profile_id = models.BigAutoField(primary_key=True, verbose_name="프로필 ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles", db_column="user_id", verbose_name="사용자 ID")
    profile_name = models.CharField(max_length=100, verbose_name="프로필 이름")
    relationship = models.CharField(max_length=50, verbose_name="관계")
    birth_date = models.DateField(null=True, blank=True, verbose_name="생년월일")
    gender = models.CharField(max_length=10, null=True, blank=True, verbose_name="성별")
    profile_image_url = models.CharField(max_length=500, null=True, blank=True, verbose_name="프로필 이미지 URL")
    is_main = models.BooleanField(default=False, verbose_name="대표 프로필 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정 일시")

    class Meta:
        db_table = "profiles"
        verbose_name = "프로필"
        verbose_name_plural = "프로필"

    def __str__(self):
        return f"{self.profile_name} ({self.relationship})"


# 3. 사용자 설정 테이블 (USER_SETTINGS)
class UserSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, db_column="user_id", related_name="setting", verbose_name="사용자 ID")
    font_size = models.IntegerField(default=16, verbose_name="폰트 크기")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정 일시")

    class Meta:
        db_table = "user_settings"
        verbose_name = "사용자 설정"
        verbose_name_plural = "사용자 설정"


# 4. 건강검진 마스터 테이블 (CHECKUPS)
class Checkup(models.Model):
    checkup_id = models.BigAutoField(primary_key=True, verbose_name="검진 기록 ID")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="checkups", db_column="profile_id", verbose_name="프로필 ID")
    checkup_date = models.DateField(verbose_name="검사 날짜")
    checkup_year = models.IntegerField(verbose_name="검진 연도")
    institution_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="검진 기관명")
    checkup_type = models.CharField(max_length=50, verbose_name="검진 유형")
    status = models.CharField(max_length=20, default="PENDING", verbose_name="확정 상태")
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name="확정 일시")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록 일시")

    class Meta:
        db_table = "checkups"
        verbose_name = "건강검진 마스터"
        verbose_name_plural = "건강검진 마스터"


# 5. 업로드 파일 관리 테이블 (CHECKUP_FILES)
class CheckupFile(models.Model):
    file_id = models.BigAutoField(primary_key=True, verbose_name="파일 ID")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="files", db_column="profile_id", verbose_name="프로필 ID")
    checkup = models.ForeignKey(Checkup, on_delete=models.SET_NULL, null=True, blank=True, related_name="files", db_column="checkup_id", verbose_name="검진 기록 ID")
    original_filename = models.CharField(max_length=255, verbose_name="원본 파일명")
    file_path = models.CharField(max_length=500, verbose_name="파일 저장 경로")
    file_type = models.CharField(max_length=10, verbose_name="파일 확장자")
    file_size = models.IntegerField(verbose_name="파일 용량(Byte)")
    ocr_status = models.CharField(max_length=20, default="PENDING", verbose_name="OCR 분석 상태")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="삭제 처리 일시")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="업로드 일시")

    class Meta:
        db_table = "checkup_files"
        verbose_name = "검진 파일"
        verbose_name_plural = "검진 파일"


# 6. 표준 검사항목 마스터 테이블 (INSPECTION_ITEMS)
class InspectionItem(models.Model):
    item_code = models.CharField(max_length=50, primary_key=True, verbose_name="검사항목 코드")
    item_name = models.CharField(max_length=100, verbose_name="검사항목명")
    standard_unit = models.CharField(max_length=30, null=True, blank=True, verbose_name="표준단위")
    category = models.CharField(max_length=50, null=True, blank=True, verbose_name="검사 분류")

    class Meta:
        db_table = "inspection_items"
        verbose_name = "표준 검사항목"
        verbose_name_plural = "표준 검사항목"

    def __str__(self):
        return f"[{self.item_code}] {self.item_name}"


# 7. 세부 검사 항목 (CHECKUP_DETAILS)
class CheckupDetail(models.Model):
    detail_id = models.BigAutoField(primary_key=True, verbose_name="상세 ID")
    checkup = models.ForeignKey(Checkup, on_delete=models.CASCADE, related_name="details", db_column="checkup_id", verbose_name="검진 기록 ID")
    item = models.ForeignKey(InspectionItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="details", db_column="item_code", verbose_name="검사항목 코드")
    item_name = models.CharField(max_length=100, verbose_name="인식/입력 항목명")
    result_value = models.CharField(max_length=100, verbose_name="결과 문자열")
    numeric_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="수치형 결과값")
    unit = models.CharField(max_length=30, null=True, blank=True, verbose_name="측정 단위")
    reference_range = models.CharField(max_length=100, null=True, blank=True, verbose_name="참고 범위")
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="OCR 신뢰도(%)")
    is_modified = models.BooleanField(default=False, verbose_name="수정 여부")
    is_comparable = models.BooleanField(default=True, verbose_name="과거 비교 가능 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")

    class Meta:
        db_table = "checkup_details"
        verbose_name = "검진 세부 결과"
        verbose_name_plural = "검진 세부 결과"


# 8. AI 분석 결과 (AI_ANALYSES)
class AiAnalysis(models.Model):
    analysis_id = models.BigAutoField(primary_key=True, verbose_name="분석 ID")
    checkup = models.OneToOneField(Checkup, on_delete=models.CASCADE, related_name="ai_analysis", db_column="checkup_id", verbose_name="검진 기록 ID")
    summary_text = models.TextField(verbose_name="AI 종합 설명")
    trend_analysis_text = models.TextField(null=True, blank=True, verbose_name="주요 변화 요약")
    safety_disclaimer = models.CharField(max_length=500, verbose_name="안전 안내 문구")
    status = models.CharField(max_length=20, default="GENERATED", verbose_name="생성 상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")

    class Meta:
        db_table = "ai_analyses"
        verbose_name = "AI 종합 분석"
        verbose_name_plural = "AI 종합 분석"


# 9. AI 진료 추천 질문 (AI_CONSULTATION_QUESTIONS)
class AiConsultationQuestion(models.Model):
    question_id = models.BigAutoField(primary_key=True, verbose_name="질문 ID")
    checkup = models.ForeignKey(Checkup, on_delete=models.CASCADE, related_name="questions", db_column="checkup_id", verbose_name="검진 기록 ID")
    question_text = models.TextField(verbose_name="추천 질문 내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")

    class Meta:
        db_table = "ai_consultation_questions"
        verbose_name = "AI 진료 추천 질문"
        verbose_name_plural = "AI 진료 추천 질문"


# 10. 표준 질병 정보 (DISEASE_CODES)
class DiseaseCode(models.Model):
    disease_code = models.CharField(max_length=20, primary_key=True, verbose_name="질병코드(KCD)")
    disease_name_ko = models.CharField(max_length=150, verbose_name="질병명(한글)")
    disease_name_en = models.CharField(max_length=150, null=True, blank=True, verbose_name="질병명(영문)")
    category = models.CharField(max_length=100, null=True, blank=True, verbose_name="질병 대분류")

    class Meta:
        db_table = "disease_codes"
        verbose_name = "표준 질병 코드"
        verbose_name_plural = "표준 질병 코드"


# 11. 공공 의약품 마스터 (MEDICATIONS)
class Medication(models.Model):
    item_seq = models.CharField(max_length=50, primary_key=True, verbose_name="품목기준코드")
    item_name = models.CharField(max_length=200, verbose_name="약품명")
    entp_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="제약사명")
    efcy_qesitm = models.TextField(null=True, blank=True, verbose_name="효능 및 효과")
    use_method_qesitm = models.TextField(null=True, blank=True, verbose_name="용법 및 용량")
    atpn_qesitm = models.TextField(null=True, blank=True, verbose_name="주의사항")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록 일시")

    class Meta:
        db_table = "medications"
        verbose_name = "의약품 마스터"
        verbose_name_plural = "의약품 마스터"


# 12. 검사항목 - 질병 매핑 (CHECKUP_DISEASE_REL)
class CheckupDiseaseRel(models.Model):
    rel_id = models.BigAutoField(primary_key=True, verbose_name="매핑 ID")
    inspection_item = models.ForeignKey(InspectionItem, on_delete=models.CASCADE, db_column="item_code", verbose_name="검사항목 코드")
    disease_code = models.ForeignKey(DiseaseCode, on_delete=models.CASCADE, db_column="disease_code", verbose_name="질병 코드")
    risk_condition = models.CharField(max_length=20, null=True, blank=True, verbose_name="위험 조건")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")

    class Meta:
        db_table = "checkup_disease_rel"
        verbose_name = "검사항목-질병 매핑"
        verbose_name_plural = "검사항목-질병 매핑"


# 13. 검사항목 - 의약품 매핑 (CHECKUP_MEDICATION_REL)
class CheckupMedicationRel(models.Model):
    rel_id = models.BigAutoField(primary_key=True, verbose_name="매핑 ID")
    inspection_item = models.ForeignKey(InspectionItem, on_delete=models.CASCADE, db_column="item_code", verbose_name="검사항목 코드")
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, db_column="item_seq", verbose_name="품목기준코드")
    recommendation_type = models.CharField(max_length=20, null=True, blank=True, verbose_name="추천/주의 유형")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 일시")

    class Meta:
        db_table = "checkup_medication_rel"
        verbose_name = "검사항목-의약품 매핑"
        verbose_name_plural = "검사항목-의약품 매핑"


# 14. 사용자 복용약 관리 (PROFILE_MEDICATIONS)
class ProfileMedication(models.Model):
    user_med_id = models.BigAutoField(primary_key=True, verbose_name="사용자 복용약 ID")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="medications", db_column="profile_id", verbose_name="프로필 ID")
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, db_column="item_seq", verbose_name="품목기준코드")
    prescription_date = models.DateField(null=True, blank=True, verbose_name="처방일/복용시작일")
    is_taking = models.BooleanField(default=True, verbose_name="현재 복용 여부")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록 일시")

    class Meta:
        db_table = "profile_medications"
        verbose_name = "사용자 복용약 기록"
        verbose_name_plural = "사용자 복용약 기록"

# 15. 처리된 이벤트 (중복 처리 방지 관리)
class ProcessedEvent(models.Model):
    event_id = models.CharField(max_length=100, primary_key=True, verbose_name="이벤트 ID")
    processed_at = models.DateTimeField(auto_now_add=True, verbose_name="처리 일시")

    class Meta:
        db_table = "processed_events"
        verbose_name = "처리된 이벤트"

# 16. 문진 마스터

class Survey(models.Model):
    survey_id = models.BigAutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="surveys", db_column="profile_id")
    survey_version = models.IntegerField(verbose_name="문진 버전")
    session_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="문진 세션 ID")
    content_json = models.JSONField(default=dict, verbose_name="일반 문진 답변")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "surveys"
        unique_together = (("profile", "survey_version"),)
        verbose_name = "문진 기록"

# 17. 문진 민감 이력 (질환·약물·메모 - 보안 접근 제한)

class SurveyHistory(models.Model):
    history_id = models.BigAutoField(primary_key=True)
    survey = models.OneToOneField(Survey, on_delete=models.CASCADE, related_name="sensitive_history", db_column="survey_id")
    diseases_info = models.TextField(null=True, blank=True, verbose_name="과거 질환 정보")
    medications_info = models.TextField(null=True, blank=True, verbose_name="복용 약물 정보")
    memo = models.TextField(null=True, blank=True, verbose_name="특이사항 메모")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "survey_histories"
        verbose_name = "문진 민감 이력"

# 18. 건강 관리 계획

class Plan(models.Model):
    plan_id = models.CharField(max_length=100, verbose_name="계획 ID")
    version = models.IntegerField(verbose_name="계획 버전")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="plans", db_column="profile_id")
    plan_data = models.JSONField(default=dict, verbose_name="계획 상세 내용")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "plans"
        unique_together = (('plan_id', 'version'),)
        verbose_name = "건강 관리 계획"

# 19. 계획 실천 기록 (일별 기록)
class PlanLog(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    plan_id = models.CharField(max_length=100, verbose_name="계획 ID")
    date = models.DateField(verbose_name="실천 날짜")
    status = models.CharField(max_length=20, default="PENDING", verbose_name="실천 상태")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "plan_logs"
        unique_together = (('plan_id', 'date'),)
        verbose_name = "실천 기록"

# 20. 계획 달성도 (시점별 보존)
class PlanProgress(models.Model):
    progress_id = models.BigAutoField(primary_key=True)
    plan_id = models.CharField(max_length=100, verbose_name="계획 ID")
    version = models.IntegerField(verbose_name="계획 버전")
    as_of = models.DateTimeField(verbose_name="달성도 집계 시점")
    progress_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="달성률(%)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "plan_progresses"
        verbose_name = "계획 달성도"