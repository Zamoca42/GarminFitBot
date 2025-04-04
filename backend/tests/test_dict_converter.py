import unittest
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union

from core.util.dict_converter import (
    camel_to_snake_case,
    camel_to_snake_dict_safe,
    get_default_value_by_type,
    get_required_fields,
)


@dataclass
class TestPrivacy:
    """테스트용 Privacy 클래스"""

    type_id: int
    type_key: str


@dataclass
class TestActivityType:
    """테스트용 ActivityType 클래스"""

    type_id: int
    type_key: str
    parent_type_id: int
    is_hidden: bool
    restricted: bool
    trimmable: bool


@dataclass
class TestEventType:
    """테스트용 EventType 클래스"""

    type_id: int
    type_key: str
    sort_order: int


@dataclass
class TestHeartRateDescriptor:
    """테스트용 HeartRateDescriptor 클래스"""

    key: str
    index: int


@dataclass
class TestHeartRateValue:
    """테스트용 HeartRateValue 클래스"""

    timestamp: int
    heart_rate: Optional[int]


@dataclass
class TestHeartRateModel:
    """테스트용 HeartRate 모델 클래스"""

    user_profile_pk: int
    calendar_date: str
    start_timestamp_gmt: datetime
    end_timestamp_gmt: datetime
    start_timestamp_local: datetime
    end_timestamp_local: datetime
    max_heart_rate: int
    min_heart_rate: int
    resting_heart_rate: int
    last_seven_days_avg_resting_heart_rate: int
    heart_rate_value_descriptors: List[TestHeartRateDescriptor]
    heart_rate_values: List[TestHeartRateValue]


@dataclass
class TestStressDescriptor:
    """테스트용 StressDescriptor 클래스"""

    key: str
    index: int


@dataclass
class TestStressValue:
    """테스트용 StressValue 클래스"""

    timestamp: int
    stress_level: Optional[int]


@dataclass
class TestStressModel:
    """테스트용 Stress 모델 클래스"""

    user_profile_pk: int
    calendar_date: str
    start_timestamp_gmt: datetime
    end_timestamp_gmt: datetime
    start_timestamp_local: datetime
    end_timestamp_local: datetime
    max_stress_level: int
    avg_stress_level: int
    stress_chart_value_offset: int
    stress_chart_y_axis_origin: int
    stress_value_descriptors_dto_list: List[TestStressDescriptor]
    stress_values: List[TestStressValue]


@dataclass
class TestStepsValueModel:
    """테스트용 StepsValue 모델 클래스"""

    start_gmt: datetime
    end_gmt: datetime
    steps: int
    pushes: int
    primary_activity_level: str
    activity_level_constant: bool


@dataclass
class TestActivityModel:
    """테스트용 Activity 모델 클래스"""

    # 필수 필드 (기본값 없음)
    activity_id: int
    activity_name: str
    start_time_local: datetime
    start_time_gmt: datetime
    activity_type: TestActivityType
    event_type: TestEventType
    duration: float
    elapsed_duration: float
    moving_duration: float
    calories: int
    has_polyline: bool
    has_splits: bool
    manual_activity: bool
    favorite: bool
    privacy: TestPrivacy
    owner_id: int
    owner_display_name: str
    owner_full_name: str
    user_pro: bool

    # 선택적 필드 (기본값 있음)
    average_speed: Optional[float] = None
    max_speed: Optional[float] = None


@dataclass
class TestModel:
    """테스트용 모델 클래스"""

    # 필수 필드 (기본값 없음)
    id: int
    name: str
    created_at: datetime
    is_active: bool
    privacy: TestPrivacy

    # 선택적 필드 (기본값 있음)
    score: Optional[float] = None
    tags: List[str] = None
    config: Dict[str, str] = None


