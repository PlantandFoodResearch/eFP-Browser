#!/usr/bin/python
#
# Module for retrieving gene expression data from the Department
# of Botany's Atgenexpress database

import MySQLdb
import re
import urllib2
from urllib2 import HTTPError
import efpConfig
import simplejson as json
import copy
import sys

class Gene:
    def __init__(self, id):
        self.conn = None
        self.connOrtho = None
        self.annotation = None
        self.alias = None
        self.geneId = None
        self.probesetId = None
        self.ncbiId = None
        #id = re.sub("(\.\d)$", "", id) # reduce splice variants (remove .n)
        self.retrieveGeneData(id)
        if(self.geneId == None):
            self.ncbiToGeneId(id)
            self.retrieveGeneData(self.geneId)
    
    def getGeneId(self):
        #primaryGene = re.sub("a","A", primaryGene)
        #primaryGene = re.sub("T","t", primaryGene)
        #primaryGene = re.sub("G","g", primaryGene)
        #primaryGene = re.sub("C","c", primaryGene)
        #primaryGene = re.sub("M","m", primaryGene)
        return self.geneId

    
    def getProbeSetId(self):
        #primaryGene = re.sub("A","a", primaryGene)
        #primaryGene = re.sub("T","t", primaryGene)
        return self.probesetId
    
    def getNcbiId(self):
        return self.ncbiId
    
    '''
    # name: retrieveGeneData
    # desc: Retrieves the probeset ID that corresponds to the given gene ID
    '''
    def retrieveGeneData(self, id):
        if(id == None):
            return
        if(efpConfig.DB_ANNO == None or efpConfig.DB_LOOKUP_TABLE == None): # annotations db not defined
            self.geneId = id  # if no lookup tables exists assume that id is valid
            self.probesetId = id
            return
        if(self.conn == None):
            self.connect()
        
        cursor = self.conn.cursor()

        ### OLD QUERY FORMAT ###########################
        #select_cmd = "SELECT t1.%s, t1.probeset FROM %s t1 WHERE (t1.probeset=%%s or t1.%s=%%s) AND t1.date=(SELECT MAX(t2.date) FROM %s t2)" % \
                     #(efpConfig.DB_LOOKUP_GENEID_COL, efpConfig.DB_LOOKUP_TABLE, efpConfig.DB_LOOKUP_GENEID_COL, efpConfig.DB_LOOKUP_TABLE)
        #################################################

        # Altered query to work with the new table, using 'ORDER BY date DESC' to get most recent entry
        select_cmd = "SELECT %s, probeset FROM %s WHERE (probeset=%%s or %s=%%s) ORDER BY date DESC" % \
                     (efpConfig.DB_LOOKUP_GENEID_COL, efpConfig.DB_LOOKUP_TABLE, efpConfig.DB_LOOKUP_GENEID_COL)


        cursor.execute(select_cmd,(id, id))
        row = cursor.fetchall()
        cursor.close()
        if len(row) > 0:
           self.geneId = row[0][0]
           self.probesetId = row[0][1]
