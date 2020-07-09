import xlwt     # 这是操作excel的库，需要安装这个库  命令: pip install xlwt
import requests
from lxml import etree

# 上面这两行是需要装的库


# 目前只取了列表页店铺名和商品名和价格信息,评价数暂时拿不到
def get_lsf_info_from_jd():
    """京东螺狮粉部分信息"""

    # 这是请求头信息
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    }

    # 这是京东搜索螺狮粉的链接
    url = 'https://search.jd.com/Search?keyword=%E8%9E%BA%E7%8B%AE%E7%B2%89&qrst=1&stock=1&page=100&s=1&click=0'
    # 这是发送请求 类似于浏览器中输入上面网址
    res = requests.get(url, headers=headers)

    # res是请求之后返回的数据  也就是页面数据  data_html是解析返回的数据
    data_html = etree.HTML(res.content)
    divs = data_html.xpath('//div[contains(@class, "gl-i-wrap")]')

    data_list = []
    # 下面这些是解析拼接的过程，很复杂，应该有更好的方法
    for d in divs:
        data_dict = {}
        print('价格: ', d.xpath('./div[2]/strong/i')[0].text)
        print('店铺: ', d.xpath('./div[5]/span/a/@title')[0] if d.xpath('./div[5]/span/a/@title') else '无信息')

        # 将商品价格店铺存入字典中，方便后期写入excel
        data_dict['price'] = d.xpath('./div[2]/strong/i')[0].text
        data_dict['shop'] = d.xpath('./div[5]/span/a/@title')[0] if d.xpath('./div[5]/span/a/@title') else '无信息'


        if d.xpath('./div[3]/a/@title') != ['']:
            print('商品: ', d.xpath('./div[3]/a/@title')[0])
            # 将商品名称存入字典中，方便后期写入excel
            data_dict['name'] = d.xpath('./div[3]/a/@title')[0]
        else:
            goods_1 = d.xpath('./div[3]/a/em/text()')
            goods_2 = d.xpath('./div[3]/a/em/font/text()')

            if len(goods_1) > len(goods_2):
                a = ''
                for i in range(len(goods_2)):
                    a += goods_1[i]
                    a += goods_2[i]
                a += goods_1[-1]
            else:
                a = ''
                for i in range(len(goods_2)):
                    a += goods_1[i]
                    a += goods_2[i]
            print('商品: ', a)
            # 将商品名称存入字典中，方便后期写入excel
            data_dict['name'] = a
        print('-' * 50)

        # 将每个商品存入列表中，列表中最终会有多个商品的信息,方便一次性写入excel中
        data_list.append(data_dict)

    # 将列表中的数据统一写入excel中
    # 创建 xls 文件对象, 就是创建一个excel文件
    wb = xlwt.Workbook()

    # 新增表单页,就是excel下面的sheet名字，可以创建多个
    sh1 = wb.add_sheet('京东商品')

    # 然后按照位置来添加数据,括号里面第一个参数是行，第二个参数是列,第三个参数是写入的数据,表示excel中第几行第几列写入什么数据
    sh1.write(0, 0, '商品名')   # 表示第一行第一列写入'商品名',行列从0开始
    sh1.write(0, 1, '店铺名')
    sh1.write(0, 2, '价格')

    # 用循环将列表中的数据写入excel中
    for index, data in enumerate(data_list):
        # 因为第一行(第一行是数字0)有商品名，店铺名等数据，所以数据从第二行开始写入，index也是从0开始,所以index需要加1
        sh1.write(index + 1, 0, data['name'])
        sh1.write(index + 1, 1, data['shop'])
        sh1.write(index + 1, 2, data['price'])

    # 最后保存文件即可,括号内就是你要生称的excel文件名,文件会生成在当前目录下
    wb.save('test_w.xls')

# get_lsf_info_from_jd()


# 淘宝获取数据
def get_lsf_info_from_tb():
    # url = 'https://detail.tmall.com/item.htm?spm=a230r.1.14.1.1a782a9d4L50l6&id=598614273525&ns=1&abbucket=20'
    url = 'https://s.taobao.com/search?q=%E8%9E%BA%E7%8B%AE%E7%B2%89&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170306&bcoffset=0&ntoffset=6&p4ppushleft=1%2C48&sort=sale-desc'
    headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        }

    res = requests.get(url, headers=headers)
    # print(res.content)
    data_html = etree.HTML(res.content)
    divs = data_html.xpath('//div[contains(@class, "item J_MouserOnverReq")]')
    # divs = data_html.xpath('//*[@id="mainsrp-itemlist"]/div/div/div[1]/div[1]/div[2]/div[2]')
    # divs = data_html.xpath('//*[@id="mainsrp-itemlist"]/div/div/div[1]/div[1]/div[2]/div[2]')
    print(divs)
    for i in divs:
        a =1



    # divs = data_html.xpath('//*[@id="J_DetailMeta"]/div[1]/div[1]/div/div[1]/h1/text()')
    # prices = data_html.xpath('//*[@id="J_PromoPrice"]/dd/div/span/text()')
    # old_prices = data_html.xpath('//*[@id="J_StrPriceModBox"]/dd/span/text()')
    # count = data_html.xpath('//*[@id="J_DetailMeta"]/div[1]/div[1]/div/ul/li[1]/div/span[2]/text()')
    # comment_count = data_html.xpath('//*[@id="J_ItemRates"]/div/span[2]/text()')
    # print(divs)
    # print(prices)
    # print(old_prices)
    # print(count)
    # print(comment_count)


get_lsf_info_from_tb()