class TestCamelToSnakeCase(unittest.TestCase):
    """camel_to_snake_case 함수 테스트"""

    def test_camel_to_snake_case(self):
        """camelCase 형식의 문자열을 snake_case로 변환하는 기능 테스트"""
        test_cases = [
            ("userName", "user_name"),
            ("UserName", "user_name"),
            ("userId", "user_id"),
            ("HTTPResponse", "http_response"),
            ("getHTTPResponse", "get_http_response"),
            ("snake_case", "snake_case"),  # 이미 snake_case인 경우
            ("", ""),  # 빈 문자열
        ]

        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(camel_to_snake_case(input_str), expected)


class TestGetRequiredFields(unittest.TestCase):
    """get_required_fields 함수 테스트"""

    def test_get_required_fields(self):
        """클래스의 필수 필드를 올바르게 감지하는지 테스트"""
        required_fields = get_required_fields(TestModel)
        expected_fields = {"id", "name", "created_at", "is_active", "privacy"}

        self.assertEqual(required_fields, expected_fields)

    def test_activity_required_fields(self):
        """Activity 모델의 필수 필드를 올바르게 감지하는지 테스트"""
        required_fields = get_required_fields(TestActivityModel)
        expected_fields = {
            "activity_id",
            "activity_name",
            "start_time_local",
            "start_time_gmt",
            "activity_type",
            "event_type",
            "duration",
            "elapsed_duration",
            "moving_duration",
            "calories",
            "has_polyline",
            "has_splits",
            "manual_activity",
            "favorite",
            "privacy",
            "owner_id",
            "owner_display_name",
            "owner_full_name",
            "user_pro",
        }

        self.assertEqual(required_fields, expected_fields)

    def test_heart_rate_required_fields(self):
        """HeartRate 모델의 필수 필드를 올바르게 감지하는지 테스트"""
        required_fields = get_required_fields(TestHeartRateModel)
        expected_fields = {
            "user_profile_pk",
            "calendar_date",
            "start_timestamp_gmt",
            "end_timestamp_gmt",
            "start_timestamp_local",
            "end_timestamp_local",
            "max_heart_rate",
            "min_heart_rate",
            "resting_heart_rate",
            "last_seven_days_avg_resting_heart_rate",
            "heart_rate_value_descriptors",
            "heart_rate_values",
        }

        self.assertEqual(required_fields, expected_fields)

    def test_stress_required_fields(self):
        """Stress 모델의 필수 필드를 올바르게 감지하는지 테스트"""
        required_fields = get_required_fields(TestStressModel)
        expected_fields = {
            "user_profile_pk",
            "calendar_date",
            "start_timestamp_gmt",
            "end_timestamp_gmt",
            "start_timestamp_local",
            "end_timestamp_local",
            "max_stress_level",
            "avg_stress_level",
            "stress_chart_value_offset",
            "stress_chart_y_axis_origin",
            "stress_value_descriptors_dto_list",
            "stress_values",
        }

        self.assertEqual(required_fields, expected_fields)

    def test_steps_value_required_fields(self):
        """StepsValue 모델의 필수 필드를 올바르게 감지하는지 테스트"""
        required_fields = get_required_fields(TestStepsValueModel)
        expected_fields = {
            "start_gmt",
            "end_gmt",
            "steps",
            "pushes",
            "primary_activity_level",
            "activity_level_constant",
        }

        self.assertEqual(required_fields, expected_fields)


