import sys
import csv
import logging  # <-- Ajout du module logging
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Configuration de base du logger
logging.basicConfig(
    level=logging.INFO,  # Pour afficher les logs de niveau INFO et supérieur
    format='%(asctime)s - %(levelname)s - %(message)s'
)

sele = FirefoxService(GeckoDriverManager().install())
# Fonction pour enregistrer le log dans le fichier CSV
def rec_log(entreprise, name, url, nb_avis_disponible, delta=None):
    logging.info(f"Entrée dans rec_log() avec entreprise={entreprise}, name={name}, url={url}, nb_avis_disponible={nb_avis_disponible}, delta={delta}")
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
    logging.info(f"Fichier log.csv existe ? {fichier_existe}")

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
    logging.info("Le log a bien été enregistré dans log.csv")

def transform_date(A):
    logging.info("Entrée dans transform_date()")
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
    logging.info("transform_date() a terminé la transformation des champs Review Time.")
    return A

def estimated_date(google_date, collected_date):
    logging.info(f"Entrée dans estimated_date() avec google_date='{google_date}', collected_date='{collected_date}'")
    units = google_date.split(" ")[1]
    nunits = google_date.split(" ")[0]
    temp = collected_date
    try:
        if (units == "minute") | (units == "minutes"):
            temp = collected_date - relativedelta(minutes=int(nunits))
        if (units == "heures") | (units == "heure"):
            temp = collected_date - relativedelta(hours=int(nunits))
        if (units == "jours") | (units == "jours"):
            temp = collected_date - relativedelta(days=int(nunits))
        if (units == "semaines") | (units == "semaine"):
            temp = collected_date - relativedelta(weeks=int(nunits))
        if units == "mois":
            temp = collected_date - relativedelta(months=int(nunits))
        if units == "ans":
            temp = collected_date - relativedelta(years=int(nunits))
    except ValueError as e:
        logging.warning(f"Problème lors de la conversion en int(nunits): {e}")
    logging.info(f"estimated_date() retourne la date estimée : {temp}")
    return temp

def get_review_summary(result_set):
    logging.info(f"Entrée dans get_review_summary() pour {len(result_set)} reviews trouvées.")
    rev_dict = {'Review Rate': [],
        'Review Time': [],
        'Review Text' : [],
        'Review date collected':[]}

    for idx, result in enumerate(result_set, start=1):
        try:
            review_rate = result.find('span',class_='kvMYJc')['aria-label']
        except Exception as e:
            logging.error(f"Erreur lors de l'extraction du 'Review Rate' : {e}")
            review_rate = "N/A"
        review_time = result.find('span',class_='rsqaWe').text
        try:
            review_text = result.find('span', class_='wiI7pd').text
        except:
            review_text = ""

        rev_dict['Review Rate'].append(review_rate)
        rev_dict['Review Time'].append(review_time)
        rev_dict['Review Text'].append(review_text)
        rev_dict['Review date collected'].append(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))

    logging.info("get_review_summary() a fini de constituer le dataframe.")
    return(pd.DataFrame(rev_dict))

def get_google_review(url, entreprise, name, nb_avis):
    logging.info(f"Entrée dans get_google_review() pour {entreprise} - {name} - nb_avis={nb_avis}")
    # Import the webdriver
    driver = webdriver.Firefox(service=sele)
    driver.get(url)

    # privacy pop-up
    xpath = "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button/span"
    try:
        driver.find_element_by_xpath(xpath).click()
        logging.info("Pop-up de confidentialité cliquée avec succès.")
    except:
        logging.warning("Pop-up de confidentialité introuvable ou déjà fermée.")

    try:
        driver.find_element_by_xpath("/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/span[1]/span/span/span[2]/span[1]/button").click()
        logging.info("Clic sur le nombre d'avis effectué.")
    except:
        logging.warning("Impossible de cliquer sur le nombre d'avis.")

    time.sleep(2)

    soup = BeautifulSoup(driver.page_source,"html.parser")

    xpath_nb_avis = "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div/div[2]/div[3]"
    try:
        total_number_of_reviews_text = driver.find_element_by_xpath(xpath_nb_avis).text
        total_number_of_reviews = float(total_number_of_reviews_text.split(" ")[-2].replace("\u202f", ""))
        logging.info(f"Nombre total d'avis détectés : {total_number_of_reviews}")
    except Exception as e:
        total_number_of_reviews = 0
        logging.error(f"Erreur lors de la récupération du nombre d'avis : {e}")

    # Catch nombre d'avis
    if nb_avis is not None:
        diff = total_number_of_reviews - float(nb_avis)
        rec_log(entreprise, name, url, total_number_of_reviews, diff)
    else:
        rec_log(entreprise, name, url, float(total_number_of_reviews))

    # Check if there are new comment
    if nb_avis == total_number_of_reviews:
        print("aucun commentaire détecter")
        logging.info("Aucun nouveau commentaire à extraire, on quitte.")
        driver.close()
        return # sys.exit()

    time.sleep(1)
    try:
        xpatrier = "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[8]/div[2]/button/span"
        driver.find_element_by_xpath(xpatrier).click()
        logging.info("Menu 'Trier' ouvert avec succès.")
    except:
        logging.warning("Échec de l'ouverture du menu 'Trier'.")

    time.sleep(2)
    try:
        xpatrecent = "/html/body/div[2]/div[3]/div[3]/div[1]/div[2]"
        driver.find_element_by_xpath(xpatrecent).click()
        logging.info("Triage par avis les plus récents cliqué avec succès.")
    except:
        logging.warning("Échec du bouton 'avis les plus récents'.")

    books_html = soup.findAll('div', class_ ="jftiEf fontBodyMedium")
    logging.info(f"Nombre de reviews trouvées avant scrolling : {len(books_html)}")

    #Find scroll layout
    old_scroll = '//*[@id="pane"]/div/div[1]/div/div/div[2]'
    old_scroll = "/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]"
    scroll = "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]"

    try:
        scrollable_div = driver.find_element_by_xpath(scroll)
    except:
        scrollable_div = None
        logging.error("Impossible de trouver l'élément scrollable.")

    if nb_avis is not None:
        total_number_of_reviews = total_number_of_reviews - float(nb_avis)

    if scrollable_div and total_number_of_reviews >= 10:
        for i in range(0, (round(total_number_of_reviews / 10 - 1))):
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)
        logging.info("Scrolling terminé pour charger d'autres avis.")
    else:
        logging.info("Pas de scrolling nécessaire ou scrollable_div introuvable.")

    try:
        liste_plus = driver.find_elements_by_xpath('//button[normalize-space()="Plus"]')
        for idx, plus_button in enumerate(liste_plus, start=1):
            try:
                plus_button.click()
            except:
                logging.warning(f"Impossible de cliquer sur le bouton 'Plus' n°{idx}.")
    except:
        logging.warning("Aucun bouton 'Plus' trouvé.")

    response = BeautifulSoup(driver.page_source, 'html.parser')
    reviews = response.find_all("div", class_="jftiEf fontBodyMedium")
    reviews = reviews[:int(total_number_of_reviews)]
    logging.info(f"Nombre de reviews réellement renvoyées : {len(reviews)}")

    driver.close()
    logging.info("Fermeture du navigateur dans get_google_review().")
    return reviews

