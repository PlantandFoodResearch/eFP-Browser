#!/usr/bin/python
#
# efpLoader.py
"""
Python script to load the data into the XML file and create the background image, from input collection
@author Benjamin Warren
@date 28-11-2011
"""
import xml.dom.minidom as xml
import sys
import os
import glob
import efpConfig 
import hashlib 
from PIL import Image, ImageDraw, ImageFont
from itertools import izip

##################
### Parameters ###
##################

# params grabbed from efpConfig.py
PADDING = efpConfig.IMAGE_PADDING # padding for image concatenation
SECTION_PADDING = efpConfig.SECTION_PADDING # padding for section concatenation
WIDTH, HEIGHT = efpConfig.IMAGE_DIMENSION # get dimensions from config file
GRAPH_WIDTH, GRAPH_HEIGHT = efpConfig.GRAPH_DIMENSION # width for included graph
CAPTION_COLOUR = efpConfig.CAPTION_COLOUR # hex-code for caption colour
CAPTION_SIZE = efpConfig.CAPTION_SIZE # size in pts of caption font
CAPTION_FONT = efpConfig.CAPTION_FONT # path to font.ttf file to use for caption font
# local params
HASH_CHUNK_SIZE = 4096 # size of input chunks used to create checksum - getChecksum(path) function

#################
### Functions ###
#################

### MAIN FUNCTION CALLED BY efpWeb.cgi --- Load data from specified collection
def loadCollection (collection):
        # set up paramterers
        collection_path = efpConfig.dataDir + "/collections/" + collection
        if ( not os.path.isdir(collection_path) ): # if there is no collection return
                return

        ### check to see if we need to process the data
        ###############################################
        # check if required XML control file and image files exist
        if ( os.path.exists(efpConfig.dataDir + "/" + collection + ".xml") and
	     os.path.exists(efpConfig.dataDir + "/" + collection + "_image.png") and
	     os.path.exists(efpConfig.dataDir + "/" + collection + "_image.tga") ):
                # check if this collection has any new data changes 
                if (not dataAltered(collection_path) ):
                        return # do not process data if it is unchanged, just exit

        # at this point either:
                # the XML control file is missing (this is required) or
                # one or both of the image files are missing (required also) or
                # the checksum is missing (data may have changed) or
                # the checksum changed (data has changed).
        # Whatever the reson, we must carry on processing the data...

        # Load existing control XML file data
        try:
                doc = xml.parse("%s/%s_header.xml" % (collection_path, collection) )
        except Exception, e:
                print >> sys.stderr, "WARNING: Could not open control file header: %s/%s_header.xml\n%s\nSkipping collection..." % (collection_path, collection, e)
                return
        #get group tag to add XML after 
        global groupElement 
        groupElement =  doc.getElementsByTagName("group")[0]

        # call loadSpecimens if the specimen dir exists
        if os.path.isdir(collection_path):
                loadSpecimens(collection, collection_path)

        # add graph coordinates element to XML control file
        viewNode = doc.getElementsByTagName("view")[0]
        graph = doc.createElement("coords")
        graph.setAttribute("graphX", "0")
        graph.setAttribute("graphY", "0")
        graph.setAttribute("graphWidth", "%s" % GRAPH_WIDTH)
        graph.setAttribute("graphHeight", "%s" % GRAPH_HEIGHT)
        graph.setAttribute("legendX", "0")
        graph.setAttribute("legendY", "%s" % GRAPH_HEIGHT)
        viewNode.insertBefore(graph, viewNode.firstChild)

        # Write XML control file
        try:
                f = open("%s/%s.xml" % (efpConfig.dataDir, collection), "w")
                doc.writexml(f)
                f.close()
        except Exception, e:
                print >> sys.stderr, "ERROR: Could not write control file: %s.xml\n%s" % (collection, e)
        return