class TestGetDefaultValueByType(unittest.TestCase):
    """get_default_value_by_type 함수 테스트"""

    def test_basic_types(self):
        """기본 타입에 대한 기본값 생성 테스트"""
        self.assertEqual(get_default_value_by_type(int), 0)
        self.assertEqual(get_default_value_by_type(float), 0.0)
        self.assertEqual(get_default_value_by_type(str), "")
        self.assertEqual(get_default_value_by_type(bool), False)
        self.assertEqual(get_default_value_by_type(list), [])
        self.assertEqual(get_default_value_by_type(dict), {})

        # datetime은 현재 시간을 반환하므로 타입만 검사
        self.assertIsInstance(get_default_value_by_type(datetime), datetime)

    def test_optional_types(self):
        """Optional 타입에 대한 기본값 생성 테스트"""
        # Optional[int]에 대해 int의 기본값(0)을 반환해야 함
        self.assertEqual(get_default_value_by_type(Optional[int]), 0)
        self.assertEqual(get_default_value_by_type(Optional[str]), "")

    def test_complex_types(self):
        """복잡한 타입에 대한 기본값 생성 테스트"""
        # 복잡한 타입은 None 반환
        self.assertIsNone(get_default_value_by_type(TestModel))
        self.assertIsNone(get_default_value_by_type(TestPrivacy))


