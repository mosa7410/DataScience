from selenium import webdriver
from bs4 import BeautifulSoup
import os
import re
import random
import time
import pandas as pd
import numpy as np

driver = webdriver.Chrome('./chromedriver.exe')
driver.implicitly_wait(3)

rating_list = []
'''
1. reviewNo 에 있는 번호로 리스트 가져옴
2. 모든 tr, td (rating, movieID) 가져올 수 있음 + userID
2. a.pg_next 가 존재할때까지 page 를 증가
'''

def get_movie_link(soup):
    movie_links = soup.select('a[href]')

    movie_links_list = []
    for link in movie_links:
        if re.search(r'st=mcode&sword' and r'&target=after$', link['href']):
            target_url = 'https://movie.naver.com/movie/point/af/list.nhn' + str(link['href'])
            movie_links_list.append(target_url)

    return movie_links_list[1:]


def get_movie_rating():
    df = pd.read_csv('./data/naver_user.csv')
    reviewNo = df['reviewNo']

    for num in reviewNo:
        next = [0]
        page = 1

        while next:
            # print('https://movie.naver.com/movie/point/af/list.nhn?st=nickname&sword={0}&target=after&page={1}'.format(num, page))
            driver.get('https://movie.naver.com/movie/point/af/list.nhn?st=nickname&sword={0}&target=after&page={1}'.format(num, page))
            # print(next)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            userId = soup.select('table.list_netizen > tbody > tr > td > a.author')
            reviewNum = soup.select('#old_content > table > tbody > tr > td.ac.num')
            rating = soup.select('table.list_netizen > tbody > tr > td.point')
            movie_links = get_movie_link(soup)

            for i in range(len(userId)):
                user = userId[i].text.replace('*', '')
                review = str(reviewNum[i]).replace('<td class="ac num">', '').replace('</td>', '')
                rate = str(rating[i]).replace('<td class="point">', '').replace('</td>', '')
                movieId = movie_links[i].replace('https://movie.naver.com/movie/point/af/list.nhn?st=mcode&sword=','').replace('&target=after', '')

                if (int(review) <= num):
                    rating_list.append([user, review, rate, movieId])

            next = soup.select('div.paging > div > a.pg_next')
            time.sleep(random.randrange(3, 5))
            page += 1

def main():
    get_movie_rating()
    r_list = pd.DataFrame(rating_list, columns=['userId', 'reviewNo', 'rating', 'movieId'])
    r_list.to_csv("./data/rating.csv", index=False)
    driver.close()

if __name__ == "__main__":
    main()
