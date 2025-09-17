import os
import json
import re
import logging
from typing import Dict, Any

import google.generativeai as genai

class GeminiService:
    """
    Google Gemini API와의 상호작용을 관리하는 서비스 클래스입니다.
    API 키 설정, 모델 초기화, 콘텐츠 생성 및 응답 파싱을 담당합니다.
    """
    def __init__(self, api_key: str):
        """
        서비스를 초기화하고 API 키를 설정합니다.

        Args:
            api_key (str): Google API 키.
        """
        if not api_key:
            raise ValueError("Google API 키가 제공되지 않았습니다.")
        genai.configure(api_key=api_key)
        self.model = None

    def _initialize_model(self, model_name: str, generation_config: Dict[str, Any], safety_settings: Dict[str, Any]):
        """모델을 초기화합니다. 캐싱하여 중복 생성을 방지합니다."""
        if self.model is None or self.model.model_name != f"models/{model_name}":
            logging.info(f"{model_name} 모델을 초기화합니다.")
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )

    def generate_content(
        self,
        prompt: str,
        model_name: str = "gemini-1.5-flash",
        generation_config: Dict[str, Any] = None,
        safety_settings: Dict[str, Any] = None
    ) -> str:
        """
        주어진 프롬프트를 사용하여 콘텐츠를 생성합니다.

        Args:
            prompt (str): 모델에 전달할 프롬프트.
            model_name (str): 사용할 모델의 이름.
            generation_config (Dict[str, Any], optional): 생성 관련 설정.
            safety_settings (Dict[str, Any], optional): 안전 관련 설정.

        Returns:
            str: 생성된 텍스트 콘텐츠. 응답이 없거나 오류 발생 시 빈 문자열 반환.
        """
        # 기본 설정값
        if generation_config is None:
            generation_config = {
                "temperature": 0.8,
                "top_p": 1,
                "top_k": 32,
                "max_output_tokens": 8192,
            }
        if safety_settings is None:
            safety_settings = {
                "HARASSMENT": "BLOCK_NONE",
                "HATE_SPEECH": "BLOCK_NONE",
                "SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "DANGEROUS_CONTENT": "BLOCK_NONE"
            }
            
        try:
            self._initialize_model(model_name, generation_config, safety_settings)
            response = self.model.generate_content(prompt)
            
            if response.parts:
                return "".join(part.text for part in response.parts if hasattr(part, "text"))
            # Safety setting 등으로 인해 응답이 차단된 경우
            logging.warning("Gemini 응답이 비어있거나 차단되었습니다.")
            return ""
        except Exception as e:
            logging.error(f"Gemini API 콘텐츠 생성 중 오류 발생: {e}")
            return ""

    def generate_json_content(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        JSON 형식의 콘텐츠를 생성하고 파싱합니다.
        LLM이 마크다운 코드 블록으로 JSON을 반환하는 경향이 있어, 이를 처리하는 로직을 포함합니다.

        Args:
            prompt (str): JSON 응답을 유도하는 프롬프트.
            **kwargs: generate_content 메서드에 전달될 추가 인자.

        Returns:
            Dict[str, Any]: 파싱된 JSON 객체. 실패 시 빈 딕셔너리 반환.
        """
        json_prompt = f"{prompt}\n\n응답은 반드시 JSON 형식이어야 하며, 다른 설명은 포함하지 마세요."
        raw_response = self.generate_content(json_prompt, **kwargs)

        if not raw_response:
            return {}

        # Markdown 코드 블록(```json ... ```)에서 순수 JSON 추출
        match = re.search(r"```json\s*(\{.*?\})\s*```", raw_response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # 코드 블록이 없는 경우, 응답 전체를 JSON으로 간주
            json_str = raw_response

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logging.error(f"JSON 파싱 오류: {e}\n원본 응답: {raw_response}")
            return {}

# --- 서비스 인스턴스 ---
# .env 파일에서 API 키를 로드하여 서비스 인스턴스를 생성합니다.
google_api_key = os.getenv("GOOGLE_API_KEY")
gemini_service = GeminiService(api_key=google_api_key) if google_api_key else None

