import re, shutil, tempfile, signal
from bs4 import BeautifulSoup
import sys
import ssl
import os
import requests
import urllib3

urllib3.disable_warnings(category = urllib3.exceptions.InsecureRequestWarning)

from time import sleep

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if len(sys.argv) != 4:
	print("\n" + bcolors.OKGREEN + "[" + bcolors.ENDC + bcolors.OKBLUE + "*" + bcolors.OKGREEN + "] Usage: python " + sys.argv[0] + " <country-code> <phone-number> <login-pin>\n" + bcolors.ENDC)
	print(bcolors.BOLD + "Example: python " + sys.argv[0] + " 1 XXXXXXXXX 1234\n" + bcolors.ENDC)
	sys.exit(0)

def signal_handler(key, frame):
	print("\n\n[*] Exiting...\n")
	sys.exit(1)

signal = signal.signal(signal.SIGINT, signal_handler)
area_code = sys.argv[1].replace("+", "")
phone_number = sys.argv[2]
login_pin = sys.argv[3]

# URL of the login page
url = 'https://web.spoofcard.com/login'
url_account = 'https://web.spoofcard.com/account'
url_settings = 'https://web.spoofcard.com/account/settings'
url_call_spoof = 'https://web.spoofcard.com/account/calls/create'
url_sms_spoof = 'https://web.spoofcard.com/account/two-way-sms/create'

def sed_inplace(filename, pattern, repl):

    pattern_compiled = re.compile(pattern)

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        with open(filename) as src_file:
            for line in src_file:
                tmp_file.write(pattern_compiled.sub(repl, line))

    shutil.copystat(filename, tmp_file.name)
    shutil.move(tmp_file.name, filename)

def sms_spoofing():
	destination_number = input('\nDestination Number [+1XXXXXXXXX]: ')
	display_number = input('\nDisplay Number [+1XXXXXXXXX]: ')
	message = input('\nEnter message to display: ')

	sms_spoofing_data = {'body': message, 'destination_address': destination_number, 'source_address': display_number, 'tos_accepted': 'true', 'oneWay': 'true'}
	sms_spoofing_headers = {'accept-encoding': 'gzip, deflate, br', 'accept-language': 'es-ES,es;q=0.9,en;q=0.8', 'content-type': 'application/x-www-form-urlencoded', 'accept': 'application/json, text/plain, */*', 'x-requested-with': 'XMLHttpRequest'}

	r = session.post(url_sms_spoof, data=sms_spoofing_data, headers=sms_spoofing_headers, verify=False)
	
	content_file = open("./response/sms_response.txt", "w")
	content_file.write(r.content.decode())
	content_file.close()
	
	with open('./response/sms_response.txt') as f:
			for lines in f:
				if (re.search("Unexpected", lines)):
					print("\n" + bcolors.FAIL + "[" + bcolors.ENDC + bcolors.FAIL + "*" + bcolors.ENDC + bcolors.FAIL + "] Message has failed to send\n" + bcolors.ENDC)
				else:
					print("\n" + bcolors.OKGREEN + "[" + bcolors.ENDC + bcolors.OKBLUE + "*" + bcolors.ENDC + bcolors.OKGREEN + "] Message has been sent\n" + bcolors.ENDC)

def call_spoofing():
	destination_number = input('\nDestination Number [+1XXXXXXXXX]: ')
	display_number = input('\nDisplay Number [+1XXXXXXXXX]: ')

	call_spoofing_data = {'destination_address': destination_number, 'display_address': display_number, 'event_type': 'outbound-call', 'plugins[background_noise][choice_index]': '8'}
	call_spoofing_headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'accept': 'application/json, text/javascript, */*; q=0.01', 'x-requested-with': 'XMLHttpRequest'}

	r = session.post(url_call_spoof, data=call_spoofing_data, headers=call_spoofing_headers, verify=False)

	content_file = open("./response/dial_response.txt", "w")
	content_file.write(r.content.decode())
	content_file.close()
    
	sed_inplace('./response/dial_response.txt', r'\,', '\n')

	dial_access_code = []

	with open('./response/dial_response.txt') as f:
			for lines in f:
				if re.search("access_code", lines):
					dial_access_code.append(lines.split(':')[1].split('"')[1])

	dial_access_number = []

	with open('./response/dial_response.txt') as f:
			for lines in f:
				if re.search("last_used_access_number", lines):
					dial_access_number.append(lines.split(':')[1].split('"')[1])

	print('\n--------------------------------------------')

	# for numbers in dial_numbers:
	# print(numbers)

	print("\n------------------")
	print("Access-Number: %s |" % dial_access_number[0])
	print("Access-Code: %s |" % dial_access_code[0])
	print('--------------------------------------------\n')

	print("[*] Now call the number listed above.")
	print("[*] Once done, you will need to enter the Access-Code provided above")
	print("[*] When finished, press <Enter> key to finish the program\n")

	input("Press <Enter> to continue...")

	os.remove("dial_response.txt")
	session.close()
      





