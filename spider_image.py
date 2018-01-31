import requests
import json
import re
import random
import os
from login import LoginHuaBan

class Spider_Image(LoginHuaBan):

    def __init__(self):
        super(Spider_Image, self).__init__()
        # self.session = requests.session()
        self.headers['User-Agent'] = '''Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36
         (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'''
        self.cookie = self.get_cookie()  # 获取cookie

    def get_home_frist_id(self):
        url = "https://huaban.com/"
        html = self.session.get(url, cookies=self.cookie).content.decode('utf-8')
        # re_pins = re.compile(r'app.page\["pins"\] = \[(.*?)\];')
        re_pins = re.compile(r'"pin_id":(.*?),')    # 获取刚开始的图片id,为了下一轮的图片做准备
        get_pins = re_pins.search(html)
        return str(get_pins.groups()[0])   # 返回用户信息， 第一张图片的id

    def get_image_pin_id(self):
        def check_raw_text(text):
            if text.strip() == "":
                return "No raw_text"
            else:
                return text
        last_img_pin_id = self.get_home_frist_id()
        num = 1
        while True:
            randoms = "".join([chr(random.randint(65, 90)).lower() for i in range(3)]) + str(random.randint(0, 9))  # 随机生成4个字母和1个数字
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
                img_raw_text = img_date['raw_text'].replace('\n', '')    # 图片介绍
                img_description = img_date['board']['description'].replace('\n', '')    # 描述
                img_title = img_date['board']['title'].replace('\n', '')    # 图片的标题
                img_type = img_date['file']['type'].split('/')[-1]    # 图片类型
                floder = "home"    # 默认爬取关注的采集
                print("正在爬取 发布者: {} 的图片 id: {} Key: {} 标题： {} 描述: {}".format(img_username, pin_id, img_key, img_title, img_description))
                self.download(pin_id, img_key, img_type, floder)
            last_img_pin_id = get_json['pins'][-1]['pin_id']

    def download(self,pin_id, key, img_type, folder):
        try:
            os.mkdir("{}".format(folder))
        except FileExistsError:
            pass
        url = "http://hbimg.b0.upaiyun.com/" + key
        req = requests.get(url, cookies=self.cookie)    # 下载图片需要登陆才行，所以需要cookie,
        with open('{}/{}.{}'.format(folder, pin_id, img_type), 'wb') as fp:
            fp.write(req.content)


if __name__ == '__main__':
    s = Spider_Image()
    s.get_image_pin_id()