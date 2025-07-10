# 📊 ForexFactory Economic Events Scraper

Скрейпер для збору макроекономічних подій США з сайту [ForexFactory](https://www.forexfactory.com/calendar). Скрипт автоматично витягує ключові економічні показники по USD (наприклад, NFP, CPI, ISM) за періоди з 2010 по 2025 роки та зберігає їх у CSV-файли.

## 📌 Мета

Отримати історичні дані по макроекономічних подіях, які можуть використовуватись для:

- Економічного аналізу
- Бектестів торгових стратегій
- Побудови баз даних для трейдингових ботів або аналітики

---

## ⚙️ Функціонал

- Скрейпінг сайту **ForexFactory** з обхідником Cloudflare (`cloudscraper`)
- Отримання подій лише по **валюті USD**
- Фільтрація лише за **важливими показниками** (NFP, ISM, CPI тощо)
- Збереження результатів у `.csv` для кожного місяця
- Обробка з 2010 по 2025 роки
- Логування процесу у консоль

---

## 📁 Структура виводу

project_root/

├── 2010/

│ ├── economic_indicators_jan1.2010.csv

│ └── ...

├── 2025/

│ └── economic_indicators_dec1.2025.csv


CSV-файли зберігаються з роздільником `\t` (табуляція) та містять:

- `Date` — дата події (YYYY-MM-DD HH:MM:SS)
- `Time` — час події
- `Currency` — валюта (USD)
- `Event` — назва події
- `Impact` — рівень впливу (0–3)
- `Actual`, `Forecast`, `Previous` — значення показника
- `PM` — ознака, чи це **pm (1)** чи **am (0)** час

---

## 🚀 Як запустити

### 🔧 1. Встановити залежності:

```bash
pip install cloudscraper beautifulsoup4 pandas
```
2. Запуск:
```
python filename.py
```
Які події враховуються:
- ISM Manufacturing PMI
- JOLTS Job Openings
- ADP Non-Farm Employment Change
- Unemployment Claims
- ISM Services PMI
- Non-Farm Employment Change
- Average Hourly Earnings m/m
- Unemployment Rate

Усі події та валюти можна змінювати, так само як дати. 

Автор: revelaut

