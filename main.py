import asyncio

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


if __name__ == '__main__':
    create_zip = asyncio.run(get_zip())
