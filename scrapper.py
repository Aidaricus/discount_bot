import requests

from bs4 import BeautifulSoup

urls = {
    "asos" : "https://www.asos.com/men/sale/cat/?cid=8409",
    "lamoda" : "https://www.lamoda.ru/c/4153/default-women/?is_sale=1&display_locations=outlet&sitelink=topmenuW&l=12"
}

def scrap(site_name):
    if site_name == 'asos':
        return scrap_asos()
    elif site_name == 'lamoda':
        return scrap_lamoda()

def scrap_asos():
    scrap_result = {"content_title": "Clear list of discount products:", "content_list" : []}
    url = urls["asos"]
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36'}
    page = requests.get(url, headers= headers)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find_all("article", class_="productTile_U0clN")
    # print(results)
    for r in results:
        res = {}
        product_info = r.find('a', class_="productLink_KM4PI")
        product_title = product_info.\
            find('div', "productDescription_sryaw").\
            find("div", class_="overflowFade_zrNEl")
        link = product_info.get('href')
        res['title'] = product_title.text.strip()
        res['link'] = link
        price =  (product_info.find('p', class_ = 'container_WYZEU').text.strip()).split('£')
        # print(price.split('£'))
        res['new_price'] = '£' + price[-1]
        res['old_price'] = '£' + price[-2]
        # break
        scrap_result['content_list'].append(res)
    return scrap_result

def scrap_lamoda():
    scrap_result = {"content_title": "Clear list of discount products:", "content_list" : []}
    url = urls["lamoda"]
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find("div", class_="grid__catalog")
    print(len(results))
    for r in results:
        res = {}
        product_info = r.find("div", class_ = "x-product-card-description")
        product_desc = product_info.find_all('div', class_ = "x-product-card-description__microdata-wrap")
        res['title'] = product_desc[1].text
        price = product_desc[0]
        try:
            res['old_price'] = price.find('span', class_ = "x-product-card-description__price-old").text
            res['new_price'] = price.find('span', class_ = "x-product-card-description__price-new x-product-card-description__price-WEB8507_price_no_bold").text
        except:
            print(price.find('span', class_ = "x-product-card-description__price-old"))
            continue
        res['link'] = "https://www.lamoda.ru" + (r.find('a', class_ = "x-product-card__link x-product-card__hit-area")).get('href')


        scrap_result['content_list'].append(res)
    return scrap_result
