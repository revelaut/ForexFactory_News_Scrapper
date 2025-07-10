from bs4 import BeautifulSoup
import cloudscraper
import pandas as pd
import logging
import time
from datetime import datetime
import os

# Налаштовуємо логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Список подій для скрейпінгу
TARGET_EVENTS = [
    "ISM Manufacturing PMI",
    "JOLTS Job Openings",
    "ADP Non-Farm Employment Change",
    "Unemployment Claims",
    "ISM Services PMI",
    "Non-Farm Employment Change",
    "Average Hourly Earnings m/m",
    "Unemployment Rate"
]


def scrape_forex_factory(month):
    # Витягуємо рік із month (наприклад, 'jan1.2015' → 2015)
    year = int(month.split('.')[1])

    url = f"https://www.forexfactory.com/calendar?month={month}"
    logging.info(f"Скрейпінг URL: {url}")

    scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'ScraperBot/1.0'})
    try:
        logging.info("Завантаження сторінки")
        response = scraper.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("tr", class_="calendar__row")

        data = []
        current_date = ""
        current_time = ""

        for row in rows:
            try:
                # Пропускаємо рядки без валюти
                currency_elements = row.find_all("td", class_="calendar__currency")
                if not currency_elements:
                    continue
                currency = currency_elements[0].text.strip()

                # Отримуємо дату
                date_elements = row.find_all("td", class_="calendar__date")
                if date_elements and date_elements[0].find("span", class_="date"):
                    current_date = date_elements[0].find("span", class_="date").text.strip()

                # Отримуємо час
                time_elements = row.find_all("td", class_="calendar__time")
                if time_elements and time_elements[0].text.strip():
                    current_time = time_elements[0].text.strip()
                else:
                    current_time = current_time or "N/A"

                # Обробка спеціальних випадків часу
                if current_time in ["All D", "Tentati", "Day"] or "th" in current_time:
                    current_time = "00:01"
                    pm = 0
                else:
                    am_pm = current_time[-2:].lower()
                    pm = 0 if am_pm == "am" else 1
                    current_time = current_time[:-2].strip() if am_pm in ["am", "pm"] else current_time

                # Отримуємо подію
                event_elements = row.find_all("td", class_="calendar__event")
                event = event_elements[0].find("span", class_="calendar__event-title").text.strip()

                # Отримуємо impact
                impact_elements = row.find_all("td", class_="calendar__impact")
                impact = "None"
                if impact_elements and impact_elements[0].find("span"):
                    impact_class = impact_elements[0].find("span").get("class")
                    if "gra" in impact_class:
                        impact = 0
                    elif "yel" in impact_class:
                        impact = 1
                    elif "ora" in impact_class:
                        impact = 2
                    elif "red" in impact_class:
                        impact = 3

                # Отримуємо значення
                actual = row.find_all("td", class_="calendar__actual")[0].text.strip()
                forecast = row.find_all("td", class_="calendar__forecast")[0].text.strip()
                previous = row.find_all("td", class_="calendar__previous")[0].text.strip()

                # Форматування дати і часу
                if current_date and current_time != "N/A":
                    try:
                        date_parts = current_date.split()[1:]  # Видаляємо день тижня (Mon, Tue тощо)
                        date_str = ' '.join(date_parts)
                        if len(date_str) > 6:
                            date_str = date_str[:6]  # Обрізаємо до "Apr 01" формату
                        dt = datetime.strptime(f"{date_str} {current_time}", "%b %d %H:%M")
                        dt = dt.replace(year=year)  # Використовуємо рік із month
                        formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception as e:
                        logging.warning(f"Помилка форматування дати для {current_date} {current_time}: {e}")
                        formatted_date = current_date
                else:
                    formatted_date = current_date

                # Логування кожної події
                logging.info(
                    f"Знайдена подія: {event}, Дата: {formatted_date}, Час: {current_time}, Валюта: {currency}")

                # Фільтруємо за TARGET_EVENTS
                if any(target_event in event for target_event in TARGET_EVENTS) and currency == "USD":
                    data.append({
                        "Date": formatted_date,
                        "Time": current_time,
                        "Currency": currency,
                        "Event": event,
                        "Impact": impact,
                        "Actual": actual,
                        "Forecast": forecast,
                        "Previous": previous,
                        "PM": pm
                    })

            except Exception as e:
                logging.error(f"Помилка в обробці рядка: {e}")
                continue

        logging.info(f"Зібрано {len(data)} подій")
        return data

    except Exception as e:
        logging.error(f"Помилка при скрейпінгу: {e}")
        return []


def main():
    # Зовнішній цикл по роках
    for year in range(2010, 2026):
        # Список місяців для поточного року
        months = [f'jan1.{year}', f'feb1.{year}', f'mar1.{year}', f'apr1.{year}',
                  f'may1.{year}', f'jun1.{year}', f'jul1.{year}', f'aug1.{year}',
                  f'sep1.{year}', f'oct1.{year}', f'nov1.{year}', f'dec1.{year}']

        # Внутрішній цикл по місяцях
        for month1 in months:
            result = scrape_forex_factory(month1)

            if result:
                df = pd.DataFrame(result)
                # Створюємо папку для року, якщо її немає
                os.makedirs(str(year), exist_ok=True)
                # Зберігаємо файл у папку року
                filename = f'{year}/economic_indicators_{month1}.csv'
                df.to_csv(filename, sep='\t', index=False)
                logging.info(f"Дані збережено в файл {filename}")
                print(df)
            else:
                print(f"Дані не знайдено для запису за {month1}")

            # Додаємо затримку між запитами
            time.sleep(2)


if __name__ == '__main__':
    main()