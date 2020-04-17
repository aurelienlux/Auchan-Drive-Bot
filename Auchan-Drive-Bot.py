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
        # get infos-retrait div
        info = parsed.find("div", {"class": ["infos-retrait"]})
        # get details paragraph
        slotInfo = info.find("p", {"class": ["details"]})
        # get innertext of paragraph as string
        status = str(slotInfo.text)
        
        status = "des samedi bla bla bla"
        # check for noSlotKeyword in status
        if noSlotKeyword in status:
            available = False
        else:
            available = status[4:]
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
        return "Slot available in {0} at '{1}'".format(location, available)

# ADD NEW LOCATIONS HERE
location2Url = {
    "Munsbach": "Munsbach-102",
    "Cloche D'Or": "magasin",
}

# settign to None so that it will definitely send messages on start-up
storedState = {loc: None for loc in location2Url.keys()}

storedState["Munsbach"] = False

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
            telegram_send.send(messages=[message])

    storedState = currentState
    iteration += 1
    
    time.sleep(120)