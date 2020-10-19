'''
Created on Nov 24, 2009

@author: rtbreit
@modified: bwarren 23/11/2011
@modified: bwarren 26/03/2016 for kiwifruit
'''
import os

DB_HOST   = 'efpdb'           # hostname of MySQL database server, for docker
DB_PORT   = 3306           # port of MySQL database service
DB_USER   = 'efpuser'            # username for database access
DB_PASSWD = 'efppass'          # password for database access
DB_ANNO   = 'efp_actinidia_annotations_lookup' # database name for annotations lookup
DB_ORTHO  = ''		# ortholog DB

# lookup table for gene annotation
DB_ANNO_TABLE = 'annotation'
# column name for gene id in this table
DB_ANNO_GENEID_COL = 'gene_id'

### NOTE ###
# The names of
# lookup table for probeset id
DB_LOOKUP_TABLE = 'gene_id_lookup'
# column name for gene id in this table
DB_LOOKUP_GENEID_COL = 'gene_id_name'

# lookup tables for ncbi ids
DB_NCBI_GENE_TABLE = None
DB_NCBI_PROT_TABLE = None
# column name for gene id in this table
DB_NCBI_GENEID_COL = None

# initial gene ids when start page is loaded
GENE_ID_DEFAULT1 = 'Acc00001.1'
GENE_ID_DEFAULT2 = 'Acc00002.1'

# Settings for generated background image
IMAGE_PADDING = 20
SECTION_PADDING = 80
IMAGE_DIMENSION = (1200, 1000)
GRAPH_DIMENSION = (64, 86)
CAPTION_FONT = '../css/DejaVuSans.ttf'
CAPTION_COLOUR = '#444444'
CAPTION_SIZE = 14

# the little graph on the tga image has a scale
# such that 1 unit is x pixels for different ranges on the x-axis of the graph
# the GRAPH_SCAL_UNIT consists of value pairs: upper end of range and scale unit
# so ((1000, 0.031), (10000, 0.003222), (1000000, 0.00031)) means:
# use 0.031 as scale unit for 0 < signal < 1000
# use 0.003222 as scale unit for 1000 < signal < 10000
# use 0.00031 as scale unit for 10000 < signal < 1000000
# see also efp.drawImage()
GRAPH_SCALE_UNIT = {}
# the default values are used if for the given data source no special values are defined
GRAPH_SCALE_UNIT["default"] = [(1000, 0.031), (10000, 0.003222), (1000000, 0.00031)]

# define additional header text for individual data sources
# you can use key 'default' for each not individually defined
datasourceHeader = {}
datasourceHeader['default'] = ''
#datasourceHeader['Seed'] = "<ul><li>Click on citations below the images for the corresponding publications.</li></ul>"

# define additional footer text for individual data sources
# you can use key 'default' for each not individually defined
datasourceFooter = {}
datasourceFooter['default'] = '<ul><li>eFP Browser by B. Vinegar <a href="http://bar.utoronto.ca/" target="_blank" alt="eFP Browser by B. Vinegar">www.bar.utoronto.ca</a>. Data and images from Plant and Food Research Ltd New Zealand</li></ul>'

# regular expression for check of gene id input (here agi and probeset id allowed)
#inputRegEx = "(At[12345CM]g[0-9]{5})|([0-9]{6}(_[xsfi])?_at)|[0-9]{6,9}"
inputRegEx = "^Acc[0-9]{5}\.[0-9]{1,2}$"

# default thresholds
minThreshold_Compare = 0.6  # Minimum color threshold for comparison is 0.6, giving us [-0.6, 0.6] on the color legend
minThreshold_Relative = 0.6 # Minimum color threshold for median is 0.6, giving us [-0.6, 0.6] on the color legend ~ 1.5-Fold
minThreshold_Absolute = 10  # Minimum color threshold for max is 10, giving us [0, 10] on the color legend

# coordinates where to write gene id, probeset id and gene alias into image
GENE_ID1_POS = (0, 0)
GENE_ID2_POS = (0, 14)
GENE_PROBESET1_POS = (120, 0)
GENE_PROBESET2_POS = (120, 14)
GENE_ALIAS1_POS = (180, 0)
GENE_ALIAS2_POS = (180, 14)

defaultDataSource = 'vegetative_growth'
# folder with XML configuration files for data sources
dataDir   = '../data'
outputDir = '../output'
wwwOutDir = '../output'

if not os.path.exists (outputDir):
    os.makedirs (outputDir)
        
dbGroupDefault = 'Vegetative_Growth'
# list of datasources in same group to find max signal 
groupDatasource          = {}
groupDatasource["Vegetative_Growth"]    = ['vegetative_growth']
groupDatasource["Flower_Fruit_Development"]    = ['flower_fruit_development']
groupDatasource["Postharvest"]    = ['postharvest']
groupDatasource["Bud_Development"]    = ['bud_development']

# mapping of xml file name to display datasource name
groupDatasourceName          = {}
groupDatasourceName["Vegetative_Growth"]    = {'vegetative_growth':'<em>Actinidia spp.</em> Vegetative Growth'}
groupDatasourceName["Flower_Fruit_Development"]    = {'flower_fruit_development':'<em>Actinidia spp.</em> Flower and Fruit Development'}
groupDatasourceName["Postharvest"]    = {'postharvest':'<em>Actinidia spp.</em> Postharvest'}
groupDatasourceName["Bud_Development"]    = {'bud_development':'<em>Actinidia spp.</em> Bud Development'}

# expressologs configuration
# list of species where expressologs should be tried to retrieve (names must be the same as in ortholog db)
# if no expressologs used, set to empty list: ()
ortholog_species = () #'SOYBEAN'

# link for found expressologs
efpLink = {}

# identifier of Species of this efp browser (also found in ortholog db, if used)
species = 'Aspp'

# translation table for species id to display name
spec_names = {}
spec_names['Aspp']      = 'Actinidia spp.'
