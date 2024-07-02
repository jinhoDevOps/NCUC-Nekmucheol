# -*- coding: utf-8 -*-

import requests
import json, yaml


class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id=None):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self._api_key,
            "X-NCP-APIGW-API-KEY": self._api_key_primary_val,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self._request_id,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
        }
        lines = []
        capture_next = False  # 추가: 다음 라인 캡쳐 여부를 결정하는 플래그

        with requests.post(
            self._host + "/testapp/v1/chat-completions/HCX-DASH-001",
            headers=headers,
            json=completion_request,
            stream=True,
        ) as r:
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if capture_next:
                        if decoded_line.startswith("data:"):
                            json_data = decoded_line[len("data:") :]
                            result_data = json.loads(json_data)
                            content_data = result_data.get("message", {}).get(
                                "content", ""
                            )
                            lines.append(content_data)  # 결과 내용 저장
                            capture_next = False  # 다음 데이터 캡처를 중지
                    if decoded_line.startswith("event:result"):
                        capture_next = True  # 다음 라인 캡쳐 플래그 활성화

        return lines


def get_discussion_result(input_text):
    # executor 생성 및 초기화
    with open('Secret.yaml', 'r')as file:
        config=yaml.safe_load(file)

    completion_executor = CompletionExecutor(
        host=config['dash']['host'],
        api_key=config['dash']['api_key'],
        api_key_primary_val=config['dash']['api_key_primary_val'],
    )
    # 토론 주제 전달 및 결과 처리
    preset_text = [
        {
            "role": "system",
            "content": "사용자 입력 받기 및 처리: 사용자로부터 입력을 받습니다. 입력된 내용은 토론의 적합성을 평가하기 위해 자동으로 분석됩니다. 분석 과정에서 주요 검토 사항은 윤리적 딜레마의 존재와 주제가 토론을 유발할 수 있는 복잡성 여부입니다. 예를 들어, '개인 프라이버시와 공공의 안전 중 어느 것이 우선해야 하는가?'는 토론을 유발할 수 있는 적합한 주제로 간주됩니다.\n\n\n결과 제공: 분석을 통해 얻은 결과는 사용자에게 명확하고 간결한 형태로 제공됩니다. 주제의 적합성 여부만을 포함하여 'True(적합)' 또는 'False(부적합)'로 표시되며, 이는 주제가 토론에 적합한 조건을 만족하는지 여부를 나타냅니다.\n\n\n응답 형태:\n결과 (result): 주제가 토론에 적합한지 여부를 나타내는 불리언 값입니다. 윤리적 딜레마가 명확하고 토론을 유발할 수 있는 복잡성이 있는 주제는 True로 반환됩니다.\n내용 (content): 결과의 판단 근거를 포함한 설명입니다. 이는 사용자가 결과를 이해하고, 주제에 대해 더 심도 있는 사고를 할 수 있도록 돕습니다.",
        },
        {"role": "user", "content": f"{input_text}"},
    ]
    request_data = {
        "messages": preset_text,
        "topP": 0.8,
        "topK": 0,
        "maxTokens": 256,
        "temperature": 0.2,
        "repeatPenalty": 5.0,
        "includeAiFilters": True,
        "seed": 0,
    }
    response = completion_executor.execute(request_data)
    result_string = response[-1]  # 가정: 마지막 항목에 결과가 포함
    # 결과 문자열을 분석하여 결과(True/False)와 내용을 추출
    result, content = parse_result(result_string)
    return result, content


def parse_result(result_string):
    """결과 문자열을 파싱하여 결과와 내용을 반환합니다."""
    lines = result_string.split("\n")
    result = None
    content = None
    for line in lines:
        line = line.strip()  # 공백 제거
        if line.startswith("결과"):
            result = line.split(":")[1].strip()  # ':' 이후 문자열을 결과로 추출
            print(f"파싱 결과: {result}")  # 디버깅을 위한 로그
        elif line.startswith("내용"):
            content = line.split(":")[1].strip()  # "내용 :" 이후 문자열을 내용으로 추출
            print(f"파싱 내용: {content}")  # 디버깅을 위한 로그
    return result, content

