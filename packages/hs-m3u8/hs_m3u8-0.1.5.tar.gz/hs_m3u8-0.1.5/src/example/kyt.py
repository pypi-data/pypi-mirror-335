# pip install hs-m3u8==0.1.4

import asyncio

from hs_m3u8 import M3u8Downloader, M3u8Key


async def main():
    url = "https://r1-ndr-private.ykt.cbern.com.cn/edu_product/esp/assets/68b6bed7-d093-7c8c-9133-95cf8205d21d.t/zh-CN/1712805650284/transcode/videos/68b6bed7-d093-7c8c-9133-95cf8205d21d-1920x1080-true-47fe81c5c8d91daf25e9fffd7082f934-eed6db5a85074b6dbbe5fa71f1243b26.m3u8"
    name = "ykt"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Origin": "https://basic.smartedu.cn",
        "Pragma": "no-cache",
        "Referer": "https://basic.smartedu.cn/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36",
        "X-ND-AUTH": 'MAC id="7F938B205F876FC3C7550081F114A1A4028222C3BFB978FD9B439192D004CB8EEB65E66BB'
        'C63E66FED6DD51F34F99411A6039E623E9A9D05",nonce="1742462574752:Z4IGAAV6"'
        ',mac="EUr56dXrCO1YGd3Ub1fj9MyJY9NxQPi7ZI14N/GFwpQ="',
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    key = M3u8Key(key=bytes.fromhex("34623235336163353939353834643437"))
    dl = M3u8Downloader(
        m3u8_url=url,
        save_path=f"../../downloads/{name}",
        max_workers=64,
        headers=headers,
        key=key,
    )
    await dl.run(del_hls=False, merge=True)


if __name__ == "__main__":
    asyncio.run(main())
