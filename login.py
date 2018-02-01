# -*- coding: utf-8 -*-
import requests
import re
import json

class LoginHuaBan:

    def __init__(self):
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Length": "60",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "huaban.com",
            "Origin": "http://huaban.com",
            "Referer": "http://huaban.com/login/?next=%2F",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": """Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 
            (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1"""
        }
        self.login_url = "https://huaban.com/auth/"
        self.session = requests.session()

    def islogin(self):
        cookie = self.get_cookie()
        url = "https://huaban.com/login/?next=%2F"
        re_url = re.compile(r'app.page\["\$url"\] = "(.*?)";')
        resp = requests.get(url, cookies=cookie).text
        get_title = re_url.search(resp)
        if get_title.groups()[0] != '/':
            return False
        else:
            return True

    def re_get_cookie(self, email, password):
        self.data = {
            "_ref": "mobile",
            "email": email,  # 输入账号
            "password": password  # 输入密码
        }
        self.session.post(self.login_url, self.data, headers=self.headers)
        url = "https://huaban.com/"
        res = self.session.get(url)
        cookie = res.cookies.get_dict()
        with open('cookie.json', 'w') as c:
            json.dump(cookie, c)

    def get_cookie(self):
        with open('cookie.json', 'r') as c:
            cookie = json.load(c)
        return cookie

    def get_user_information(self):
        cookie = self.get_cookie()  # 获取cookie
        url = "https://huaban.com/"
        html = self.session.get(url, cookies=cookie).content.decode('utf-8')
        re_user = re.compile(r'"user":(.*?), "avatar"')    # 获取用户的信息(id,用户名,花瓣个人主页)
        get_user = re_user.search(html)
        json_user = json.loads(get_user.groups()[0] + '}')
        return json_user
