from decimal import Decimal
from django.db.models import F
from .models import CheckupDetail, Profile


class TimeSeriesAnalysisService:
    @staticmethod
    def calculate_profile_trends(profile_id: int, item_name: str = None):
        """
        특정 프로필의 과거 검진 기록 수치 변화를 시계열로 계산하는 엔진
        """
        # 1. 프로필의 확정 완료 또는 분석 가능한 검진 상세 기록 조회 (날짜 오름차순)
        details = CheckupDetail.objects.filter(
            checkup__profile_id=profile_id,
            numeric_value__isnull=False,
            is_comparable=True
        ).select_related('checkup').order_by('checkup__checkup_date', 'created_at')

        if item_name:
            details = details.filter(item_name=item_name)

        # 2. 검사항목별로 수치 시계열 그룹화
        trend_data = {}

        for detail in details:
            name = detail.item_name
            if name not in trend_data:
                trend_data[name] = []

            trend_data[name].append({
                'detail_id': detail.detail_id,
                'checkup_id': detail.checkup_id,
                'date': str(detail.checkup.checkup_date),
                'year': detail.checkup.checkup_year,
                'value': float(detail.numeric_value),
                'unit': detail.unit or '',
                'reference_range': detail.reference_range or '',
            })

        # 3. 시계열 변화량 및 증감률 계산
        analysis_result = {}

        for name, records in trend_data.items():
            if not records:
                continue

            # 이전 기록 대비 변화량 계산
            for i in range(len(records)):
                if i == 0:
                    records[i]['diff_from_previous'] = 0.0
                    records[i]['change_rate_percent'] = 0.0
                    records[i]['trend_status'] = 'BASELINE'
                else:
                    prev_val = records[i - 1]['value']
                    curr_val = records[i]['value']
                    diff = round(curr_val - prev_val, 2)

                    rate = round((diff / prev_val) * 100, 2) if prev_val != 0 else 0.0

                    # 수치 변화 상태 정의
                    if diff > 0:
                        status = 'INCREASE'
                    elif diff < 0:
                        status = 'DECREASE'
                    else:
                        status = 'STABLE'

                    records[i]['diff_from_previous'] = diff
                    records[i]['change_rate_percent'] = rate
                    records[i]['trend_status'] = status

            # 최신 기록 대비 총 변화 요약
            latest = records[-1]
            first = records[0]
            total_diff = round(latest['value'] - first['value'], 2)
            total_rate = round((total_diff / first['value']) * 100, 2) if first['value'] != 0 else 0.0

            analysis_result[name] = {
                'item_name': name,
                'unit': latest['unit'],
                'latest_value': latest['value'],
                'total_records_count': len(records),
                'overall_change': total_diff,
                'overall_change_rate': total_rate,
                'history': records
            }

        return analysis_result