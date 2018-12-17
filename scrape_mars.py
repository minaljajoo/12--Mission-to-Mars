#Dependencies
import pandas as pd
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup
import pymongo
import requests
import time

########### Chrome browser ####################
def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

########### Start of Mars scrape all info ####################
def scrape_info():
    browser_open = init_browser()
    news =mars_news_info(browser_open)
    image_url = mars_image_info(browser_open)
    weather = mars_weather_info(browser_open)
    table = mars_facts_info(browser_open)
    hemispheres = mars_hemispheres_info(browser_open)
    mars_all_data ={"mars_news":news,"featured_image_url":image_url,"mars_weather": weather, "mars_facts":table, "mars_hemispheres": hemispheres}
   
    
    # Close the browser after scraping
    browser_open.quit()

    # Return results
    return mars_all_data
 ########### End of Mars scrape all info #############
########### Start of Mars News info #################
#NASA Mars News
def mars_news_info(browser):
    # Visit Mars news site and pull the latest news and the article
    #Visit the news link and get more details
    mars_news =[]
    url_news = "https://mars.nasa.gov/news/"
    browser.visit(url_news)
    time.sleep(2)
    # Scrape page into Soup
    html_news = browser.html
    soup_news = BeautifulSoup(html_news, "html.parser")
    
    #---------------------
    # <div class="content_title"> -- from inspect for referance
    news_titles = soup_news.find_all("div", class_="content_title")
    latest_news_title = news_titles[0].text
    mars_news.append(latest_news_title)
    #---------------------
    # <div class="article_teaser_body"> -- from inspect for referance
    news_text = soup_news.find_all("div", class_="article_teaser_body")
    latest_news_text = news_text[0].text
    mars_news.append(latest_news_text)
    #---------------------
    # <a href> -- from inspect for referance
    text_info_link = news_titles[0].find("a")["href"]
    url_detail = url_news + text_info_link
    #Visit the url for more details of the news
    browser.visit(url_detail)
    time.sleep(3)
    html_details = browser.html
    soup_details = BeautifulSoup(html_details, "html.parser")
    #---------------------
    # <div class="wysiwyg_content"> -- from inspect for referance
    news_detail = soup_details.find_all("div", class_="wysiwyg_content")
    news_detali_text = news_detail[0].find("p").text
    mars_news.append(news_detali_text)
    return ( mars_news)
########### End of Mars News info ########################

########### Start of Mars Featured image info ####################
### JPL Mars Space Images - Featured Image
#* Use splinter to navigate the site and find the image url for the current Featured Mars Image 
def mars_image_info(browser):
    url_image = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url_image)
    time.sleep(3)
    browser.click_link_by_partial_text("FULL IMAGE")
    time.sleep(3)
    browser.click_link_by_partial_text("more info")
    #---------------------
     # Scrape page into Soup
    html_image = browser.html
    soup_img = BeautifulSoup(html_image, "html.parser")
    # <img class="main_image" src="/spaceimages/images/largesize/PIA14579_hires.jpg"> -- from inspect for referance
    mars_image = soup_img.find("img", class_="main_image")
    mars_image_link = mars_image["src"]       
    mars_image_url = url_image[:24]+mars_image_link
    return (mars_image_url)
########### End of Mars featureed image info ##################
########### Start of Mars Weather info ########################
#Visit the Mars Weather twitter account here and scrape the latest Mars weather tweet from the page. 
def mars_weather_info(browser):
    url_weather = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url_weather)
    time.sleep(1)
    #---------------------
     # Scrape page into Soup
    html_weather = browser.html
    soup_weather = BeautifulSoup(html_weather, "html.parser")
    #<p class="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text"> -- from inspect for referance
    mars_weather_page = soup_weather.find_all("p", class_="TweetTextSize")
    mars_weather = mars_weather_page[0].text
    return (mars_weather)

########### End of Mars Weather info ########################
########### Start of Mars Facts info ########################
#Visit the Mars Facts webpage here and use Pandas to scrape the table containing facts about the planet including Diameter, Mass, etc.
def mars_facts_info(browser):
    url_facts = "http://space-facts.com/mars/"
    browser.visit(url_facts)
    time.sleep(3)
    #---------------------
     # Scrape page into Soup
    html_facts = browser.html
    soup_facts = BeautifulSoup(html_facts, "html.parser")
    # <table id="tablepress-mars" class="tablepress tablepress-id-mars"> -- from inspect for referance
    mars_facts = soup_facts.find("table", id="tablepress-mars")
    table_row = mars_facts.find_all("tr")
    mars_td_1 = []
    mars_td_2 = []
    for col in table_row:
        table_col = col.find_all("td")
        mars_td_1.append(table_col[0].text)
        mars_td_2.append(table_col[1].text.strip())
    mars_table_df = pd.DataFrame({"Description": mars_td_1,
                                "Value": mars_td_2
                                })
    mars_table_html = mars_table_df.to_html(index=False,justify="left")
    return (mars_table_html)
########### End of Mars Facts info ########################

########### Start of Mars Hemispheres info ##################
#Visit the USGS Astrogeology site to obtain high resolution images for each of Mar"s hemispheres.
def mars_hemispheres_info(browser):
    #Read the url and get info
    url_hem = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url_hem)
    time.sleep(3)
    #---------------------
     # Scrape page into Soup
    html_hem = browser.html
    soup_hem = BeautifulSoup(html_hem, "html.parser")
    # store the main part of url for future use
    url_hem_main = url_hem[:29]
    # <div class="description"><a href="/search/map/Mars/Viking/cerberus_enhanced"> -- from inspect for referance
    # get title and link from main page
    hem_info = soup_hem.find_all("div", class_="description")
    hemisphere_image_urls = []
    for hem in hem_info:
        desc_title = hem.find("h3").text
        desc = hem.find("a")["href"]
        desc_link = (url_hem_main + desc)
        # Go to the link to get the full image
        browser.visit(desc_link)
        time.sleep(3)
        html_desc = browser.html
        soup_desc = BeautifulSoup(html_desc, "html.parser")
        # <img class="wide-image"
        # src="/cache/images/cfa62af2557222a02478f1fcd781d445_cerberus_enhanced.tif_full.jpg">
        # -- from inspect for referance
        hem_img = soup_desc.find_all("img", class_="wide-image")
        hem_img_link = hem_img[0]["src"]
        hem_desc = (url_hem_main+hem_img_link)
        img_title_dict = {"title": desc_title, "img_url": hem_desc}

        hemisphere_image_urls.append(img_title_dict)
    return (hemisphere_image_urls)
########### End of Mars Hemispheres info ##################