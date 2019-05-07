import asyncio
import aiohttp
import re


urls = [f'http://www.baidu.com/s?wd={i}' for i in range(10)]
loop = asyncio.get_event_loop()
results = []


def parse(url, response):
    response = response.decode('utf8', errors='ignore')
    search = re.search(r'<title>(.*)</title>', response)
    title = search.group(1) if search else ''
    results.append((url, title))


async def fetch(url):
    async with aiohttp.ClientSession(loop=loop) as session:
        async with session.get(url) as response:
            response = await response.read()
            parse(url, response)


if __name__ == '__main__':
    tasks = [fetch(target) for target in urls]
    loop.run_until_complete(asyncio.gather(*tasks))
    print(results)
