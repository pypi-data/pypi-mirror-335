import xml.etree.ElementTree as ET
import re
import json


def extract_git_links_xml(path):
    root = ET.parse(path)

    links = []
    git_pattern = re.compile(r"https?://(?:www\.)?github\.com/[^\s]+")

    for elem in root.iter():
        if elem.text:
            match = git_pattern.search(elem.text)
            if match:
                links.append(match.group(0))

    return links

def extract_links_lineby_line(path):
    with open(path,"r") as f:
        file=f.readlines()
    
    return list(file)


def extract_git_links_json(path):
    def search(doc, links):
        if isinstance(doc, dict):
            for key, data in doc.items():
                search(data, links)
        elif isinstance(doc, list):
            for data in doc:
                search(data, links)
        elif isinstance(doc, str):
            match = git_pattern.search(doc)
            if match:
                links.append(match.group(0))

    ext = path.split(".")[-1]
    with open(path, "r") as file:
        if ext.lower() == "json":
            doc = json.load(file)
        else:
            doc = [json.loads(line) for line in file]

    links = []

    git_pattern = re.compile(r"https?://(?:www\.)?github\.com/[^\s]+")
    search(doc, links)
    return links
