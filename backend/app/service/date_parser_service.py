import logging
from datetime import date, datetime
from typing import Optional, Tuple

import pytz
from langchain_google_genai import ChatGoogleGenerativeAI

from api.common.schema.date_parser import Date
from app.agent.prompt import create_parse_date_prompt
from core.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)


class DateParserService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GEMINI_API_KEY,
        ).with_structured_output(Date)

    async def parse_to_date(self, origin: str) -> Tuple[Optional[date], Optional[str]]:
        """
        자연어 기반 날짜를 파싱하고 검증 (미래 날짜 등)
        :return: (유효한 날짜 or None, 에러 메시지 or None)
        """
        try:
            today = datetime.now(pytz.timezone("Asia/Seoul")).date()
            prompt = create_parse_date_prompt().invoke(
                {"today": today, "query": origin}
            )
            date_parser = self.llm.invoke(prompt)

            logger.info(f"날짜 파싱 결과: {date_parser}")

            if not date_parser:
                return None, "날짜를 인식할 수 없습니다."

            parsed_date_raw = date_parser.date

            if isinstance(parsed_date_raw, date):
                parsed_date = parsed_date_raw
            elif isinstance(parsed_date_raw, str):
                try:
                    parsed_date = datetime.strptime(parsed_date_raw, "%Y-%m-%d").date()
                except ValueError:
                    return None, "날짜 형식이 올바르지 않습니다. (예: 2024-04-01)"
            else:
                return None, "알 수 없는 날짜 형식입니다."

            if parsed_date > today:
                return (
                    None,
                    f"{parsed_date}은(는) 미래 날짜입니다. 오늘 이전의 날짜를 입력해 주세요.",
                )

            return parsed_date, None
        except Exception as e:
            logger.error(f"날짜 파싱 오류: {e}", exc_info=True)
            return None, "날짜 처리 중 오류가 발생했습니다."