class TestCamelToSnakeDictSafe(unittest.TestCase):
    """camel_to_snake_dict_safe 함수 테스트"""

    def test_basic_conversion(self):
        """기본 camelCase -> snake_case 변환 테스트"""
        input_dict = {
            "userName": "John",
            "userId": 123,
            "isActive": True,
            "createdAt": "2025-04-01T12:00:00Z",
        }

        expected = {
            "user_name": "John",
            "user_id": 123,
            "is_active": True,
            "created_at": "2025-04-01T12:00:00Z",
        }

        result = camel_to_snake_dict_safe(input_dict)
        self.assertEqual(result, expected)

    def test_nested_dict_conversion(self):
        """중첩된 딕셔너리 변환 테스트"""
        input_dict = {
            "userName": "John",
            "userProfile": {
                "firstName": "John",
                "lastName": "Doe",
                "contactInfo": {
                    "emailAddress": "john@example.com",
                    "phoneNumber": "123-456-7890",
                },
            },
        }

        expected = {
            "user_name": "John",
            "user_profile": {
                "first_name": "John",
                "last_name": "Doe",
                "contact_info": {
                    "email_address": "john@example.com",
                    "phone_number": "123-456-7890",
                },
            },
        }

        result = camel_to_snake_dict_safe(input_dict)
        self.assertEqual(result, expected)

    def test_list_in_dict_conversion(self):
        """리스트 내의 딕셔너리 변환 테스트"""
        input_dict = {
            "userName": "John",
            "userPosts": [
                {"postId": 1, "postTitle": "Hello"},
                {"postId": 2, "postTitle": "World"},
            ],
        }

        expected = {
            "user_name": "John",
            "user_posts": [
                {"post_id": 1, "post_title": "Hello"},
                {"post_id": 2, "post_title": "World"},
            ],
        }

        result = camel_to_snake_dict_safe(input_dict)
        self.assertEqual(result, expected)

    def test_empty_input(self):
        """빈 입력에 대한 테스트"""
        self.assertEqual(camel_to_snake_dict_safe({}), {})
        self.assertEqual(camel_to_snake_dict_safe(None), {})

    def test_error_handling(self):
        """오류 처리 테스트"""
        # 잘못된 타입의 키가 있는 경우
        input_dict = {
            "userName": "John",
            123: "Invalid Key",  # 숫자 키 (변환 중 오류 발생할 수 있음)
        }

        # 오류가 발생하지 않고 처리 가능한 키만 변환되어야 함
        result = camel_to_snake_dict_safe(input_dict)
        self.assertEqual(result.get("user_name"), "John")
        self.assertTrue(123 in result)

    def test_default_values_by_model(self):
        """모델 클래스를 사용한 기본값 설정 테스트"""

        @dataclass
        class SimpleModel:
            id: int
            name: str
            is_active: bool
            score: Optional[float] = None

        # 일부 필드가 누락된 입력
        input_dict = {
            "id": 1,
            # name is missing
            # is_active is missing
            "score": 9.5,
        }

        result = camel_to_snake_dict_safe(input_dict, cls=SimpleModel)

        # 누락된 필드에 기본값이 설정되어야 함
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "")  # str 기본값
        self.assertEqual(result["is_active"], False)  # bool 기본값
        self.assertEqual(result["score"], 9.5)  # 입력값 유지

    def test_custom_default_values(self):
        """사용자 정의 기본값 설정 테스트"""

        @dataclass
        class CustomModel:
            id: int
            name: str
            config: Dict[str, str]

        # 모든 필드가 누락된 입력
        input_dict = {}

        # 사용자 정의 기본값 설정
        field_defaults = {
            "id": 999,
            "name": "Default Name",
            "config": {"key": "value"},
        }

        result = camel_to_snake_dict_safe(
            input_dict, cls=CustomModel, field_defaults=field_defaults
        )

        # 사용자 정의 기본값이 설정되어야 함
        for field, value in field_defaults.items():
            self.assertIn(field, result)
            self.assertEqual(result[field], value)

    def test_activity_model_missing_fields(self):
        """Activity 모델의 누락된 필드에 대한 기본값 설정 테스트"""
        # 일부 필드가 누락된 활동 데이터
        activity_data = {
            "activityId": 12345,
            "activityName": "아침 달리기",
            "startTimeLocal": "2025-04-03T06:00:00.000Z",
            "startTimeGmt": "2025-04-02T21:00:00.000Z",
            "activityType": {
                "typeId": 1,
                "typeKey": "running",
                "parentTypeId": 17,
                "isHidden": False,
                "restricted": False,
                "trimmable": True,
            },
            "eventType": {"typeId": 8, "typeKey": "fitness", "sortOrder": 10},
            "duration": 1800.0,
            "elapsedDuration": 1850.0,
            # moving_duration 필드 누락
            "calories": 250,
            "hasPolyline": True,
            # has_splits 필드 누락
            "manualActivity": False,
            "favorite": False,
            "privacy": {"typeId": 1, "typeKey": "private"},
            "ownerId": 9876,
            "ownerDisplayName": "홍길동",
            "ownerFullName": "홍길동",
            "userPro": False,
            "averageSpeed": 10.5,
            "maxSpeed": 12.3,
        }

        # 안전한 변환 함수 사용
        result = camel_to_snake_dict_safe(activity_data, cls=TestActivityModel)

        # 누락된 필드에 기본값이 설정되었는지 확인
        self.assertEqual(result["activity_id"], 12345)
        self.assertEqual(result["activity_name"], "아침 달리기")
        self.assertEqual(result["calories"], 250)

        # 누락된 필드인 moving_duration과 has_splits에 기본값이 설정되었는지 확인
        self.assertIn("moving_duration", result)
        self.assertEqual(
            result["moving_duration"], 0.0
        )  # float 타입이므로 0.0으로 설정됨

        self.assertIn("has_splits", result)
        self.assertEqual(result["has_splits"], False)  # bool 타입이므로 False로 설정됨

    def test_heart_rate_model_missing_fields(self):
        """HeartRate 모델의 누락된 필드에 대한 기본값 설정 테스트"""
        # 일부 필드가 누락된 심박수 데이터
        heart_rate_data = {
            "userProfilePk": 12345,
            "calendarDate": "2025-04-03",
            "startTimestampGmt": "2025-04-03T00:00:00.000Z",
            "endTimestampGmt": "2025-04-03T23:59:59.999Z",
            "startTimestampLocal": "2025-04-03T09:00:00.000Z",
            "endTimestampLocal": "2025-04-04T08:59:59.999Z",
            "maxHeartRate": 180,
            # min_heart_rate 필드 누락
            "restingHeartRate": 60,
            # last_seven_days_avg_resting_heart_rate 필드 누락
            "heartRateValueDescriptors": [
                {"key": "timestamp", "index": 0},
                {"key": "heartrate", "index": 1},
            ],
            "heartRateValues": [
                [1617408000000, 70],
                [1617408300000, 72],
                [1617408600000, 75],
            ],
        }

        # 안전한 변환 함수 사용
        result = camel_to_snake_dict_safe(heart_rate_data, cls=TestHeartRateModel)

        # 누락된 필드에 기본값이 설정되었는지 확인
        self.assertEqual(result["user_profile_pk"], 12345)
        self.assertEqual(result["max_heart_rate"], 180)
        self.assertEqual(result["resting_heart_rate"], 60)

        # 누락된 필드에 기본값이 설정되었는지 확인
        self.assertIn("min_heart_rate", result)
        self.assertEqual(result["min_heart_rate"], 0)  # int 타입이므로 0으로 설정됨

        self.assertIn("last_seven_days_avg_resting_heart_rate", result)
        self.assertEqual(
            result["last_seven_days_avg_resting_heart_rate"], 0
        )  # int 타입이므로 0으로 설정됨

    def test_stress_model_missing_fields(self):
        """Stress 모델의 누락된 필드에 대한 기본값 설정 테스트"""
        # 일부 필드가 누락된 스트레스 데이터
        stress_data = {
            "userProfilePk": 12345,
            "calendarDate": "2025-04-03",
            "startTimestampGmt": "2025-04-03T00:00:00.000Z",
            "endTimestampGmt": "2025-04-03T23:59:59.999Z",
            "startTimestampLocal": "2025-04-03T09:00:00.000Z",
            "endTimestampLocal": "2025-04-04T08:59:59.999Z",
            "maxStressLevel": 95,
            "avgStressLevel": 42,
            # stress_chart_value_offset 필드 누락
            # stress_chart_y_axis_origin 필드 누락
            "stressValueDescriptorsDtoList": [
                {"key": "timestamp", "index": 0},
                {"key": "stressLevel", "index": 1},
            ],
            "stressValuesArray": [
                [1617408000000, 40],
                [1617408300000, 45],
                [1617408600000, 50],
            ],
        }

        # 안전한 변환 함수 사용
        result = camel_to_snake_dict_safe(stress_data, cls=TestStressModel)

        # 누락된 필드에 기본값이 설정되었는지 확인
        self.assertEqual(result["user_profile_pk"], 12345)
        self.assertEqual(result["max_stress_level"], 95)
        self.assertEqual(result["avg_stress_level"], 42)

        # 누락된 필드에 기본값이 설정되었는지 확인
        self.assertIn("stress_chart_value_offset", result)
        self.assertEqual(
            result["stress_chart_value_offset"], 0
        )  # int 타입이므로 0으로 설정됨

        self.assertIn("stress_chart_y_axis_origin", result)
        self.assertEqual(
            result["stress_chart_y_axis_origin"], 0
        )  # int 타입이므로 0으로 설정됨

    def test_steps_value_model_missing_fields(self):
        """StepsValue 모델의 누락된 필드에 대한 기본값 설정 테스트"""
        # 일부 필드가 누락된 걸음수 데이터
        steps_data = {
            "startGmt": "2025-04-03T06:00:00.000Z",
            "endGmt": "2025-04-03T06:15:00.000Z",
            "steps": 500,
            # pushes 필드 누락
            "primaryActivityLevel": "active",
            # activity_level_constant 필드 누락
        }

        # 안전한 변환 함수 사용
        result = camel_to_snake_dict_safe(steps_data, cls=TestStepsValueModel)

        # 누락된 필드에 기본값이 설정되었는지 확인
        self.assertEqual(result["steps"], 500)
        self.assertEqual(result["primary_activity_level"], "active")

        # 누락된 필드에 기본값이 설정되었는지 확인
        self.assertIn("pushes", result)
        self.assertEqual(result["pushes"], 0)  # int 타입이므로 0으로 설정됨

        self.assertIn("activity_level_constant", result)
        self.assertEqual(
            result["activity_level_constant"], False
        )  # bool 타입이므로 False로 설정됨


if __name__ == "__main__":
    unittest.main()
