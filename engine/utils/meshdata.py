from __future__ import annotations
from typing import Tuple
import xml.etree.ElementTree as ET
import os
from pathlib import Path

UNEXIST = [523962, 523963, 523952, 523953, 523944, 523945, 523934, 523935, 533927]
FILE_NOT_EXIST_ELEVATION = -100

class MeshCode:
    memo = {}

    def __init__( self,
                  latitude: float, #<deg>
                  longitude: float, #<deg>
                  ) -> None:
        assert   0 <= latitude and latitude < 66
        assert 100 <= longitude and longitude < 180
        self._latiitude = latitude
        self._longitude = longitude

        _code = self.xy2mesh(latitude, longitude)
        self.primary   = _code[0]
        self.secondary = _code[1]
        self.residue   = _code[2]

        self.label = "{:d}-{:02d}".format(self.primary, self.secondary)
    
    @staticmethod
    def xy2mesh( lat: float,
                 lon: float,
                 ) -> Tuple[int, int, int]:
        lat_ful = lat * 1.5
        lon_ful = lon - 100
        lat_1st = int(lat_ful)
        lon_1st = int(lon_ful)
        lat_2nd = int((lat_ful - lat_1st) * 8)
        lon_2nd = int((lon_ful - lon_1st) * 8)
        lat_rest= int(((lat_ful - lat_1st) * 8 - lat_2nd) *  750)
        lon_rest= int(((lon_ful - lon_1st) * 8 - lon_2nd) * 1125)

        first  = lat_1st * 100 + lon_1st
        second = lat_2nd * 10  + lon_2nd
        rest = (749 - lat_rest) * 1125 + lon_rest
        return first, second, rest

    def _meshfile_path(self) -> str:
        dirname = Path(__file__).parent.parent
        name = "FG-GML-{:d}-{:02d}-dem10b-20161001.xml".format(self.primary, self.secondary)
        path = os.path.join(dirname, "resource", "PackDLMap", name)
        return path
    
    def _read_meshfile(self) -> None:
        meshfile = self._meshfile_path()
        tree = ET.parse(meshfile)
        root = tree.getroot()
        xpath = "/".join([
            "{http://fgd.gsi.go.jp/spec/2008/FGD_GMLSchema}DEM",
            "{http://fgd.gsi.go.jp/spec/2008/FGD_GMLSchema}coverage",
            "{http://www.opengis.net/gml/3.2}rangeSet",
            "{http://www.opengis.net/gml/3.2}DataBlock",
            "{http://www.opengis.net/gml/3.2}tupleList",
        ])
        data = root.find(xpath).text.split("\n")[1:-1]
        data = [float(d.split(",")[-1]) for d in data]
        self.memo[self.label] = data

    def elevation(self):
        if self.label not in self.memo:
            try:
                self._read_meshfile()
            except FileNotFoundError as e:
                if self.primary*100 + self.secondary in UNEXIST:
                    return FILE_NOT_EXIST_ELEVATION
                else:
                    raise e
        return self.memo[self.label][self.residue]
