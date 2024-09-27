import scrapper

def keyword_content(site, keyword):
    clcontent = scrapper.scrap(site)
    rescontent = {'content_title' : f'Скидки c фильтром, по ключевому слову {keyword}', 'content_list' : []}
    for con in clcontent['content_list']:
        if keyword.lower() in con['title'].lower():
            rescontent['content_list'].append(con)
    return rescontent
