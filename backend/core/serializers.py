from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Profile


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['user_email', 'password', 'name', 'phone_number', 'provider']

    def create(self, validated_data):
        # 비밀번호 해시 암호화 저장
        raw_password = validated_data.pop('password')
        validated_data['password_hash'] = make_password(raw_password)

        user = User.objects.create(**validated_data)

        # 회원가입 시 기본 본인 프로필 자동 생성
        Profile.objects.create(
            user=user,
            profile_name=user.name,
            relationship="본인",
            is_main=True
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'profile_id', 'profile_name', 'relationship',
            'birth_date', 'gender', 'profile_image_url',
            'is_main', 'created_at', 'updated_at'
        ]
        read_only_fields = ['profile_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # API 요청을 보낸 로그인 유저 정보 자동 매핑
        user = self.context['request'].user

        # 새 프로필이 대표 프로필(is_main=True)로 설정될 경우, 기존 대표 프로필 해제
        if validated_data.get('is_main', False):
            Profile.objects.filter(user=user, is_main=True).update(is_main=False)

        return Profile.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # 수정 시 대표 프로필(is_main=True)로 변경되면 기존 대표 프로필 해제
        if validated_data.get('is_main', False) and not instance.is_main:
            Profile.objects.filter(user=user, is_main=True).update(is_main=False)

        return super().update(instance, validated_data)