#       else:
#          self.geneId = id  # if not found assume correct??? help with switching between data sets with and without a lookup db and table
#          self.probesetId = id
        return

    '''
    # name: ncbiToGeneId
    # desc: Returns the AGI corresponding to the NCBI gi accession
    # notes: NCBI gi accession comes from NCBI Linkout. Need to check whether NCBI gi accession is a NCBI GeneID or NCBI RefSeq.
    '''
    def ncbiToGeneId(self, ncbi_gi):
        if (ncbi_gi == None):
            return None
        if(efpConfig.DB_ANNO == None or efpConfig.DB_NCBI_GENE_TABLE == None): # ncbi lookup db not defined
            return None
        if(self.conn == None):
            self.connect()
        
        cursor = self.conn.cursor()
        
        select_cmd = "SELECT t1.%s FROM %s t1 WHERE t1.geneid=%%s or t1.protid=%%s" % (efpConfig.DB_NCBI_GENEID_COL, efpConfig.DB_NCBI_GENE_TABLE)
        cursor.execute(select_cmd,(ncbi_gi))
        row = cursor.fetchall()
        cursor.close()
        if len(row) != 0:
            self.geneId = row[0][0]
            self.ncbiId = ncbi_gi
        return

    def getAnnotation(self):
        if(efpConfig.DB_ANNO == None or efpConfig.DB_ANNO_TABLE == None): # annotations db not defined
            return None
        if(self.annotation == None):
            if(self.conn == None):
                self.connect()
               
            # Return the annotation and alias for a given geneId
            cursor = self.conn.cursor()
            select_cmd = "SELECT annotation FROM %s WHERE %s=%%s AND date = (SELECT MAX(date) FROM %s)" % (efpConfig.DB_ANNO_TABLE, efpConfig.DB_ANNO_GENEID_COL, efpConfig.DB_ANNO_TABLE)
            cursor.execute(select_cmd, (self.geneId,));
            result = cursor.fetchone()
            if result != None:
                self.annotation = result[0]
                cursor.close()
                splitter = re.compile('__')
                items = splitter.split(self.annotation)
                splitter = re.compile('_')
                aliases = splitter.split(items[0])
                if len(items) == 1:
                    aliases[0] = ''
                self.alias = aliases[0]
        return self.annotation
    
    def getSequence(self):
        if(efpConfig.DB_ORTHO == None): # annotations db not defined
            return None
        if(self.connOrtho == None):
            self.connectOrthoDB()   
        cursor = self.connOrtho.cursor()
        select_cmd = "SELECT sequence FROM %s WHERE gene = %%s" % (efpConfig.spec_names[efpConfig.species].lower())
        cursor.execute(select_cmd, (self.getGeneId()))
        seq = cursor.fetchone()
        if (seq == None):
            return None
        return seq[0]
    
    def getOrthologs(self, spec1, spec2):
        if(efpConfig.DB_ORTHO == None): # annotations db not defined
            return None
        if(self.connOrtho == None):
            self.connectOrthoDB()   
        cursor = self.connOrtho.cursor()
        
        scc_probesets = {}
        scc_genes = {}
        align_probesets = {}

        #selecting queries from the orthologs db for spec2 GENE IDs
        select_cmd = "SELECT t2.Gene_A, t3.sequence, t2.SCC_Value, t2.Probeset_A FROM orthologs_scc t2 LEFT JOIN %s t3 ON t3.gene = t2.Gene_A WHERE t2.Probeset_B = %%s AND t2.Genome_A = %%s AND t2.Genome_B = %%s" % (efpConfig.spec_names[spec2].lower()) + \
                     " UNION SELECT t2.Gene_B, t3.sequence, t2.SCC_Value, t2.Probeset_B FROM orthologs_scc t2 LEFT JOIN %s t3 ON t3.gene = t2.Gene_A WHERE t2.Probeset_A = %%s AND t2.Genome_B = %%s AND t2.Genome_A = %%s" % (efpConfig.spec_names[spec2].lower())
        cursor.execute(select_cmd, (self.getProbeSetId(), spec2, spec1, self.getProbeSetId(), spec2, spec1))
        rows = cursor.fetchall()
        
        for row in rows:
            gene = row[0]
            gene = efpConfig.spec_names[spec2]+ '_' + gene
            seq = row[1]
            if(seq != None):
                align_probesets[gene] = seq
            scc = row[2]
            probeset = [row[3]]
            scc_genes[row[3]] = row[0]
            if scc in scc_probesets:
                scc_probesets[scc].extend(probeset)
            else:
                scc_probesets[scc] = list()
                scc_probesets[scc].extend(probeset)
        cursor.close()
        return scc_genes, scc_probesets, align_probesets
    
    def getAlias(self):
        if(self.alias == None):
            self.getAnnotation()
        return self.alias
    
    def connect (self):
        try:
            self.conn = MySQLdb.connect (host = efpConfig.DB_HOST, port = efpConfig.DB_PORT, user = efpConfig.DB_USER, passwd = efpConfig.DB_PASSWD, db = efpConfig.DB_ANNO)
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

    def connectOrthoDB (self):
        try:
            self.connOrtho = MySQLdb.connect (host = efpConfig.DB_HOST, port = efpConfig.DB_PORT, user = efpConfig.DB_USER, passwd = efpConfig.DB_PASSWD, db = efpConfig.DB_ORTHO)
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])


class Gene_ATX (Gene):
    def __init__(self, id):
        Gene.__Init(self, id)
        self.geneId = self.checkGene(id)
        
    '''
    # name: checkGene
    # desc: Searchs for At-TAX geneId    
    '''
    def checkGene(self, gene):
        if(gene == None):
            return None
        gene = re.sub("t", "T", gene)
        gene = re.sub("g", "G", gene)
        file = open('%s/geneid.txt' % efpConfig.dataDir)
        if gene+'\n' not in file:
            file.close()
            return None
        else:
            file.close()
            return gene
