# -*- coding: utf-8 -*-

import requests
import json
import yaml

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request,belif):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }
        capture_next = False

        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-003',
                           headers=headers, json=completion_request, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    # print(decoded_line)
                    if capture_next:
                        if decoded_line.startswith('data:'):
                            json_data = decoded_line[len('data:'):]
                            result_data = json.loads(json_data)
                            content_data = result_data.get('message', {}).get('content')
                            break
                    if decoded_line.startswith('event:result'):
                        capture_next = True

        return content_data
def create_preset_text(input_list,belif):
    roles = ["user", "assistant"]
    preset_text = [{"role":"system","content":"- [배경] 상황내에서 이야기 해야합니다."
                                              "\n- [2번] 문장에만 공감해야합니다."
                                              "\n\n- [1번] 문장에는 반박해야합니다.\n- 대화형으로 말해야합니다"
                                              "\n\n\n\n\n--------------------"
                                              "\n예시1)\n질문)\n[배경] 우리 집에 밤마다 귀신이 나타나는데 그 귀신이 박보영을 닮았다면 이사 가야 되나 말아야 되나? "
                                              "\r\n\r\n[1번] 이사를 가는게 좋아\r\n1. 귀신 때문에 일상생활에 지장이 생길 수 있어요. 안전을 위해서라도 이사를 가는 것이 좋을 것 같아요."
                                              "\r\n\r\n[2번] 이사를 가지 않는게 좋아\r\n1. 귀신이 나타날 때마다 대처할 방법을 찾아보거나, 귀신에게 도움을 요청해볼 수도 있지 않을까요?"
                                              "\n\n\n답변)\n이사를 가지 않는게 정말 무조건 좋아, 실질적으로 피해를 주지 않기도 하고, 또 박보영의 머리라면 오히려 이득 아닐까?"}]

    for i, content in enumerate(input_list):
        role = roles[i % 2]  # 역할이 번갈아가며 지정됨
        preset_text.append({"role": role, "content": content})
    # print(preset_text)
    preset_text.append({"role":"user", "content": belif+content[-1]})

    return preset_text


def SecondPersona(prompt,belif):
    with open('Secret.yaml', 'r')as file:
        config=yaml.safe_load(file)

    completion_executor = CompletionExecutor(
        host=config['SecondPersona']['host'],
        api_key=config['SecondPersona']['api_key'],
        api_key_primary_val=config['SecondPersona']['api_key_primary_val'],
        request_id=config['SecondPersona']['request_id']
    )

    preset_text = create_preset_text(prompt,belif)

    request_data = {
        'messages': preset_text,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 256,
        'temperature': 0.64,
        'repeatPenalty': 5.0,
        'stopBefore': [],
        'includeAiFilters': False,
        'seed': 0
    }

    # print(preset_text)
    # completion_executor.execute(request_data)
    result = completion_executor.execute(request_data,belif)
    return result
