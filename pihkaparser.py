from selenium import webdriver #Browser control with options/waits/exceptions. 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json

def main():
	opts = Options()
	opts.add_argument('--headless')
	opts.add_argument('--disable-gpu')
	opts.add_argument('window-size=1000,1000')
	
	driver = webdriver.Chrome(options=opts)
	#print "Getting info for username " + username
	driver.get("http://lintulahti.pihka.fi/")

	html_source = driver.page_source.encode("utf-8")

	soup = BeautifulSoup(html_source, 'html.parser')
	
	menu = dict()
	
	day_elems = soup.findAll('div', { "class": ["menu-day"] })
	for elem in day_elems:
		day = elem.find('h3')
		day = unicode(day.span.string).strip()
		foods = elem.findAll('li')
		foodarray = []
		for food in foods:
			foodarray.append( unicode(food.span.string).strip() )
		#print "" # Empty line
		menu[day] = foodarray
	
	driver.close()
	
	return menu

def asString():
	menu = main()
	response = ""
	for key in menu:
		response += key + "\n"
		foods = menu[key]
		for food in foods:
			response += food + "\n"
		response += "\n"
	return response		


if __name__ == '__main__':
	print asString()