def get_list_review_google(url, entreprise, name, nb_avis=None):
    logging.info(f"Entrée dans get_list_review_google() pour url={url}, entreprise={entreprise}, name={name}, nb_avis={nb_avis}")
    tmp = get_google_review(url, entreprise, name, nb_avis)
    if tmp is None:
        logging.info("Aucune review récupérée, fin de la fonction.")
        return
    tmp = get_review_summary(tmp)
    tmp = transform_date(tmp)
    tmp["review estimated date"] = [estimated_date(i, j) for i, j in zip(
        tmp["Review Time"], tmp["Review date collected"])]

    tmp = tmp.replace('\|', ',', regex=True)
    filename = entreprise + "_" + name  # Nom pour le fichier CSV

    # Vérifier si le fichier existe
    if os.path.isfile(filename + '.csv'):
        tmp.to_csv(filename + '.csv', sep='|', encoding='utf-8', index=False, mode='a', header=False)
        logging.info(f"{len(tmp)} reviews ajoutées au fichier existant : {filename}.csv")
    else:
        tmp.to_csv(filename + '.csv', sep='|', encoding='utf-8', index=False)
        logging.info(f"Fichier créé : {filename}.csv avec {len(tmp)} reviews.")
    return tmp

def test():
    logging.info("Début de la fonction test().")
    # Chemin vers le fichier CSV
    chemin_fichier = 'log.csv'

    # Charger le fichier CSV avec pandas
    data_frame = pd.read_csv(chemin_fichier)
    logging.info(f"log.csv chargé avec {len(data_frame)} lignes.")

    # Convertir la colonne "date" en type datetime
    data_frame['date'] = pd.to_datetime(data_frame['date'])

    # Trier le dataframe par ordre décroissant de la colonne de date
    data_frame = data_frame.sort_values('date', ascending=False)

    # Regrouper les lignes par les colonnes qui doivent être identiques
    groupes = data_frame.groupby(['entreprise', 'name', 'url'])
    logging.info("Groupby effectué sur (entreprise, name, url).")

    # Sélectionner la ligne la plus récente dans chaque groupe
    lignes_recentes = groupes.apply(
        lambda x: x[x['date'] == x['date'].max()]['nb_avis'])

    # Parcourir les lignes sélectionnées
    for index, nb_avis in lignes_recentes.iteritems():
        entreprise = index[0]
        name = index[1]
        url = index[2]
        logging.info(f"test() - groupe : entreprise={entreprise}, name={name}, url={url}, nb_avis={nb_avis}")
        get_list_review_google(url, entreprise, name, nb_avis)

if __name__ == "__main__":
    #entreprise = "Leroy Merlin"
    #url = 'https://www.google.fr/maps/place/Leroy+Merlin+Collégien/@48.8350548,2.660387,17z/data=!4m8!3m7!1s0x47fa21b36c8d581f:0x4b608c92ba1bf7f!8m2!3d48.8350548!4d2.6625757!9m1!1b1!16s%2Fg%2F1pxwgmh18'
    #name = 'Collegien'
    #get_list_review_google(url, entreprise,name)
    #rec_log(
    #    entreprise="BR Peformance",
    #    name="Amiens",
    #    url="https://www.google.fr/maps/place/BR-Performance+Amiens/@49.8540983,1.8203346,17z/data=!4m8!3m7!1s0x47e767cabeb3b4ef:0x9561abfd476e0ddd!8m2!3d49.8540949!4d1.8229095!9m1!1b1!16s%2Fg%2F11j4y7sjv0?entry=ttu",
    #    nb_avis_disponible=0)
    test()
