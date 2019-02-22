# /usr/bin/env python
# coding:utf-8
"""
Author: zhiying
URL: www.zhouzying.cn
Data: 2019-01-24
Description: B站用户信息爬虫
抓取字段：用户id，昵称，性别，头像，等级，经验值，粉丝数，生日，地址，注册时间，签名，等级与经验值等。抓取之后生成B站用户数据报告。
"""
import requests
import time
import pymysql.cursors


def get_info():
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
              'Chrome/69.0.3497.100 Safari/537.36"}

    # B站创始人的个人信息url = 'http://api.bilibili.com/x/space/acc/info?mid=2&jsonp=jsonp'
    # 对应页面为http://space.bilibili.com/2
    # mid = 1 开始， mid = 5406,5824存在异常
    mid = 5825
    while True:

        url = 'http://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(mid)
        r = requests.get(url, headers=headers)
        if r.json()['code'] == 0:
            # print(r.json()['data']['name'])
            data = r.json()['data']
            yield data

        if r.json()['code'] == -400:
            with open('log.txt', 'a', encoding='utf-8') as f:
                f.write("B站共有{}用户。\n".format(mid - 1))
                f.close()
            break
        # 每爬1000条休息10s
        if mid % 1000 == 0:
            time.sleep(10)
        mid += 1


def save_to_databases():
    # Connect to the database
    connection = pymysql.connect(host='localhost',      # host是数据库主机地址
                                 user='root',     # 数据库用户名
                                 password='',   # 数据库密码
                                 # 数据库名(可选)
                                 db='Bilibili_infos',          # 选择要操作的数据库名(可选)
                                 charset='utf8mb4',         # 字符(可选)
                                 cursorclass=pymysql.cursors.DictCursor)     # 可选参数
    print("MySQL登录成功")
    try:
        for item in get_info():
            # 用户id
            uid = item['mid']
            # 昵称
            name = item['name']
            # 性别

            sex = item['sex']
            # 头像
            face_url = item['face']
            # 等级
            rank = item['level']
            # 经验值
            coins = item['coins']
            # 生日
            birth = item['birthday']
            # 地址
            # place = item['']
            # 签名
            sign = item['sign']
            sign = sign.strip()
            # 注册时间
            jointime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item['jointime']))

            # 关注数
            # 粉丝数
            # 播放数
            print('用户id：{} 昵称：{} 性别：{} 等级：{} 经验值：{} 生日：{} 签名：{} 注册时间：{}'.format(uid, name, sex, rank, coins, birth, sign, jointime))
            try:
                with connection.cursor() as cursor:
                    # Create a new record
                        # sql = "INSERT INTO `infos` (`uid`, `name`, `sex`, `birth`, `sign`, `jointime`, `face_url`, `rank`, `coins`) VALUES (uid, name, sex, birth, sign, jointime, face_url, rank, coins);"
                        # sql = "INSERT INTO info3 (uid, name, sign) VALUES ({},{}, {})".format(uid, name, sign)

                        cursor.execute('INSERT INTO `info4` (`uid`, `name`, `sex`, `rank`, `coins`, `birth`,'
                                       ' `sign`, `jointime`) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s");'
                                       % (uid, name, sex, rank, coins, birth, sign, jointime))

                        # connection is not autocommit by default. So you must commit to save
                        # your changes.
                connection.commit()

            except:
                with open('error.txt', 'a') as f:
                    f.write('{} 出现错误！\n'.format(uid))
                    f.close()
                continue

    finally:
        connection.close()


save_to_databases()
