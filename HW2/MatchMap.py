import csv
import math
import sys

LINKPVID_INDEX = 0
REFNODEID_INDEX = 1
SHAPEINFO_INDEX = 14

PROBE_SAMPLEID_INDEX = 0
PROBE_DATE_INDEX = 1
PROBE_SOURCECODE = 2
PROBE_LAT_INDEX = 3
PROBE_LONG_INDEX = 4
PROBE_ALTITUDE = 5
PROBE_SPEED = 6
PROBE_HEADING = 7

## Read and store link data
## For each probe point, compare and match the maps

class MapMatching(object):
    def __init__(self):
        self.linkSegmentData = {}
        self.probeData = {}
        self.output = []

    def __segmentLink__(self, link):
        shapeInfo = link.split('|')
        segmentLink = []
        for shape in shapeInfo: 
            segmentLink.append(tuple(shape.split('/')))
        return segmentLink
    
    def __calcDistBetweenPoints__(self,pointA, pointB):
        ## Uses haversine formula
        if len(pointA) == 3:
            pointA = pointA[:-1]
        if len(pointB) == 3:
            pointB = pointB[:-1]
        a = tuple(map(float,pointA))
        b = tuple(map(float,pointB))

        radius = 6372.8
        latDiff = math.radians(b[0] - a[0])
        lngDiff = math.radians(b[1] - a[1])
        aLat = math.radians(a[0])
        bLat = math.radians(b[0])

        valA = math.sin(latDiff / 2) ** 2 + math.cos(aLat) * math.cos(bLat) * math.sin(lngDiff / 2) ** 2
        valC = 2 * math.asin(math.sqrt(valA))
        return radius * valC
    
    def __calcDistAndProjection__(self, pointA, pointB, pointC):
        ## calc projection of C on AB
        ## calc distance between AB and C
        ## calc lat and long of mapMatchedPoint
        ## calc distance between actual point and mapMatchedPoint
        a = tuple(map(float, pointA[:-1]))
        b = tuple(map(float, pointB[:-1]))
        c = tuple(map(float, pointC))
        
        vecAB = (b[0] - a[0], b[1] - a[1])
        vecAC = (c[0] - a[0], c[1] - a[1])

        lenAB = math.sqrt(vecAB[0] ** 2.0 + vecAB[1] ** 2.0)
        unitAB = (vecAB[0]/lenAB, vecAB[1]/lenAB)

        scalingACOntoAB = (vecAC[0] * 1.0/lenAB, vecAC[1] * 1.0/lenAB)

        dotProd = unitAB[0] * scalingACOntoAB[0] + unitAB[1] * scalingACOntoAB[1]

        if dotProd < 0.0:
            dotProd = 0.0
        elif dotProd > 1.0:
            dotProd = 1.0
        
        projCOnAb = (vecAB[0] * dotProd, vecAB[1] * dotProd)
        distFromCtoProj = self.__calcDistBetweenPoints__(projCOnAb, a) * 1000.0

        diffVec = (vecAC[0] - projCOnAb[0], vecAC[1] - projCOnAb[1])

        distFromCtoProj = math.sqrt(diffVec[0] ** 2 + diffVec[1] ** 2)
        projCOnAb = (projCOnAb[0] + a[0], projCOnAb[1] + a[1])

        return (distFromCtoProj, projCOnAb)

    def __matchProbeToLinkData__(self, lat, lng):
        ## for each link point
        ## find the perp distance between 
        closestMapMatchedPoint = (0.0, 0.0)
        minPerpDist = 10000000.0
        minDistFromRef = 0.0
        minLinkData = ('', 0, '')

        for linkElem in self.linkSegmentData:
            link = self.linkSegmentData[linkElem]
            distFromRef = 0.0
            for i in range(1, len(link)):
                perpDist , mapMatchedPoint = self.__calcDistAndProjection__(link[i-1], link[i], (lat, lng))
                if perpDist < minPerpDist and perpDist < 15:
                    minPerpDist = perpDist
                    closestMapMatchedPoint = mapMatchedPoint
                    minLinkData = (link, i, linkElem)

        for i in range(1, minLinkData[1]):
            minDistFromRef += self.__calcDistBetweenPoints__(minLinkData[0][i-1], minLinkData[0][i])
        minDistFromRef += self.__calcDistBetweenPoints__(minLinkData[0][minLinkData[1] - 1], closestMapMatchedPoint)
        minDistFromRef *= 1000.0
        return (closestMapMatchedPoint, minPerpDist, minDistFromRef, minLinkData[2])
    
    def readDataFromLinkDataFile(self):
        with open('Partition6467LinkData.csv') as linkCSV:
            linkReader = csv.reader(linkCSV, delimiter=',')
            for row in linkReader:
                linkPVID = row[LINKPVID_INDEX]
                segment = self.__segmentLink__(row[SHAPEINFO_INDEX])
                self.linkSegmentData[linkPVID] = segment
    
    def readAndMatchProbeData(self):
        with open('Partition6467ProbePoints.csv') as probeCSV:
            probeReader = csv.reader(probeCSV, delimiter=',')
            print('Started Matching')
            count = 1
            direction = 'X'
            prevProbeId = ''
            prevDistFromRef = 0
            for probe in probeReader:
                ## For each probe match probe to link data
                lat = probe[PROBE_LAT_INDEX]
                lng = probe[PROBE_LONG_INDEX]
                curProbeId = probe[PROBE_SAMPLEID_INDEX]
                print(str(count) + '. Matching : ' + lat + ',' + lng)
                count += 1
                sampleID = probe[PROBE_SAMPLEID_INDEX]
                date = probe[PROBE_DATE_INDEX]
                sourceCode = probe[PROBE_SOURCECODE]
                altitude = probe[PROBE_ALTITUDE]
                speed = probe[PROBE_SPEED]
                heading = probe[PROBE_HEADING]
                matchedPoint, perpDistFromLink, distFromRef, linkID = self.__matchProbeToLinkData__(lat, lng)

                if prevProbeId == curProbeId:
                    if prevDistFromRef < distFromRef:
                        direction = 'T'
                    else:
                        direction = 'F'
                
                prevProbeId = curProbeId
                prevDistFromRef = distFromRef

                op = sampleID + ',' + date + ',' + sourceCode + ',' 
                op += str(matchedPoint[0]) + ',' + str(matchedPoint[1]) + ','
                op += altitude + ',' + speed + ',' 
                op += heading + ',' + linkID + ','
                op += direction + ',' + str(distFromRef) + ',' + str(perpDistFromLink * 1000) + '\n'
                print(direction)
                self.output.append(op)
    
    def writeOutputToFile(self):
        with open('MapMathcedData.csv', 'w') as outFile:
            for s in self.output:
                outFile.write(s)
            outFile.close()



if __name__ == '__main__':
    mapMatcher = MapMatching()
    mapMatcher.readDataFromLinkDataFile()
    mapMatcher.readAndMatchProbeData()
    mapMatcher.writeOutputToFile()