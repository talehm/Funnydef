 #!/usr/bin/python
import requests
import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from multiprocessing import Pool
from functools import partial
import os
import sys
import signal
import csv
import re, time
from subprocess import Popen, PIPE
import numpy as np




''' def keyExecutor(i):
        switcher={
                3:'3049de80-5491-11ea-8f72-af685da1b20e',
                0:'650ca0b0-5498-11ea-8f72-af685da1b20e',
                2:'25efb800-549c-11ea-8f72-af685da1b20e',
                1:'5e663790-549c-11ea-8f72-af685da1b20e'
             }
        return switcher.get(i,"Invalid key") '''
        
def sendRequest(url,api_key, body):
    cmd = ["curl",
                "-k", 
                "-X", 
                "POST", 
                "-H",api_key , 
                "-H", "Content-Type: application/json",
                url, 
                "-d", body]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate(b"input data that is passed to subprocess' stdin")
    return output

def renderSimilarTerms(quota, response):
    keywords=''
    for keyword in response:
        if len(keywords) > quota:
            last_key=-len(keyword)-1
            keywords=keywords[:last_key]
            break
        else:
            keywords+=", "+keyword["term"]

    return keywords

def corticalApiwithTerm(withTerm, quota, api_key, text):
    start_index=len(withTerm)
    url = "http://api.cortical.io/rest/expressions/similar_terms?retina_name=en_associative&start_index={}&max_results=20&pos_type=NOUN&sparsity=1.0&get_fingerprint=false".format(start_index)
    
    terms=[]
    for term in withTerm:
        terms.append({"term":term})
    body = {"or": [ 
            {"text": text},
            {"and": terms}]}
    body = json.dumps(body)
    time.sleep(7)
    response=sendRequest(url, api_key, body)
    response=json.loads(response)
    return renderSimilarTerms(quota, response)
    #return term


def corticalApiwithText(data):
    value = data
    api_key = "3049de80-5491-11ea-8f72-af685da1b20e"
    url="http://api.cortical.io/rest/text/keywords?retina_name=en_synonymous"
    body = value["title"] + " " + value["body"]

    output=sendRequest(url, api_key, body).decode("utf-8") \
            .replace("]","") \
            .replace("[","") \
            .replace("\"","") \
            .replace(",",", ") 
    keywords = value["title"] +  ". Cute sarcastic funny jokes in english. " + \
            "Funny hilarious "+value["category"]+" jokes. " + \
            "Best sarcastic jokes about "+output
    withTerm=output.split(", ")

    quota=160 - len(keywords)
    if quota > 0:
        keywords+=corticalApiwithTerm(withTerm, quota, api_key, body)
        print(keywords)

def main():
    with open('wocka.json', 'r+') as json_file:
        args = json.load(json_file)
        for data in args:
            corticalApiwithText(data)
            time.sleep(7)


if __name__ == '__main__':
    main()