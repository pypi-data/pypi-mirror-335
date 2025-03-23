MJ_RELAX = 0
d1 = {"mj_fast_blend": 0.08,
    "mj_fast_custom_oom": 0,
    "mj_fast_describe": 0.04,
    "mj_fast_high_variation": 0.08,
    "mj_fast_imagine": 0.08,
    "mj_fast_inpaint": 0,
    "mj_fast_low_variation": 0.08,
    "mj_fast_modal": 0.08,
    "mj_fast_pan": 0.08,
    "mj_fast_pic_reader": 0,
    "mj_fast_prompt_analyzer": 0,
    "mj_fast_prompt_analyzer_extended": 0,
    "mj_fast_reroll": 0.08,
    "mj_fast_shorten": 0.08,
    "mj_fast_upload": 0.01,
    "mj_fast_upscale": 0.04,
    "mj_fast_upscale_creative": 0.08,
    "mj_fast_upscale_subtle": 0.08,
    "mj_fast_variation": 0.08,
    "mj_fast_zoom": 0.08,}

d2 = {
"mj_relax_blend": 0.08 * MJ_RELAX,
    "mj_relax_custom_oom": 0,
    "mj_relax_describe": 0.04 * MJ_RELAX,
    "mj_relax_high_variation": 0.08 * MJ_RELAX,
    "mj_relax_imagine": 0.08 * MJ_RELAX,
    "mj_relax_inpaint": 0,
    "mj_relax_low_variation": 0.08 * MJ_RELAX,
    "mj_relax_modal": 0.08 * MJ_RELAX,
    "mj_relax_pan": 0.08 * MJ_RELAX,
    "mj_relax_pic_reader": 0,
    "mj_relax_prompt_analyzer": 0,
    "mj_relax_prompt_analyzer_extended": 0,
    "mj_relax_reroll": 0.08 * MJ_RELAX,
    "mj_relax_shorten": 0.08 * MJ_RELAX,
    "mj_relax_upload": 0.01 * MJ_RELAX,
    "mj_relax_upscale": 0.04 * 1,
    "mj_relax_upscale_creative": 0.08 * 1,
    "mj_relax_upscale_subtle": 0.08 * 1,
    "mj_relax_variation": 0.08 * 1,
    "mj_relax_zoom": 0.08 * MJ_RELAX,
}

d = dict(zip(d1, d2))


def fetch_video_result(file_id: str):
    print("---------------视频生成成功，下载中---------------")
    url = "https://api.minimax.chat/v1/files/retrieve?file_id="+file_id
    headers = {
        'authorization': 'Bearer '+api_key,
    }

    response = requests.request("GET", url, headers=headers)
    print(response.text)

    download_url = response.json()['file']['download_url']
    print("视频下载链接：" + download_url)
    with open(output_file_name, 'wb') as f:
        f.write(requests.get(download_url).content)
    print("已下载在："+os.getcwd()+'/'+output_file_name)


