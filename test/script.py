import time
import psycopg2
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

SITE_URL = "http://web-app:3000"

DB_HOST = "postgres"
DB_PORT = 5432
DB_NAME = "requests"
DB_USER = "postgres"
DB_PASS = "postgres"

fake = Faker("ru_RU")

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")
options.add_argument("--disable-features=HSTSPolicyBypassList,HTTPS-FirstMode,HttpsUpgrades,SSLVersionMin")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--incognito")

print("Инициализация Selenium...")
driver = webdriver.Chrome(options=options)

unique_mark = int(time.time())
created_emails = []

try:
    print(f"\n[Шаг 1] Заполняем форму 100 раз через Selenium на {SITE_URL}...")

    for i in range(1, 101):
        driver.get(SITE_URL)
        time.sleep(0.2)

        full_name = fake.name()
        phone = fake.phone_number()
        email = f"selenium_{unique_mark}_{i}@example.com"
        message = fake.sentence(nb_words=10)

        created_emails.append(email)

        try:
            driver.find_element(By.NAME, "fullName").send_keys(full_name)
            driver.find_element(By.NAME, "phone").send_keys(phone)    
            driver.find_element(By.NAME, "email").send_keys(email)
            driver.find_element(By.NAME, "message").send_keys(message)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
        except Exception:
            print(f"❌ Не найдены поля формы на шаге {i}. Проверьте атрибуты name в HTML.")
            break

        if i % 20 == 0:
            print(f"-> Отправлено через браузер: {i}/100")

    print("Эмуляция завершена.")

finally:
    driver.quit()
    print("Браузер закрыт.")

print(f"\n[Шаг 2] Подключение к PostgreSQL ({DB_HOST}:{DB_PORT}) для проверки...")
time.sleep(3)

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM requests WHERE email = ANY(%s);",
        (created_emails,),
    )
    count_in_db = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(DISTINCT full_name)
        FROM requests
        WHERE email = ANY(%s);
        """,
        (created_emails,),
    )
    distinct_names = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT MIN(id), MAX(id)
        FROM requests
        WHERE email = ANY(%s);
        """,
        (created_emails,),
    )
    min_id, max_id = cursor.fetchone()

    cursor.execute(
        """
        SELECT id, full_name, phone, email, message
        FROM requests
        WHERE email = ANY(%s)
        ORDER BY id
        LIMIT 5;
        """,
        (created_emails,),
    )
    sample = cursor.fetchall()

    print("=" * 60)
    print(f"Всего найдено записей:       {count_in_db} из 100")
    print(f"Уникальных имён (full_name): {distinct_names} из 100")
    print(f"Диапазон id:                 {min_id} .. {max_id}")
    print("=" * 60)
    print("Примеры записей:")
    for row in sample:
        print(f"  id={row[0]} | {row[1]} | {row[2]} | {row[3]}")

    cursor.close()
    conn.close()
except Exception as db_err:
    print(f"❌ Ошибка подключения напрямую к БД: {db_err}")