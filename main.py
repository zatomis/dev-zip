from datetime import datetime

import aiofiles
import asyncio
from aiohttp import web



async def archive(request):
    response = web.StreamResponse()
    response.content_type = 'application/zip'
    response.content_disposition = 'attachment; filename="files.zip"'
    await response.prepare(request)

    # request.url.parts[2]
    # args = ["*"]
    # command = ["zip", "-j", f"photos/{request.url.parts[2]}/*", "-r", "-",]
    command = ["zip", "-r", "-", "-j", f"photos/{request.url.parts[2]}/.*"]
    proc = await asyncio.create_subprocess_exec(*command, stdout = asyncio.subprocess.PIPE, stderr = asyncio.subprocess.PIPE)
    while True:
        if proc.stdout.at_eof():
            break
        stdout = await proc.stdout.read(100)
        await response.write(stdout)
    await proc.wait()
    return response

    # while True:
    #     formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     message = f'{formatted_date}<br>'  # <br> — HTML тег переноса строки
    #     await response.write(message.encode('utf-8'))
    #     await asyncio.sleep(INTERVAL_SECS)

async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
