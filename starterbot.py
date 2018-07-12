# -*- coding: utf-8 -*-
import os
import time
import re
import urllib.request
import thetoken
import http.client
import urllib, uuid, json
from random import randint
#import imp.reload
#import sys
#sys.setdefaultencoding('utf8')
from slackclient import SlackClient
import giphy_client
from giphy_client.rest import ApiException
import keys

# instantiate Slack client
slack_client = SlackClient(thetoken.TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM

# ms translate
#subscriptionKey = '0883489a3ca34d30bafd7913e2657fb4'

host = 'api.cognitive.microsofttranslator.com'
path = '/translate?api-version=3.0'

# Translate to German and Italian.
params = "&to=en";

def translate (content):
    subscriptionKey = keys.subKey
    headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    conn = http.client.HTTPSConnection(host)
    conn.request ("POST", path + params, content.encode('utf-8'), headers)
    response = conn.getresponse ()
    response = response.read ()
    translated = json.loads(response.decode('utf-8'))
    return translated[0]["translations"][0]["text"]

#bot starts here


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            return event["text"],event["channel"]
    return None, None
def handle_command(command, channel):
    api_key = keys.api_key
    # create an instance of the API class
    api_instance = giphy_client.DefaultApi()
    try:
       # Search Endpoint
       requestBody = [{
             'Text' : command,
       }]
       content = json.dumps(requestBody, ensure_ascii=False).encode('utf-8')
       result = translate (content.decode('utf-8'))
       api_response = api_instance.gifs_search_get(api_key, urllib.parse.quote_plus(result), limit=20)
       print (urllib.parse.quote_plus(result))
       print (result)
       if api_response and len(api_response.data) > 0:             
             rand = randint(0,len(api_response.data)-1)
             slack_client.api_call("chat.postMessage", channel=channel, text=api_response.data[rand].url)
    except ApiException as e:
    
        print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)    
    
if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            try:
                command, channel = parse_bot_commands(slack_client.rtm_read())
            except Exception as e:
                print(e)
                if slack_client.rtm_connect(with_team_state=False):
                    starterbot_id = slack_client.api_call("auth.test")["user_id"]
                    command, channel = parse_bot_commands(slack_client.rtm_read())            
            if command:
                if command[:10] == ".translate":
                   slack_client.api_call("chat.postMessage", channel=channel, text=translate(json.dumps([{'Text' : command[10:], }])))
                if command[:7] == ".mustaa":
                    html_content = urllib.request.urlopen('http://www.caverna.fi/lounas/').read()
                    matches = re.findall('Mustaa makkaraa', html_content.decode('latin-1'))
                    if len(matches) == 0: 
                        slack_client.api_call("chat.postMessage", channel=channel, text="https://media.giphy.com/media/3o7btT1T9qpQZWhNlK/giphy.gif")
                    else:
                        slack_client.api_call("chat.postMessage", channel=channel, text="https://media.giphy.com/media/1zSiX3p2XEZpe/giphy.gif")
                handle_command(command, channel)
                time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
