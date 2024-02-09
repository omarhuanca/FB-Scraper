import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from selenium.webdriver.common.by import By
from datetime import datetime

import sys, re, csv
from random import randint

FB_URL = "https://www.facebook.com/login/device-based/regular/login/"
FB_USER = "ohuanca@t2company.com.uy"
FB_PASS = "Internetes3!"
FB_FRIENDS_URL = "https://www.facebook.com/profile.php?id=61556176318834&sk=friends"  # << < This is sample link

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77"
                  " Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

# Chrome Driver Options
options = Options()
options.add_argument("disable-notifications")
options.add_argument("disable-popup")
# options.add_argument('headless')  # Will not show browser window

# Setting up Chrome Driver and bs4
chrome_driver_path = "/usr/bin/chromedriver"
driver = webdriver.Chrome(options=options)
response = requests.get(url=FB_URL, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')


# Animation function
def animated_loading(name):
    chars = "/—\|"
    for char in chars:
        sys.stdout.write('\r' + name + char)
        sleep(.1)
        sys.stdout.flush()


# Logging to FB Account
def fb_login():
    try:
        animated_loading("[+] logging to FB account...")
        driver.get(FB_URL)
        # sleep(randint(5, 8))
        driver.find_element(By.ID, "email").send_keys(FB_USER)
        driver.find_element(By.ID, "pass").send_keys(FB_PASS)
        driver.find_element(By.NAME, "login").click()
        # sleep(randint(5, 8))
    except NoSuchElementException:
        block_text = driver.find_element(By.XPATH, '//*[@id="error_box"]/div[1]').text
        if "You can't use this feature at the moment" == block_text:
            # animated_loading("[*] Account is Blocked!!")
            driver.quit()
        animated_loading("[+] re-logging to FB account...")
        # sleep(randint(5, 8))
        fb_login()


# Re_direction to FB friend page
def load_fb_friend_page():
    try:
        animated_loading("[+] loading friend url & setting up...")
        sleep(randint(5, 8))
        driver.get(url=FB_FRIENDS_URL)
        sleep(randint(5, 8))
        for _ in range(4):  # <<< Make sure set the range, it depend on your friend list amount, and it will scroll
            # page to get load all names >>>
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            sleep(randint(5, 8))
    except NoSuchElementException:
        animated_loading("[+] re_loading friend url...")
        sleep(randint(5, 8))
        load_fb_friend_page()


# Collect all FB friends names
def get_friend_names():
    try:
        animated_loading("[+] collecting friends names...")
        # sleep(randint(5, 8))
        list_item = driver.find_elements(By.XPATH,
                                         "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div/div/div/div/div/div[3]/div/div[2]/div[1]/a")
        # sleep(randint(4, 8))
        all_names = []

        for item in list_item:
            nam = item.find_element(By.CSS_SELECTOR, "span")
            if "mutual friend" in nam.text:
                pass
            else:
                all_names.append(nam.text)
            print(nam.text)
        cleaned_all_names = list(filter(None, all_names))
        return cleaned_all_names
    except NoSuchElementException:
        animated_loading("[+] re-collecting friends names...")
        # sleep(randint(5, 8))
        get_friend_names()


# Collect and set all FB profile links form that FB names
def get_profile_link():
    try:
        animated_loading("[+] collecting profile links...")
        # sleep(randint(4, 8))
        link_item = driver.find_elements(By.XPATH,
                                         "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div/div/div/div/div/div[3]/div/div[2]/div[1]/a")
        # sleep(randint(4, 8))
        all_links = []
        for link in link_item:
            href = link.get_attribute("href")
            if "friends_mutual" in href:
                pass
            else:
                all_links.append(href)

        cleaned_all_links = list(dict.fromkeys(all_links))
        return cleaned_all_links

    except NoSuchElementException:
        animated_loading("[+] re-collecting profile links...")
        # sleep(randint(4, 8))
        get_profile_link()


# Collecting FB data: [ Names, FB Profile Links, Phone Number, Gender, Birth Day ]
def get_data_info():
    all_friends_phone_number = []
    all_friends_email = []
    all_friends_gender = []
    all_friends_date = []
    all_friends_year = []
    all_friends_language = []
    # Have to separate each link, because some of profile links have username, and others just default fb numbers

    for each_link in get_profile_link():
        animated_loading("[+] gathering data...")
        print("\n")
        print(f"[+] Current Link: {each_link} <<<")
        try:
            if "profile.php" in each_link:
                driver.get(url=f"{each_link}&sk=about_contact_and_basic_info")
            else:
                driver.get(url=f"{each_link}/about_contact_and_basic_info")

            sleep(randint(1, 3))
            phones = driver.find_elements(By.XPATH, "//div[@class='x78zum5 xdt5ytf xz62fqu x16ldp7u']/div[1]/span")
            ph_list = []
            url_value = get_profile_from_url(each_link)
            for pn_item in phones:
                if len(pn_item.text) > 0:
                    ph_list.append(pn_item.text)
            for pn_item in ph_list:
                if pn_item == "Mobile":
                    item_id = ph_list.index(pn_item) - 1
                    all_friends_phone_number.append({url_value: ph_list[item_id]})
                if pn_item == "Email":
                    item_id = ph_list.index(pn_item) - 1
                    all_friends_email.append({url_value: ph_list[item_id]})
                if pn_item == "Gender":
                    item_info = ph_list.index(pn_item) - 1
                    all_friends_gender.append({url_value: ph_list[item_info]})
                if pn_item == "Birth date":
                    item_date = ph_list.index(pn_item) - 1
                    all_friends_date.append({url_value: ph_list[item_date]})
                if pn_item == "Birth year":
                    item_year = ph_list.index(pn_item) - 1
                    all_friends_year.append({url_value: ph_list[item_year]})
                if pn_item == "Languages":
                    item_year = ph_list.index(pn_item) - 1
                    all_friends_language.append({url_value: ph_list[item_year]})
            sleep(2)
        except NoSuchElementException:
            print("No Details")
            continue
    return all_friends_phone_number, all_friends_email, all_friends_gender, all_friends_date, all_friends_year, all_friends_language


def get_profile_from_url(url_value):
    unique_myid = ''
    profile = filter_string(r"com{1}", url_value)
    if "=" in profile:
        username_value = filter_string(r"[?]", profile)
    else:
        username_value = profile

    string_dot = filter_string(r"[0-9]+", username_value)
    number = filter_string(r"[a-z\\.]+", username_value)

    username_value = change_value_string(username_value)
    string_dot = change_value_string(string_dot)

    if len(username_value) > len(string_dot):
        if len(username_value) > len(number):
            unique_myid = username_value
    elif len(string_dot) > len(number):
        unique_myid = string_dot
    elif len(number) > len(username_value):
        unique_myid = number

    return unique_myid


def change_value_string(potential_string):
    if "=" in potential_string:
        potential_string = ''
    return potential_string


def filter_string(regex, potential_string):
    split_response = ''
    if len(potential_string) > 0 and len(regex) > 0:
        regex_string = re.search(regex, potential_string)
        if regex_string is not None:
            split_string = potential_string[:regex_string.start()] + potential_string[regex_string.end():]
            split_response = split_string[regex_string.end() + 1 - (regex_string.end() - regex_string.start()):]

    return split_response


def containkeyInDictionary(key, dictionary_array):
    flag = False
    for item in dictionary_array:
        if key in item:
            flag = True

    return flag


def getValueDictionary(key, dictionary_array):
    response = ""
    for item in dictionary_array:
        if key in item:
            response = item[key]

    return response


def print_row(data_array):
    csvOut = '%s.csv' % datetime.now().strftime("%Y_%m_%d_%H%M")
    # sleep(3)
    writer = csv.writer(open(csvOut, 'w', encoding="utf-8"))
    for item in data_array:
        print("print_item")
        print(item)
        writer.writerow(item)




# Loading logo
art = '''
  _____  ____         ____    ____  ____      _     ____   _____  ____  
 |  ___|| __ )       / ___|  / ___||  _ \    / \   |  _ \ | ____||  _ \ 
 | |_   |  _ \  _____\___ \ | |    | |_) |  / _ \  | |_) ||  _|  | |_) |
 |  _|  | |_) ||_____|___) || |___ |  _ <  / ___ \ |  __/ | |___ |  _ < 
 |_|    |____/       |____/  \____||_| \_\/_/   \_\|_|    |_____||_| \_\


'''

print(art)
# sleep(2)

# Calling all the functions
fb_login()
load_fb_friend_page()
fb_names = get_friend_names()
fb_links = get_profile_link()
fb_numbers, fb_emails, fb_genders, fb_birth_dates, fb_birth_years, fb_languages = get_data_info()
sleep(randint(4, 8))
item_array = []

# Print final result in to console, also save in text file current directory
i = 0
for fb_link in fb_links:

    username = get_profile_from_url(fb_link)
    fb_name_i = ""
    fb_link_i = ""
    fb_number_i = ""
    fb_email_i = ""
    fb_gender_i = ""
    fb_birth_date_i = ""
    fb_birth_year_i = ""
    fb_language_i = ""

    if len(fb_names) > i:
        fb_name_i = fb_names[i]
    if len(fb_links) > i:
        fb_link_i = fb_links[i]
    if containkeyInDictionary(username, fb_numbers):
        fb_number_i = getValueDictionary(username, fb_numbers)
    if containkeyInDictionary(username, fb_emails):
        fb_email_i = getValueDictionary(username, fb_emails)
    if containkeyInDictionary(username, fb_genders):
        fb_gender_i = getValueDictionary(username, fb_genders)
    if containkeyInDictionary(username, fb_birth_dates):
        fb_birth_date_i = getValueDictionary(username, fb_birth_dates)
    if containkeyInDictionary(username, fb_birth_years):
        fb_birth_year_i = getValueDictionary(username, fb_birth_years)
    if containkeyInDictionary(username, fb_languages):
        fb_language_i = getValueDictionary(username, fb_languages)

    #data = f"{fb_name_i} | {fb_link_i} | {fb_number_i} | {fb_email_i} | {fb_gender_i} | " \
    #       f"{fb_birth_date_i}-{fb_birth_year_i} | {fb_language_i}"


    item_array.append([fb_name_i, fb_link_i, fb_number_i, fb_email_i, fb_gender_i, fb_birth_date_i, fb_birth_year_i,
              fb_language_i])

    #print(item_array)
    i = i + 1

print_row(item_array)

# Closing the selenium driver
driver.quit()
