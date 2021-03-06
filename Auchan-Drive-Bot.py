# Import required libraries
from bs4 import BeautifulSoup
import requests
import telegram_send
import time

noSlotKeyword = "Aucun"

# function that returns the availability of a valid auchan location
def getAvailability(location):
    try:
        # interpolate location with base url
        url = "https://www.auchandrive.lu/drive/{0}/".format(location2Url[location])
        print("url of {0}:".format(location), url)
        # get page using request
        page = requests.get(url, verify=False)
        # get parsed content
        parsed = BeautifulSoup(page.text, "html.parser")
        # get next slot
        slotInfo = parsed.find("div", {"class": ["info-drive_next-slot"]})
        # get innertext of paragraph as string
        fullStatus = str(slotInfo.text)
        # process innertext
        status = fullStatus[28:]
        
        # check for noSlotKeyword in status
        if noSlotKeyword in status:
            available = False
        else:
            available = status
    except:
        available = None
        telegram_send.send(messages=["An error has occurred getting the availability of {0}".format(location)])
        print("\n")

    return available

def getMessageContent(location, available):
    if available == False:
        return "Slots no longer available in {0}".format(location)
    elif available == None:
        return None
    elif isinstance(available, str):
        translate = [dateTranslate[word] if word in dateTranslate.keys() else word for word in available.split(" ")]
        translate[0] += ","
        return "*Slots available in {0}*\n\nNext slot: {1}".format(location, " ".join(translate))

dateTranslate = {
    "lundi": "Monday",
    "mardi": "Tuesday",
    "mercredi": "Wednesday",
    "jeudi": "Thursday",
    "vendredi": "Friday",
    "samedi": "Saturday",
    "dimanche": "Sunday",
    "janvier": "January",
    "février": "February",
    "mars": "March",
    "avril": "April",
    "mai": "May",
    "juin": "June",
    "juillet": "July",
    "août": "August",
    "septembre": "September",
    "octobre": "October",
    "novembre": "November",
    "décembre": "December",
    "à": "at"
}

# ADD NEW LOCATIONS HERE
location2Url = {
    "Munsbach": "Munsbach-102",
    "Cloche D'Or": "magasin",
}

# settign to None so that it will definitely send messages on start-up
storedState = {loc: None for loc in location2Url.keys()}

print("initial state:", storedState)

iteration = 0

while True:
    print('\n\n#####################################')
    print('Iteration {0}'.format(iteration))
    print('#####################################\n')
    
    # for each key (location), get its availability
    currentState = { loc: getAvailability(loc) for loc in location2Url.keys() }
    
    print("current state:", currentState)

    # for each key (location),check if current state is different to old state
    diff = { loc: True if currentState[loc] != storedState[loc] else False for loc in location2Url.keys() }
    
    print("difference:", diff)

    messages = { loc: getMessageContent(loc, currentState[loc]) if diff[loc] else None for loc in location2Url.keys() }
    print("messages", messages)

    for loc in location2Url.keys():
        message = messages[loc]
        if messages[loc] is not None:
            telegram_send.send(messages=[message], parse_mode="markdown")

    storedState = currentState
    iteration += 1
    
    time.sleep(120)
