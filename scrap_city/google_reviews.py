import sys
import csv
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

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
    if (units == "minute") | (units == "minutes") :
        temp = collected_date - relativedelta(minutes=int(nunits))
    if (units == "heures") | (units == "heure") :
        temp = collected_date - relativedelta(hours=int(nunits))
    if (units == "jours") | (units == "jours") :
        temp = collected_date - relativedelta(days=int(nunits))
    if (units == "semaines") | (units == "semaine") :
        temp = collected_date - relativedelta(weeks=int(nunits))
    if units == "mois" :
        temp = collected_date - relativedelta(months=int(nunits))
    if units == "ans" :
        temp = collected_date - relativedelta(years=int(nunits))
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
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
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

    xpath_nb_avis = "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div/div[2]/div[3]"
    #total_number_of_reviews = soup.find("div", class_="gm2-caption").text
    total_number_of_reviews =driver.find_element_by_xpath(xpath_nb_avis).text



    ## Catch nombre d'avis
    total_number_of_reviews = float(
        total_number_of_reviews.split(" ")[-2].replace("\u202f", ""))
    if nb_avis is not None :
        rec_log(entreprise, name, url, total_number_of_reviews,
            total_number_of_reviews - float(nb_avis))
    else :
        rec_log(entreprise, name, url, float(total_number_of_reviews))

    # Check if there are new comment
    if nb_avis == total_number_of_reviews:
        print("aucun commentaire détecter")
        driver.close()
        return # sys.exit()

    time.sleep(1)
    try :
        xpatrier = "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[8]/div[2]/button/span"
        driver.find_element_by_xpath(xpatrier).click()
    except :
        print("echec ouverture Trier")

    time.sleep(2)
    try :
        xpatrecent = "/html/body/div[2]/div[3]/div[3]/div[1]/div[2]"
        driver.find_element_by_xpath(xpatrecent).click()
    except :
        print("echec du bouton avis les plus récents")
    ## Catch cellule of reviews

    books_html = soup.findAll('div', class_ ="jftiEf fontBodyMedium")
    len(books_html)




    #Find scroll layout
    old_scroll = '//*[@id="pane"]/div/div[1]/div/div/div[2]'
    old_scroll = "/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]"
    scroll = "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]"

    scrollable_div = driver.find_element_by_xpath(scroll)
    #Scroll as many times as necessary to load all reviews


    if nb_avis is not None :
        total_number_of_reviews = total_number_of_reviews - float(nb_avis)

    if total_number_of_reviews >= 10 :
        for i in (range(0, (round(total_number_of_reviews / 10 - 1)))):
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
    reviews = reviews[:int(total_number_of_reviews)]


    driver.close()
    return reviews

def get_list_review_google(url, entreprise,name, nb_avis=None):
    tmp = get_google_review(url, entreprise, name, nb_avis)
    if tmp is None :
        return
    tmp = get_review_summary(tmp)
    tmp = transform_date(tmp)
    tmp["review estimated date"] = [estimated_date(i, j) for i, j in zip(
        tmp["Review Time"], tmp["Review date collected"])]
    tmp = tmp.replace('\|', ',', regex=True)
    name = entreprise + "_" + name  # Remplacez par le nom souhaité pour le fichier CSV

    # Code pour générer le dataframe tmp

    # Vérifier si le fichier existe
    if os.path.isfile(name + '.csv'):
        # Le fichier existe, ajouter les lignes au fichier CSV existant
        tmp.to_csv(name + '.csv', sep='|', encoding='utf-8', index=False, mode='a', header= False)
    else:
        # Le fichier n'existe pas, créer un nouveau fichier CSV avec les lignes
        tmp.to_csv(name + '.csv', sep='|', encoding='utf-8', index=False)
    return tmp

def test():
    # Chemin vers le fichier CSV
    chemin_fichier = 'log.csv'

    # Charger le fichier CSV avec pandas
    data_frame = pd.read_csv(chemin_fichier)

    # Convertir la colonne "date" en type datetime
    data_frame['date'] = pd.to_datetime(data_frame['date'])

    # Trier le dataframe par ordre décroissant de la colonne de date
    data_frame = data_frame.sort_values('date', ascending=False)
    # Regrouper les lignes par les colonnes qui doivent être identiques
    groupes = data_frame.groupby(['entreprise', 'name', 'url'])

    # Sélectionner la ligne la plus récente dans chaque groupe
    lignes_recentes = groupes.apply(
        lambda x: x[x['date'] == x['date'].max()]['nb_avis'])

    # Obtenir les lignes correspondantes du dataframe original
    #lignes_selectionnees = data_frame.loc[lignes_recentes]
    # Parcourir les lignes sélectionnées
    for index, nb_avis in lignes_recentes.iteritems():
        entreprise = index[0]
        name = index[1]
        url = index[2]
        nb_avis = nb_avis
        #delta = row['delta']
        get_list_review_google(url, entreprise, name, nb_avis)

if __name__ == "__main__":
    #entreprise = "Leroy Merlin"
    #url = 'https://www.google.fr/maps/place/Leroy+Merlin+Collégien/@48.8350548,2.660387,17z/data=!4m8!3m7!1s0x47fa21b36c8d581f:0x4b608c92ba1bf7f!8m2!3d48.8350548!4d2.6625757!9m1!1b1!16s%2Fg%2F1pxwgmh18'
    #name = 'Collegien'
    #get_list_review_google(url, entreprise,name)
    #rec_log(
    #    entreprise="Autobac",
    #    name="Autobacs Herblay",
    #    url=
    #    "https://www.google.com/maps/place/Autobacs+Herblay/@49.0043754,2.1765449,17z/data=!4m8!3m7!1s0x47e660be3166eaa3:0x875bbd5e31321cc6!8m2!3d49.0043754!4d2.1765449!9m1!1b1!16s%2Fg%2F1tdzkw9t?entry=ttu",
    #    nb_avis_disponible=0)
    test()
