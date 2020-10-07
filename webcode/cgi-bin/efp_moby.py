import sys
import os
import tempfile
import efp, efpConfig
import re
import PHPSerialize

fct = sys.argv[1]
primaryGene = sys.argv[2]
secondaryGene = sys.argv[3]
dataSource = sys.argv[4]
mode = sys.argv[5]
thresholdIn = sys.argv[6]
grey_low = sys.argv[7]
grey_stddev = sys.argv[8]
img = None
threshold = None
error = 0
errorStrings = []
alertStrings = []
lowAlert = 0
sdAlert = 0

alertMessages = ''
errorMessages = ''

# Serialize data from XML file into a Specimen object
spec = efp.Specimen()
xmlName = "%s/%s.xml" % (efpConfig.dataDir, dataSource)
spec.load(xmlName)
view = spec.getView("all")  ## TODO: what if there are more than one view (Development_Map_AtTAX) or the view has different name ??

imgFilename = "%s/%s_image.png" % (efpConfig.dataDir, dataSource)

if thresholdIn != None:
    try:
        threshold = float(thresholdIn)
    except:
        error = 1
        errorStr = 'Invalid Threshold Value "%s"'%thresholdIn
        errorStrings.append(errorStr)
else:
    threshold=0.0

gene1 = view.createGene(primaryGene)
gene2 = view.createGene(secondaryGene)

# If either of these gene IDs are None (bad inputs), then we just
# spit out the default image again
if gene1.getGeneId() == None:
    errorStr = 'The requested Primary gene / probeset ID "%s" cannot be found in %s datasource ' % (primaryGene, view.dbGroup)
    error = 1
    errorStrings.append(errorStr)
elif mode == 'Compare' and gene2.getGeneId() == None:
    error = 1
    errorStr = 'The requested Secondary gene / probeset ID "%s" cannot be found in %s datasource <br>' % (secondaryGene, view.dbGroup)
    errorStrings.append(errorStr)
elif primaryGene == secondaryGene and mode == 'Compare':
    error = 1
    errorStr = 'The requested Secondary gene / probeset ID "%s" must be different than the Primary ID<br>' % secondaryGene
    errorStrings.append(errorStr)
else:
    if mode == 'Absolute':
        (img,viewMaxSignal,viewMaxSignal1,viewMaxSignal2,sdAlert) = view.renderAbsolute(gene1, threshold, grey_mask=grey_stddev)
    elif mode == 'Relative':
        (img,viewMaxSignal,viewMaxSignal1,viewMaxSignal2,lowAlert) = view.renderRelative(gene1, threshold, grey_mask=grey_low)
    elif mode == 'Compare':    
        (img,viewMaxSignal,viewMaxSignal1,viewMaxSignal2) = view.renderComparison(gene1, gene2, threshold)

    # find the max signal across all datasources and provide a link to that datasource
    (maxSignalInDatasource, maxDatasource) = view.getMaxInDatasource(gene1)
    maxSignalInDatasource = round(maxSignalInDatasource,2)
    maxDatasource = re.sub("_"," ", maxDatasource)
    alertStr = "This transcript reaches its maximum expression level (expression potential) of %s in the %s data source." % (maxSignalInDatasource, maxDatasource)
    alertStrings.append(alertStr)

    if threshold == 0.0:
        alertStr = ""
        threshold = viewMaxSignal
        alertStr = "Used a threshold value of %s"%threshold
        alertStrings.append(alertStr)
        # alert the user if SD filter or low filter should be activated
        if grey_stddev != "on" and sdAlert == 1 and mode == 'Absolute':
            grey_stddev_flag = "on"
            alertStr = "Some samples exhibit high standard deviations for replicates. You can use standard deviation filtering to mask those with a deviation greater than half their expression value."
            alertStrings.append(alertStr)
        # alert the user if SD filter or low filter should be activated
        if grey_low != "on" and lowAlert == 1 and mode == 'Relative':
            grey_low_flag = "on"
            alertStr = "Some sample ratios were calculated with low values that exhibit higher variation, potentially leading to ratios that are not a good reflection of the biology. You can low filter below 20 units to mask these."
            alertStrings.append(alertStr)

if len(alertStrings) > 0:
    alertMessages = '#'.join(alertStrings)
        
if len(errorStrings) > 0:
    errorMessages = '#'.join(errorStrings)

if img != None and fct == "efp":
    imgFilename = view.drawImage(mode, maxSignalInDatasource, viewMaxSignal1, viewMaxSignal2, gene1, gene2, img)
elif fct == "chart":
    chartFile = tempfile.mkstemp(suffix='.png', prefix='efp-', dir='../output')
    imgFilename = chartFile[1]
    os.system("chmod 644 " + imgFilename)
    view.saveChart(imgFilename, mode)
list = imgFilename.split("/")
file = list[-1]
s = PHPSerialize.PHPSerialize()
match = re.search("efp-\w+.png", file)
if (match):
    serialized_data=s.serialize(file)
    print "%s"%(serialized_data)
