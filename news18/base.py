import re
from dateparser import parse
from bs4 import BeautifulSoup as bs
from news18 import logger
import requests
import random

desktop_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']

proxies = {
    'http': 'http://35.173.16.12:8888/?noconnect',
    'https':'http://35.173.16.12:8888/?noconnect'
}


def proxied_request(url, extra_headers={}, params={}):
    headers = {
        'User-Agent':random.choice(desktop_agents),
        # 'Accept': ('text/html,application/xhtml+xml,application/xml;'
        #            'q=0.9,*/*;q=0.8'),
        # 'Accept-Language': 'en-US,en;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    headers.update(extra_headers)

    # if url.startswith('http://'):
    #     p = proxies('http')
    # else:
    #     p = proxies('https')
    resp = requests.get(url, headers=headers, proxies=proxies, params=params)
    return resp


def news18(page=0):
    try:
        news18Dict = {}
        news18Dict['success'] = True
        base_url = 'https://www.news18.com/newstopics/lay-off/page-{0}'.format(str(page))
        try:
            req = proxied_request(base_url)
            logger.info('successful request to news18 connector {0}'.format(base_url))
        except Exception as e:
            news18Dict['success'] = False
            news18Dict['errorMessage'] = str(e)
            logger.warning('request to news18 connector {0} failed: {1}'.format(base_url, str(e)))
            return news18Dict
        if req.status_code == 200:
            news18Dict['data'] = []
            soup = bs(req.content, 'lxml')
            try:
                unwanted = soup.find('li',class_='next')
                unwanted.extract()
                total_pages = soup.find('div',class_='pagination').find_all('li')[-1].text.strip()
            except Exception as e:
                logger.warning('Error with finding the total pages {0} of page {1}'.format(str(e), page))
                total_pages = 1
            news18Dict['total_pages'] = total_pages
            try:
                cards = soup.find_all('li', style='float:none;')
            except Exception as e:
                cards = []
                return news18Dict
            for item in cards:
                news18Dict['success'] = True
                try:
                    titles = item.find('h2').text.strip()
                except AttributeError:
                    titles = None
                try:
                    snippet = item.p.find('a').text.strip()
                    if snippet is '':
                        snippet = None
                except AttributeError:
                    snippet = None
                try:
                    date = item.find({'span', 'a'}, class_='post-date').contents[-1].strip()
                    posted_at = parse(date)
                except (IndexError,AttributeError):
                    date = None
                try:
                    url = item.h2.a.get('href')
                except AttributeError:
                    url = None
                try:
                    req1 = proxied_request(url)
                    soup1 = bs(req1.content, 'lxml')
                    logger.info('request to the content url {0} of news18 connector is successful'.format(url))
                except Exception as e:
                    logger.warning('request to the content url {0} of news18 connector failed : {1}'.format(url,str(e)))
                try:
                    article_body = soup1.find('div', id='article_body')
                    articles = article_body.text.split(
                        '.update_date{font-size:12px;color:#666;display:block;text-align:left}')[0].split(
                        '<div id="web728x90_ROS" align="center" style="margin-bottom:20px;"></div>')[0].split(
                        '@media only screen and (max-width:740px)')[0].strip()
                    article = re.sub(r'[\n\r\t]', '', articles)
                except Exception as e:
                    logger.warning('Error with content part of the url {0}: {1}'.format(url,str(e)))
                    article = None
                obj = {}
                obj['title'] = titles
                obj['snippet'] = snippet
                obj['url'] = url
                if 'videos' in url:
                    obj['content'] = None
                else:
                    obj['content'] = article
                obj['date'] = posted_at
                obj['category'] = 'Layoffs'
                obj['source'] = 'news18'
                news18Dict['data'].append(obj)
            return news18Dict
    except Exception as e:
        logger.error('Error in scraping page {0} of the news18 connector : {1}'.format(page, str(e)))
        return None