import csv
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from urllib.parse import quote_plus
import pandas as pd

def driverinitialize():
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--incognito")
    driver=uc.Chrome(options=chrome_options)
    driver.set_page_load_timeout(100)
    return driver
def data_scraper():
    driver = driverinitialize()
    links=open("music_links.text","r").read().split("\n")

    # with open('music_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    #     fieldnames = ['Link', 'Biogharapy','Type', 'YEAR', 'TITLE', 'ARTIST(s)', 'Rating_value', 'Releases']
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    main_data = []
    url_desc_data = []
    

    for link in links:
        url = link
        driver.get(url)
        time.sleep(10)
        desc=""; type_=""; year=""; title=""; artist=""; rating=""; releases=""
        try:
            descs = driver.find_elements(By.XPATH, '//*[@id="content"]/div[4]/div/p')
            desc_parts = []
            for des in descs:
                dec_1 = des.get_attribute("innerText")
                try:
                    dec_2 = des.find_element(By.XPATH, './b').get_attribute("innerText")
                    dec_2 += ' ' + des.find_element(By.XPATH, './i').get_attribute("innerText")
                except:
                    dec_2 = ''
                if dec_1 or dec_2:
                    desc_parts.append(f'{dec_1} {dec_2}'.strip())
            desc = ' '.join(desc_parts).strip()
            print(desc)
            url_desc_data.append({
                'Link': url,
                'Biography': desc
            })
        except Exception as e:
            print(f"An error occurred while extracting description: {e}")
        try:
            tables = driver.find_elements(By.XPATH, '//table[@class="tbl release-group-list"]')
            for table in tables:
                h3_element = table.find_element(By.XPATH, './/preceding::h3[1]')
                type_ = h3_element.get_attribute("innerText")
                print(f"\nType: {type_}")
                rows = table.find_elements(By.XPATH, './/tbody/tr')
                for row in rows:
                    try:
                        year = row.find_element(By.XPATH, './td[1]').get_attribute("innerText")
                        print(f"\nYear: {year}")
                    except Exception as e:
                        print(f"An error occurred while extracting year: {e}")

                    try:
                        title = row.find_element(By.XPATH, './td[2]/a/bdi').get_attribute("innerText")
                        print(f"\nTitle: {title}")
                    except Exception as e:
                        print(f"An error occurred while extracting title: {e}")

                    try:
                        td_content = row.find_element(By.XPATH, './td[3]').text
                        bdi_elements = row.find_elements(By.XPATH, './td[3]//bdi')
                        artist_names = [bdi.get_attribute("innerText") for bdi in bdi_elements]
                        artist = ' '.join(artist_names)
                        artist_text = td_content.replace(artist, '').strip()  
                        artist = f"{artist_text}".strip() 
                        
                        if artist == '':
                            artist = row.find_element(By.XPATH, './td[3]/a/bdi').get_attribute("innerText")
                            print(f"\nArtist: {artist}")
                        else:
                            print(f"\nArtist: {artist}")
                    except:
                        pass
                        
                        
                    try:
                        rating = row.find_element(By.XPATH, './td[4]/span[@class="inline-rating"]/span').get_attribute("innerText")
                        print(f"\nRating: {rating}")
                    except Exception as e:
                        print(f"An error occurred while extracting rating: {e}")

                    try:
                        releases = row.find_element(By.XPATH, './td[5]').get_attribute("innerText")
                        print(f"\nReleases: {releases}")
                    except Exception as e:
                        print(f"An error occurred while extracting releases: {e}")
                    main_data.append({
                        'Link': url if url else '',
                        'TITLE': title if title else '',
                        # 'Biography': desc if desc else '',
                        'Type': type_ if type_ else '',
                        'YEAR': year if year else '',
                        'ARTIST(s)': artist if artist else '',
                        'Rating_value': rating if rating else '',
                        'Releases': releases if releases else '',
                    })
        except Exception as e:
            print(f"An error occurred while extracting tables and their data: {e}")
    driver.quit()
    df_main = pd.DataFrame(main_data)
    df_url_desc = pd.DataFrame(url_desc_data)
    with pd.ExcelWriter('music_data.xlsx', engine='openpyxl') as writer:
        df_main.to_excel(writer, sheet_name='Main Data', index=False)
        df_url_desc.to_excel(writer, sheet_name='URL and Description', index=False)
data_scraper()
