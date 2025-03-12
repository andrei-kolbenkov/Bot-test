import sqlite3
import requests
from lxml import html


# Функция для очистки цены
def clean_price(price):
    if price == "Цена не найдена" or price.startswith("Ошибка"):
        return None
    cleaned_price = price.replace('₽', '').replace(' ', '').replace(',', '.')
    cleaned_price = ''.join(filter(lambda x: x.isdigit() or x == '.', cleaned_price))
    return float(cleaned_price) if cleaned_price else None

# Функция для парсинга цены
def parse_price(url, xpath):
    try:
        response = requests.get(url)
        response.raise_for_status()
        tree = html.fromstring(response.content)
        price_element = tree.xpath(xpath)
        if price_element:
            return price_element[0].text
        else:
            return "Цена не найдена"
    except Exception as e:
        return f"Ошибка при парсинге: {e}"

# Функция для получения данных из бд
def fetch_sites_from_db():
    conn = sqlite3.connect('sites.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title, url, xpath FROM sites")
    sites = cursor.fetchall()
    conn.close()
    return sites

# Функция для вычисления средней цены
def calculate_average_price(prices):
    valid_prices = [price for price in prices if price is not None]
    if not valid_prices:
        return None
    return sum(valid_prices) / len(valid_prices)

# Основная функция
def get_average_price():
    # Получаем данные из базы данных
    sites = fetch_sites_from_db()
    prices = []
    # Парсим цены для каждого товара
    for site in sites:
        title, url, xpath = site
        price = parse_price(url, xpath)
        cleaned_price = clean_price(price)

        if __name__ == "__main__":
            print(f"Сайт: {title}")
            print(f"URL: {url}")
            print(f"Цена: {price}")
            print("-" * 40)

        if cleaned_price is not None:
            prices.append(cleaned_price)

    # Вычисляем среднюю цену
    average_price = calculate_average_price(prices)
    if average_price is not None:
        formatted_price = f"{average_price:.2f}".replace('.', ',')
        return f"Средняя цена всех товаров: {formatted_price} RUB"
    else:
        return "Не удалось вычислить среднюю цену."

# Запуск скрипта
if __name__ == "__main__":
    print(get_average_price())