import sys
import csv
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import os
from dateutil.relativedelta import relativedelta


def estimated_date(google_date,collected_date) :
    units = google_date.split(" ")[1]
    nunits = google_date.split(" ")[0]
    print(units,nunits,collected_date)
    if (units == "heures") | (units == "heure") :
        temp = collected_date - relativedelta(hours=int(nunits))
    if (units == "jours") | (units == "jours") :
        temp = collected_date - relativedelta(day=int(nunits))
    if (units == "semaines") | (units == "semaine") :
        temp = collected_date - relativedelta(weeks=int(nunits))
    if units == "mois" :
        temp = collected_date - relativedelta(month=int(nunits))
    if units == "ans" :
        temp = collected_date - relativedelta(years=int(nunits))
    else :
        temp = None
    return temp

def get_review_summary(result_set):
    rev_dict = {'Review Rate': [],
        'Review Time': [],
        'Review Text' : [],
        'Review date collected':[]}
    for result in result_set:
        review_rate = result.find('span', class_='kvMYJc')["aria-label"]
        review_time = result.find('span',class_='rsqaWe').text
        review_text = result.find('span',class_='wiI7pd').text
        rev_dict['Review Rate'].append(review_rate)
        rev_dict['Review Time'].append(review_time)
        rev_dict['Review Text'].append(review_text)
        rev_dict['Review date collected'].append(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
    return(pd.DataFrame(rev_dict))

def get_google_review(url) :
    # Import the webdriver
    driver = webdriver.Firefox()
    driver.get(url)

    # privacy pop-up
    xpath = "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/span"
    try :
        driver.find_element_by_xpath(xpath).click()
    except :
        print("xpath not necessary")


    try :
        driver.find_element_by_xpath("/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/span[1]/span/span/span[2]/span[1]/button").click()
    except :
        print("Clique sur le nombre d'avis")
    #### expand the review

    time.sleep(2)

    class_ = "ODSEW-KoToPc-ShBeI gXqMYb-hSRGPd"

    soup = BeautifulSoup(driver.page_source,"html.parser")

    xpath_nb_avis = "/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div/div[2]/div[2]"
    #total_number_of_reviews = soup.find("div", class_="gm2-caption").text
    total_number_of_reviews =driver.find_element_by_xpath(xpath_nb_avis).text



    ## Catch nombre d'avis
    total_number_of_reviews = int(total_number_of_reviews.split(" ")[-2].replace("\u202f",""))
    #total_number_of_reviews = soup.find("div", class_="gm2-caption").text
    #a = total_number_of_reviews
    time.sleep(1)
    try :
        xpatrier = "/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[8]/div[2]/button/span/span"
        driver.find_element_by_xpath(xpatrier).click()
    except :
        print("echec ouverture Trier")

    time.sleep(2)
    xpatrecent ="/html/body/div[3]/div[3]/div[1]/ul/li[2]"
    driver.find_element_by_xpath(xpatrecent).click()

    ## Catch cellule of reviews

    books_html = soup.findAll('div', class_ ="jftiEf fontBodyMedium")
    len(books_html)




    #Find scroll layout
    old_scroll = '//*[@id="pane"]/div/div[1]/div/div/div[2]'
    scroll = "/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]"
    scrollable_div = driver.find_element_by_xpath(scroll)
    #Scroll as many times as necessary to load all reviews
    for i in range(0,(round(total_number_of_reviews/10 - 1))):
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight',
                    scrollable_div)
            time.sleep(2)


    #Find scroll layout
    scrollable_div = driver.find_element_by_xpath(scroll)




    #Scroll as many times as necessary to load all reviews
    for i in range(0,(round(total_number_of_reviews/10 - 1))):
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight',
                    scrollable_div)
            time.sleep(2)

    liste_plus =driver.find_elements_by_xpath('//button[normalize-space()="Plus"]')

    for i in liste_plus :
        try :
            i.click()
        except :
            print("tant pis")

    response = BeautifulSoup(driver.page_source, 'html.parser')


    #reviews = response.find_all('div',
    #                            class_='MyEned')

    reviews = response.find_all("div",class_="MyEned")



    driver.close()
    return reviews

def get_list_review_google(url):
    tmp = get_google_review(url)
    tmp = get_review_summary(tmp)
    tmp["review estimated date"] = [estimated_date(i, j) for i, j in zip(
        tmp["Review Time"], tmp["Review date collected"])]
    return tmp


if __name__ == "__main__":
    get_google_review("https://www.google.com/maps/place/Compose+-+Ponthieu/@48.8715544,2.3043444,17z/data=!3m1!5s0x47e66fc407cec387:0x83b327e8760e2d11!4m7!3m6!1s0x47e66fc407fa0ad7:0x796e899d5b8cb330!8m2!3d48.8715544!4d2.3065331!9m1!1b1")
