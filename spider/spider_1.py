from selenium import webdriver
from bs4 import BeautifulSoup
import time
import yaml


DRIVER = webdriver.Chrome(executable_path='/Users/cao/dev/spider/chromedriver')


def get_department_city():
    url = "https://www.haodf.com/keshi/list.htm"
    departments = []
    DRIVER.get(url)
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    current_page = soup.find_all("div", {"class": "bxmd"})[-1]
    for item in current_page.find_all("li"):
        departments.append(item.find("a").text)
    # DRIVER.close()
    return departments

def get_tb():
    url = "https://s.taobao.com/search?q=%E8%9E%BA%E7%8B%AE%E7%B2%89&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170306&bcoffset=0&ntoffset=6&p4ppushleft=1%2C48&sort=sale-desc"
    DRIVER.get(url)
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    current_page = soup.find_all("div", {"class": "shop"})
    print(len(current_page))

get_tb()

def get_department_city_1():
    url = "https://www.guahao.com/hospital/2/%E4%B8%8A%E6%B5%B7/all/%E4%B8%8D%E9%99%90/p1"
    departments = []
    DRIVER.get(url)
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    current_page = soup.find_all("li", {"class": "g-hospital-item J_hospitalItem"})
    for li in current_page:
        departments.append(li.find('a', {"class": "cover-bg seo-anchor-text"}).text.strip())

    # DRIVER.close()
    return departments

def get_department_city_2():
    url = "https://www.guahao.com/hospital/2/%E4%B8%8A%E6%B5%B7/all/%E4%B8%8D%E9%99%90/p1"
    departments = []
    DRIVER.get(url)
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    current_page = soup.find_all("li", {"class": "g-hospital-item J_hospitalItem"})
    for li in current_page:
        item = {}
        item['name'] = li.find('a', {"class": "cover-bg seo-anchor-text"}).text.strip()
        item['level'] = li.find('em').text.strip()
        item['addr'] = li.find('p', {"class": "addr"}).text.strip()
        item['tel'] = li.find('p', {"class": "tel"}).text.strip()
        departments.append(item)

    # DRIVER.close()
    return departments


# 获取所有地区
def get_all_area():
    """获取所有地区医院"""
    url = 'https://www.guahao.com/nav'
    DRIVER.get(url)
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    current_page = soup.find_all("div", {"class": "block"})[1]

    area_dict = {}
    for area in current_page.find_all('li')[1:]:
        area_name = area.find('a', {"class": "name"}).text.strip()
        hos_area = area.find_all('a', {"class": "item"})
        hos_list = []
        for a_tag in hos_area:
            a_tag_dict = {}
            a_tag_dict['hos_area_name'] = a_tag.text.strip()
            a_tag_dict['url'] = a_tag.get('href')
            hos_list.append(a_tag_dict)
        area_dict[area_name] = hos_list

    return area_dict


def get_hos_deps():
    """获取医院科室"""

    """获取所有地区"""
    url = 'https://www.guahao.com/hospital/b20f1915-66d5-46d9-b539-0d742b0eedd6000'
    DRIVER.get(url)
    soup = BeautifulSoup(DRIVER.page_source, "html.parser")
    current_page = soup.find_all("li", {"class": "g-clear"})
    dep_dict = {}
    for li in current_page:
        main_dep = li.find('label').text.strip()
        a_tags = li.find_all('a')
        tag_list = []
        for a in a_tags:
            url = a.get('href')
            if a.get('title'):
                dep_name = a.get('title').strip()
            else:
                dep_name = a.text.strip()
            tag_list.append({'dep_name': dep_name, 'url': url})
        dep_dict[main_dep] = tag_list

    return dep_dict


# if __name__ == "__main__":
    # hospitalCityList = get_department_city_2()
    # hospitalCityList = get_all_area()
    # hospitalCityList = get_hos_deps()
    # with open("./hos_departments.yaml", "w") as f:
    #
    #     documents = yaml.dump(hospitalCityList, f, allow_unicode=True)
    # DRIVER.quit()
