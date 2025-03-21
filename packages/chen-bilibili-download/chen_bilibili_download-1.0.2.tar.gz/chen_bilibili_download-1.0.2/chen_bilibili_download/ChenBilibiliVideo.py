""" 这是获取哔哩哔哩音频的类
    (还未能实现视频合并，没想好如何处理2025年3月3日)
    1. 可进行搜索
    2. 可显性显示
    3. 可自动判断是否为特殊模式（多个单独，多个和为一个单独）
    4. 可单个下载
    5. 可多个下载（单进程、多进程）"""
import os
from .ChenSpiderBasicInfo import ChenSpiderBasicInfo
import json
import multiprocessing
import re
import time
from os import makedirs
from os.path import exists
import requests
from lxml import etree
import prettytable as pt
from moviepy import VideoFileClip, AudioFileClip


class ChenBilibiliVideo(ChenSpiderBasicInfo):
    """
    这是获取哔哩哔哩音频的类
    1. 可进行搜索
    2. 可显性显示
    3. 可自动判断是否为特殊模式（多个单独，多个和为一个单独）
    4. 可单个下载
    5. 可多个下载（单进程、多进程）
    """

    def __init__(self):
        super().__init__()

        try:
            with open('Chen_Cookies.json_1', 'r', encoding='utf-8') as file_json:
                cookies = json.load(file_json)
            cookies['bili_ticket_expires'] = str(int(time.time()) + 3 * 86400)
            self.dir_file_name = None
            self.cookies = cookies
        except Exception:
            user_profile = os.environ.get("USERPROFILE")  # Windows
            # 拼接出桌面的路径
            desktop_path = os.path.join(user_profile, "Desktop")+ "/下载的歌曲"
            # 如果不存在则创建，如果存在则不执or行后边代码
            exists(desktop_path) or makedirs(desktop_path)
            print('下载地址为：',desktop_path)
            self.dir_file_name = desktop_path
            self.cookies = None
        self.headers['Referer'] = 'https://www.bilibili.com/'
        self.search_info_dict = None
        self.search_video_url = None
        self.search_video_title = None
        self.bilibili_play_tree = None
        self.bilibili_play_info = None
        self.bilibili_play_single_name = None
        self.bilibili_play_name = None
        self.judge_if_multiply_video_index = None
        self.down_model = None
        self.info_url = None
        self.video_url = None
        self.audio_url = None
        self.last_name = None

        self.video_module = None

    def get_desktop_path(self):
        # 获取当前用户的主目录
        user_profile = os.environ.get("USERPROFILE")  # Windows

        # 拼接出桌面的路径
        desktop_path = os.path.join(user_profile, "Desktop")
        return desktop_path

    def search_system(self):
        """ 搜索函数，输入要搜索的字符串，输出列表显示，输入想要的视频，返回想要的视频ULR和TITLE"""
        keyword = input('输入想要查询的:')
        info_dict = []
        url = fr'https://search.bilibili.com/video?keyword={keyword}'
        try:
            request = requests.get(url=url, headers=self.headers, proxies=self.random_proxy).text
            tree = etree.HTML(request)
            div_list = tree.xpath('//div[@class = "video-list row"]')[0]
            href_url = div_list.xpath('//div[@class = "bili-video-card__info--right"]/a/@href')
            title = div_list.xpath('//div[@class = "bili-video-card__info--right"]/a/h3/@title')
            # play_volume = div_list.xpath('//span[@class = "bili-video-card__stats--item"][1]/span/text()')
            # print(href_url)
            # print(title)
            # print(play_volume)
            # input("这是以恶搞段点")
            table = pt.PrettyTable()
            table.title = '搜索列表'
            table.field_names = ['标号', '标题名称']
            for i in range(len(href_url)):
                value_dict = {
                    "Title": title[i],
                    'href': 'https:' + str(href_url[i]),
                    # 'play_volume': play_volume[i]
                }
                info_dict.append(value_dict)
                table.add_row([i + 1, title[i]])
            print(table)

            search_idex = int(input('输入想要获取的编号:'))
            self.search_video_url = info_dict[search_idex - 1]['href']
            self.search_video_title = info_dict[search_idex - 1]['Title']
            # print(self.search_video_url)
            # print(self.search_video_title)
            return self.search_video_url, self.search_video_title
        except Exception:
            print('查询出现错误！！')

    def change_standard_filename(self, filename):
        """ 这是一个将文件名称标准化的函数 """
        # 去除前后空格
        filename = filename.strip()

        # 替换操作系统不允许的字符（Windows的例子）
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, "_", filename)

        # 确保文件名没有过长
        max_length = 200  # Windows文件名最大长度限制
        if len(filename) > max_length:
            filename = filename[:max_length]
        return filename

    def judge_if_multiply_video(self, module=0):
        """ 这是一个判断是否是下载当前音乐还是当前全部音乐的函数 """
        if int(module) == 0:
            self.info_url = 'https://www.bilibili.com/video/' + input("输入视频代码：如（BV1aumjYZEcG）")
        if int(module) == 1:
            self.info_url = self.search_video_url

        request = requests.get(url=self.info_url, headers=self.headers,
                               proxies=self.get_random_proxy()).text
        tree = etree.HTML(request)
        # 检测是否为单独视频合并的
        if tree.xpath('/html/body//div[@class="video-pod__list section"]'):
            self.video_module = "String"
            multiply_video_info = tree.xpath(
                '/html/body//div[@class="video-pod__list section"]')
            main_video_list = [sole_video_name.xpath("./div/div/div[1]/@title")[0] for sole_video_name in
                               multiply_video_info[0].xpath('./div')]
            table = pt.PrettyTable()
            table.title = '视频列表'
            table.field_names = ['标号', '标题名称']
            for i in range(len(main_video_list)):
                table.add_row([i + 1, main_video_list[i]])
            print(f'【+】一共搜索出{len(main_video_list)}个【+】')
            print(table)
            self.judge_if_multiply_video_index = int(input("检测到有多个视频是否全部下载？|【0】否、【1】是|："))
            if self.judge_if_multiply_video_index == 0:
                return self.info_url
            if self.judge_if_multiply_video_index == 1:
                sole_video_list = ['https://www.bilibili.com/video/' + sole_video.xpath('./@data-key')[0] for sole_video
                                   in multiply_video_info[0].xpath('./div')]
                return sole_video_list
        # 检测是否为合集
        if tree.xpath(
                '/html/body//div[@class="video-pod__list multip list"]'):
            self.video_module = "Number"
            multiply_video_info = tree.xpath(
                '/html/body//div[@class="video-pod__list multip list"]')
            main_video_list = [sole_video_name.xpath('.//div[@class="title"]/@title')[0] for sole_video_name in
                               multiply_video_info[0].xpath('./div')]
            table = pt.PrettyTable()
            table.title = '视频列表'
            table.field_names = ['标号', '标题名称']
            for i in range(len(main_video_list)):
                table.add_row([i + 1, main_video_list[i]])
            print(f'【+】一共搜索出{len(main_video_list)}个【+】')
            print(table)
            self.judge_if_multiply_video_index = int(input("检测到有多个视频是否全部下载？|【0】否、【1】是|："))
            if self.judge_if_multiply_video_index == 0:
                return self.info_url
            if self.judge_if_multiply_video_index == 1:
                sole_video_list = [self.info_url + '?p=' + str(sole_video_page) for sole_video_page
                                   in range(1, len(multiply_video_info[0].xpath('./div')) + 1)]

                return sole_video_list
        else:
            print('没发现其他音乐！正在下载该音乐！')
            # print(self.info_url)
            return self.info_url

    def get_bilibili_play_info(self, info_url):
        """ 这是一个获得全部播放信息的函数 """
        '''
        参数意思：
            buvid3: 唯一标识用户的ID，用于追踪和识别用户。
            b_nut: 哔哩哔哩用于记录用户信息的参数，可能与广告或个性化推荐相关。
            _uuid: 唯一标识符，用于区分每个用户，保证用户在不同会话中的一致性。
            enable_web_push: 启用或禁用网页推送通知，值通常为 "DISABLE" 或 "ENABLE"。
            buvid4: 另一个用于标识用户的唯一ID，可能用于会话、数据跟踪等。
            DedeUserID: 哔哩哔哩用户ID，用于标识用户在B站的账户。
            DedeUserID__ckMd5: DedeUserID字段的MD5加密值。
            rpdid: 哔哩哔哩用于追踪用户行为的标识符。
            header_theme_version: 记录用户选择的B站网页主题的版本（例如“CLOSE”表示关闭了某个功能或设置）。
            buvid_fp_plain: 用于标识用户设备的字段，通常用于数据收集。
            fingerprint: 唯一的浏览器指纹，帮助识别用户设备和行为。
            LIVE_BUVID: 与直播相关的唯一标识符，标识用户观看直播时的设备。
            buvid_fp: 用户的设备指纹，用于识别和追踪。
            PVID: 页面访问标识符，通常用于跟踪页面加载的次数。
            enable_feed_channel: 表示是否启用某种类型的内容推荐或频道功能。
            home_feed_column: 用户在主页上看到的推荐内容的列数。
            bmg_af_switch: 可能与广告推送或其他功能相关的开关参数。
            bmg_src_def_domain: 用于指示广告或资源请求的源域名。
            CURRENT_QUALITY: 当前播放的视频质量设置。
            bp_t_offset_103117556: 一种与用户视频观看偏好相关的标识符。
            bili_ticket: 用于认证和授权的令牌。
            bili_ticket_expires: bili_ticket 的过期时间戳。
            SESSDATA: 会话数据，包含用户登录状态和其他信息。
            bili_jct: 用于防止CSRF攻击的令牌。
            sid: 会话ID，用于标识用户当前的会话状态。
            browser_resolution: 用户浏览器的屏幕分辨率。
            CURRENT_FNVAL: 当前的视频播放设置，可能与视频的质量或格式有关。
            b_lsid: 哔哩哔哩的会话ID，可能用于跟踪用户在网站上的行为和状态。

        '''
        if self.cookies:
            request = requests.get(url=info_url,cookies=self.cookies, headers=self.headers, proxies=self.get_random_proxy()).text
        else:
            request = requests.get(url=info_url, headers=self.headers,
                                   proxies=self.get_random_proxy()).text
        tree = etree.HTML(request)
        self.bilibili_play_name = self.change_standard_filename(
            tree.xpath('/html/body/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/h1/@title')[0])
        if self.video_module == "Number":
            self.bilibili_play_single_name = self.change_standard_filename(
                tree.xpath('/html/head/title/text()')[0][:-14])
        info = tree.xpath('/html/head/script[4]')[0].text[20:]
        # 全部播放数据字典
        self.bilibili_play_info = json.loads(info)
        # pprint.pprint(self.bilibili_play_info['data']['dash']['video'])
        # input()
        # print(self.bilibili_play_info)
        # input('这是个断点')
        # 视频数据
        self.video_url = self.bilibili_play_info['data']['dash']['video'][0]['baseUrl']
        # 音频数据
        self.audio_url = self.bilibili_play_info['data']['dash']['audio'][0]['baseUrl']
        # print(self.video_url,self.audio_url)

    def according_m4a_url_to_down_bilibili_video(self, video_url, dir_file_name, bilibili_play_name, last_name=".mp4"):
        """ 根据m4aurl来下载视频"""
        request = requests.get(url=video_url, headers=self.headers).content
        exists(dir_file_name) or makedirs(dir_file_name)
        with open(f"{dir_file_name}/{bilibili_play_name}{last_name}",
                  'wb') as fp:
            fp.write(request)
        print(f"{dir_file_name}/{bilibili_play_name}{last_name}下载完毕")

    def down_bilibili_audio(self):
        """ 下载音频 (或者视频，还没更新视频) """
        dir_file_name = self.dir_file_name
        # try:
        request = requests.get(url=self.audio_url, headers=self.headers).content
        print(f'开始下载音乐：{self.change_standard_filename(self.bilibili_play_name)}')

        if self.video_module == "String":
            # 如果不存在则创建，如果存在则不执or行后边代码
            exists(dir_file_name) or makedirs(dir_file_name)
            with open(f"{dir_file_name}/{self.change_standard_filename(self.bilibili_play_name)}{self.last_name}",
                      'wb') as fp:
                fp.write(request)
            # print("下载地址为：", dir_file_name)
            print(f"\t{self.change_standard_filename(self.bilibili_play_name)}下载完毕\n", "\t\t下载地址为：",
                  f"{dir_file_name}/{self.bilibili_play_name}{self.last_name}")
        if self.video_module == "Number":
            # 如果不存在则创建，如果存在则不执or行后边代码
            exists(dir_file_name + "/" + self.change_standard_filename(self.bilibili_play_name)) or makedirs(
                dir_file_name + "/" + self.change_standard_filename(self.bilibili_play_name))
            with open(
                    f"{dir_file_name}/{self.change_standard_filename(self.bilibili_play_name)}/{self.change_standard_filename(self.bilibili_play_single_name)}{self.last_name}",
                    'wb') as fp:
                fp.write(request)
            # print("下载地址为：", dir_file_name)
            print(f"\t{self.change_standard_filename(self.bilibili_play_single_name)}下载完毕\n", "\t\t下载地址为：",
                  f"{dir_file_name}/{self.change_standard_filename(self.bilibili_play_name)}/{self.change_standard_filename(self.bilibili_play_single_name)}{self.last_name}")
        else:
            with open(
                    f"{dir_file_name}/{self.change_standard_filename(self.bilibili_play_name)}{self.last_name}",
                    'wb') as fp:
                fp.write(request)
            # print("下载地址为：", dir_file_name)
            if self.video_module != "Number" and self.video_module != "String":
                print(f"\t{self.change_standard_filename(self.bilibili_play_name)}下载完毕\n", "\t\t下载地址为：",
                      f"{dir_file_name}/{self.change_standard_filename(self.bilibili_play_name)}{self.last_name}")

        # except Exception as e:
        #     print(self.bilibili_play_name, '下载发生错误')
        #     print(e)

    def down_bilibili_video(self):
        """ 下载视频 """
        dir_file_name = self.dir_file_name
        audio_request = requests.get(url=self.audio_url, headers=self.headers).content
        video_request = requests.get(url=self.video_url, headers=self.headers).content

        try:
            if self.video_module == "String":
                # 如果不存在则创建，如果存在则不执or行后边代码
                exists(dir_file_name) or makedirs(dir_file_name)
                # 写入音频
                audio_file_name = f"{dir_file_name}/{self.change_standard_filename(self.bilibili_play_name)}-audio.mp3"
                with open(audio_file_name, 'wb') as fp:
                    fp.write(audio_request)
                # 写入视频
                video_file_name = f"{dir_file_name}/{self.change_standard_filename(self.bilibili_play_name)}-video{self.last_name}"
                with open(video_file_name, 'wb') as fp:
                    fp.write(video_request)
                print(f"\t{self.change_standard_filename(self.bilibili_play_name)}音、视频下载完毕\n",
                      f"\t\t下载地址为{video_file_name}")
                print('正在合并视频~~~~~~')
                # 加载视频和音频
                video = VideoFileClip(video_file_name)
                audio = AudioFileClip(audio_file_name)
                # 将音频添加到视频中
                video = video.with_audio(audio)
                # 输出合并后的视频文件
                output_path = f"{dir_file_name}/{self.change_standard_filename(self.bilibili_play_name)}{self.last_name}"
                video.write_videofile(output_path)
                # 删除音频、视频文件
                os.remove(audio_file_name)
                os.remove(video_file_name)
                print(output_path, "视频下载完毕")

            if self.video_module == "Number":
                # 如果不存在则创建，如果存在则不执or行后边代码
                exists(dir_file_name + "/" + self.change_standard_filename(self.bilibili_play_name)) or makedirs(
                    dir_file_name + "/" + self.change_standard_filename(self.bilibili_play_name))
                # 写入音频
                audio_file_name = f"{dir_file_name}/{self.change_standard_filename(self.bilibili_play_name)}/{self.change_standard_filename(self.bilibili_play_single_name)}-audio.mp3"
                with open(audio_file_name, 'wb') as fp:
                    fp.write(audio_request)
                # 写入视频
                video_file_name = f"{dir_file_name}/{self.change_standard_filename(self.bilibili_play_name)}/{self.change_standard_filename(self.bilibili_play_single_name)}-video{self.last_name}"
                with open(video_file_name, 'wb') as fp:
                    fp.write(video_request)
                # print("下载地址为：", dir_file_name)
                print(f"\t{self.change_standard_filename(self.bilibili_play_single_name)}音、视频下载完毕\n",
                      f"\t\t下载地址为：{video_file_name}", )
                print('正在合并视频~~~~~~')
                # 加载视频和音频
                video = VideoFileClip(video_file_name)
                audio = AudioFileClip(audio_file_name)
                # 将音频添加到视频中
                video = video.with_audio(audio)
                # 输出合并后的视频文件
                output_path = f"{dir_file_name}/{self.change_standard_filename(self.bilibili_play_name)}/{self.change_standard_filename(self.bilibili_play_single_name)}{self.last_name}"
                video.write_videofile(output_path)
                # 删除音频、视频文件
                os.remove(audio_file_name)
                os.remove(video_file_name)
                print(output_path, "视频下载完毕")

        except Exception:
            print(self.bilibili_play_name, '下载发生错误')

    def judge_download_video_or_audio(self):
        """ 判断下载的下载器 """
        down_model = self.down_model
        if down_model == "v":
            self.last_name = ".mp4"
            self.down_bilibili_video()
        else:
            self.last_name = ".mp3"
            self.down_bilibili_audio()

    def multiply_down_bilibili_video(self, info_url):
        """ 多进程下载 """
        self.get_bilibili_play_info(info_url)
        # self.down_bilibili_audio()
        self.judge_download_video_or_audio()

    def main(self, down_model="a", dir_file_name="D:/歌曲"):
        """ 这是下载的总函数 """
        # --------------------基本参数----------------- #
        # 下载文件夹名称：(可更改)
        self.down_model = down_model
        if not self.dir_file_name:
            self.dir_file_name = fr"{dir_file_name}"
        # ------------------------------------------- #
        # 判断是否用下载器
        judge_if_use_search = 0
        if int(input('是否启用搜索引擎？|【0】否、【1】是|：')) == 1:
            self.search_system()
            judge_if_use_search = 1

        sole_video_list = self.judge_if_multiply_video(judge_if_use_search)
        # print(type(sole_video_list),sole_video_list)
        if type(sole_video_list) == list:
            if_multiply = int(input('是否多进程下载？|【0】否、【1】是|：'))
            print("【正在下载请稍等。。。。。】")
            # now_time = time.time()
            if int(if_multiply) == 0:
                for info_url in sole_video_list:
                    self.get_bilibili_play_info(info_url)
                    # self.down_bilibili_audio()
                    self.judge_download_video_or_audio()
                # print(time.time() - now_time)
            if int(if_multiply) == 1:
                pool = multiprocessing.Pool()
                pool.map(self.multiply_down_bilibili_video, sole_video_list)
                pool.close()
                pool.join()
                # print(time.time() - now_time)
        else:
            print("【正在下载请稍等。。。。。】")
            self.get_bilibili_play_info(sole_video_list)
            self.judge_download_video_or_audio()
