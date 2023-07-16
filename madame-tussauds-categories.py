import wikipedia
import concurrent.futures
from tqdm import tqdm
import matplotlib.pyplot as plt
import sqlite3
from collections import Counter
import pandas as pd

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('categories.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS categories
             (name TEXT PRIMARY KEY, category TEXT)''')

def get_category(name):
    conn = sqlite3.connect('categories.db')
    c = conn.cursor()
    # First try to get the category from the database
    c.execute("SELECT category FROM categories WHERE name=?", (name,))
    row = c.fetchone()
    if row is not None:
        return row[0]

    # If the person is not in the database, fetch the category from Wikipedia
    try:
        page = wikipedia.page(name)
        categories = [category.lower() for category in page.categories]
        category_dict = {
            "Actor": ["actor", "actress", "film actor", "television actor"],
            "Musician": ["musician", "singer", "songwriter", "rapper", "composer", "band"],
            "Politician": ["politician", "president", "prime minister", "leader", "mayor", "governor"],
            "Sportsperson": ["footballer", "cricketer", "basketball player", "athlete", "tennis player", "golfer", "swimmer"],
            "Scientist": ["scientist", "physicist", "chemist", "biologist", "astronomer", "mathematician"],
            "Writer": ["writer", "novelist", "playwright", "poet", "journalist", "author"],
            "Artist": ["artist", "painter", "sculptor", "photographer", "designer"],
            "Academic": ["professor", "scholar", "academic", "educator"],
            "Businessperson": ["businessperson", "entrepreneur", "ceo", "executive", "investor"],
            "Engineer": ["engineer", "inventor"],
            "Fashion Designer": ["fashion designer", "stylist"],
            "Model": ["model"],
            "Producer": ["film producer", "music producer", "television producer"],
            "Director": ["film director", "theatre director", "television director"],
            "Dancer": ["dancer", "choreographer"],
            "Chef": ["chef", "cook"],
            "Architect": ["architect"],
            "Comedian": ["comedian", "humorist"],
            "TV Personality": ["television personality", "presenter", "host", "reporter"],
            "Philanthropist": ["philanthropist"],
            "Humanitarian": ["humanitarian"],
            "Activist": ["activist"],
            "Astronaut": ["astronaut"],
            "Military Personnel": ["military personnel", "soldier", "general", "admiral"],
            "Lawyer": ["lawyer", "attorney", "judge"],
            "Historian": ["historian"],
            "Philosopher": ["philosopher"],
            "Psychologist": ["psychologist"],
            "Social Worker": ["social worker"],
            "Civil Servant": ["civil servant"],
            "Journalist": ["journalist"],
            "Photographer": ["photographer"],
            "Inventor": ["inventor"],
            "Animator": ["animator"]
        }
        for category in categories:
            if "births" in category or "deaths" in category:
                continue
            for category_name, keywords in category_dict.items():
                if any(keyword in category for keyword in keywords):
                    # Store the category in the database for future use
                    c.execute("INSERT OR IGNORE INTO categories VALUES (?, ?)", (name, category_name))
                    conn.commit()
                    return category_name
        return "Other"
    except:
        return None

def scrape_wiki():
    names = wikipedia.page("List of wax figures displayed at Madame Tussauds museums").links
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        categories = list(tqdm(executor.map(get_category, names), total=len(names)))
    category_counts = Counter(categories)
    fig, ax = plt.subplots()
    ax.bar(category_counts.keys(), category_counts.values())
    ax.set_xlabel('Category')
    ax.set_ylabel('Count')
    ax.set_title('Category counts')
    plt.xticks(rotation=90)
    plt.show()

def plot_categories():
    conn = sqlite3.connect('categories.db')
    df = pd.read_sql_query("SELECT category, COUNT(*) as count FROM categories GROUP BY category", conn)
    conn.close()
    plt.figure(figsize=(10, 6))
    bars = plt.barh(df['category'], df['count'], color='steelblue')
    plt.xlabel('Count')
    plt.title("Distribution of Categories in Madame Tussaud's wax figures")
    plt.gca().invert_yaxis()
    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2, f'{width}', ha='left', va='center')

    plt.show()

plot_categories()
