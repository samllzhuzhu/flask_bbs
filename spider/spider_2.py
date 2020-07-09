import requests
from lxml.html import etree



def yao():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "JSESSIONID=6B1F49F292CF84BA3D1CF0D94F85A9DA.7; FSSBBIl1UgzbN7N82S=7IjIFrpOVU3BOgM7uKaVpkeRi7yDupoFNPSV4y9b.LOWBAbzr1A5NWbRJcymxquX; FSSBBIl1UgzbN7N82T=2SNJY9AhIdVn.2Oc7oBxkiQ5rC3l6vBR.WZEgzV0AdKb_.pP1iF0AGqJhxgFw3aTxT43cZUslnMIQj4HZe58BDjp1S1G4yEyeLF40LFw5WaDA94R8CjEzmwBQ8Ihc76ugKkq6Pgc02GXTdb_fQUnY7mlrKOJYVeUU3tpLX916ASAj5DvH6tZIcDWZDN8_F96eDwuI6ReW5rQ3O63wF8TNrcTej6dI5h5AawjW_NpefOGeinMP29dKVwnH99dYBGNpwLr.mymIXydlNT618LdMiTvbL6NHi9DC_xlqearOOuMGvq"
    }

    # url = 'http://qy1.sfda.gov.cn/datasearchcnda/face3/base.jsp?tableId=25&tableName=TABLE25&title=%E5%9B%BD%E4%BA%A7%E8%8D%AF%E5%93%81&bcId=152904713761213296322795806604'
    url = 'http://qy1.sfda.gov.cn/datasearchcnda/face3/content.jsp?tableId=25&tableName=TABLE25&Id=167077'
    res = requests.get(url, headers=headers)
    print(res.content)
    data_html = etree.HTML(res.content)
    print(data_html)
    dl = data_html.xpath('//div[contains(@class, "listmain")]')
    # dl = data_html.xpath('//*[@id="content"]/div/table[2]')
    print(dl)


    # url_1 = 'http://qy1.sfda.gov.cn/datasearchcnda/face3/search.jsp?tableId=25&bcId=152904713761213296322795806604&MmEwMD=GBK-2uyNQbqBKelKPvub2mdztWWFE0EG52dePi77SBlAReDcuNrDMWtARPANchL5VFGpq6.Zh5o6Jah4YL..TdX_bl_TMfCIDPoQh.9u7pVL6FuOwglr4IbGoz7_Pr.ZQdwjunouQYw9zWAa1y9MgoFiG.3Z1SJ4AWTGWnmuknkJik_EDkYrEC9suPi.LkSwgGOU.DUS7rbdUUjVZZJl.q1TwD4mwSjJMpX6ObweDYFvVcYe5WEIAtNfBzW.BNsRKdwuKHLS4RMldLTQcmbfb_x8JoksKsu_SfPokTjRYqA7wrj96S.BFyvbGbuZ4NA9VasEHbo9yCXYeHaey6OkYVFGwnAJSDYE9dpvBZswIEZtsEauHYaXRk3h8HNzJ_FomDqUNBgsjP57x5tzVpW19bnYbI0._C3qx9txEMrfBTgb6yZyJ.l'
    # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # data = requests.post(url_1, headers=headers)
    # print(data)


def get_lsf_info_from_jd():
    """京东螺狮粉部分信息"""

    # 这事请求头信息
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    }

    # 这是京东搜索螺狮粉的链接
    url = 'https://search.jd.com/Search?keyword=%E8%9E%BA%E7%8B%AE%E7%B2%89&qrst=1&stock=1&page=1&s=1&click=0'

    # 这是发送请求 类似于浏览器中输入上面网址
    res = requests.get(url, headers=headers)

    # res是请求之后返回的数据  也就是页面数据  data_html是解析返回的数据
    data_html = etree.HTML(res.content)
    divs = data_html.xpath('//div[contains(@class, "gl-i-wrap")]')

    # 下面这些是解析的过程，很复杂，可能有更好的方法
    for d in divs:
        print('价格: ', d.xpath('./div[2]/strong/i')[0].text)
        print('店铺: ', d.xpath('./div[5]/span/a/@title')[0] if d.xpath('./div[5]/span/a/@title') else '无信息')
        if d.xpath('./div[3]/a/@title') != ['']:
            print('商品: ', d.xpath('./div[3]/a/@title')[0])
        else:
            data1 = d.xpath('./div[3]/a/em/text()')
            data2 = d.xpath('./div[3]/a/em/font/text()')

            if len(data1) > len(data2):
                a = ''
                for i in range(len(data2)):
                    a += data1[i]
                    a += data2[i]
                a += data1[-1]
            else:
                a = ''
                for i in range(len(data2)):
                    a += data1[i]
                    a += data2[i]
            print('商品: ', a)
        print('-' *  50)


get_lsf_info_from_jd()


# yao()


def duanzi():
    url = 'https://ishuo.cn/'

    response = requests.get(url)
    data_html = etree.HTML(response.content)
    print(response.content)
    print(data_html)

    res = data_html.xpath('//div[contains(@class, "content")]')
    for r in res:
        print(r.text)

# duanzi()


def yao_2():
    headers = {"Cookie": "nsunid=3kkIKF4T87VLmnzeIZTzAg==; __utmc=191491435; __utmz=191491435.1578365874.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=191491435.1358424781.1578365874.1578368580.1578374165.3; __utmt=1; __utmb=191491435.7.10.1578374165"}
    ll = '/html/body/name/table[5]/tr/td[3]/table/tr[3]/td/table/tr/td/table[3]'
    url = 'http://www.pharmnet.com.cn/search/index.cgi?p=3&terms=&c1=47'

    response = requests.get(url, headers=headers)
    html = response.content.decode('gbk')
    html = html.replace('<!--', '"').replace('-->', '"')
    data_html = etree.HTML(html)
    print(data_html)
    res = data_html.xpath(ll)
    print(res)
    for r in res:
        print(r.xpath('.//td/a/span')[0].text)

# yao_2()


def yao_3():
    for i in range(1000):
        url = 'https://yi.9939.com/{}/'.format(i)

        res = requests.get(url)
        html = etree.HTML(res.content)
        data = html.xpath('//div[contains(@class, "drugbase")]/ul/li')
        for d in data:
            print(d.xpath('./span')[0].text, d.xpath('./p')[0].text)
        print('-----------------------------------------------')

# yao_3()


def guo():
    # url = 'http://mobile.nmpa.gov.cn/datasearch/QueryList?tableId=25&searchF=Quick%20Search&searchK=&pageIndex=1&pageSize=10'
    # url = 'http://mobile.nmpa.gov.cn/datasearch/QueryList?tableId=25&searchF=Quick%20Search&searchK=&pageIndex=1&pageSize=20'
    url = 'http://mobile.nmpa.gov.cn/datasearch/QueryRecord?tableId=25&searchF=ID&searchK=136'
    data = requests.get(url)
    print(data)
    print(data.content)
    # print(data.content)
    # data = list(eval(data.content))
    # for i in data:
    #     print(str(i['ID']), i['CONTENT'])
    #     print('-' * 50)

    # url = 'http://mobile.nmpa.gov.cn/datasearch/QueryRecord?tableId=25&searchF=ID&searchK=136061'
    # data = requests.get(url)
    # data = list(eval(data.content))
    # for i in data:
    #     pass

# guo()