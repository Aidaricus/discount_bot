import requests

from bs4 import BeautifulSoup

urls = {
    "asos" : "https://www.asos.com/men/sale/cat/?cid=8409",
}

def scrap(site_name):
    if site_name == 'asos':
        return scrap_asos()
    elif site_name == 'lamoda':
        pass
        # return scrap_lamoda()

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
        links = product_info.get('href')
        res['title'] = product_title.text.strip()
        res['link'] = links
        res['price'] = product_info.find('p', class_ = 'container_WYZEU').text.strip()
        scrap_result['content_list'].append(res)
    return scrap_result