# Load specimens from specified collection
def loadSpecimens(collection, collection_path):
        # initialise parameters
        curr_height = HEIGHT
        font = ImageFont.truetype(CAPTION_FONT, CAPTION_SIZE)
        x_pos = GRAPH_WIDTH 
        y_pos = CAPTION_SIZE
        ### generate blank background image
        output_image = Image.new("RGB", (WIDTH, curr_height), "White")
        # get list of subsections of collection
        subsections = os.listdir(collection_path)
        subsections.sort() # sort to ensure lexicographic order for drawing sections
        # for all sections in the collection
        for section in subsections:
                if ( section.find(".") == -1 ): # ignore hidden directories and files(like file.ext)
                        section_path = os.path.join(collection_path, section )
                        try:
                                data = xml.parse( os.path.join(section_path, '%s.xml') % (section) )
                        except Exception, e:
                                print >> sys.stderr, "WARNING: %s\nSkipping to next section...\n" % e
                                continue # try next section...
                        section_max_height = 0
                        section_line_height = 0

                        draw = ImageDraw.Draw(output_image)
                        section_node = data.getElementsByTagName("section")[0]
                        section_title = section_node.getAttribute("name")
                        draw.text( (x_pos, y_pos), section_title, font=font, fill=CAPTION_COLOUR)
                        y_pos += CAPTION_SIZE*1.5
                        del draw

                        # get list of image files to draw for this section
                        files = glob.glob( os.path.join(section_path, '*.png') )
                        files.sort() # sort them to ensure correct drawing order
                        for imgfile in files: # find max height of this section 1st:
                                curr = Image.open(imgfile) 
                                section_max_height = max(section_max_height, curr.size[1])
                        # resize image if no more vertical space left
                        if y_pos + section_max_height + PADDING > curr_height:
                                output_image = extend_image(output_image, (y_pos + section_max_height + PADDING - curr_height) ) # get a resized image
                                curr_height = output_image.size[1] # update height of image

                        init_x_pos = x_pos # store starting x position
                        # for each compnent (corresponds to one image file exactly)
                        for component in data.getElementsByTagName("component"):
                                try:
                                        image = Image.open( os.path.join(section_path, '%s.png') % component.getAttribute("name") ) # open the image or if an error occurs;
                                except Exception, e:
                                        print sys.stderr, "WARNING: can't load image\n%s\n" % e
                                        continue # try next image

                                # get the dimensions of the image 
                                w, h = image.size
                                # track current line's max height
                                section_line_height = max(section_line_height, h)
                                # test for available space to draw image
                                new_x_pos = x_pos + w + PADDING # the new x_pos if we draw this image
                                if new_x_pos > WIDTH: # If it won't fit, do a soft return
                                        y_pos += ( section_line_height + PADDING)
                                        x_pos = init_x_pos 
                                        # resize image if no more vertical space left
                                        if y_pos + section_max_height + PADDING > curr_height:
                                                output_image = extend_image(output_image, (y_pos + section_max_height + PADDING - curr_height) )
                                                curr_height = output_image.size[1]
                                # temporarily shift y_pos to bottom-align images in section 
                                old_y_pos = y_pos
                                if h < section_max_height:
                                        y_pos += (section_max_height - h)
                                # Call importXMLData to write extra data to generated XML control file
                                # the offset is the current x, y position we have just drawn to
                                caption = importXMLData(component, (x_pos,y_pos))
                                # draw image to main image
                                output_image.paste( image, (x_pos, y_pos) )
                                # Add text desc if available
                                draw = ImageDraw.Draw(output_image)
                                x_text_pos = x_pos + ( w - font.getsize(caption)[0] )/2
                                draw.text( (x_text_pos, y_pos + h), caption, font=font, fill=CAPTION_COLOUR)
                                # move right to next drawing position
                                x_pos += (w + PADDING)
                                # resore y_pos from alignment shift
                                y_pos = old_y_pos
                                del draw # clean up
                                del image # clean up
                        # Finish processing section
                        new_y = max(GRAPH_HEIGHT + SECTION_PADDING, section_max_height + SECTION_PADDING)
                        y_pos += new_y
                        x_pos = GRAPH_WIDTH 
                        # Loop back and do next section

        # Save as a png and save as a Targa file
        output_image.save("%s/%s_image.png" % (efpConfig.dataDir, collection) )
        # Only possible with the PIL save targa patch (PILv1.1.6)
        output_image.save("%s/%s_image.tga" % (efpConfig.dataDir, collection) )
        # clean up
        del font
        del output_image
        return

