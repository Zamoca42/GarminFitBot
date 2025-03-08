from fastapi import Request

from api.common.schema import ResponseModel


class ProfileController:
    async def get_profile(self, request: Request) -> ResponseModel:
        return ResponseModel(
            message="프로필 조회 성공", data=request.user.garmin_client.user_profile
        )
