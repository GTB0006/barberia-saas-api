from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

_driver = None


def iniciar_whatsapp():
    global _driver

    if _driver:
        return _driver

    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=C:/whatsapp_profile")
    options.add_argument("--profile-directory=Default")

    _driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    _driver.get("https://web.whatsapp.com")
    time.sleep(20)  # tiempo real para que cargue WhatsApp

    return _driver


def enviar_mensaje(numero, mensaje):
    driver = iniciar_whatsapp()

    url = f"https://web.whatsapp.com/send?phone={numero}&text={mensaje}"
    driver.get(url)

    time.sleep(10)

    try:
        # 🟢 BOTÓN ENVIAR (WhatsApp cambia iconos, este selector funciona)
        boton_enviar = driver.find_element(
            By.XPATH,
            '//button[@aria-label="Enviar"]'
        )

        # 🚀 CLICK REAL vía JavaScript
        driver.execute_script("arguments[0].click();", boton_enviar)

        print("✅ WhatsApp enviado correctamente")
        time.sleep(2)

    except Exception as e:
        print("❌ Error enviando WhatsApp:", e)

