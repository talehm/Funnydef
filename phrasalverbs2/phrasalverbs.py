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
import re


def wordapi(cursor, word, wordIndex, writer):
    url = ("https://wordsapiv1.p.rapidapi.com/words/{}").format(word).rstrip("\n\r")

    headers = {
        'x-rapidapi-host': "wordsapiv1.p.rapidapi.com",
        'x-rapidapi-key': "e6f5ffc334msh51cac891fbed19bp1803a4jsnf43e3b008e36"
    }
    # print("Requesting word")
    response = requests.request("GET", url, headers=headers)

    response = json.loads(response.text)
    if response.get('success') is None:
        # print("Writing to DB")
        sendtoDB(cursor, word, response, writer, wordIndex)
    else:
        # print("no word")
        row = {'Index': wordIndex,
               'Word': word.rstrip(), 'Status': 'Not Found'}
        writer.writerow(row)
        return None


def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).lower().title()


def generateContent(verb, data):
    i = 1
    word = '<h3><span style=\"color: #ff0000;\">' + \
        verb.capitalize()+'</span></h3><br>'
    content = word
    for key, value in data.items():
        # print(value)
        section = convert(key)
        if key == "descriptions" or key == "derivatives" or key == "examples" or key == "synonyms":
            values = ''
            l = 0
            for j in data[key]:
                l = l+1
                values = values+j.capitalize()+'<br>'
            content = content+'<span style=\"color: #0000ff;\">'+section+': </span><br>' +\
                values+'</br>'

    return content.encode('utf-8').replace("'", "\\'").replace('"', '\\"')


def sendtoDB(action, cursor, verb, data, writer):
    try:
        word = verb
        print(verb)
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        post_title = word.capitalize().rstrip()+" Definition, " + \
            word.capitalize().rstrip() + " Meaning"
        post_name = post_title.lower().replace(" ", "-").replace(',', '')
        post_content = generateContent(verb, data)

        guid = "https://test.funnydef.com/forums/topic/{}/".format(
            post_name).replace(',', '')
        if action == 0:
            query = "INSERT INTO JJD_posts (post_author,"\
                " post_date,"\
                " post_date_gmt,"\
                " post_content,"\
                " post_title,"\
                " post_name,"\
                " post_modified,"\
                " post_modified_gmt,"\
                " post_parent,"\
                " guid,"\
                " post_type )"\
                " VALUES ({},'{}','{}','{}','{}','{}','{}','{}',{},'{}','{}')".format(
                    1, date, date, post_content, post_title, post_name, date, date, 612, guid, "topic")

        else:
            query = "UPDATE JJD_posts set post_content='{}' where post_title='{}'".format(
                post_content, post_title)
        cursor.execute(query)
        seo_title = '%%title%%%%sep%% Dictionary %%sep%% %%sitename%%'
        seo_metadesc = word + " definition, "+word+" meaning, "+word+" means, what  does "+word + \
            " mean, meaning of "+word+", "+word+" synonyms, " + \
            word+" antonyms, opposite of "+word
        seo_focus = word+" definition " + word + " meaning"
        data = [
            (cursor.lastrowid, '_yoast_wpseo_title', seo_title),
            (cursor.lastrowid, '_yoast_wpseo_metadesc', seo_metadesc),
            (cursor.lastrowid, '_yoast_wpseo_focuskw', seo_focus),
        ]
        querySeo = "INSERT INTO JJD_postmeta (post_id,meta_key,meta_value) VALUE (%s, %s, %s)"

        cursor.executemany(querySeo, data)
    except Exception as e:
        print(e)
        row = {'Word': word.rstrip(), 'Status': 'Error' + e}
        writer.writerow(row)
        return None
    finally:
        row = {'Word': word.rstrip(), 'Status': 'Added'}
        writer.writerow(row)
        print("Word is added")


def checkDB(data):
    try:
        connection = mysql.connector.connect(host='162.241.31.95',
                                             database='thrdsren_WPPBV',
                                             user='thrdsren_admin',
                                             password='k2gVBjw4!')
        if connection.is_connected():
            print("You're connected to database ")
            cursor = connection.cursor()

            with open('output/phrasalverbs.csv', 'a') as filedata:
                try:
                    for verb, value in data.items():
                        writer = csv.DictWriter(filedata, delimiter=',', lineterminator='\n', fieldnames=[
                            "Word", "Status"])
                        post_title = verb.capitalize().rstrip()+" Definition, " + \
                            verb.capitalize().rstrip() + " Meaning"
                        query = "SELECT EXISTS(SELECT * from JJD_posts WHERE post_title='%s');" % post_title.rstrip()
                        try:
                            cursor.execute(query)
                        except Exception as e:
                            print(e)
                        checkWord = cursor.fetchone()
                        sendtoDB(checkWord[0], cursor, verb, value,  writer)
                        """ if checkWord[0] == 0:
                            print("API Request")
                            sendtoDB(cursor, verb, value,  writer)
                            # wordapi(cursor, word, wordIndex, writer)
                        else:
                            print("Already exists")
                            row = {
                                'Word': verb.rstrip(), 'Status': 'Exists'}
                            writer.writerow(row) """

                except IndexError:
                    print("Finished")
                    # os.kill(os.getppid(), signal.SIGQUIT)
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def main():
    try:
        with open('data.json') as f:
            data = json.load(f)
            # dictArray = reformatData(data)
            checkDB(data)
            # print(k)
            # pickVerb(word)
            """ for verb, value in data.items():
                checkDB(verb, value) """
            #generateContent(verb, value)
            # value = json.loads(value)
            # print(verb)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