banner = "\n╱╱╱╱╱╱╱╱╱╱╱╱╱╭━┳━╮╭━╮\n"
banner += "╱╱╱╱╱╱╱╱╱╱╱╱╱┃╭┫┃╰╯┃┃\n"
banner += "╭━━┳━━┳━━┳━━┳╯╰┫╭╮╭╮┣━━╮\n"
banner += "┃━━┫╭╮┃╭╮┃╭╮┣╮╭┫┃┃┃┃┃┃━┫" + bcolors.WARNING + " (Owner Marcelo Vázquez - aka " + bcolors.ENDC + bcolors.OKBLUE + "s4vitar" + bcolors.ENDC + bcolors.WARNING + ")\n" + bcolors.ENDC
banner += "┣━━┃╰╯┃╰╯┃╰╯┃┃┃┃┃┃┃┃┃┃━┫\n"
banner += "╰━━┫╭━┻━━┻━━╯╰╯╰╯╰╯╰┻━━╯\n"
banner += "╱╱╱┃┃\n"
banner += "╱╱╱╰╯\n"

print(banner)


print("\n" + bcolors.OKGREEN + "[" + bcolors.ENDC + bcolors.OKBLUE + "*" + bcolors.ENDC + bcolors.OKGREEN + "] Collecting data...\n" + bcolors.ENDC)

os.remove("./response/content_response.txt")


session = requests.Session()

# Send a GET request to the login page to get the initial HTML
response = session.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the login form
form = soup.find('form', {'id': 'loginForm'})  # adjust the form ID if needed

# Extract the form fields
fields = {}
for input_field in form.find_all('input'):
    # fields[input_field['name']] = input_field.get('value', '')
	fields['provider_type'] = 'phone'
	fields['access_token'] = ''
	fields['redirect_url'] = ''
	fields['countrycode'] = str(area_code)
	fields['phone_number'] = str(phone_number)
	fields['login-pin'] = str(login_pin)
	
# Send a POST request to the login page with the form data
response = session.post(url, data=fields)
# print(response)
# Check if the login was successful
if response.status_code == 200:
    # print("Logged In!")
    # You can now access the protected pages using the same Session object
    # The Session object will store the cookies and session data
	# print(response.content)
    # Example: Send a GET request to a protected page
	response = session.get(url_account)
	content_file = open("./response/content_response.txt", "w")
	content_file.write(response.content.decode())
	content_file.close()
    # print(response.content)

	with open('./response/content_response.txt') as f:
        #for lines in f:
		soup = BeautifulSoup(f, 'html.parser')
		if (soup.find('span', {'id': 'credits_remaining'})):
			form = soup.find('span', {'id': 'credits_remaining'}).string
		else:
			print(bcolors.OKGREEN + "[" + bcolors.ENDC + bcolors.OKBLUE + "*" + bcolors.ENDC + bcolors.OKGREEN + "] The data entered does not correspond to any account\n" + bcolors.ENDC)
			print(bcolors.OKGREEN + "[" + bcolors.ENDC + bcolors.OKBLUE + "*" + bcolors.ENDC + bcolors.OKGREEN + "] Please, create an account first at https://www.spoofcard.com\n" + bcolors.ENDC)
			sys.exit(0)

        # Extract the form fields
		fields = {}
		# for input_field in form.find_all('h4'):
		# print('Credits Remaining: ')
		# print(form)
		total_creds = form

else:
	print(bcolors.OKGREEN + "[" + bcolors.ENDC + bcolors.OKBLUE + "*" + bcolors.ENDC + bcolors.OKGREEN + "] The data entered does not correspond to any account\n" + bcolors.ENDC)
	print(bcolors.OKGREEN + "[" + bcolors.ENDC + bcolors.OKBLUE + "*" + bcolors.ENDC + bcolors.OKGREEN + "] Please, create an account first at https://www.spoofcard.com\n" + bcolors.ENDC)
	os.remove("./response/content_response.txt")
	sys.exit(0)

print("*****************************")
print("Credits on Account: %s " % total_creds + '')
print("*****************************")

if total_creds == "0":
	print('\n' + bcolors.FAIL + "You have no credits available" + bcolors.ENDC + '\n')
	sys.exit(0)

print("\n     " + bcolors.WARNING + "[" + bcolors.ENDC + bcolors.HEADER + "MENU" + bcolors.ENDC + bcolors.WARNING + "]" + bcolors.ENDC)
print("-----------------")
print("1. Call Spoofing")
print("2. SMS Spoofing")
print("0. Exit")
print("-----------------")

menu_option = input("Choose option: ")

if menu_option == "1":
	call_spoofing()
elif menu_option == "2":
	sms_spoofing()
elif menu_option == "0":
	sys.exit(0)
else:
	print("\nInvalid Option\n")

