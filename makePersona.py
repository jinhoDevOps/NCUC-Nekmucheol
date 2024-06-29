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

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }
        capture_next = False

        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-DASH-001',
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

        print(type(content_data))
        # content_data를 튜플로 분리
        if content_data:
            parts = content_data.split('\n\n')
            if len(parts) >= 2:
                return list(parts)

        return None


        # with requests.post(self._host + '/testapp/v1/chat-completions/HCX-DASH-001',
        #                    headers=headers, json=completion_request, stream=True) as r:
        #     for line in r.iter_lines():
        #         if line:
        #             print(line.decode("utf-8"))


def extract_event_result_part(text):
    lines = text.strip().split("\n")
    event_result_part = []
    capture = False

    for line in lines:
        if line.startswith("event:result"):
            capture = True
        if capture:
            event_result_part.append(line)

    return "\n".join(event_result_part)
def makePersona(prompt):
    with open('Secret.yaml', 'r')as file:
        config=yaml.safe_load(file)

    completion_executor = CompletionExecutor(
        host=config['makePersona']['host'],
        api_key=config['makePersona']['api_key'],
        api_key_primary_val=config['makePersona']['api_key_primary_val'],
        request_id=config['makePersona']['request_id']
    )

    preset_text = [{"role":"system","content":"- 의견에서 어떤 관점이 있는지 분류하는 AI 입니다.\n- 의견은 2가지로 나와야 하며, 다른 AI 명령 프롬폼트의 그 내용을 넣을꺼야\n- 항상 명령체로 글을 만들어줘\n\n\n--------------------------------------------------\n\n\n\n\n예시 1) \n우리 집에 밤마다 귀신이 나타나는데 그 귀신이 박보영을 닮았다면 이사 가야 되나 말아야 되나?\n\n\n1)\n내 의견에 동조해줘\n \n이사를 가는게 좋아\n1. 이사를 가는게 좋다고 말해줘\n\n\n2)\n내 의견에 동조해줘\n \n이사를 가지 않는게 좋아\n1. 이사를 가지 않는게 좋다고 말해줘\n\n"},
                   {"role":"user","content":"우리 집에 밤마다 귀신이 나타나는데 그 귀신이 박보영을 닮았다면 이사 가야 되나 말아야 되나?"},
                   {"role":"assistant","content":"1. 내 의견에 동조해줘 \n   - 이사를 가는게 좋아  \n   - 이유는 박보영을 닮아서 무섭지 않을 것 같기 때문이야\n\n2. 내 의견에 동조해줘 \n   - 이사를 가지 않는게 좋아  \n   - 이유는 귀신이 나타날 때마다 박보영이라고 생각하면 무섭지 않을 것 같기 때문이야"},
                   {"role":"user","content":prompt},]

    request_data = {
        'messages': preset_text,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 256,
        'temperature': 0.5,
        'repeatPenalty': 5.0,
        'stopBefore': [],
        'includeAiFilters': False,
        'seed': 0
    }

    result = completion_executor.execute(request_data)
    return result
