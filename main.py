from keep_alive import keep_alive
keep_alive()
send_email()
send_telegram()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import requests

# === CONFIGURATION ===
nin = "109990887032670003"
card_number = "250199032670"

email_from = "fazfaz1504@gmail.com"
email_password = "ebflpcqeorvmqkhx"
email_to = "fazfaz1504@gmail.com"

telegram_token = "8249997354:AAEe1gPRHCFGQ9JkL8XmLVLSV_pu3JmwXoA"
telegram_chat_id = "5445970640"

check_interval = 600  # en secondes (10 minutes)

# === NOTIFICATION EMAIL (disponible) ===
def send_email():
    subject = "🔔 Rendez-vous ANEM disponible !"
    body = "Un rendez-vous est disponible sur https://minha.anem.dz/pre_inscription"

    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_from, email_password)
    server.sendmail(email_from, email_to, msg.as_string())
    server.quit()
    print("[INFO] Email envoyé (DISPO) !")

# === NOTIFICATION EMAIL (pas dispo) ===
def send_email_pas_dispo():
    subject = "🔕 Pas de rendez-vous ANEM"
    body = "Aucun rendez-vous n'est disponible pour le moment sur https://minha.anem.dz/pre_inscription"

    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_from, email_password)
    server.sendmail(email_from, email_to, msg.as_string())
    server.quit()
    print("[INFO] Email envoyé (PAS DISPO) !")

# === NOTIFICATION TELEGRAM (disponible) ===
def send_telegram():
    message = "🔔 Rendez-vous ANEM disponible ! Va vite sur https://minha.anem.dz/pre_inscription"
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {"chat_id": telegram_chat_id, "text": message}
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print("[INFO] Message Telegram envoyé (DISPO) !")
    else:
        print("[ERREUR] Échec envoi Telegram (DISPO)")

# === NOTIFICATION TELEGRAM (pas dispo) ===
def send_telegram_pas_dispo():
    message = "🔕 Aucun rendez-vous ANEM pour le moment."
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {"chat_id": telegram_chat_id, "text": message}
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print("[INFO] Message Telegram envoyé (PAS DISPO) !")
    else:
        print("[ERREUR] Échec envoi Telegram (PAS DISPO)")

# === VÉRIFICATION DU RENDEZ-VOUS ===
def check_rdv():
    print("[INFO] Vérification des rendez-vous...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://minha.anem.dz/pre_inscription")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "code1"))).send_keys(nin)
        driver.find_element(By.ID, "code2").send_keys(card_number)
        driver.find_element(By.ID, "btnPreInscription").click()

        try:
            popup_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "swal2-confirm")))
            popup_btn.click()
        except TimeoutException:
            pass

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "formErrorContent")))
        if "لا يوجد أي موعد متاح حاليا" not in driver.page_source:
            print("[ALERTE] Rendez-vous DISPONIBLE !")
            send_email()
            send_telegram()
        else:
            print("[INFO] Aucun rendez-vous pour le moment.")
            send_email_pas_dispo()
            send_telegram_pas_dispo()

    except Exception as e:
        print(f"[ERREUR] Problème pendant l'exécution : {e}")
    finally:
        driver.quit()

# === BOUCLE INFINIE ===
if __name__ == "__main__":
    print("[INFO] Lancement du bot ANEM...")
    while True:
        check_rdv()
        time.sleep(check_interval)
