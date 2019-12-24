#!/usr/bin/env python3

from googlesearch import search
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from xml.dom import minidom

import re, os, time

name = '"Bodo Zalan" OR "Zalan Bodo"'
organizationName = 'Babes Bolyai university'
page = 'homepage'
slides = 'slide OR presentation OR powerpoint'

query = name + organizationName + page
folder = "./dataset2/"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}

def getListOfURL(query):
    """
    Gets the links to the search query using the google search.
    """
    my_results_list = []

    print('doing search')
    for i in search(query, lang = 'en', num = 5, start = 0, stop = 5, pause = 5.0):   
        my_results_list.append(i)
    
    print('search done')

    # my_results_list.append('http://www.cs.ubbcluj.ro/~zbodo/')
    return my_results_list


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True, headers=headers)) as resp:
            if is_good_response(resp):
                return (resp, resp.content)
            else:
                return (resp, resp.content)

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return (None, '')


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)

def is_pdf_content(resp):
    """
    Returns True if the response seems to be PDF, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('pdf') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def getListOfElement(raw_html, element, findHref = True):
    html = BeautifulSoup(raw_html, 'html.parser')
    listOfAnchor = html.find_all(element, href = findHref)
    return listOfAnchor

def attributeIfExxists(dict, key):
    try:
        if type(dict[key])==list:
            return dict[key]
        else:
            return [str(dict[key])]
    except:
        return []

def listOfAnchorAttributes(anchor):
    res = []
    res += attributeIfExxists(anchor, 'class')
    res += attributeIfExxists(anchor, 'id')
    res += attributeIfExxists(anchor, 'href')
    return res

def get_href_att(anchor):
    h = attributeIfExxists(anchor, 'href')
    if len(h) > 0:
        return h[0]
    else:
        return None

def get_id_att(anchor):
    h = attributeIfExxists(anchor, 'id')
    if len(h) > 0:
        return h[0]
    else:
        return None

def get_onClick_att(anchor):
    x = attributeIfExxists(anchor, 'onclick')
    if len(x) > 0:
        h = str(x[0])
        inputAtt = h[ h.find('(')+1 : h.find(')') ]
        if len(h) > 0:
            return h[0]
        else:
            return None
    return None

def createAnchorLink(aLink, parentLink):
    if "http" in aLink:
        return aLink
    else:
        return parentLink + "/" + aLink


def tryDownloadPres(link, parentLink, folderToSave):
    (resp, c) = simple_get(link)
    paperNr = 0
    if resp != None and resp.status_code == 200:
        print('Got something on', link)
        listOfAnchor = getListOfElement(c, 'a')
        for anchor in listOfAnchor:
            href = get_href_att(anchor)
            if href != None:
                l = createAnchorLink(href, parentLink)
                (resp, content) = simple_get(l)
                if resp != None and is_pdf_content(resp):
                    print(l)
                    paperNr = paperNr + 1
                    if not os.path.exists(folderToSave):
                        os.mkdir(folderToSave)

                    file = open(folderToSave+str(paperNr)+"pres.pdf", 'wb')
                    print(file)
                    file.write(content)
                    file.close()

        return True
    return False

def searchForPDFs(link, folderToSave):
    # html content
    (resp, content) = simple_get(link)
    listOfAnchor = getListOfElement(content, 'a')

    done = False

    for anchor in listOfAnchor:
        if any( ('representation' not in s.lower() and 'presentation' in s.lower() or 'slide' in s.lower()) for s in listOfAnchorAttributes(anchor)):
            href = get_href_att(anchor)
            #local link in page
            if  href != None:
                print('Try href link')
                hrefLink = createAnchorLink(href, link)
                done = tryDownloadPres(hrefLink, link, folderToSave)
                if done:
                    break
            
            id = get_id_att(anchor)
            if id != None:
                print('Try id link')
                idLink = createAnchorLink(id, link)
                done = tryDownloadPres(idLink, link, folderToSave)
                if done:
                    break

            onClick = get_onClick_att(anchor)
            if onClick != None:
                print("Try onclick link")
                clickLink = createAnchorLink(onClick, link)
                done = tryDownloadPres(clickLink, link, folderToSave)
                if done:
                    break
        
        if done:
                print('We get the presentations page. Stopping.')
                break
        


orcid_path = "./orcid_data/996"


def getOrgAndPerson(xmlPath):
    xmlDoc = minidom.parse(xmlPath)
    orgElems = xmlDoc.getElementsByTagName('common:organization')
    resElems = xmlDoc.getElementsByTagName('common:source-name')
    if len(orgElems) > 0 and len(resElems) > 0:
        orgChild = orgElems[0].childNodes
        orgName = orgChild[1].firstChild.nodeValue
        researcherName = resElems[0].firstChild.nodeValue
        # print(orgName, " ", researcherName)

        return (orgName, researcherName)
    
    return (None, None)

def goThroughOrcidData():
    nr = 0
    for x in os.listdir(orcid_path):
        fullPath = os.path.join(orcid_path, x)
        worskPath = fullPath + '/works/'
        educationsPath = fullPath + '/educations/'
        empPath = fullPath + '/employments/'
        if os.path.isdir(fullPath) == True:
            dirList = os.listdir(fullPath)
            hasEducations = 'educations' in dirList
            hasEmployments = 'employments' in dirList
            if 'works' in dirList and (hasEducations or hasEmployments):
                nr +=1
                # for work in os.listdir(worskPath):
                #     xmlDoc = minidom.parse(worskPath + '/' + work)
                #     url = xmlDoc.getElementsByTagName('common:url')
                #     print('Work url ', url)
                #     print(xmlDoc)

                if hasEducations:
                    eduXML = educationsPath + os.listdir(educationsPath)[0]
                    (orgName, resName) = getOrgAndPerson(eduXML)
                    if orgName != None:
                        sQuery = resName + " " + page
                        print(sQuery)

                if not hasEducations:
                    empXML = empPath + os.listdir(empPath)[0]
                    (orgName, resName) = getOrgAndPerson(empXML)
                    if orgName != None:
                        sQuery = resName  + ' ' + page
                        print(sQuery)

                listOfURL = getListOfURL(sQuery)

                folderToSave = folder + x + '/'

                for link in listOfURL:
                    searchForPDFs(link, folderToSave)


                time.sleep(20)


    
    
    print("number ", nr)

goThroughOrcidData()
            

        
                

            