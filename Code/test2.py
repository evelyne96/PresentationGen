#!/usr/bin/env python3

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from xml.dom import minidom
from pathlib import Path

import re, os, time

orcid_path = 'https://pub.orcid.org/v3.0/'
researcher_url_endpoint = '/researcher-urls'

id = '0000-0002-4857-878X'


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    
    if resp == None or resp.status_code != 200:
        return False

    content_type = resp.headers['Content-Type']
    if content_type == None:
        return False

    content_type = content_type.lower()
    return (content_type.find('html') > -1)

def is_pdf_content(resp):
    """
    Returns True if the response seems to be PDF, False otherwise.
    """
    try:
        if resp == None or resp.status_code != 200:
            return False

        content_type = resp.headers['Content-Type']
        if content_type == None:
            return False

        content_type = content_type.lower()
        return (content_type.find('pdf') > -1)
    except KeyError:
        return False

def is_ppt_content(resp):
    if resp == None or resp.status_code != 200:
        return False

    try:
        content_type = resp.headers['Content-Type']
        if content_type == None:
            return False

        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 
                and content_type is not None 
                and content_type.find('powerpoint') > -1)
    except KeyError:
        return False


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True, headers=headers, timeout=7)) as resp:
            if is_good_response(resp):
                return (resp, resp.content)
            else:
                return (resp, resp.content)

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return (None, '')

def research_url_path(orcid_id):
    return orcid_path + orcid_id + researcher_url_endpoint

def get_researcher_homePage(orcid_id):
    url = research_url_path(orcid_id)
    (resp, content) = simple_get(url)

    if resp != None:
        xmlDoc = minidom.parseString(content)
        webpageDom = xmlDoc.getElementsByTagName('researcher-url:url')
        if webpageDom != None and len(webpageDom) > 0:
            webpage_url = webpageDom[0].firstChild.nodeValue
            print('Page: ', orcid_id, ' ' ,webpage_url)
            return webpage_url

    return None


def searchForPresentations(link, folderToSave):
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

# get_researcher_homePage(id)

orcid_data_dir = '../orcid_data/json/'

def getListOfElement(raw_html, element, findHref = True):
    try:
        if raw_html == None:
            return []

        html = BeautifulSoup(raw_html, 'html.parser')
        listOfAnchor = html.find_all(element, href = findHref)
        return listOfAnchor
    except:
        return []

def attributeIfExxists(dict, key):
    try:
        if type(dict[key])==list:
            return dict[key]
        else:
            return [str(dict[key])]
    except:
        return []

def get_href_att(anchor):
    h = attributeIfExxists(anchor, 'href')
    if len(h) > 0:
        return h[0]
    else:
        return None

def createAnchorLink(aLink, parentLink):
    if "http" in aLink or 'www.' in aLink:
        return aLink
    else:
        return parentLink + "/" + aLink

def getPublicationsPage(home_page_url):
    (resp, content) = simple_get(home_page_url)
    listOfAnchor = getListOfElement(content, 'a')

    publications_anchors = [] 
    for a in listOfAnchor:
        if 'publication' in str(a).lower():
            href = get_href_att(a)

            if  href != None:
                hrefLink = createAnchorLink(href, home_page_url)
                publications_anchors.append((a, hrefLink))
            
    return publications_anchors

def getLiElements(content):
    liList = getListOfElement(content, 'li', findHref=False)
    
    return liList

def nrOfAcceptedElements(anchors):
    nr = 0
    for a in anchors:
        href = get_href_att(a)
        if 'pdf' in str(href).lower() or 'ppt' in str(href).lower() or 'powerpoint' in str(href).lower():
            nr +=1
    return nr


def processPubAnchors(pubs_anchors, folderToSave, parentLink):
    nr = 0
    # print('Pubs anchors', pubs_anchors)
    for (a, link) in pubs_anchors:
        (resp, content) = simple_get(link)
        liList = getLiElements(content)
        # print(liList)
        # when you find someting
        if liList != None:
            for li in liList:
                anchors = li.find_all('a', href = True)
                numberOdfValidAnchors = nrOfAcceptedElements(anchors)
                if numberOdfValidAnchors > 1 and ('pdf' in str(anchors).lower()):
                    pairFolder = folderToSave+'/'+str(nr)
                    if not os.path.exists(folderToSave):
                        os.mkdir(folderToSave)
                        
                    if not os.path.exists(pairFolder):
                        os.mkdir(pairFolder)
                        nr += 1

                    anchor_nr = 0 
                    for a in anchors:
                        href = get_href_att(a)
                        if href != None:
                            l = createAnchorLink(href, parentLink)
                            (resp, content) = simple_get(l)
                            file = None
                            if is_pdf_content(resp):
                                file = open(pairFolder+'/'+str(anchor_nr)+".pdf", 'wb')
                            if is_ppt_content(resp):
                                file = open(pairFolder+'/'+str(anchor_nr)+".ppt", 'wb')
                            if file != None:
                                print('Saving into folder', pairFolder)
                                anchor_nr += 1
                                file.write(content)
                                file.close()
                    
                    

dataset_path = '../dataset2/'
def goThroughOrcidData():
    nr = 0
    for x in os.listdir(orcid_data_dir):
        print(x)
        current_dir = orcid_data_dir+x
        for y in os.listdir(current_dir):
            profile_id = Path(y).resolve().stem
            print('Profile', profile_id)
            homepage_url  = get_researcher_homePage(profile_id)
            if homepage_url != None:
                pubs_anchors = getPublicationsPage(homepage_url)
                folderToSave = dataset_path + profile_id

                processPubAnchors(pubs_anchors, folderToSave, homepage_url)

            # time.sleep(2)
        
        
        # break

goThroughOrcidData()

# profile_id = '0000-0002-2901-0144'
# homepage_url = 'http://www.ds.mpg.de'
# pubs_anchors = getPublicationsPage(homepage_url)
# folderToSave = dataset_path + profile_id
# processPubAnchors(pubs_anchors, folderToSave, homepage_url)


