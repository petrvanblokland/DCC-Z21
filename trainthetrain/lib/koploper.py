# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
#
#     Copyright (c) 2023+ TYPETR
#     Usage by MIT License
# ..............................................................................
#
#    TYPETR __init__.py
#
#   The KoploperIO class implements the methods neede for reading/writing existing databases.
#   For that it offers an api to read/write all data that the original Koploper application can hold.
#   Since development will be an ongoing process for while (reverse engineering the database architecture),
#   some files will be stored at placeholder names until it is known what function they have.
# 
#   Translating the Dutch Koploper names into these terms:
#   baan.dba
#   BAAN    Baan            Layout Collection of “Baan” element
#   LIJN    Lijn            Track
#   WISS    Wissel          Point
#   PBLK    Blok?           Block
#   LIBL    ?
#   WSTR    Wisselstraat    Points
#   INBL    ?
#   BZWL    ?
#
#   blok.dba
#   BLKT    ?
#   BLOK    Blok            Block
#   BLVN
#   BLRI
#   
#   dvre.dba
#   kopd.dba
#   SEIN1   Sein1           Signal1
#   SEIN2   Sein2           Signal2
#   N2BRO
#   SEBE2
#   SEBE3
#   BZTM1   Bezetmelder1
#   BZTM2   Bezetmelder2
#   BTTT1
#   BTTT2
#   BTTT3
#   BTTT4
#   BTYP1
#   OPST4
#   ...
#
import codecs

EXT_BCK = '.bck'
EXT_TXT = '.txt'

FILE_BAAN = 'baan.dba'

ID_BAAN = 'BAAN'
ID_LIJN = 'LIJN'

TAG_FILEPATH = '[<<>>]' # Marker for file name data below

class File:
    def __init__(self):
        pass

class Baan(File): # Koploper “Baan”

    BAAN_LINE_LENGTH = 32
    LIJN_LINE_LENGTH = 6
    def __init__(self):
        self.layout = [] # Set of “Baan” elements
        self.tracks = []

    def __repr__(self):
        return(f'<{self.__class__.__name__} layout={len(self.layout)} tracks={len(self.tracks)}>')

    def appendLine(self, line):
        """Add a line of fields"""
        vLine = [] # Line with translated values
        for value in line:
            if value == 'FALSE':
                vLine.append(False)
            elif value == 'TRUE':
                vLine.append(True)
            else:
                try:
                    v = int(value)
                    vf = float(value)
                    if v == int(vf):
                        vLine.append(v)
                    else:
                        vLine.append(vf)
                except ValueError:
                    vLine.append(value)
        if vLine[0] == ID_BAAN:
            #BAAN    L   0   Perron 1b   140 300 0   Arial   8   0   FALSE   TRUE    FALSE   FALSE   TRUE    -1  -1  TRUE    
            #8454143 0   0   0   FALSE   FALSE   0   FALSE   FALSE   0   -1  -1  -1  FALSE
            assert len(line) == self.BAAN_LINE_LENGTH, f'BAAN line was {len(line)} excepted {self.BAAN_LINE_LENGTH}'
            self.layout.append(vLine)
        elif vLine[0] == ID_LIJN:
            #LIJN    10  0   218 228 0
            assert len(line) == self.LIJN_LINE_LENGTH
            self.tracks.append(vLine)
        else:
            pass # Element type not yet implemented

class KoploperIO:
    """Constructor of KoploperIO, reading/writing Koploper databases."""

    def __init__(self, path):
        """
        >>> kl = KoploperIO('../docs/koploper/StationLelybaan.txt')
        >>> kl
        <KoploperIO ../docs/koploper/StationLelybaan.txt>
        >>> len(kl.elements[0].layout)
        27
        >>> len(kl.elements[0].tracks)
        76
        >>> kl = KoploperIO('../docs/koploper/Hennie.bck')
        >>> kl
        <KoploperIO ../docs/koploper/Hennie.bck>
        """
        self.read(path) # Read the databse, construct internal data containers.

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.path}>'

    def read(self, path):
        """Read the Koploper database file at path. This can be a folder of (backup) file."""
        self.path = path
        # Prepare storage for data components
        self.comments = []
        self.connectors = []
        self.elements = []

        if path.endswith(EXT_BCK):
            fin = codecs.open(self.path, 'r')
            data = fin.read()
            fin.close()
        elif path.endswith(EXT_TXT):
           # Needs to be fixed, reading the 0xff of the binary.
            fin = codecs.open(self.path, 'r', encoding='utf-8')
            data = fin.read()
            fin.close()
        else:
            raise ValueError(f'Unknown type of data file: {path}')

        self.txt = data.replace(chr(0x0d), '') # Remove newlines, just to be sure
        # have their own line. Each line probably is separated by Windows' <cr><lf>
        # Parse the data. The Koploper data file seems to be relative simple, as all of items

        e = None # Current element to add a line of data to.

        for line in self.txt.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                self.comments.append(line)
            elif line.startswith(TAG_FILEPATH): # Select the file type for this data block
                if line.endswith(FILE_BAAN):
                    e = Baan()
                    self.elements.append(e)
                # More file types here.
                else:
                    e = None

            if e is not None:
                fields = line.split('\t')
                if fields[0] in (ID_BAAN, ID_LIJN):
                    e.appendLine(line.split('\t'))
        

    def write(self, path=None):
        pass

if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod()[0])


