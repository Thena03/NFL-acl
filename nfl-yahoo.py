import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

KEYWORDS = ["ACL", "KNEE", "MCL", "MENISCUS", "Knee", "Knee - ACL", "Knee - Meniscus", "Knee - MCL"]

# ---------- DRIVER ----------
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


# ---------- YAHOO ----------
def scrape_yahoo(driver, season):
    url = "https://sports.yahoo.com/nfl/injuries/"
    driver.get(url)

    data = []

    try:
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
        )
    except:
        return []

    for row in rows:
        try:
            cols = row.find_elements(By.TAG_NAME, "td")
            player = cols[0].text
            position = cols[1].text
            injury = cols[2].text
            date = cols[3].text

            if any(k in injury.upper() for k in KEYWORDS):
                data.append({
                    "Season": season,
                    "Player": player,
                    "Team": position,
                    "Injury": injury,
                    "Date": date,
                    "Source": "Yahoo"
                })
        except:
            continue

    return data

# ---------- MAIN ----------
def main():
    driver = init_driver()
    all_data = []

    current_year = 2025
    seasons = list(range(current_year - 4, current_year + 1))

    for season in seasons:
        print(f"\nScraping season {season}...")

        season_data = []
        #season_data.extend(scrape_espn(driver, season))
        #season_data.extend(scrape_nfl(driver, season))
        season_data.extend(scrape_yahoo(driver, season))

        df_season = pd.DataFrame(season_data)
        df_season.to_csv(f"nfl_knee_acl_injuries_{season}.csv", index=False)

        print(f"Saved {len(df_season)} injuries for {season}")
        all_data.extend(season_data)

    driver.quit()

    df_master = pd.DataFrame(all_data)
    df_master.to_csv("nfl_knee_acl_injuries_last_5_seasons.csv", index=False)

    print(f"\n✅ Master CSV saved with {len(df_master)} total injuries")

if __name__ == "__main__":
    main()
