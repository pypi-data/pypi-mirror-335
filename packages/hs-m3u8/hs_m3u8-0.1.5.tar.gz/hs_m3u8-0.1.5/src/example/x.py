import asyncio

from hs_m3u8 import M3u8Downloader


async def main():
    url = (
        "https://video.twimg.com/ext_tw_video/1879556885663342592/pu/pl/Vcvv0UK9lOhezJt1.m3u8?variant_version=1&tag=12"
    )
    name = "x"
    dl = M3u8Downloader(m3u8_url=url, save_path=f"../../downloads/{name}", max_workers=64)
    await dl.run(del_hls=False, merge=True)


if __name__ == "__main__":
    asyncio.run(main())
