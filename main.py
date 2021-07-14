from io import BytesIO
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
from pathlib import Path
import requests
from zipfile import ZipFile
import subprocess
import sys
from getpass import getuser

tabs_title_and_handle = []
videos_list = []
file_dir = "\\".join(__file__.split("\\")[:-1]) + "\\"
# file_dir = "\\".join(sys.executable.split("\\")[:-1]) + "\\"
# print(f"\nRunning file: {sys.executable}\n")
print("Running Script...")

def add_to_startup(file_path=""):
    if file_path == "":
        file_path = sys.executable
    username = getuser()
    bat_path = f'C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    with open(bat_path + '\\' + "youtube_view_adder.bat", "w+") as bat_file:
        bat_file.write(r'start "" %s' % file_path)

def grep_video_link_from_playlist(playlist_url):
    driver.get(playlist_url)
    playlist_video = driver.find_elements_by_id("video-title")
    for element in playlist_video:
        videos_list.append(element.get_attribute("href"))



## If got error download chromedriver.exe of supported version for your operating system in same folder as this program
playlist_url = sys.argv[1].split(",") if len(sys.argv) > 1 else None

if Path(file_dir + "chromedriver.exe").exists():
    add_to_startup()
else:
    add_to_startup()
    version = subprocess.check_output('wmic datafile where name="C:\\\\Program Files (x86)\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe" get Version /value', shell=False)
    version = version.decode("utf-8").strip()
    version_number = version.split("=")[1].split(".")[0]
    response = requests.get("https://chromedriver.storage.googleapis.com/?delimiter=/&prefix=" + version_number)
    soup = BeautifulSoup(response.content, "html.parser")
    version = soup.find("commonprefixes").find("prefix").text
    chrome_link = f"https://chromedriver.storage.googleapis.com/{version}chromedriver_win32.zip"
    print("downloading chromedriver")
    response = requests.get(chrome_link).content
    zipfile = ZipFile(BytesIO(response))
    f = open(file_dir + "chromedriver.exe", "wb")
    for line in zipfile.open("chromedriver.exe").readlines():
        f.write(line)
    f.close()


options = Options()
options.headless = True
options.add_argument('--disable-gpu')
options.add_argument("--log-level=3")
try:
    driver = webdriver.Chrome(executable_path=file_dir + "chromedriver.exe", options=options)
except WebDriverException:
    print("exiting")
    sys.exit()

if playlist_url == None:
    playlist_url = ["https://www.youtube.com/playlist?list=PL8lbiX1cYmrY4EHDjhAErt85bxWb_mf9w"]

for _ in playlist_url:
    grep_video_link_from_playlist(_)

tabs_title_and_handle.append({"title": driver.title, "handle": driver.current_window_handle})
for index, video in enumerate(videos_list):
    driver.execute_script(f"window.open('{video}')")
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(index+2))
    windows = driver.window_handles
    tab = [x for x in windows if x not in [i["handle"] for i in tabs_title_and_handle]][0]
    driver.switch_to.window(tab)
    tabs_title_and_handle.append({"title": driver.title, "handle": driver.current_window_handle})
    sleep(1)
    try:
        WebDriverWait(driver, 10).until(lambda x: x.find_element_by_id("ytp-caption-window-container"))
    except TimeoutException:
        pass
    play_button = driver.find_element_by_class_name("ytp-play-button.ytp-button.ytp-play-button-playlist")
    soup = BeautifulSoup(play_button.get_attribute('outerHTML'), "html.parser")
    soup = soup.find_all("button")[0]
    state = soup["aria-label"]
    if state == "Play (k)":
        play_button.click()
    
    mute_button = driver.find_element_by_class_name("ytp-mute-button.ytp-button")
    soup = BeautifulSoup(mute_button.get_attribute('outerHTML'), "html.parser")
    soup = soup.find_all("button")[0]
    state = soup["aria-label"]
    if state == "Mute (m)":
        mute_button.click()
    
    driver.execute_script("document.querySelector('video').loop = true;")
    sleep(0.5)

print(tabs_title_and_handle)