# extend given image vertically(y only) with whitespace specified by extension arg
def extend_image(image, extension):
        height = image.size[1] + extension
        extended_image = Image.new("RGB", (WIDTH, height), "White")
        extended_image.paste(image, (0,0))
        return extended_image 

### import the xml data from the images corresponding <compnent> tag 
def importXMLData(component, offset):
        #load XML from svg image
        caption = ""
        for tissueNode in component.getElementsByTagName("tissue"):
                # correct map coordinates with offset
                for area in tissueNode.getElementsByTagName("area"):
                        # sets the old area coordinates to the offset ones
                        area.setAttribute("coords", applyCoordsOffset(area.getAttribute("coords"), offset) )
                # append tissue element to control file doc
                groupElement.appendChild(tissueNode)
        caption = component.getAttribute("caption")
        # return the caption for this image
        return caption

# apply an (x,y) offset to html image map coordinate list
def applyCoordsOffset(coordsList, offset):
        coordinates = pairwise( coordsList.split(",") )
        offset_x = offset[0]
        offset_y = offset[1]
        newList = ""
        for c in coordinates:
                x = int(c[0]) + int(offset_x)
                y = int(c[1]) + int(offset_y)
                newList += "%s,%s," % (x, y)
        newList = newList[:-1]
        return newList 

# return an iterable list in pairs(2-tuples)
def pairwise(iterable):
        "s -> (s0,s1), (s2,s3), (s4, s5), ..."
        a = iter(iterable)
        return izip(a, a)

# return 0 if data in collection is unchanged, return 1 if data changed
def dataAltered(collection_path):
        new_checksum = getChecksum(collection_path) # Always calculate new md5 checksum
        md5_file_path = collection_path + "_checksum.md5"
        # if it exists read the old checksum
        if (os.path.exists(md5_file_path)):
                try: # load last md5 checksum from collections dir
                        checksum_file = open(md5_file_path, "r")
                        old_checksum = checksum_file.readline()
                        # test old checksum against new checksum
                        if (new_checksum == old_checksum): # compare with old checksum
                                checksum_file.close()
                                return False # return 0, signals data unchanged
                except Exception, e:
                        print >> sys.stderr, "ERROR: %s\n" % e
        # if we get this far,
        # either checksum file does not exist or it is old, either way:
        try: # open and overwrite/create the checksum file for writing
                checksum_file = open(md5_file_path, "w")
        except Exception, e:
                print >> sys.stderr, "WARNING: %s\n" % e
        checksum_file.write(new_checksum) # overwrite with new checksum
        # close checksum file
        checksum_file.close()
        return True # return 1, signals data changed

# return a md5 checksum of all subdirs and files below the path given
def getChecksum(path):
        chksum = hashlib.md5() # make empty md5
        for root, dirs, files in os.walk(path): # for all files in collection
                for file in files:
                        curr = os.path.join(root, file)
                        try: # try to open the file for reading in binary mode
                                f = open(curr, "rb")
                        except:
                                f.close()
                                continue # if we can't open it continue to next file
                        while 1:
                                buf = f.read(HASH_CHUNK_SIZE) # get a chunk
                                if not buf: break # break when EOF reached
                                chksum.update(hashlib.md5(buf).hexdigest()) # update checksum (hex format)
                        f.close()
        return chksum.hexdigest() # return checksum (hex format)
        

#############################################
# FOR TESTING ONLY:
if (__name__ == "__main__") :
        loadCollection("malus_domestica")
else:
        pass
