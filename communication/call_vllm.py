
import asyncio
import functools
import openai
import json
import time


from glob import glob
from tqdm import tqdm
from threading import Thread

# ------------------------------------------------
# constant
# ------------------------------------------------
GPT_TIMEOUT = 60


# ------------------------------------------------
# utils
# ------------------------------------------------

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception(f'function [{func.__name__}] timeout [{timeout} seconds] exceeded!')]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

def get_response_data(args, model, content, openai_api_key, openai_api_base):
    openai_api_key = "EMPTY" if openai_api_key is None else openai_api_key
    openai_api_base = "http://localhost:8000/v1" if openai_api_base is None else openai_api_base
    client = openai.OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )
    _t = None
    # try:
    _t = time.time()
    if is_instruct(model):
        response = call_gpt(args, model, client, stream=args.stream, prompt=content)
    else:
        response = call_gpt(args, model, client, stream=args.stream, messages=content)
    _t = time.time() - _t
    # except Exception as e:
    #     print('timeout occur', str(e))
    #     raise e

    data = {
        "response": response,
        "elapsed_time": _t,
    }
    return data


def is_instruct(model): return "instruct" in model

@timeout(GPT_TIMEOUT)
def call_gpt(args, model, client, **kwargs):
    if is_instruct(model) and ("gpt" in model):
        response = client.completions.create(model=model, **kwargs, **args.gpt_kwargs)
    else:
        response = client.chat.completions.create(model=model, **kwargs, **args.gpt_kwargs)
    return response

# ------------------------------------------------

class args: # hard coded
    model = "mistralai/Mistral-7B-Instruct-v0.2"
    system_prompt = "You are a helpful assistant."

    gpt_kwargs = {
        "max_new_tokens": 50,
        "temperature": 0.6,
        "top_p": 0.95,
        "n": 1,
        "stop": ["<|eot|>", "</s>", ". "],
    }
    stream = True
    max_trial = 5
    max_worker = 8

    openai_api_key = "None"

    url_format = "http://{host}:{port}/v1"
    npc_info_map = {
        "Jinsoyun": {
            "model": "Jinsoyun",
            "host": "cs-gpu-02",
            "port": "4200",
            "log": "./logs/npc_0.log",
        },
        # "Lusung": {
        #     "model": "Lusung",
        #     "host": "node32",
        #     "port": "4201",
        #     "log": "./logs/npc_1.log",
        # },
        # "npc_2": {
        #     "model": "mistralai/Mistral-7B-Instruct-v0.2",
        #     "host": "",
        #     "port": "4202",
        #     "log": "./logs/npc_2.log",
        # },
        # "npc_3": {
        #     "model": "mistralai/Mistral-7B-Instruct-v0.2",
        #     "host": "",
        #     "port": "4203",
        #     "log": "./logs/npc_3.log",
        # },
    }

def get_npc_log_path(args, npc_name):
    return args.npc_info_map[npc_name]["log"]

def get_npc_url(args, host, npc_name):
    port = args.npc_info_map[npc_name]["port"]
    url = args.url_format.format(host=host, port=port)
    return url

async def get_async_response(args, model, prompt, openai_api_key, openai_api_base, async_id):
    messages = [
        {"role": "user", "content": prompt},
    ]
    
    content = messages
    
    data, i, errors, elapsed_time = {}, 0, [], None
    response = None
    while i < args.max_trial:
        try:
            data = get_response_data(args, model, content, openai_api_key, openai_api_base)
            response = data["response"]
            elapsed_time = data["elapsed_time"]
            break
        except Exception as e:
            errors.append(e)
            print(e)
            # raise e
            i += 1

    if args.stream:
        output = ""
        print(f"{async_id}:", end=" ")
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                output += content
                print(content, flush=True, end="")
    else:
        print("generation complete on async_id", async_id)
        print(response.choices[0].message.content)
        output = response.choices[0].message.content.strip()
    
    status = {
        "response": response,
        "output": output,
        "elapsed_time": elapsed_time,
        "errors": errors,
        "url": openai_api_base,
        "id": async_id,
    }
    return status


async def call_npc_response(args, prompt_arr):
    tasks = list()
    npc_info_map = args.npc_info_map
    for i, (npc_name, data) in enumerate(npc_info_map.items()):
        host = data["host"]
        model = data["model"]
        npc_url = get_npc_url(args, host, npc_name)
        tasks.append(
            get_async_response(
                args, model, prompt_arr[i], 
                openai_api_key=args.openai_api_key, openai_api_base=npc_url,
                async_id=npc_name
            )
        )
    # for task in asyncio.as_completed(tasks):
    #     result = await task
    results = await asyncio.gather(*tasks)
    return results

def simple_chat():
    args.stream = False
    prompt_arr=[]
    prompt1 = """I want you to act like Jinsoyun. I want you to respond and answer like Jinsoyun, using the tone, manner and vocabulary Jinsoyun would use. You must know all of the knowledge of Jinsoyun.
The status of you is as follows:
Location: Coffee Shop - Afternoon
Status: Jinsoyun is casually chatting with Miles.
The interactions are as follows:
Miles (speaking): Hi Jinsoyun, What's your name?<|eot|>"""
    prompt2 = """I want you to act like Lusung. I want you to respond and answer like Lusung, using the tone, manner and vocabulary Lusung would use. You must know all of the knowledge of Lusung.
The status of you is as follows:
Location: Coffee Shop - Afternoon
Status: Lusung is casually chatting with Miles.
The interactions are as follows:
Miles (speaking): Hi Lusung, What's your name?<|eot|>"""

    prompt_arr.append(prompt1)
    prompt_arr.append(prompt2)
    status = asyncio.run(call_npc_response(args, prompt_arr))
    for response in status:
        if not args.stream:
            print(f"{response['id']}: {response['output']}")

if __name__ == "__main__":
    simple_chat()










