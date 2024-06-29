from SecondPersona import SecondPersona
from makePersona import makePersona
from FirstPersona import FirstPersona


if __name__ == '__main__':
    prompt = input()
    persona = None
    persona = makePersona(prompt)


    # print(type(persona))
    # persona.append('난 바보야')
    # print(persona[0])

    # print(FirstPersona(persona[0]))
    print("1번 주장" + persona[0])
    print("2번 주장" + persona[1])

    for last_prompt in persona:
        persona.append(FirstPersona((persona),persona[0]))
        print("페르소나1번: " + persona[-1])
        persona.append(SecondPersona((persona),persona[1]))
        print("페르소나2번: " + persona[-1])
        if len(persona) > 8:
            break
