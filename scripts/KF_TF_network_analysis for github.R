

library(WGCNA)

setwd("C:/Data/TF study EFP")
OutputDir <- c("C:/Data/TF study EFP")

tag <- c("KF_TFs_")
myTOMType <- "KF TFs" # "unsigned"

options(stringsAsFactors = FALSE) 

KFData = read.csv("ForEFP_TFsSel4.csv")
dim(KFData)
names(KFData)
KFNames<-KFData[,1:3]
row.names(KFData)<-KFData[,1]
KFData<-KFData[,-(1:3)]
head(KFData)

datExpr0 = as.data.frame(t(KFData))

gsg = goodSamplesGenes(datExpr0, verbose = 3)
gsg$allOK 

#===================================================================================== # 
# phylogeny
#===================================================================================== 

sampleTree = hclust(dist(datExpr0), method = "average")

par(cex = 0.6); par(mar = c(0,4,2,0)) 
plot(sampleTree, main = "Sample clustering to detect outliers", sub="", xlab="", cex.lab = 1.5,cex.axis = 1.5, cex.main = 2) 

traitData = read.csv("MetaData.csv"); 
dim(traitData) 
names(traitData) 

# Trait data needs to be NUMERIC 

KFSamples = rownames(datExpr0);

cbind(KFSamples, allTraits$Name); 
datTraits = allTraits; 
rownames(datTraits) = KFSamples 
datTraits<-datTraits[,-1]
head(datTraits)

#===================================================================================== # 
# Code chunk # Networks
#===================================================================================== 


powers = c(c(1:10), seq(from = 12, to=20, by=2))

sft = pickSoftThreshold(datExpr0, powerVector = powers, verbose = 8)

par(mfrow = c(1,2));
cex1 = 0.9;
plot(sft$fitIndices[,1], -sign(sft$fitIndices[,3])*sft$fitIndices[,2],
xlab="Soft Threshold (power)",ylab="Scale Free Topology Model Fit,signed R^2",type="n",
main = paste("Scale independence"))


text(sft$fitIndices[,1], -sign(sft$fitIndices[,3])*sft$fitIndices[,2],
labels=powers,cex=cex1,col="red");
# this line corresponds to using an R^2

abline(h=0.90,col="red")

plot(sft$fitIndices[,1], sft$fitIndices[,5],
xlab="Soft Threshold (power)",ylab="Mean Connectivity", type="n",
main = paste("Mean connectivity"))
text(sft$fitIndices[,1], sft$fitIndices[,5], labels=powers, cex=cex1,col="red")


net = blockwiseModules(datExpr0, power = 6,
TOMType = "unsigned", minModuleSize = 30,
reassignThreshold = 0, mergeCutHeight = 0.25,
numericLabels = TRUE, pamRespectsDendro = FALSE,
saveTOMs = TRUE,
saveTOMFileBase = "femaleMouseTOM",
verbose = 3)

sizeGrWindow(12, 9)

# Convert labels to colors for plotting
mergedColors = labels2colors(net$colors)
# Plot the dendrogram and the module colors underneath

plotDendroAndColors(net$dendrograms[[1]], mergedColors[net$blockGenes[[1]]],
"Module colors",
dendroLabels = FALSE, hang = 0.03,
addGuide = TRUE, guideHang = 0.05)

moduleLabels <- net$colors
moduleColors <- labels2colors(net$colors)
MEs <- net$MEs;
geneTree <- net$dendrograms[[1]];

### line up the expression vs trait 

# Define numbers of genes and samples

nGenes <- ncol(datExpr0)
nSamples <- nrow(datExpr0)

# Recalculate MEs with color labels (calculates EigenValues for each gene)
MEs0 <- moduleEigengenes(datExpr0, moduleColors)$eigengenes
MEs <- orderMEs(MEs0)
moduleTraitCor <- cor(MEs,datTraits, use = "p");
moduleTraitPvalue <- corPvalueStudent(moduleTraitCor, nSamples)

par(mar = c(6, 8.5, 3, 3))

# Will display correlations and their p-values
textMatrix <- paste(signif(moduleTraitCor, 2), " (", signif(moduleTraitPvalue, 1), ")", sep = "")
dim(textMatrix) <- dim(moduleTraitCor)

rownames(textMatrix) <-rownames(moduleTraitCor)
colnames(textMatrix) <- colnames(datTraits)

substring(names(MEs),3,length(names(MEs))),
labeledHeatmap(Matrix = moduleTraitCor,
               xLabels = colnames(datTraits),
               yLabels = names(MEs),
               ySymbols = names(MEs),
               colorLabels = FALSE,
               colors = blueWhiteRed(50),
               #textMatrix = textMatrix,
               setStdMargins = FALSE,
               #cex.text = 0.18,
               #cex.lab.y = 0.22,
               zlim = c(-1,1),
               main = paste0(myTOMType," Module-trait relationships"))

ModuleTab<-table(moduleColors)

write.table(ModuleTab,"ModuleTable.txt",sep="\t")


#### TOM matrix

TOM = TOMsimilarityFromExpr(datExpr0, power = 6);

dissTOM = 1-TOMsimilarityFromExpr(datExpr0, power = 6);
# Transform dissTOM with a power to make moderately strong connections more visible in the heatmap
plotTOM = dissTOM^7;

# Set diagonal to NA for a nicer plot
diag(plotTOM) = NA;
sizeGrWindow(9,9)
TOMplot(plotTOM, geneTree, moduleColors, main = "Network heatmap plot, all genes")



### Eigen factors

# Recalculate module eigengenes
MEs = moduleEigengenes(datExpr0, moduleColors)$eigengenes

# Isolate weight
Flower = as.data.frame(datTraits$Flower);
names(Flower) = "Flower"

