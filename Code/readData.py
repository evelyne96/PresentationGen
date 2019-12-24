#!/usr/bin/env python3

import json
from typing import List
import urllib.request

fileName = './newData.json'
json_data = {}

class Author:
    def __init__(self, name: str):
        self.name = name
        
    @classmethod
    def from_json(cls, data):
        return cls(**data)


class Link:
    def __init__(self, rel: str, href: str, type: str, title: str = None):
        self.rel = rel
        self.href = href
        self.type = type
        self.title = title
        
    @classmethod
    def from_json(cls, data):
        return cls(**data)


class Tag:
    def __init__(self, term: str, scheme: str, label: str):
        self.term = term
        self.scheme = scheme
        self.label = label
        
    @classmethod
    def from_json(cls, data):
        return cls(**data)


class Paper:
    """
    Custom Paper data Class
    """
    def __init__(self, author: List[Author], day: int, id: str, link: List[Link], month: int, summary: str, tag: List[Tag], title: str, year: int):
        self.author = author
        self.day = day
        self.id = id
        self.link = link
        self.month = month
        self.summary = summary
        self.tag = tag
        self.title = title
        self.year = year
        
    @classmethod
    def from_json(cls, data):
        day = data['day']
        id = data['id']
        month = data['month']
        summary = data['summary']
        title = data['title']
        year = data['year']
        author = []
        for a in data['author']:
            author.append(Author.from_json(a))
        tag = []
        for t in data['tag']:
            tag.append(Tag.from_json(t))
        link = []
        for l in data['link']:
            link.append(Link.from_json(l))
         
        return Paper(author, day, id, link, month, summary, tag, title, year)



with open(fileName, 'r') as file:
        json_data = json.load(file)

papers = []

for paper in json_data:
    papers.append(Paper.from_json(paper))

#print(papers)
folder = './dataset_papers/'
startDownload = False
for paper in papers:
    linkToDownload = paper.link[1].href
    if paper.id == 'cs0308025v1':
        startDownload = True

    if startDownload:
        response = urllib.request.urlopen(linkToDownload)
        id = paper.id.replace("/", "")
        file = open(folder+id+".pdf", 'wb')
        file.write(response.read())
        file.close()



