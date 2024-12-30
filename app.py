import streamlit as st
import os
import pandas as pd

# On importe votre fonction de collecte
from scrap_city.google_reviews import get_list_review_google

def main():
    st.title("Scraper Google Reviews")
    st.markdown("""
    Cette application Streamlit permet de récupérer des commentaires Google Maps
    en entrant simplement l'URL Google, ainsi que le nom de l'entreprise et un identifiant.
    """)

    # Champs de saisie
    url = st.text_input("Entrez le lien Google Maps :", "")
    entreprise = st.text_input("Nom de l'entreprise :", "")
    lieu = st.text_input("Identifiant du lieu (ex: 'Collegien') :", "")

    # Bouton pour lancer la collecte
    if st.button("Lancer la collecte"):
        if url and entreprise and lieu:
            # Appel à votre fonction
            st.info("Collecte en cours...")
            get_list_review_google(url, entreprise, lieu)  # Génère <entreprise>_<lieu>.csv
            csv_file_name = f"{entreprise}_{lieu}.csv"

            if os.path.exists(csv_file_name):
                st.success("Scraping terminé ! Vous pouvez télécharger le CSV ci-dessous.")

                # Lecture du CSV pour éventuellement l'afficher ou juste permettre le download
                with open(csv_file_name, "rb") as f:
                    st.download_button(
                        label="Télécharger le fichier CSV",
                        data=f,
                        file_name=csv_file_name,
                        mime="text/csv"
                    )

                # Optionnel : Aperçu rapide du CSV
                df = pd.read_csv(csv_file_name, sep='|')
                st.dataframe(df)
            else:
                st.error("Le fichier CSV n'a pas été trouvé.")
        else:
            st.warning("Veuillez remplir tous les champs (URL, entreprise, lieu).")

if __name__ == "__main__":
    main()
