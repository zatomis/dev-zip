from datetime import datetime

import aiofiles
import asyncio
from aiohttp import web

INTERVAL_SECS = 1


async def get_zip():
    args = ["img.png", "img_1.png", "img_2.png", "img_3.png"]
    command = ["zip", "-r", "-", *args]
    proc = await asyncio.create_subprocess_exec(*command, stdout = asyncio.subprocess.PIPE, stderr = asyncio.subprocess.PIPE)
    bytes_zip = b''
    while True:
        if proc.stdout.at_eof():
            break
        stdout = await proc.stdout.read(100)
        if stdout:
            print(f'[stdout] {stdout}')
            bytes_zip += stdout
    await proc.wait()
    with open("zip_file.zip", "wb") as file:
        file.write(bytes_zip)



async def archive(request):

    # raise NotImplementedError
    response = web.StreamResponse()

    # Большинство браузеров не отрисовывают частично загруженный контент, только если это не HTML.
    # Поэтому отправляем клиенту именно HTML, указываем это в Content-Type.
    response.headers['Content-Type'] = 'text/html'

    # Отправляет клиенту HTTP заголовки
    await response.prepare(request)

    while True:
        formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f'{formatted_date}<br>'  # <br> — HTML тег переноса строки

        # Отправляет клиенту очередную порцию ответа
        await response.write(message.encode('utf-8'))

        await asyncio.sleep(INTERVAL_SECS)

async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    # create_zip = asyncio.run(get_zip())
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
