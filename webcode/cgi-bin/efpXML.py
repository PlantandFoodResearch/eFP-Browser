#!/usr/bin/python
#
# Module for determining the names of the XML files (data sources)available for the eFP Browser

import os
import sys

def findXML(dir):
    xML = []
    files = os.listdir(dir)
    for f in files:
        if f.endswith(".xml") and not f.startswith("efp_"):
            xML.append(f[0:-4])
    ### added to also search the collections directory
    collection_dir = os.path.join(dir, "collections") # get collection dir
    for c in os.listdir(collection_dir): # for each item in the dir
        # if it is not hidden AND is a directory
        if ( not c.startswith(".") and os.path.isdir(os.path.join(collection_dir, c)) ):
                xML.append(c) # append to the list of data sources

    return set(xML) # return the set, i.e. remove duplicates

if __name__ == '__main__':
    pass

