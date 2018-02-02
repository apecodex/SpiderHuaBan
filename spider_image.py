import requests
import json
import re
import random
import os
from login import LoginHuaBan
from urllib.parse import unquote
import time


class SpiderImage(LoginHuaBan):
    """
    爬取图片的的地址
    """
    def __init__(self):
        super(SpiderImage, self).__init__()
        # self.session = requests.session()
        self.headers['User-Agent'] = '''Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36
         (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'''
        self.cookie = self.get_cookie()  # 获取cookie

    def get_home_frist_id(self):
        """获取第一轮的第一个图片id，为下一轮做准备"""
        url = "https://huaban.com/"
        html = self.session.get(url, cookies=self.cookie).content.decode('utf-8')
        re_pins = re.compile(r'"pin_id":(.*?),')    # 获取刚开始的图片id,为了下一轮的图片做准备
        get_pins = re_pins.search(html)
        return str(get_pins.groups()[0])   # 返回用户信息， 第一张图片的id

    # 获取关注的作者发布的图片
    def get_home_image(self):
        def check_raw_text(text):    # 部分作者的这一个值的空的
            if text.strip() == "":
                return "No raw_text"
            else:
                return text

        last_img_pin_id = self.get_home_frist_id()    # 得到第一轮的第一个id
        num = 1
        while True:
            randoms = "".join([chr(random.randint(65, 90)).lower() for r in range(3)]) + str(random.randint(0, 9))  # 随机生成4个字母和1个数字
            url  = "http://huaban.com/?jd2{}&max={}&limit=20&wfl=1".format(randoms, last_img_pin_id)
            get_json = json.loads(self.session.get(url, cookies=self.cookie).content.decode('utf-8'))
            if get_json['pins'] == []:    #  如果为空列表,则判断爬取完成~
                print("爬完啦~共计: {} 张图片".format(num))
                break
            for img_date in get_json['pins']:
                num += 1
                img_username = img_date['user']['username']    # 发布图片的作者
                pin_id = img_date['pin_id']    # 图片的id
                img_key = img_date['file']['key']    # 图片的key,用于拼接图片的url地址
                img_raw_text = check_raw_text(img_date['raw_text'].replace('\n', ''))    # 图片介绍, 部分为空
                img_description = img_date['board']['description'].replace('\n', '')    # 描述
                img_title = img_date['board']['title'].replace('\n', '')    # 图片的标题
                img_type = img_date['file']['type'].split('/')[-1]    # 图片类型
                floder = "home"    # 默认爬取关注的采集
                print("正在爬取 发布者: {} 的图片 id: {} Key: {} 标题： {} 描述: {}".format(img_username, pin_id, img_key, img_title, img_description))
                self.download(pin_id, img_key, img_type, floder)    # 下载图片
            last_img_pin_id = get_json['pins'][-1]['pin_id']

    def get_all_image(self, args):
        if args == "all":
            url = "https://huaban.com/{}".format(args)
            folder = "all"
        else:
            folder = unquote(args)
            url = "https://huaban.com/search/?q={}&jd5gz4om&page=1&per_page=20&wfl=1".format(args)
            get_total = self.session.get(url, cookies=self.cookie).content.decode('utf-8')
            re_search_total = re.compile(r'app.page\["pin_count"\] = (.*?);')
            get_search_total = re_search_total.search(get_total)
            search_total = int(get_search_total.groups()[0])
            if search_total == 0:
                print("没有搜索到关于 '{}' 的图片".format(args))
                exit()
            else:
                print("搜索到的 '{}' 共计 {} 张".format(folder, search_total))
        total = 1
        snum = 2
        while True:
            html = self.session.get(url, cookies=self.cookie).content.decode('utf-8')
            re_search_total = re.compile(r'app.page["pin_count"] = (.*?);')
            re_pins = re.compile(r'app.page\["pins"\] = \[(.*?)\];')    # 所有数据
            get_pins = re_pins.findall(html)
            re_pin_id = re.compile(r'"pin_id":(.*?),')    # 所有的图片id
            re_user_id = re.compile(r'"file":(.*?})')
            re_username = re.compile(r'"username":"(.*?)",')    # 用户名
            re_title_description = re.compile(r'"title":"(.*?)", "description":"(.*?)", ')    # 标题和描述
            get_pin_id_key = [i for i in re_pin_id.findall(get_pins[0]) if '}' not in i]    # 用户id和图片的key
            if get_pin_id_key == []:
                print("爬完啦~共计: {}".format(total))
                break
            get_title_description = re_title_description.findall(get_pins[0])    # 图片的标题和描述
            get_username = re_username.findall(get_pins[0])
            for i, t, pid, u in zip(re_user_id.findall(get_pins[0]), get_title_description, get_pin_id_key, get_username):
                get_data_json = json.loads(i.replace('[{"color":', ''))
                get_data_json['title'] = t[0]
                get_data_json['description'] = t[1]
                get_data_json['pin_id'] = pid
                get_data_json['username'] = u
                pin_id = get_data_json['pin_id']
                username = get_data_json['username']
                key = get_data_json['key']
                title = get_data_json['title']
                description = get_data_json['description']
                types = get_data_json['type'].split('/')[-1]
                print("正在爬取 第 {} 张 发布者: {} 的图片 id: {} Key: {} 标题： {} 描述: {}".format(total, username, pin_id, key, title, description))
                self.download(pin_id, key, types, folder)
                total += 1
            randoms = "".join([chr(random.randint(65, 90)).lower() for i in range(3)]) + str(random.randint(0, 9))  # 随机生成4个字母和1个数字
            last_id = get_data_json['pin_id']
            if args == "all":
                url = "https://huaban.com/all/?jd4{}&max={}&limit=20&wfl=1".format(randoms, last_id)
            else:
                url = "https://huaban.com/search/?q={}&jd5gz4om&page={}&per_page=20&wfl=1".format(args, snum)
                snum+=1
            time.sleep(1+random.random())

    def download(self, pin_id, key, img_type, folder):
        try:
            os.mkdir("{}".format(folder))
        except FileExistsError:
            pass
        url = "http://hbimg.b0.upaiyun.com/" + key
        req = requests.get(url, cookies=self.cookie)    # 下载图片需要登陆才行，所以需要cookie,
        with open('{}/{}.{}'.format(folder, pin_id, img_type), 'wb') as fp:
            fp.write(req.content)
