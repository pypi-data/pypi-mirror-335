from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv(filename="env.txt"))

from openai import OpenAI

def client_ollama(base_url='http://localhost:11434/v1/'):
    client = OpenAI(
        base_url=base_url,
        api_key='key',#必需但可以随便填写
    )
    return client


def chat_ollama(prompt, response_format="text", model='deepseek-r1:1.5b',temperature=0,base_url='http://localhost:11434/v1/'):
    client = OpenAI(
        base_url=base_url,
        api_key='key',#必需但可以随便填写
    )
    
    response = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user','content': prompt,}],
        temperature=temperature,   # 模型输出的随机性，0 表示随机性最小
        # 返回消息的格式，text 或 json_object
        response_format={"type": response_format},
    )

    if response.choices is None:
        err_msg = response.error["message"]
        raise Exception(f"{err_msg}")

    return response.choices[0].message.content          # 返回模型生成的文本


