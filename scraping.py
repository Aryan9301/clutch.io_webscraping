import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse
import socket
import requests.packages.urllib3.util.connection as urllib3_cn
import sys



def allowed_gai_family(): return socket.AF_INET
urllib3_cn.allowed_gai_family = allowed_gai_family

baseURL = 'https://clutch.co'
webDevURL = 'https://clutch.co/web-developers'
androidURL = 'https://clutch.co/directory/android-application-developers'
csvHeaderRow = ['Company', 'Website', 'Location', 'Contact', 'Rating', 'Review Count', 'Hourly Rate', 'Min Project Size', 'Employee Size']


def getNextURL(soup):
    elem = soup.select_one('.page-item.next')
    if elem:
        return baseURL + elem.a.attrs['href']
    return None

#new requests for contact number
def extractContactNo(URL):
    response = requests.get(URL, timeout = 5)
    soup = BeautifulSoup(response.content, 'html5lib')
    return soup.select_one('.contact.phone_icon').getText().strip()


#data extraction
def extractData(elemList, collectContactNo):
    dataList = list()
    for elem in elemList:
        data = dict()
        data['Company'] = elem.h3.getText().strip()
        parsedURL = urlparse(elem.select_one('.website-link__item').attrs['href'])
        data['Website'] = parsedURL.scheme + '://' + parsedURL.netloc
        dataElems = elem.select('.list-item.custom_popover')
        data['Min Project Size'] = dataElems[0].span.getText().strip()
        data['Hourly Rate'] = dataElems[1].span.getText().strip()
        data['Employee Size'] = dataElems[2].span.getText().strip()
        data['Location'] = dataElems[3].span.getText().strip()
        data['Rating'] = elem.select_one('.rating').getText().strip()
        data['Review Count'] = elem.select_one('.reviews-link').a.getText().strip()
        URL = baseURL + elem.select_one('.website-profile').a.attrs['href']
        data['Contact'] = extractContactNo(URL) if collectContactNo else None
        print('\n', data, '\n')
        dataList.append(data)
    return dataList

def chooseDomain():
    print('Select domain: ?\n\n1.Android\n2.Web Development\n3.Exit\n\n')
    while True:
        choice = int(input('Choice: '))
        if 1 <= choice <= 2:
            return choice
        elif choice == 3:
            print('Byeeeee')
            sys.exit()
        else:
            print('Wrong!!\nChoose from 1, 2 or 3.\n')

def collectData(choice):
    print()
    fileName = input('Provide the name of file to which data should be written: ')
    print()
    promptString = """\nDo you wish to collect contact numbers in the data? Collecting contact numbers would make data collection significantly slower,
we recommend to press no unless absolutely necessary as you can always lookup contact info when really required.
\nEnter your choice(y/n): """
    collectContactNo = input(promptString).lower() == 'y'
    print()
    if choice == 1:
        collectAndroidData(collectContactNo, fileName)
    elif choice == 2:
        collectWebDevData(collectContactNo, fileName)


def collectAndroidData(collectContactNo, fileName):
    fileName = fileName if fileName.endswith('.csv') else fileName + '.csv'
    #Flush the file before the starting the process
    androidData = open(fileName, 'w')
    csvWriter = csv.DictWriter(androidData, csvHeaderRow)
    csvWriter.writeheader()
    androidData.close()
    URL = androidURL
    while True:
        with open(fileName, 'a') as androidDataFile:
            csvWriter = csv.DictWriter(androidDataFile, csvHeaderRow)
            # Set a low timeout because requests module tries to connect with ipv6 first which is not working for this site
            response = requests.get(URL, timeout=5)
            soup = BeautifulSoup(response.content, 'html5lib')
            list = soup.select('.provider.provider-row')
            data = extractData(list, collectContactNo)
            csvWriter.writerows(data)
            URL = getNextURL(soup)
            if not URL:
                return

def collectWebDevData(collectContactNo, fileName):
    fileName = fileName if fileName.endswith('.csv') else fileName + '.csv'
    webDevData = open(fileName, 'w')
    csvWriter = csv.DictWriter(webDevData, csvHeaderRow)
    csvWriter.writeheader()
    webDevData.close()
    URL = webDevURL
    while True:
        with open(fileName, 'a') as webDevDataFile:
            csvWriter = csv.DictWriter(webDevDataFile, csvHeaderRow)
            response = requests.get(URL, timeout=5)
            soup = BeautifulSoup(response.content, 'html5lib')
            list = soup.select('.provider.provider-row')
            data = extractData(list, collectContactNo)
            csvWriter.writerows(data)
            URL = getNextURL(soup)
            if not URL:
                return

def main():
    collectData(chooseDomain())

if __name__ == '__main__':
    main()
