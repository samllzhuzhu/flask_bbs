import re
import os
import json
import xlwt
import requests



s = requests.Session()
# cookies序列化文件
COOKIES_FILE_PATH = 'taobao_login_cookies.txt'


class UsernameLogin:

    def __init__(self, loginId, umidToken, ua, password2):
        """
        账号登录对象
        :param loginId: 用户名
        :param umidToken: 新版登录新增参数
        :param ua: 淘宝的ua参数
        :param password2: 加密后的密码
        """
        # 检测是否需要验证码的URL
        self.user_check_url = 'https://login.taobao.com/newlogin/account/check.do?appName=taobao&fromSite=0'
        # 验证淘宝用户名密码URL
        self.verify_password_url = "https://login.taobao.com/newlogin/login.do?appName=taobao&fromSite=0"
        # 访问st码URL
        self.vst_url = 'https://login.taobao.com/member/vst.htm?st={}'
        # 淘宝个人 主页
        self.my_taobao_url = 'http://i.taobao.com/my_taobao.htm'

        # 淘宝用户名
        self.loginId = loginId
        # 淘宝用户名
        self.umidToken = umidToken
        # 淘宝关键参数，包含用户浏览器等一些信息，很多地方会使用，从浏览器或抓包工具中复制，可重复使用
        self.ua = ua
        # 加密后的密码，从浏览器或抓包工具中复制，可重复使用
        self.password2 = password2

        # 请求超时时间
        self.timeout = 3

    def _user_check(self):
        """
        检测账号是否需要验证码
        :return:
        """
        data = {
            'loginId': self.loginId,
            'ua': self.ua,
        }
        try:
            response = s.post(self.user_check_url, data=data, timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            print('检测是否需要验证码请求失败，原因：')
            raise e
        check_resp_data = response.json()['content']['data']
        needcode = False
        # 判断是否需要滑块验证，一般短时间密码错误多次可能出现
        if 'isCheckCodeShowed' in check_resp_data:
            needcode = True
        print('是否需要滑块验证：{}'.format(needcode))
        return needcode

    def _get_umidToken(self):
        """
        获取umidToken参数
        :return:
        """
        response = s.get('https://login.taobao.com/member/login.jhtml')
        st_match = re.search(r'"umidToken":"(.*?)"', response.text)
        print(st_match.group(1))
        return st_match.group(1)

    @property
    def _verify_password(self):
        """
        验证用户名密码，并获取st码申请URL
        :return: 验证成功返回st码申请地址
        """
        verify_password_headers = {
            'Origin': 'https://login.taobao.com',
            'content-type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d9HjW9WC&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F',
        }
        # 验证用户名密码参数
        verify_password_data = {
            'ua': self.ua,
            'loginId': self.loginId,
            'password2': self.password2,
            'umidToken': self.umidToken,
            'appEntrance': 'taobao_pc',
            'isMobile': 'false',
            'returnUrl': 'https://www.taobao.com/',
            'navPlatform': 'MacIntel',
        }
        try:
            response = s.post(self.verify_password_url, headers=verify_password_headers, data=verify_password_data,
                              timeout=self.timeout)
            response.raise_for_status()
            # 从返回的页面中提取申请st码地址
        except Exception as e:
            print('验证用户名和密码请求失败，原因：')
            raise e
        # 提取申请st码url
        apply_st_url_match = response.json()['content']['data']['asyncUrls'][0]
        # 存在则返回
        if apply_st_url_match:
            print('验证用户名密码成功，st码申请地址：{}'.format(apply_st_url_match))
            return apply_st_url_match
        else:
            raise RuntimeError('用户名密码验证失败！response：{}'.format(response.text))

    def _apply_st(self):
        """
        申请st码
        :return: st码
        """
        apply_st_url = self._verify_password
        try:
            response = s.get(apply_st_url)
            response.raise_for_status()
        except Exception as e:
            print('申请st码请求失败，原因：')
            raise e
        st_match = re.search(r'"data":{"st":"(.*?)"}', response.text)
        if st_match:
            print('获取st码成功，st码：{}'.format(st_match.group(1)))
            return st_match.group(1)
        else:
            raise RuntimeError('获取st码失败！response：{}'.format(response.text))

    def login(self):
        """
        使用st码登录
        :return:
        """
        # 加载cookies文件
        if self._load_cookies():
            return True
        # 判断是否需要滑块验证
        self._user_check()
        st = self._apply_st()
        headers = {
            'Host': 'login.taobao.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        try:
            response = s.get(self.vst_url.format(st), headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('st码登录请求，原因：')
            raise e
        # 登录成功，提取跳转淘宝用户主页url
        my_taobao_match = re.search(r'top.location.href = "(.*?)"', response.text)
        if my_taobao_match:
            print('登录淘宝成功，跳转链接：{}'.format(my_taobao_match.group(1)))
            self.my_taobao_url = my_taobao_match.group(1)
            self._serialization_cookies()
            return True
        else:
            raise RuntimeError('登录失败！response：{}'.format(response.text))

    def _load_cookies(self):
        # 1、判断cookies序列化文件是否存在
        if not os.path.exists(COOKIES_FILE_PATH):
            return False
        # 2、加载cookies
        s.cookies = self._deserialization_cookies()
        # 3、判断cookies是否过期
        try:
            self.get_taobao_nick_name()
        except Exception as e:
            os.remove(COOKIES_FILE_PATH)
            print('cookies过期，删除cookies文件！')
            return False
        print('加载淘宝cookies登录成功!!!')
        return True

    def _serialization_cookies(self):
        """
        序列化cookies
        :return:
        """
        cookies_dict = requests.utils.dict_from_cookiejar(s.cookies)
        with open(COOKIES_FILE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            print('保存cookies文件成功！')

    def _deserialization_cookies(self):
        """
        反序列化cookies
        :return:
        """
        with open(COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            cookies = requests.utils.cookiejar_from_dict(cookies_dict)
            return cookies

    def get_taobao_nick_name(self):
        """
        获取淘宝昵称
        :return: 淘宝昵称
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        try:
            response = s.get(self.my_taobao_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('获取淘宝主页请求失败！原因：')
            raise e
        # 提取淘宝昵称
        nick_name_match = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if nick_name_match:
            print('登录淘宝成功，你的用户名是：{}'.format(nick_name_match.group(1)))
            return nick_name_match.group(1)
        else:
            raise RuntimeError('获取淘宝昵称失败！response：{}'.format(response.text))

    def get_lsf_data(self):
        """获取螺蛳粉数据"""
        url = 'https://s.taobao.com/search?data-key=sort&data-value=sale-desc&ajax=true&_ksTS=1594262627349_715&callback=jsonp716&q=%E8%9E%BA%E7%8B%AE%E7%B2%89&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20200709&ie=utf8&sort=sale-desc'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'referer': "https://s.taobao.com/search?q=%E8%9E%BA%E7%8B%AE%E7%B2%89&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20200709&ie=utf8&sort=sale-desc",
            "cookie": "_samesite_flag_=true; cookie2=11f681ee3b5378744f173af6c6c559d4; t=18abb07fbb833c5081cab648fbd3937f; _tb_token_=e7b573808355b; thw=cn; enc=wBuAjMGd3VkFLnlPFvSdgmWHpAASOIYM8LbnH%2FADHKdXeK3Ubbs4sUuE%2FUXXzK7Jc8eDU%2Bghw9%2FP1mCUWPcp3A%3D%3D; _fbp=fb.1.1587094587364.848272401; tk_trace=oTRxOWSBNwn9dPyorMJE%2FoPdY8zfvmw%2Fq5hoqSoYRXNmalzzjhmUQ7%2Fjv18OWOxqjZPtuLCjmOdoLofAH%2FtIZnMM%2BXvdIvf3u2AWr4wt4kl%2FIPLheyD%2FpeqgDWcWaNE15vMcxDf75WicYs9zLFloC8HeEg3EryHUobS%2Bgqm3NT25sdLTWZGS%2FBVFRgTFC6zjtL7sBLB1oUcmoZQpyCQcPHloGSNYjkJy6h%2FHsPmS35NagonNmCs4jKZPPS3m7Q%2F%2FW0KHRW1oCECukldthSLm%2FYKgmM0%3D; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; cna=Lj/WFnF0yFQCASrEu7t0XqvF; v=0; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci%3D-1_1; lgc=%5Cu66F9%5Cu6D41%5Cu6C13%5Cu554A%5Cu66F9%5Cu6D41%5Cu6C13; dnk=%5Cu66F9%5Cu6D41%5Cu6C13%5Cu554A%5Cu66F9%5Cu6D41%5Cu6C13; tracknick=%5Cu66F9%5Cu6D41%5Cu6C13%5Cu554A%5Cu66F9%5Cu6D41%5Cu6C13; _m_h5_tk=82655ab83f4862cd6862c1ed85da0cf6_1594208160875; _m_h5_tk_enc=5d17e3fe6730dbe439ff9a69c2408cbe; sgcookie=ELpG0z4t9zfkDjkIw%2BETQ; unb=2237568151; uc3=lg2=W5iHLLyFOGW7aA%3D%3D&vt3=F8dBxGJkmBouEs9leHg%3D&id2=UUpidXGcASC82A%3D%3D&nk2=0R7gT350llqfVDM%2Bv40%3D; csg=af4879c4; cookie17=UUpidXGcASC82A%3D%3D; skt=dd162bd0f924cdcf; existShop=MTU5NDI2MDY4MA%3D%3D; uc4=nk4=0%400yaeJuPFN2MMVe6bHIOCuW%2B%2FyDoKJCSekQ%3D%3D&id4=0%40U2gosEAttjG0MAGydzEtd358f96a; _cc_=WqG3DMC9EA%3D%3D; _l_g_=Ug%3D%3D; sg=%E6%B0%9310; _nk_=%5Cu66F9%5Cu6D41%5Cu6C13%5Cu554A%5Cu66F9%5Cu6D41%5Cu6C13; cookie1=WvKT1KyPXX7w9fFyD1oVNn7lRE8ayN2MxS%2BvmH7%2BfYQ%3D; tfstk=cov5BPVJSep2OfcUU3iVz_e2wbBFap2500_DVIrIWD3UZ-tfksbuQNgJeH4YH1If.; uc1=cookie14=UoTV6OOOt2z80Q%3D%3D&cookie16=UIHiLt3xCS3yM2h4eKHS9lpEOw%3D%3D&existShop=false&cookie21=WqG3DMC9FxUx&cookie15=V32FPkk%2Fw0dUvg%3D%3D&pas=0; JSESSIONID=D8265DC36CD2659D50E191EF98F66681; l=eBSsW2WHQsd3cA56BOfZhurza779GIRfguPzaNbMiOB1txfnldFXqHw3C0YDI3QQEtCfTety3gWfeRh9JM4Nw2HvCbKrCyCuux7d.; isg=BMrKo2McoQPapSzm1U7Sm2McG7Zsu04V70u8OlQDF53EB2vBPEtpJVkxF3Pb98at"
        }
        response = s.get(url, headers=headers)
        data = json.loads(re.match(".*?({.*}).*",  str(response.content, 'utf-8'), re.S).group(1))
        data = data['mods']['itemlist']['data']['auctions']
        data_list = []
        for i in range(20):
            data_dict = {}
            d = data[i]
            print('排名:', i+1)
            print('标题:', d['raw_title'])
            print('价格:', d['view_price'])
            print('店铺名:', d['nick'])
            print('收货:', d['view_sales'])
            print('地址:', d['item_loc'])
            nid = d['nid']
            count_url = 'https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?jsv=2.4.8&appKey=12574478&api=mtop.taobao.detail.getdetail&v=6.0&dataType=jsonp&ttid=2017%40taobao_h5_6.6.0&AntiCreep=true&type=jsonp&callback=mtopjsonp2&data=%7B%22itemNumId%22%3A%22{}%22%7D'.format(nid)
            count_data = s.get(count_url, headers=headers)
            count_data = json.loads(re.match(".*?({.*}).*", str(count_data.content, 'utf-8'), re.S).group(1))
            print('评价数', count_data['data']['item']['commentCount'])
            print('收藏数', count_data['data']['item']['favcount'])
            data_dict['num'] = i+1
            data_dict['title'] = d['raw_title']
            data_dict['price'] = d['view_price']
            data_dict['shop_name'] = d['nick']
            data_dict['view_sales'] = d['view_sales']
            data_dict['address'] = d['item_loc']
            data_dict['comment'] = count_data['data']['item']['commentCount']
            data_dict['collect'] = count_data['data']['item']['favcount']
            data_list.append(data_dict)
            print('-'*50)

        # 写入excel
        # 将列表中的数据统一写入excel中
        # 创建 xls 文件对象, 就是创建一个excel文件
        wb = xlwt.Workbook()

        # 新增表单页,就是excel下面的sheet名字，可以创建多个
        sh1 = wb.add_sheet('淘宝数据')

        # 然后按照位置来添加数据,括号里面第一个参数是行，第二个参数是列,第三个参数是写入的数据,表示excel中第几行第几列写入什么数据
        sh1.write(0, 0, '排名')  # 表示第一行第一列写入'商品名',行列从0开始
        sh1.write(0, 1, '标题')
        sh1.write(0, 2, '价格')
        sh1.write(0, 3, '店铺名')
        sh1.write(0, 4, '收货数')
        sh1.write(0, 5, '地址')
        sh1.write(0, 6, '评价数')
        sh1.write(0, 7, '收藏数')

        # 用循环将列表中的数据写入excel中
        for index, data in enumerate(data_list):
            # 因为第一行(第一行是数字0)有商品名，店铺名等数据，所以数据从第二行开始写入，index也是从0开始,所以index需要加1
            sh1.write(index + 1, 0, data['num'])
            sh1.write(index + 1, 1, data['title'])
            sh1.write(index + 1, 2, data['price'])
            sh1.write(index + 1, 3, data['shop_name'])
            sh1.write(index + 1, 4, data['view_sales'])
            sh1.write(index + 1, 5, data['address'])
            sh1.write(index + 1, 6, data['comment'])
            sh1.write(index + 1, 7, data['collect'])

        # 最后保存文件即可,括号内就是你要生称的excel文件名,文件会生成在当前目录下
        wb.save('taobao.xls')


if __name__ == '__main__':
    # 说明：loginId、umidToken、ua、password2这4个参数都是从浏览器登录页面复制过来的。
    # 如何复制4个参数：
    # # 1、浏览器打开：https://login.taobao.com/member/login.jhtml
    # # 2、F12打开调试窗口，左边有个Preserve log，勾选上，这样页面跳转请求记录不会丢失
    # # 3、输入用户名密码登录，然后找到请求：newlogin/login.do 这个是登录请求
    # # 4、复制上面的4个参数到下面，基本就可以运行了
    # # 5、如果运行报错可以微信私聊猪哥，没加猪哥微信的可以关注猪哥微信公众号[裸睡的猪]，回复：加群

    # 淘宝用户名：手机 用户名 都可以
    loginId = '18075345266'
    # 改版后增加的参数，后面考虑解密这个参数
    umidToken = 'f12c27e447e64ec525b223fb537dd1dc9a2732fa',
    # 淘宝重要参数，从浏览器或抓包工具中复制，可重复使用
    ua = '125#cFKcavRmcWQJwOKw+A++xfdSuDf2r14YEXzdh0wkDDIBTQwbklxmCws5mQlciZE+fTXcK7kGlpdRRUm5Jp3ZKD9ncVCwyrBlz5uoITpGc6fMRYphtM9249kg5YryBUUL204QUX/xPp5hfGhYOCUDYPQnp15HSAD67g7fRvQfemrEyrZXlPVucrjFwCnve3xCNgTNYAMml+gWU4ixu4gZgyNSLlsT6B6gno8QTTz0GHaKlOgs/gOzJSp6jwjf/j326vnCtJf7ClgSHKRzbUD1ybcRkjZaOAcwUOHDvgA5/6EcUjcScvsOcgDbUgs5N3gsfJXbf1Id/e2SiOjffrl2fdBiieo4gGE4DXBwCNyU3NDIUmntaLowccDURgnzwEgfJmwVRuuGsPHJk0zRuQrFv0LI5Ak6R2e5bSxCJxtPkNubqd+HmShCdaWEodeSIT2lsCf2g88Bnw5oIzfc4rUPzjsF26/iB6HLprGZS/lPIatxGAUvCRP7Kb4+awgC7+wHQ0DsOjB6U+FULtKE4eYfgmDr0FmMvbPlUjuuR6bYYhg23qqaw7h1aaUpd5trO87/opeorTelGDOwiz/HBnVmpll4WQI8OVSQvkdlYiVmrJF5sop7+lYUnMGUjPGquWYvHFGYvmnDwxFssejbm+FfZUDVcD977U265Xy4/uQA87rFWAi/6q3QbUx3n4mGrjXO40g5OHhpaFC8s5aUtM/q+s/vLN0+DMTEg3B2zPbyoYmKm6iDfjD7EVQzBO4GB7927fMm0MllEQ5hK08kTKPMFAQUPl0I4LjdlWclDhZJJF7MMmbSo5x0MabXgPvBb/17cDd4wCJYpJGjA+qVtSfwq7ReEYd+RRLUEq9v9EC16lllPoZ9SuB1QYV514KcY/tRrFgZdVnqXAssyr8Chpz30VgK+JGWLyjSV0+2rl1hK2Dg9C6OYCacbV8s0gZqiJ8eeGL3ynTJalK7hx0F/84dBthCCp7Xf4m9wJXoLwUwOr1kwt9x0GFPI9nh8qMOXRPW6s2='
    # 加密后的密码，从浏览器或抓包工具中复制，可重复使用
    password2 = '7a92772ca7a7e48747fe0a2981258847cde9eeab30f0bc3d9245675ec302bb9124cc61be24b0fbddb24e93bc75c3738bbb50b07bd20d5be4d6d1c8f4267ebf616f0a6c3559d45eb8f81ca4cd0a03217a4467a55daa006d6f7d04b527cc4efba51f3c1d972e94bf2974cec304023fdd7fa8bdaa30bb9c5cb3543015289f7de7cd'

    # 登录
    ul = UsernameLogin(loginId, umidToken, ua, password2)
    ul.login()
    # ul.get_taobao_nick_name()

    # 获取螺狮粉数据
    ul.get_lsf_data()

