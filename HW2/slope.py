import csv
import sys
import math
from helper import MatchedProbe, SlopeLink

def readfile():
    if len(sys.argv) == 3:
        matchdataFile = sys.argv[1]
        LinkdataFile = sys.argv[2]
    else:
        print("input the matchedPoint file and LinkData file.")
        sys.exit(1)

    return matchdataFile, LinkdataFile

def readMatchedData(fileName):
    print("reading matchedProbe data file")
    matchedProbeList =[]
    with open(fileName, newline='') as csvfile:
        probes = csv.reader(csvfile)
        for r in probes:            
            aprobe = MatchedProbe(r)
            matchedProbeList.append(aprobe)
    print("Completed.")
    return matchedProbeList

def readLinkfile(fileName):
    print("Reading link data file")
    listOfLink =[]
    with open(fileName, newline='') as csvfile:
        links = csv.reader(csvfile)
        for r in links: 
            shape = []
            slopeInfo = []
            if r[14] != None:           
                points = r[14].split('|')
                lat, lon, alt = points[0].split('/')
                shape.append((float(lat), float(lon)))
                if alt != '':
                    alt = float(alt)
            if r[16] != '':
                slopeinfo = r[16].split('|') 
                for slope in slopeinfo:
                    s = slope.split('/')
                    slopeInfo.append((float(s[0]),float(s[1])))
            alink = SlopeLink(r, shape, alt, slopeInfo)
            listOfLink.append(alink)
    print("Completed.")
    return listOfLink

def evaluateSlope(matchedProbeList, listOfLink):
    print("Evaluating slope")
    slopeResults = []
    for point in matchedProbeList:
        link = next((link for link in listOfLink if link.id == point.linkID))
        if len(link.slopeinfo) > 0:            
            matchRefDis = math.sqrt(abs(point.distFromRef ** 2 - point.distFromLink ** 2))
            slope = link.slopeinfo[0][1]
            for i in range(1, (len(link.slopeinfo))):
                if matchRefDis < link.slopeinfo[i][0]:
                    slope = link.slopeinfo[i-1][1]
            
            evaSlope = calSlope(point.distFromRef, link.alt, point.alt)
            slopeResults.append((point.linkID, point.lat, point.lon, evaSlope, slope, abs(evaSlope - slope)))

    print("Completed")
    return slopeResults

def calSlope(dist, alt1, alt2):

    return math.degrees(math.atan((alt2 - alt1) / dist))
 

def writeOutput(fileName, slopeResult):
    print("writing to outputfile")
    with open(fileName,'w', newline ='') as csvfile:
        for r in slopeResult:
            output = csv.writer(csvfile)
            output.writerow((r))
    print("Writing completed")

def main():
    matchdataFile, LinkdataFile = readfile()
    matchedProbeList = readMatchedData(matchdataFile)
    listOfLink = readLinkfile(LinkdataFile)
    slopeResults = evaluateSlope(matchedProbeList, listOfLink)
    outputName = "LinkSlopeAndEvaSlope.csv"
    writeOutput(outputName, slopeResults)

if __name__ == '__main__':
    main()
