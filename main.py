import tyro
from dataclasses import dataclass
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pywhatkit

# pywhatkit.sendwhatmsg('+41793305447', 'Auto message test', 11, 43, wait_time=30, tab_close=True, close_time=2)

@dataclass
class Args:
    whatsapp_group_id: str = None
    """The ID of the WhatsApp group to send messages to."""
    remind_hours: int = 6
    """The number of hours left on a turn to start reminding the player."""
    gmr_game_url: str = "http://multiplayerrobot.com/Game#12345"

def send_whatsapp_message(message, group_id):
    """Sends a WhatsApp message to the user."""

    pywhatkit.sendwhatmsg_to_group_instantly(group_id, message, wait_time=10, tab_close=True,
                                   close_time=2)


def get_current_player(browser):
    current_player_elem = browser.find_element(By.CLASS_NAME, "game-host")
    elementList = current_player_elem.find_elements(By.TAG_NAME, "img")

    current_player_steam_id = '!ERR'
    for element in elementList:
        if element.size['height'] == STEAM_ICON_SIZE:
            current_player_steam_id = element.accessible_name
            break

    return current_player_steam_id


def get_time_left(browser):
    turn_timer_elem = browser.find_element(By.ID, "turn-timer-container")
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
SLEEP_TIME = 1800 #in seconds

# Main logic

if __name__ == "__main__":
    args = tyro.cli(Args)

    browser = webdriver.Firefox()
    browser.get(args.gmr_game_url)

    # Hello world
    send_whatsapp_message(f"Hi! I'm your friendly neighborhood Civ turn reminder bot. I'll send a message when your turn starts, and then every hour once you have under {args.remind_hours} hours left on your turn. If you ignore me I'll make sure Gandhi nukes you first. Have fun!")
    last_player = None

    hours_left_last_message = math.inf
    while True:
        browser.refresh()
        time.sleep(1)
        current_player = get_current_player(browser)
        days_left, hours_left = get_time_left(browser)
        if current_player != last_player:
            msg = f"It's {current_player}'s turn to play! You have {days_left} days and {hours_left} hours left."
            send_whatsapp_message(msg)
            last_player = current_player
            hours_left_last_message = math.inf
        if days_left < 1 and hours_left < args.remind_hours and hours_left < hours_left_last_message:
            msg = f"Time's running out for {current_player}! You have {hours_left} hours left."
            send_whatsapp_message(msg, args.whatsapp_group_id)
            hours_left_last_message = hours_left
        time.sleep(SLEEP_TIME)