# Add the weight to existing module eigengenes
MET = orderMEs(cbind(MEs, Flower))

# Plot the relationships among the eigengenes and the trait
#sizeGrWindow(5,7.5);
par(cex = 0.9)
plotEigengeneNetworks(MET, "", marDendro = c(0,4,1,2), marHeatmap = c(3,4,1,2), cex.lab = 0.8, xLabelsAngle
= 90)





# ------------------------------------------------------------------------------------
###  module analysis (in this instance Yellow module)
# ------------------------------------------------------------------------------------

# Define variable weight containing the weight column of datTrait
Root = as.data.frame(datTraits$Root);
names(Root) = "Root"
# names (colors) of the modules
modNames = substring(names(MEs), 3)

geneModuleMembership = as.data.frame(cor(datExpr0, MEs, use = "p"));
MMPvalue = as.data.frame(corPvalueStudent(as.matrix(geneModuleMembership), nSamples));

names(geneModuleMembership) = paste("MM", modNames, sep="");
names(MMPvalue) = paste("p.MM", modNames, sep="");

geneTraitSignificance = as.data.frame(cor(datExpr0, Root, use = "p"));
GSPvalue = as.data.frame(corPvalueStudent(as.matrix(geneTraitSignificance), nSamples));

names(geneTraitSignificance) = paste("GS.", names(Root), sep="");
names(GSPvalue) = paste("p.GS.", names(Root), sep="");


module = "yellow"
column = match(module, modNames);
moduleGenes = moduleColors==module;
sizeGrWindow(7, 7);
par(mfrow = c(1,1));
verboseScatterplot(abs(geneModuleMembership[moduleGenes, column]),
abs(geneTraitSignificance[moduleGenes, 1]),
xlab = paste("Module Membership in", module, "module"),
ylab = "Gene significance for root",
main = paste("Module membership vs. gene significance\n"),
cex.main = 1.2, cex.lab = 1.2, cex.axis = 1.2, col = module)

names(datExpr0)[moduleColors=="yellow"]

temp<-cbind(KFNames,moduleColors)

write.table(temp,"ModuleColours.txt", sep="\t")

# ------------------------------------------------------------------------------------
### Exporting modules to cytoscape
# ------------------------------------------------------------------------------------


probes = names(datExpr0)
inModule = is.finite(match(moduleColors, module));
modProbes = probes[inModule];
modGenes = modProbes 
# Select the corresponding Topological Overlap
modTOM = TOM[inModule, inModule];
dimnames(modTOM) = list(modProbes, modProbes)


# Export the network into edge and node list files Cytoscape can read
cyt = exportNetworkToCytoscape(modTOM,
edgeFile = paste("CytoscapeInput-edges-", paste(module, collapse="-"), ".txt", sep=""),
nodeFile = paste("CytoscapeInput-nodes-", paste(module, collapse="-"), ".txt", sep=""),
weighted = TRUE,
threshold = 0.02,
nodeNames = modProbes,
altNodeNames = modGenes,
nodeAttr = moduleColors[inModule]);

head(modTOM)

dim(modTOM)

# ------------------------------------------------------------------------------------
### top hub genes  
# ------------------------------------------------------------------------------------

#install.packages("igraph")
library("igraph")


colorh = moduleColors
hubs <- chooseTopHubInEachModule(datExpr0, moduleColors, power = 2, type = "signed")

hubs

#-------------------------------------------------------------------------------------------
###  connectivity
#-------------------------------------------------------------------------------------------

modules = "yellow"

inModule = is.finite(match(moduleColors, modules));
modProbes = probes[inModule];
modGenes = modProbes 
# Select the corresponding Topological Overlap
modTOM = TOM[inModule, inModule];
dimnames(modTOM) = list(modProbes, modProbes)

# Export the network into edge and node list files Cytoscape can read
cyt = exportNetworkToCytoscape(modTOM,
edgeFile = paste("CytoscapeInput-edges-", paste(modules, collapse="-"), ".txt", sep=""),
nodeFile = paste("CytoscapeInput-nodes-", paste(modules, collapse="-"), ".txt", sep=""),
weighted = TRUE,
threshold = 0.02,
nodeNames = modProbes,
altNodeNames = modGenes,
nodeAttr = moduleColors[inModule]);


YellowEdges<-read.table("CytoscapeInput-edges-yellow.txt",sep="\t",header=T)
YellowNodes<-read.table("CytoscapeInput-nodes-yellow.txt",sep="\t",header=T)

temp<-cbind(YellowNodes[,2:3], rep("NA", length=YellowNodes[,1]),rep("NA",length=YellowNodes[,1]))
colnames(temp)<-c("Gene", "Col", "Connect", "Freq")

YellowEdgescount<-YellowEdges[(YellowEdges$weight > 0.2),]

test1<-table(YellowEdgescount$fromNode)
test2<-table(YellowEdgescount$toNode)

 
for (i in 1:length(temp[,1])){

temp[i,3]<-sum(YellowEdges[YellowEdges$fromNode == YellowNodes[i,1],3])+ sum(YellowEdges[YellowEdges$toNode == YellowNodes[i,1],3])

temp[i,4]<-sum(na.omit(c(test1[YellowNodes[i,1]], test2[YellowNodes[i,1]])))
}

YellowConOut<-temp

YellowConOutN<-cbind(YellowConOut[,1:2],as.numeric(YellowConOut[,3])/length(YellowConOut[,3]),as.numeric(YellowConOut[,4])/length(YellowConOut[,4])*100)
colnames(YellowConOutN)<-colnames(YellowConOut)
YellowConOutNOrder<-YellowConOutN[order(-YellowConOutN[,3]),]

write.table(YellowConOutN,"Colconnect.txt")


#-----------------------------------------------------------------------------------------------------------








