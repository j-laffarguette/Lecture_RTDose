import pandas as pd
import re


class LectureMccCuve():
    def __init__(self, mccFile):
        self.collOffsetCrossPlane = None
        self.collOffsetInPlane = None
        self.mccFile = mccFile
        self.positions = []
        self.values = []
        self.listeCle = []
        # dataframes = []
        self.line_in_measurement = False
        self.depth = None
        self.key = None
        self.scanCurve = None
        self.fieldInPlane = None
        self.fieldCrossPlane = None
        self.dictMCC = {}
        print('self.mccFile : ', self.mccFile)

        self.getValues(self.mccFile)
        self.listeCle = list(self.dictMCC.keys())

    def getValues(self, mccFile):
        with open(mccFile, "rt") as file:
            for line in file:
                line_striped = line.strip("\n")
                searchScanCurve = re.search("SCAN_CURVETYPE=(\w+)", line_striped)
                searchFieldInPlane = re.search("^\t\tFIELD_INPLANE=(\d+\.\d+)$", line_striped)
                searchFieldCrossPlane = re.search("^\t\tFIELD_CROSSPLANE=(\d+\.\d+)$", line_striped)
                searchDepth = re.search("SCAN_DEPTH=(\d+\.\d+)", line_striped)
                searchSSD = re.search('SSD=(\d+\.\d+)', line_striped)
                searchCOLL_OFFSET_INPLANE = re.search("COLL_OFFSET_INPLANE=(-?\d+\.\d+)", line_striped)
                searchCOLL_OFFSET_CROSSPLANE = re.search("COLL_OFFSET_CROSSPLANE=(-?\d+\.\d+)", line_striped)
                # recherche SCAN_OFFAXIS_INPLANE
                searchOffAxisInPlane = re.search("SCAN_OFFAXIS_INPLANE=(-?\d+\.\d+)", line_striped)

                if searchScanCurve:
                    self.scanCurve = searchScanCurve.group(1)
                if searchFieldInPlane:
                    self.fieldInPlane = searchFieldInPlane.group(1)
                if searchFieldCrossPlane:
                    self.fieldCrossPlane = searchFieldCrossPlane.group(1)
                if searchDepth:
                    self.depth = searchDepth.group(1)
                if searchSSD:
                    self.SSD = searchSSD.group(1)
                if searchOffAxisInPlane:
                    self.offAxisInPlane = searchOffAxisInPlane.group(1)
                if searchCOLL_OFFSET_INPLANE:
                    self.collOffsetInPlane = searchCOLL_OFFSET_INPLANE.group(1)
                if searchCOLL_OFFSET_CROSSPLANE:
                    self.collOffsetCrossPlane = searchCOLL_OFFSET_CROSSPLANE.group(1)

                if "BEGIN_DATA" in line_striped:
                    self.line_in_measurement = True
                    if self.depth:
                        self.key = str(self.scanCurve) + str(' Field Size = ') + str(self.fieldInPlane) + str(' ') \
                                   + str(self.fieldCrossPlane) + str(' , depth = ') + str(self.depth) + str(' , SSD = ') \
                                   + str(self.SSD) + str(' , offAxisInPlane = ') + str(self.offAxisInPlane) + str(
                            ' , collOffsetInPlane = ') \
                                   + str(self.collOffsetInPlane) + str(' , collOffsetCrossPlane = ') + str(
                            self.collOffsetCrossPlane)

                    else:
                        self.key = str(self.scanCurve) + str(' Field Size = ') + str(self.fieldInPlane) + str(' ') \
                                   + str(self.fieldCrossPlane) + str(' , SSD = ') + str(self.SSD) \
                                   + str(' , offAxisInPlane = ') + str(self.offAxisInPlane) \
                                   + str(' , collOffsetInPlane = ') + str(self.collOffsetInPlane) \
                                   + str(' , collOffsetCrossPlane = ') + str(self.collOffsetCrossPlane)

                elif "END_DATA" in line_striped:
                    data = {'position': self.positions, 'value': self.values}
                    df = pd.DataFrame(data=data, index=[i for i in range(len(self.positions))])
                    # dataframes.append(df.astype(float))
                    self.dictMCC[self.key] = df
                    self.line_in_measurement = False
                    self.positions.clear()
                    self.values.clear()
                    self.listeCle.clear()
                    self.key = None
                elif self.line_in_measurement:
                    self.positions.append(line.split()[0])
                    self.values.append(line.split()[1])

    def printDict(self):
        print('dict : ', self.dictMCC)
