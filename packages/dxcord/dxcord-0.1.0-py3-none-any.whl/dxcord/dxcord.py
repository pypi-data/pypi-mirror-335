## CREDIT:  
##      Created by: s0rdeal
##      
##      https://github.com/greg6775/Discord-Api-Endpoints/blob/master/Endpoints.md | Really good documentation for discord api endpoints

## CONTACT:
##      Discord: qdbv / s0rdeal
##      Twitter: s0rdeal
##      GitHub: s0rdeal
##      Telegram : @s0rdeal

## DISCLAIMER:
##      Some features can rate limit your account, use this at your own risk.



import requests as req
import colorama
from colorama import Fore
import time

r = Fore.RED
g = Fore.GREEN
re = Fore.RESET
b = Fore.BLUE
c = Fore.CYAN
y = Fore.YELLOW
m = Fore.MAGENTA
lm = Fore.LIGHTMAGENTA_EX
lr = Fore.LIGHTRED_EX
ly = Fore.LIGHTYELLOW_EX
lg = Fore.LIGHTGREEN_EX

uri = 'https://canary.discord.com/api/v10' # If some features are not working use this url instead : https://discord.com/api/v9

class Client():
    def __init__(self, token=""):
        self.token = token


    def GetDms(self):
        headers = {'Authorization':self.token}
        url = f'{uri}/users/@me/channels'
        res = req.get(url=url,headers=headers)

        if res.status_code == 200:
            channels = res.json()  
            for channel in channels:
                for recipient in channel.get('recipients', []):
                    print(f"{b}User ID: {c}{recipient['id']} {re}| {b}Username: {c}{recipient['username']}{re}")
        else:
            print(f"{r}Error: {res.status_code} - {res.text}")

    def GetCountry(self):
        headers = {'Authorization':self.token}
        url = f'{uri}/users/@me/billing/country-code'
        res = req.get(url=url,headers=headers)

        if res.status_code == 200:
            ct = res.json()
            print(f"{m}Country {re}| {lm}{ct['country_code']}{re}")
        else:
            print(f"{r}Error : {res.status_code} - {res.text}")

    
    def GetGuilds(self):
        headers = {'Authorization':self.token}
        url = f'{uri}/users/@me/guilds'
        res = req.get(url=url,headers=headers)

        if res.status_code == 200:
            guilds = res.json()
            for guild in guilds:
                print(f"{lg}Guild ID: {y}{guild['id']} {re}| {lg}Guild Name: {y}{guild['name']}{re}")
        else:
            print(f"{r}Error: {res.status_code} - {res.text}")

    
    def GetFriends(self):
        headers = {'Authorization':self.token}
        url = f'{uri}/users/@me/relationships'
        res = req.get(url=url,headers=headers)

        friends = res.json()

        if res.status_code == 200:
            for friend in friends:
                print(f"{r}User ID: {lr}{friend['id']} {re}| {r}Username: {lr}{friend['user']['username']}{re}")

        else:
            print(f"{r}Error: {res.status_code} - {res.text}")


    def TokenLookup(self):
        headers = {'Authorization': self.token}
        uri = "https://discordapp.com/api/v6"  # Assurez-vous que `uri` est défini
        url = f'{uri}/users/@me'
        purl = f'{uri}/users/@me/billing/payment-sources'

        res = req.get(url=url, headers=headers)

        if res.status_code == 200:
            profile = res.json()
            print(f"{g}Username: {lg}{profile['username']} {re}| {r}User ID: {lr}{profile['id']} {re}| {b}Email: {c}{profile['email']}{re}\n"
                f"{lg}Phone: {g}{profile['phone']} {re}| {r}Flags: {lr}{profile['flags']} {re}| {m}Locale: {lm}{profile['locale']} {re}| "
                f"{b}MFA: {c}{profile['mfa_enabled']} {re}| {y}NITRO : {y}{profile['premium_type']}{re}")

            payment_methods = 0
            payment_type = ""
            valid = 0

            try:
                response = req.get(purl, headers=headers)
                response.raise_for_status()
                data = response.json()

                for x in data:
                    if 'type' in x and 'invalid' in x:
                        if x['type'] == 1:
                            payment_type += "CreditCard "
                        elif x['type'] == 2:
                            payment_type += "PayPal "

                        if not x['invalid']:
                            valid += 1
                            payment_methods += 1

            except req.exceptions.RequestException as e:
                print(f"Error fetching payment methods: {e}")

            print(f"Valid Payment Methods: {valid}")
            print(f"Payment Types: {payment_type}")

        else:
            print(f"{r}Error: {res.status_code} - {res.text}")


    
    def SendMessage(self,ChannelId,Message):
        headers = {'Authorization':self.token}
        url = f'{uri}/channels/{ChannelId}/messages'
        data ={
            'content':f'{Message}',
            'flags':0,
            'mobile_network_type':'unknown',
            'tts': False
        }
        res = req.post(url=url,headers=headers,json=data)

        if res.status_code == 200:
            print(f"{g}Message sent successfully : {y}{Message}{re}")
        else:
            print(f"{r}Error: {res.status_code} - {res.text}")

    def RemoveFriend(self,UserId):
        headers = {'Authorization':self.token}
        url = f'{uri}/users/@me/relationships/{UserId}'
        res = req.delete(url=url,headers=headers)
        if res.status_code == 204:
            print(f"{g}Friend removed successfully{re}")
        else:
            print(f"{r}Error: {res.status_code} - {res.text}")

    def SetLanguage(self,CountryCode):
        AllCountryCodes = ['da','de','en-GB','en-US','es-ES','fr','hr','it','lt','hu','nl','no','pl','pt-BR','ro','fi','sv-SE','vi','tr','cs','el','bg','ru','uk','th','zh-CN','ja','ko']
        headers = {'Authorization':self.token}
        url = f'{uri}/users/@me/settings'
        data = {
            'locale':f'{CountryCode}'
        }
        res = req.patch(url=url,headers=headers,json=data)

        if CountryCode not in AllCountryCodes:
            print(f"{r}Error: Invalid Country Code{re}")

        else:
            if res.status_code == 200:
                print(f"{g}Language set to {CountryCode}{re}")  
            else:
                print(f"{r}Error: {res.status_code} - {res.text}")



    def SetHypesquad(self, house):
        headers = {'Authorization':self.token}
        url = f'{uri}/hypesquad/online'
        data = {'house_id': house}
    
        res = req.post(url=url,headers=headers,json=data)
        if res.status_code == 204:
            print(f"{g}Hypesquad set to {house}{re}")
        else:
            print(f"{r}Error: {res.status_code} - {res.text}")

    def BlockUser(self,UserId):
        headers = {'Authorization':self.token}
        url = f'{uri}/users/@me/relationships/{UserId}'
        data = {'type':2}

        res = req.put(url=url,headers=headers,json=data)
        if res.status_code == 204:
            print(f"{g}User blocked successfully{re}")
        else:
            print(f"{r}Error: {res.status_code} - {res.text}")

    def UnblockUser(self,UserId):
        headers = {'Authorization':self.token}
        url = f'{uri}/users/@me/relationships/{UserId}'
        data = {'type':0}

        res = req.delete(url=url,headers=headers,json=data)
        if res.status_code == 204:
            print(f"{g}User unblocked successfully{re}")
        else:
            print(f"{r}Error: {res.status_code} - {res.text}")

    def GetMessage(self, ChannelId):
        headers = {'Authorization': self.token}
        url = f'{uri}/channels/{ChannelId}/messages'

        res = req.get(url=url, headers=headers)
        if res.status_code == 200:
            messages = res.json()
            for message in messages:
                print(f"{g}Message ID: {y}{message['id']} {re}| {m}Username: {lm}{message['author']['username']} | {g}Message: {y}{message['content']}{re}")
                if 'attachments' in message:
                    for attachment in message['attachments']:
                        print(f"{c}Attachment URL: {b}{attachment['url']}{re}")
                if 'embeds' in message:
                    for embed in message['embeds']:
                        if 'url' in embed:
                            print(f"{c}Embed URL: {b}{embed['url']}{re}")
                        if 'image' in embed and 'url' in embed['image']:
                            print(f"{c}Image URL: {b}{embed['image']['url']}{re}")
        else:
            print(f"{r}Error: {res.status_code} - {res.text}")


        




## CREDIT:  
##      Created by: s0rdeal
##      
##      https://github.com/greg6775/Discord-Api-Endpoints/blob/master/Endpoints.md | Really good documentation for discord api endpoints

## CONTACT:
##      Discord: qdbv / s0rdeal
##      Twitter: s0rdeal
##      GitHub: s0rdeal
##      Telegram : @s0rdeal

## DISCLAIMER:
##      Some features can rate limit your account, use this at your own risk.

