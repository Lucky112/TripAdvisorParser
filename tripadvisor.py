import requests
from bs4 import BeautifulSoup
import pandas as pd
from lxml import html
from lxml import etree




def make_ta_request(addr):
    s = requests.Session()
    s.headers.update({
        'Referer': 'https://www.tripadvisor.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    })

    url = 'https://www.tripadvisor.com' + addr
    request = s.get(url)

    return request.text

def get_review_ratings_from(tree):
    ratings = []
    user_choices = tree.xpath('//*[@class="choices"]')
    if len(user_choices) == 0:
        return []

    user_choices = user_choices[0]
    checkboxes = user_choices.xpath('./*[@class="ui_checkbox item"]')
    for box in checkboxes:
        value = box.xpath('./*[@class="row_num  is-shown-at-tablet"]')
        if len(value) > 0 :
            ratings.append((box.get('data-value'), value[0].text))
    return ratings

def get_rating(node):
  for i, k in enumerate((10, 20, 30, 40, 50)):
    rate = node.xpath(f'.//*[@class="ui_bubble_rating bubble_{k}"]')
    if len(rate) > 0:
      return i+1

def get_review_from(tree):
    review_list = []
    reviews = tree.xpath('//*[@class="review-container"]')
    for review in reviews:
        id = review.get('data-reviewid')
        review_text = None
        summary = review.xpath('./*/*/*/*/*[@class="prw_rup prw_reviews_text_summary_hsx"]')
        if len(summary) > 0 :
            summary = summary[0]
            textcont = summary.xpath('./div/p')
            if len(textcont) > 0 :
                review_text = textcont[0].text

        visit_date = None
        visit = review.xpath('./*/*/*/*/*[@class="prw_rup prw_reviews_stay_date_hsx"]')
        if len(visit) > 0 :
            visit = visit[0].text_content().split(":")
            if len(visit) == 2 :
                visit_date = visit[1]

        rating = get_rating(review)

        usefull_count = None
        usefull = review.xpath('.//*[@class="numHelp "]')
        if len(usefull) > 0:
            usefull = usefull[0].text
            if usefull:
                usefull_count = usefull.split()[0]

        review_list.append((id, visit_date, review_text, rating, usefull_count))
    return review_list







df = pd.read_csv('main_task.csv', sep=',')
print(df['URL_TA'])


results = []

for i, url in enumerate(df['URL_TA']):
    print(i)
    htmltext = make_ta_request(url).encode('utf-8')
    parser = html.HTMLParser(recover=True, encoding='utf-8')
    tree = etree.fromstring(htmltext, parser)
    results.append((get_review_ratings_from(tree), get_review_from(tree)))

    if (i+1) % 500 == 0:
      res = pd.DataFrame(results, columns=['rating', 'reviews'])
      res.to_csv(f"ta_parsing_results_{i}.csv", encoding='utf-8')

res = pd.DataFrame(results, columns=['rating', 'reviews'])

res.to_csv("ta_parsing_results.csv", encoding='utf-8')

