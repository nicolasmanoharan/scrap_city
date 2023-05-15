import sys
import csv
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import os
from dateutil.relativedelta import relativedelta


# Fonction pour enregistrer le log dans le fichier CSV
def rec_log(entreprise, name, url, nb_avis_disponible, delta=None):
    # Obtenir la date et l'heure actuelles
    date_execution = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Créer un DataFrame avec les nouvelles données du log
    log_data = {
        'entreprise': [entreprise],
        'name': [name],
        'url': [url],
        'nb_avis': [nb_avis_disponible],
        'delta': [delta],
        'date': [date_execution]
    }
    new_df = pd.DataFrame(log_data)

    # Vérifier si le fichier CSV existe
    fichier_existe = os.path.isfile('log.csv')

    if fichier_existe:
        # Lire le fichier CSV existant
        existing_df = pd.read_csv('log.csv')

        # Concaténer les données existantes avec les nouvelles données
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)

        # Écrire le DataFrame mis à jour dans le fichier CSV
        updated_df.to_csv('log.csv', index=False)
    else:
        # Écrire le DataFrame initial dans un nouveau fichier CSV
        new_df.to_csv('log.csv', index=False)

    # Afficher un message de confirmation
    print('Le log a été enregistré avec succès.')




def transform_date(A):
    #A["Review Rate"] = [i.split("\xa0")[0] for i in A["Review Rate"]]
    A["Review Time"] = [i.strip("il y a ") for i in A["Review Time"]]
    A["Review Time"] = [i.replace("une", "1") for i in A["Review Time"]]
    A["Review Time"] = [i.replace("un", "1") for i in A["Review Time"]]
    A["Review Time"] = [i.replace("\xa0", " ") for i in A["Review Time"]]
    A["Review Time"] = [i.replace("ans", "an") for i in A["Review Time"]]
    A["Review Time"] = [i.replace("an", "ans") for i in A["Review Time"]]
    A["Review Time"] = [i.replace("jours", "jour") for i in A["Review Time"]]
    A["Review Time"] = [i.replace("jour", "jours") for i in A["Review Time"]]
    A["Review Time"] = [i.replace("semaine", "semaines")
                        for i in A["Review Time"]]
    A["Review Time"] = [i.replace("semaines", "semaine")
                        for i in A["Review Time"]]
    A["Review date collected"] = pd.to_datetime(A["Review date collected"])
    return A

def estimated_date(google_date,collected_date) :
    units = google_date.split(" ")[1]
    nunits = google_date.split(" ")[0]
    print(units,nunits,collected_date)
    if (units == "heures") | (units == "heure") :
        temp = collected_date - relativedelta(hours=int(nunits))
    if (units == "jours") | (units == "jours") :
        temp = collected_date - relativedelta(days=int(nunits))
    if (units == "semaines") | (units == "semaine") :
        temp = collected_date - relativedelta(weeks=int(nunits))
    if units == "mois" :
        temp = collected_date - relativedelta(month=int(nunits))
    if units == "ans" :
        temp = collected_date - relativedelta(years=int(nunits))
    else :
        print(nunits)
        print(temp)
    return temp

def get_review_summary(result_set):
    rev_dict = {'Review Rate': [],
        'Review Time': [],
        'Review Text' : [],
        'Review date collected':[]}
    for result in result_set:
        review_rate = len(result.findAll('img', attrs={'class':'hCCjke vzX5Ic','src':'//maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_14.png'}))
        review_time = result.find('span',class_='rsqaWe').text

        try :
            review_text = result.find('span', class_='wiI7pd').text
        except :
            review_text = ""
        rev_dict['Review Rate'].append(review_rate)
        rev_dict['Review Time'].append(review_time)
        rev_dict['Review Text'].append(review_text)
        rev_dict['Review date collected'].append(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
    return(pd.DataFrame(rev_dict))


def get_google_review(url, entreprise, name, nb_avis):
    # Import the webdriver
    driver = webdriver.Firefox()
    driver.get(url)

    # privacy pop-up
    xpath = "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button/span"
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

    xpath_nb_avis = "/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div[1]/div/div[2]/div[2]"
    #total_number_of_reviews = soup.find("div", class_="gm2-caption").text
    total_number_of_reviews =driver.find_element_by_xpath(xpath_nb_avis).text

    print(total_number_of_reviews)


    ## Catch nombre d'avis
    total_number_of_reviews = int(total_number_of_reviews.split(" ")[-2].replace("\u202f",""))
    rec_log(entreprise, name, url, total_number_of_reviews)
    #total_number_of_reviews = soup.find("div", class_="gm2-caption").text
    #a = total_number_of_reviews
    time.sleep(1)
    try :
        xpatrier = "/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div[8]/div[2]/button/span/span"
        driver.find_element_by_xpath(xpatrier).click()
    except :
        print("echec ouverture Trier")

    time.sleep(2)
    xpatrecent = "/html/body/div[3]/div[3]/div[1]/div[2]"
    driver.find_element_by_xpath(xpatrecent).click()

    ## Catch cellule of reviews

    books_html = soup.findAll('div', class_ ="jftiEf fontBodyMedium")
    len(books_html)




    #Find scroll layout
    old_scroll = '//*[@id="pane"]/div/div[1]/div/div/div[2]'
    old_scroll = "/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]"
    scroll = "/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]"
    scrollable_div = driver.find_element_by_xpath(scroll)
    #Scroll as many times as necessary to load all reviews
    for i in (range(0, (round(total_number_of_reviews / 10 - 1)))):
        print(i)
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight',
                scrollable_div)
        time.sleep(2)
    try :
        liste_plus =driver.find_elements_by_xpath('//button[normalize-space()="Plus"]')
    except :
        print("stop")
    for i in liste_plus :
        try :
            i.click()
        except :
            print("tant pis")

    response = BeautifulSoup(driver.page_source, 'html.parser')


    #reviews = response.find_all('div',
    #                            class_='MyEned')

    reviews = response.find_all("div", class_="jftiEf fontBodyMedium")



    driver.close()
    return reviews


def get_list_review_google(url, entreprise,name, nb_avis=None):
    tmp = get_google_review(url, entreprise, name, nb_avis)
    tmp = get_review_summary(tmp)
    tmp = transform_date(tmp)
    tmp["review estimated date"] = [estimated_date(i, j) for i, j in zip(
        tmp["Review Time"], tmp["Review date collected"])]
    tmp = tmp.replace('\|', ',', regex=True)
    tmp.to_csv(name + '.csv',sep='|', encoding='utf-8')
    return tmp


if __name__ == "__main__":
    entreprise = "leroymerlin"
    url = 'https://www.google.fr/maps/place/Leroy+Merlin+Lognes/@48.8337414,2.642878,17z/data=!4m22!1m13!4m12!1m4!2m2!1d2.2511616!2d48.9684992!4e1!1m6!1m2!1s0x47e6055c73ac4625:0x9eb7882300ea97b1!2sleroy+merlin+lognes!2m2!1d2.6435539!2d48.8337096!3m7!1s0x47e6055c73ac4625:0x9eb7882300ea97b1!8m2!3d48.8337096!4d2.6435539!9m1!1b1!16s%2Fg%2F1tgfvyb1'
    name = 'leroymerlin lognes'
    temp = get_list_review_google(url, entreprise,name)
    print(temp)
