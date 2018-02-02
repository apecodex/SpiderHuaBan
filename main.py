from login import LoginHuaBan
from spider_image import SpiderImage
from urllib.parse import quote
import os

"""
main file

email 输入账号
password 输入密码
----------------
url: 
默认爬取关注的图片
all 爬取最新的图片
search 爬取搜索到的图片
----------------
"""

class Main():
    if os.path.exists("cookie.json") == False:
        with open("cookie.json", 'w') as w:
            w.write("{}")

    def __init__(self):
        self.l = LoginHuaBan()
        self.s = SpiderImage()

        self.email = ""    # 输入账号
        self.password = ""    # 输入密码
        self.url = ""    # 输入需要爬取的页面,默认爬取关注的发布者的图片,即 ""   注: 默认为 "" 爬取最新的图片 all  爬取搜索的图片 search
        self.search = ""    # 输入要爬取的图片关键字。例如: 美女。 注: 如果要爬取搜索的图片，请在上面的 self.url 写上 search

    def run(self):
        try:
            information = self.l.get_user_information()
            print("|" + "-" * int(len(information['username']) + len(str(information['user_id'])) + len("https://huaban.com/") + len(information['urlname']) + 24) + "|")
            print("| username: {} id: {} home: {} |".format(information['username'], information['user_id'], "https://huaban.com/" + information['urlname']))
            print("|" + "-" * int(len(information['username']) + len(str(information['user_id'])) + len("https://huaban.com/") + len(information['urlname']) + 24) + "|")
            if self.url == "":
                print("爬取关注的图片.............")
                self.s.get_home_image()
            elif self.url == "all":
                print("爬取最新的图片..............")
                self.s.get_all_image("all")
            elif self.url == "search":
                print("爬取搜索的图片..............")
                if self.search == "":
                    print("请输入要爬取的关键字~")
                else:
                    q = quote(self.search)
                    self.s.get_all_image(q)
            else:
                print("开发中......")
        except TypeError:
            pass

    def main(self):
        if self.email == "" or self.password == "":
            print("请输入账号和密码")
        else:
            if self.l.islogin() == True:
                self.run()
            elif self.l.islogin() == False:
                print("登陆中......")
                self.l.re_get_cookie(self.email, self.password)
                if self.l.islogin() == True:
                    print("请重新运行代码")
                elif self.l.islogin() == False:
                    print("账号或密码错误!")
            else:
                pass

if __name__ == '__main__':
    m = Main()
    m.main()
