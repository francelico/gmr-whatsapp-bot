import tyro
import platform
from dataclasses import dataclass
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import time
import pywhatkit

@dataclass
class Args:
    whatsapp_group_id: str = None
    """The ID of the WhatsApp group to send messages to."""
    gmr_game_url: str = None
    """The URL of the GMR game to monitor (e.g. http://multiplayerrobot.com/Game#12345)."""
    remind_hours: int = 6
    """The number of hours left on a turn to start reminding the player."""

def make_driver():
    # different for ubuntu 22.04
    if platform.freedesktop_os_release().get("VERSION_CODENAME") == "jammy":
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        geckodriver_path = "/snap/bin/geckodriver"  # specify the path to your geckodriver
        driver_service = Service(executable_path=geckodriver_path)

        driver = webdriver.Firefox(options=options, service=driver_service)
    else:
        driver = webdriver.Firefox()
    return driver

def send_whatsapp_message(message, group_id):
    """Sends a WhatsApp message to the user."""

    pywhatkit.sendwhatmsg_to_group_instantly(group_id, message, wait_time=10, tab_close=True,
                                   close_time=2)


def get_current_player(driver):
    current_player_elem = driver.find_element(By.CLASS_NAME, "game-host")
    elementList = current_player_elem.find_elements(By.TAG_NAME, "img")

    current_player_steam_id = '!ERR'
    for element in elementList:
        if element.size['height'] in [STEAM_ICON_SIZE, STEAM_ICON_SIZE_HOST]:
            current_player_steam_id = element.accessible_name
            if element.size['height'] == STEAM_ICON_SIZE_HOST:
                current_player_steam_id = current_player_steam_id.split(" ")[0]
            break

    return current_player_steam_id


def get_time_left(driver):
    turn_timer_elem = driver.find_element(By.ID, "turn-timer-container")
    time_left_list = turn_timer_elem.find_elements(By.CLASS_NAME, "turn-timer-text")
    days_left = '!ERR'
    hours_left = '!ERR'
    for e in time_left_list:
        if "day" in e.text:
            days_left = int(e.text.split(" ")[0])
        elif "hour" in e.text:
            hours_left = int(e.text.split(" ")[0])
    return int(days_left), int(hours_left)

# Constants
STEAM_ICON_SIZE = 76.0
STEAM_ICON_SIZE_HOST = 80.0
SLEEP_TIME = 1800 #in seconds

if __name__ == "__main__":
    args = tyro.cli(Args)
    assert args.whatsapp_group_id is not None, "Please provide a WhatsApp group ID."
    assert args.gmr_game_url is not None, "Please provide a GMR game URL."

    driver = make_driver()
    driver.get(args.gmr_game_url)

    # Hello world
    msg = f"Hi! I'm your friendly neighborhood Civ turn reminder bot. I'll send a message when your turn starts, and then every hour once you have under {args.remind_hours} hours left on your turn. If you ignore me I'll make sure Gandhi nukes you first. Have fun!"
    send_whatsapp_message(msg, args.whatsapp_group_id)
    last_player = None

    hours_left_last_message = math.inf
    while True:
        driver.refresh()
        time.sleep(1)
        current_player = get_current_player(driver)
        days_left, hours_left = get_time_left(driver)
        if current_player != last_player:
            msg = f"It's {current_player}'s turn to play! You have {days_left} days and {hours_left} hours left."
            send_whatsapp_message(msg, args.whatsapp_group_id)
            last_player = current_player
            hours_left_last_message = math.inf
        if days_left < 1 and hours_left < args.remind_hours and hours_left < hours_left_last_message:
            msg = f"Time's running out for {current_player}! You have {hours_left} hours left."
            send_whatsapp_message(msg, args.whatsapp_group_id)
            hours_left_last_message = hours_left
        time.sleep(SLEEP_TIME)
