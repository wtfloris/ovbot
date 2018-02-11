import requests as rq
import sys
import secret as sc
from bs4 import BeautifulSoup
import csv

statfile = "stations.txt"

def fetch(args):
    url = "https://webservices.ns.nl/ns-api-avt?station="
    dest_specified = False
    try:
        orig_station_input, offset = getFullArgument(args, 0)
        station_output = getStation([orig_station_input])
        orig_station = station_output[:station_output.index(' ')]
    except:
        orig_station = input("Geef stationi por favoroni: ")
        return "Kill je moet wel zeggen waarvandaan"
    try:
        dest = args[offset]
        dest_station, trash = getFullArgument(args, offset)
        dest_specified = True
    except:
        pass

    requrl = url+orig_station
    usnm = sc.username
    pswd = sc.password

    try:
        req = rq.get(requrl, auth=(usnm, pswd))
    except:
        return "An error occured."

    soup = BeautifulSoup(req.text, "lxml")
    if soup.find_all("error") != []:
        return "Error: "+soup.find("message").text

    if dest_specified == True:
        return getSingleDest(soup, dest_station)
    else:
        reply = getAllDest(soup)
        if reply == -1:
            return "An error occured."
        else:
            return "Next trains from "+getStationFN([orig_station])+":\n"+getAllDest(soup)

def getAllDest(soup):
    reply = ""
    count = 0
    for p in soup.find_all("vertrekkendetrein"):
        count += 1
        reply += p.find("eindbestemming").text
        reply += " -- "
        vtindex = p.find("vertrektijd").text.index("T")+1
        reply += p.find("vertrektijd").text[vtindex:vtindex+5]
        try:
            reply += p.find("vertrekvertragingtekst").text[0:2]
        except:
            pass
        reply += "\n"
        if count == 5:
            break
    if reply == "":
        reply = -1
    else:
        reply = "Destination -- Departure time (+delay)\n"+reply
    return reply

def getSingleDest(soup, dest_station):
    reply = ""
    dest_station = getStationFN([dest_station])
    count = 0
    for p in soup.find_all("vertrekkendetrein"):
        if p.find("eindbestemming").text.lower() == dest_station.lower():
            count += 1
            reply += p.find("eindbestemming").text
            reply += " -- "
            vtindex = p.find("vertrektijd").text.index("T")+1
            reply += p.find("vertrektijd").text[vtindex:vtindex+5]
            try:
                reply += p.find("vertrekvertragingtekst").text[0:2]
            except:
                pass
            reply += "\n"
        if count == 5:
            break
    if reply == "":
        reply = "Sorry, no trains found"
    else:
        reply = "Destination -- Departure time (+delay)\n"+reply
    return reply

def getStation(args):
    station, q = getFullArgument(args, 0)
    reply = ""
    file = "stations.txt"
    if station == "error":
        return "Something went wrong, check your input."
    with open(file, "r") as csvfile:
        content = csv.reader(csvfile, delimiter=":")
        for row in content:
            for entry in row:
                if station.lower() in entry.lower():
                    reply += row[0]+" -- "+row[3]+"\n"
                    break
    if reply == "":
        reply = "Sorry, couldn't find anything matching "+station
    return reply

def getStationFN(args):
    station, q = getFullArgument(args, 0)
    reply = ""
    if station == "error":
        return "Something went wrong, check your input."
    fullname = getStationByCode(station)
    if fullname != -1:
        return fullname
    with open(statfile, "r") as csvfile:
        content = csv.reader(csvfile, delimiter=":")
        for row in content:
            for entry in row:
                if station.lower() in entry.lower():
                    return row[3]
    return "Sorry, couldn't find anything matching "+station

def getStationByCode(code):
    with open(statfile, "r") as csvfile:
        content = csv.reader(csvfile, delimiter=":")
        for row in content:
            if code.lower() == row[0].lower():
                return row[3]
    return -1

def getFullArgument(args, q):
    try:
        if '"' in args[q]:
            if args[q][0] == '"' and args[q][-1] == '"':
                return args[q]
            ret = ""
            end = False
            i = q
            n = q
            while(end == False):
                i += 1
                if '"' in args[i]:
                    end=True
            while n < i+1:
                ret += args[n]+" "
                n += 1
        else:
            return args[q], q+1
        return ret[1:-2], i+1
    except:
        return "error", -1





