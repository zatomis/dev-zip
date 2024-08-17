import os
from functools import partial
from subprocess import TimeoutExpired
import argparse
import aiofiles
import asyncio
from aiohttp import web
import logging


logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Скрипт скачивания всех фотографий с лендинга в один клик"
    )
    parser.add_argument(
        '--logging',
        action='store_false',
        help='Вкл/выкл логирование',
    )
    parser.add_argument(
        '--dest_folder',
        default='photos',
        type=str,
        help='Путь к каталогу с фотографиями',
    )
    parser.add_argument(
        '--delay_answer',
        default=1,
        type=int,
        help='Задержка ответа в сек.',
    )
    args = parser.parse_args()
    return args


async def archive(request, folder, delay):
    response = web.StreamResponse()
    work_dir = f"{folder}/{request.url.parts[2]}/"
    if os.path.isdir(work_dir):
        logger.info(f"Send archive from  - {work_dir}")
        response.content_type = 'application/zip'
        response.headers['Content-Disposition'] = 'attachment; \
            filename="filename.zip"'
        await response.prepare(request)
        files_in_dir = os.listdir(f"./{work_dir}")
        command = ["zip", "-r", "-", *files_in_dir]
        proc = await asyncio.create_subprocess_exec(*command,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE,
                                                    cwd=work_dir)
        logger.info(f"Pid = {proc.pid}")
        try:
            while not proc.stdout.at_eof():
                stdout = await proc.stdout.read(100)
                logger.info(f"Read bytes - {stdout}")
                await asyncio.sleep(delay)
                await response.write(stdout)
            await proc.wait()
            return response
        except (asyncio.CancelledError, TimeoutExpired):
            logger.warning(f"Download was interrupted. Kill process №{proc.pid}")
            proc.kill()
            raise
    else:
        logger.warning(f"По указанному пути {work_dir}. Архив не существует или был удален.")
        response.headers['Content-Type'] = 'text/html'
        await response.prepare(request)
        message = f'По указанному пути <br>Архив не существует или был удален.<br>'
        await response.write(message.encode('cp1251'))
        return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


def main():
    parsed_arguments = parse_arguments()
    if parsed_arguments.logging:
        logging.basicConfig(
            format='%(filename)s:%(lineno)d - %(levelname)-8s - %(asctime)s - %(funcName)s - %(name)s - %(message)s',
            level=logging.INFO
        )
    else:
        logging.basicConfig(
            format='%(filename)s:%(lineno)d - %(levelname)-8s - %(asctime)s - %(funcName)s - %(name)s - %(message)s',
            level=logging.WARNING
        )

    parsed_arguments = parse_arguments()
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', partial(archive,
                                                    folder=parsed_arguments.dest_folder,
                                                    delay=parsed_arguments.delay_answer)),
    ])
    web.run_app(app)


if __name__ == '__main__':
    main()
