import asyncio

from liteauto import google, parse, wlanswer
from liteauto.parselite import aparse

from litegen import LLM

def llm(query,
        api_key='ollama',
        model="hf.co/bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF:Q8_0"):
    llm = LLM(api_key=api_key)
    for _ in llm.completion(model=model, prompt=query,
                            stream=True):
        if _:
            yield _.choices[0].delta.content

async def search_ai(query,api_key='ollama',
        model="hf.co/bartowski/DeepSeek-R1-Distill-Qwen-1.5B-GGUF:Q8_0"):
    responses = [x for x in await aparse(google(query,max_urls=3)) if x.content]
    res = [(r.url,wlanswer(r.content,query,k=3)) for r in responses]
    for x in llm(query="\n".join([r[1] for  r in res],
                           ) + f" \n Quickly think about the above results and write a summary of the above results for question : {query}",
                 api_key=api_key,
                 model=model):
        yield x
    yield "\n"+"-"*20+"\n".join(r[0] for r in res)

async def main():
    async for x in search_ai('what is ai agents'):
        print(x, end="", flush=True)

if __name__ == '__main__':
    asyncio.run(main())
