import rhinoscriptsyntax as rs
import random as r
import math as m
from itertools import permutations

###################################################
######             Amina Bakunowicz          ######
######                MSc Thesis             ######
######                 UEL 2013              ######
######        NEURAL SELF-ORGANISING MAPS    ######
######          AND GENETIC ALGORITHM:       ######
######       EVOLVING 3D CELLULAR AUTOMATA   ######
######            ARCHITECTURAL MODEL        ######
######        (boxes only, no arch model)    ######
###################################################

# Global Variables for GA
initPOPCOUNT = rs.GetInteger("please enter the number of individuals?", 3, 3, 50)
GENERATIONS = rs.GetInteger("evolve over how many generations?", 1, 1, 500)
selectionChoice = rs.GetInteger("Selection type: if Goldberg Roulette, enter 1; if optimised random, enter 2; if optimised artificial, enter 3", 1, 1, 3)
geneLength = 4
MUTATION_RATE = 0.2
CROSSOVER_RATE = 1.0
FitnCoevRate = 5 # % by which a fitness componenet threshold should grow by with each gneration
minFitLevel = 7 # min % over the average fitness of the best individual that a potential parent should possess in order to become a parent

FLOORHEIGHT = 4

# Globals for CA

CAunitsX = 3 # Number of CA units along X
CAunitsY = 3 # Number of CA units along Y
CAunitsZ = 1 # Number of CA units along Z

widthCA = 17 #width of the CA unit

statesCAall = ["living", "working", "resting"]
GSratio = 1.618
POPmax = initPOPCOUNT * 1.6 # max size of a generation

# Global Variables for SOM

FNUM = CAunitsX*CAunitsY*CAunitsZ * 2 + 6 # Number of the parameters in the neural vector and it equals to the number of genes
uSPACE = CAunitsX * widthCA + 50  # Neural grid U-direction Spacing
vSPACE = CAunitsY * widthCA + 50  # Neural grid V-direction Spacing
neuron = [] # Neurons (map)
input = []
WINLEARN_RATE = 0.2


class Individual:
    def __init__(self, __id, _colour):
        # length of the chromosome 
        self.alleles = (0,1)
        self.geneNum = FNUM # number of genes and it equals to the number of the parameters in the neural vector
        self.geneLength = geneLength  # length of each gene 
        self.values = [] # This list will store all the genes (only used in body plan)
        self.chromLength = self.geneNum*self.geneLength  
        self.chromosome = self.makeChromosome()
        self.id = __id
        self.fitness = 0
        self.guid = None
        self.originIndiv = []
        self.colour = _colour
        self.clusterFitness = 0
        self.clusterIndList = []
        self.grid = None
        
    def makeChromosome(self):
        # local list is returned
        chrom = []
        for a in range(self.chromLength):
            chrom.append(r.choice(self.alleles))
        return chrom
    def mutate(self):
        
        # Change a piece of DNA
        errorPoint  = r.randrange(0, self.chromLength)
        if self.chromosome[errorPoint] == 0:
            self.chromosome[errorPoint] = 1
        else:
            self.chromosome[errorPoint] = 0
    def decode(self):
        
        # Set up a counter to access chromosone index.
        counter = 0
        localList = []
        
        # For each gene calculate the thisValue nd append to the list
        for g in range(self.geneNum):
            thisValue = 0
            for i in range(self.geneLength):
                if(self.chromosome[counter] == 1):
                    thisValue += m.pow(2, self.geneLength-i)
                counter += 1
            localList.append(thisValue)
            
        self.values = localList
        
    def drawBodyplan(self, id, gen, finished, statesCA, BetwGens):
        
        area = 0
        guid = []
        grid = []
        originsCA = []
        originsCAmodel = []
        CAmodelGuid =[]
        
        gridX = widthCA*CAunitsX + 80 # The spacing between individuals
        gridY = BetwGens # The spacing between generations
        
        # Set the origin point ready to draw an individual
        self.originIndiv = [gridX*id, gridY, 0]
        
        n = 0
        m = 0
        for z in range (CAunitsZ):
            for y in range (CAunitsY):
                for x in range (CAunitsX):
                    
                    # collects coordinates of each CA unit for the display original CA model
                    if id ==0 and gen == 0:
                        coordCAmodel = [x*widthCA, y*widthCA + BetwGens,z*FLOORHEIGHT]
                        originsCAmodel.append(coordCAmodel)
                        
                        
                    # move the origin for each CA unit by genes defined 2D vector
                    n += 2
                    coordCA = [self.originIndiv[0]+(x*widthCA) + (self.values[n + 4]/2), self.originIndiv[1]+(y*widthCA) + (self.values[n + 5]/2),z*FLOORHEIGHT]
                    originsCA.append(coordCA)
                    
                    planeOrigin = [self.originIndiv[0]+(x*widthCA), self.originIndiv[1]+(y*widthCA), z*FLOORHEIGHT]
                    # draw a rectangle of CA's grid for each unit on the ground
                    if z == 0:
                        myPlane = rs.PlaneFromFrame(planeOrigin, [widthCA,0,0], [0,widthCA,z*FLOORHEIGHT])
                        rect = rs.AddRectangle(myPlane, widthCA, widthCA)
                        rs.ObjectColor(rect, [80,80,80])
                        grid.append(rect)
                    
                    # creates a display line between the origing of the unit#s grid rectangle
                    # and an origin of the 3D box of the unit
                    m += 1
                    #if statesCA[m-1] != "void" and self.values[n + 4]!=0 and self.values[n + 5]!=0:
                        #line = rs.AddLine(planeOrigin,coordCA)
                        #rs.ObjectColor(line, [0,255,255])
        self.grid = grid[:]
        # goes through every unit of every individual and draws a appropriate
        # geometry depending on the state of the unit
        for i in range (len(statesCA)):
            
            # displays original CA model 
            if id ==0 and gen == 0:
                coordCAmodel = originsCAmodel[i]
                pt1 = [coordCAmodel[0], coordCAmodel[1], coordCAmodel[2]]
                pt2 = [pt1[0] + widthCA, pt1[1], pt1[2]]
                pt3 = [pt1[0] + widthCA, pt1[1] + widthCA, pt1[2]]
                pt4 = [pt1[0], pt1[1] + widthCA, pt1[2]]
                pt5 = [coordCAmodel[0], coordCAmodel[1], coordCAmodel[2] + FLOORHEIGHT]
                pt6 = [pt1[0] + widthCA, pt1[1], pt1[2] + FLOORHEIGHT]
                pt7 = [pt1[0] + widthCA, pt1[1] + widthCA, pt1[2] + FLOORHEIGHT]
                pt8 = [pt1[0], pt1[1] + widthCA, pt1[2] + FLOORHEIGHT]
                pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
                CAmodelBox =  rs.AddBox(pts)
                rs.MoveObject(CAmodelBox, [-1*(widthCA*CAunitsX + 300), 0,0])
                
                if statesCA[i] == "living":
                    rs.ObjectColor(CAmodelBox, [204,51,51])
                if statesCA[i] == "working":
                    rs.ObjectColor(CAmodelBox, [51,51,204])
                if statesCA[i] == "resting":
                    rs.ObjectColor(CAmodelBox, [51,204,51])
                CAmodelGuid.append(CAmodelBox)
            
            coordCA = originsCA[i]
            
            if statesCA[i] == "living":
                livingBox = self.drawLiving(coordCA)
                guid.append(livingBox)
                
            if statesCA[i] == "working":
                workingBox = self.drawWorking(coordCA)
                guid.append(workingBox)
                
            if statesCA[i] == "resting":
                restingBox = self.drawResting(coordCA)
                guid.append(restingBox)
                
        self.guid = guid[:]
        rs.ObjectColor(self.guid, self.colour)
        # colours population purple
        #rs.ObjectColor(self.guid, (102,51,255))
        
        # Assess the fitness: proximity of the boxes' centroids
        # within Moore neighborhood and min intersection volume
        # list originsCA[] has all origins of this individual's boxes. 
        self.assessFitness(gen)
        
        
    def assessFitness(self, gen):
        
        # fitness according to the proximity of the proportion of the box to 
        # Golden Section Ratio defined as a global variable GSratio
        GSfactor = 0
        
        # checks the ration of the width vs length of Living CA unit
        # and adds to fitness factor GSfactor depending on this ratio
        pt1 = [0, 0, 0]
        pt2 = [pt1[0] + self.values[0] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.values[0] + 3, pt1[1] + self.values[1] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.values[1] + 3, pt1[2]]
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioLiving = dst1/dst2
        else: ratioLiving = dst2/dst1
        GSfactor += 12/abs(ratioLiving-GSratio)
        
        # check the floor area of the Living CA unit
        pts = [pt1, pt2, pt3, pt4]
        srf = rs.AddSrfPt(pts)
        areaLiving = rs.Area(srf)
        rs.DeleteObject(srf)
        
        # checks the ration of the width vs length of Working CA unit
        # and adds to fitness factor GSfactor depending on this ratio
        pt1 = [0, 0, 0]
        pt2 = [pt1[0] + self.values[2] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.values[2] + 3, pt1[1] + self.values[3] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.values[3] + 3, pt1[2]]
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioWorking = dst1/dst2
        else: ratioWorking = dst2/dst1
        GSfactor += 12/abs(ratioWorking-GSratio)
        
        # check the floor area of the WOrking CA unit
        pts = [pt1, pt2, pt3, pt4]
        srf = rs.AddSrfPt(pts)
        areaWorking = rs.Area(srf)
        rs.DeleteObject(srf)
        
        # checks the ration of the width vs length of Resting CA unit
        # and adds to fitness factor GSfactor depending on this ratio
        pt1 = [0, 0, 0]
        pt2 = [pt1[0] + self.values[4] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.values[4] + 3, pt1[1] + self.values[5] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.values[5] + 3, pt1[2]]
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioResting = dst1/dst2
        else: ratioResting = dst2/dst1
        GSfactor += 12/abs(ratioResting-GSratio)
        
        # check the floor area of the Resting CA unit
        pts = [pt1, pt2, pt3, pt4]
        srf = rs.AddSrfPt(pts)
        areaResting = rs.Area(srf)
        rs.DeleteObject(srf)
        
        distances = 0
        areas = 0
        XXfactor = 0
        XXareasFactor = 0
        totalAreaFactor = 0
        distFactor = 0
        objects = []
        # fitness criteria keeps the neighboring boxes as close as possible 
        # maintaining the initial spatial arrangement 
        for z in range (CAunitsZ):
            for y in range (CAunitsY):
                for x in range (CAunitsX):
                    
                    # check the area of the CA unit and add it to the total area
                    index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                    boxThis = self.guid[index-1]
                    totalAreaFactor += rs.SurfaceArea(boxThis)[0]
                    
                    if x != 0 and y != 0 and x != CAunitsX-1 and y != CAunitsY - 1:
                        # determines its own box, its neighboring boxes and their centroids
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                        boxThis = self.guid[index-1]
                        if boxThis is not None: centroidThis = rs.SurfaceVolumeCentroid(boxThis)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x + 1
                        boxS = self.guid[index-1]
                        if boxThis is not None: centroidS = rs.SurfaceVolumeCentroid(boxS)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x + 2
                        boxSE = self.guid[index-1]
                        if boxThis is not None: centroidSE = rs.SurfaceVolumeCentroid(boxSE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 2
                        boxE = self.guid[index-1]
                        if boxThis is not None: centroidE = rs.SurfaceVolumeCentroid(boxE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x + 2
                        boxNE = self.guid[index-1]
                        if boxThis is not None: centroidNE = rs.SurfaceVolumeCentroid(boxNE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x + 1
                        boxN = self.guid[index-1]
                        if boxThis is not None: centroidN = rs.SurfaceVolumeCentroid(boxN)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x
                        boxNW = self.guid[index-1]
                        if boxThis is not None: centroidNW = rs.SurfaceVolumeCentroid(boxNW)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x
                        boxW = self.guid[index-1]
                        if boxThis is not None: centroidW = rs.SurfaceVolumeCentroid(boxW)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x
                        boxSW = self.guid[index-1]
                        if boxThis is not None: centroidSW = rs.SurfaceVolumeCentroid(boxSW)[0]
                        
                        # works out the sum of the distances between the neighbouring units
                        if centroidS is not None and centroidThis is not None: dist1 = rs.Distance(centroidThis,centroidS)
                        if centroidSE is not None and centroidThis is not None:dist2 = rs.Distance(centroidThis,centroidSE)
                        if centroidE is not None and centroidThis is not None:dist3 = rs.Distance(centroidThis,centroidE)
                        if centroidNE is not None and centroidThis is not None:dist4 = rs.Distance(centroidThis,centroidNE)
                        if centroidN is not None and centroidThis is not None:dist5 = rs.Distance(centroidThis,centroidN)
                        if centroidNW is not None and centroidThis is not None:dist6 = rs.Distance(centroidThis,centroidNW)
                        if centroidW is not None and centroidThis is not None:dist7 = rs.Distance(centroidThis,centroidW)
                        if centroidSW is not None and centroidThis is not None:dist8 = rs.Distance(centroidThis,centroidSW)
                        distances = dist1+dist2+dist3+dist4+dist5+dist6+dist7+dist8
                        distFactor += distances
                        
                        # works out the sum of the intersection areas of the neighbouring units
                        THISxS = rs.BooleanIntersection(boxThis,boxS, False)
                        if (THISxS != [] and THISxS is not None):
                            XXareasFactor += rs.SurfaceArea(THISxS)[0]
                            objects.append(THISxS)
                            #XXfactor += 100
                            
                        THISxSE = rs.BooleanIntersection(boxThis,boxSE, False)
                        if (THISxSE != [] and THISxSE is not None):
                            XXareasFactor += rs.SurfaceArea(THISxSE)[0]
                            objects.append(THISxSE)
                            #XXfactor += 100
                        
                        THISxE = rs.BooleanIntersection(boxThis,boxE, False)
                        if (THISxE != [] and THISxE is not None):
                            XXareasFactor += rs.SurfaceArea(THISxE)[0]
                            objects.append(THISxE)
                            #XXfactor += 100
                            
                        THISxNE = rs.BooleanIntersection(boxThis,boxNE, False)
                        if (THISxNE != [] and THISxNE is not None):
                            XXareasFactor += rs.SurfaceArea(THISxNE)[0]
                            objects.append(THISxNE)
                            #XXfactor += 100
                            
                        THISxN = rs.BooleanIntersection(boxThis,boxN, False)
                        if (THISxN != [] and THISxN is not None):
                            XXareasFactor += rs.SurfaceArea(THISxN)[0]
                            objects.append(THISxN)
                            #XXfactor += 100
                            
                        THISxNW = rs.BooleanIntersection(boxThis,boxNW, False)
                        if (THISxNW != [] and THISxNW is not None):
                            XXareasFactor += rs.SurfaceArea(THISxNW)[0]
                            objects.append(THISxNW)
                            #XXfactor += 100
                            
                        THISxW = rs.BooleanIntersection(boxThis,boxW, False)
                        if (THISxW != [] and THISxW is not None):
                            XXareasFactor += rs.SurfaceArea(THISxW)[0]
                            objects.append(THISxW)
                            #XXfactor += 100
                            
                        THISxSW = rs.BooleanIntersection(boxThis,boxSW, False)
                        if (THISxSW != [] and THISxSW is not None):
                            XXareasFactor += rs.SurfaceArea(THISxSW)[0]
                            objects.append(THISxSW)
                            #XXfactor += 100
                            
                        if objects != []:
                            rs.DeleteObjects(objects)
                        
                        
        if distFactor != 0: distFactor = 17000*CAunitsZ/distFactor
        if XXareasFactor  != 0: XXareasFactor = 150000*CAunitsZ/XXareasFactor
        totalAreaFactor = totalAreaFactor*0.017/CAunitsZ
        WRareaFactor = areaWorking/areaResting*110
        RLareaFactor = areaResting/areaLiving*110
        if GSfactor > 200: GSfactor = 200
        
        # In order to gain some fitness an individual (or a neuron) must have 
        # the components of the fitness factor defined accepted level. 
        # If one of the Fitness Factor constituents is below the 
        # defined threshold, its total fitness is written down to zero.
        if selectionChoice == 2 or selectionChoice == 3: 
            fitThreshold = gen*(FitnCoevRate) + 50
        else: fitThreshold = 0
        if distFactor>fitThreshold and XXareasFactor>fitThreshold and totalAreaFactor>fitThreshold and RLareaFactor>fitThreshold and WRareaFactor>fitThreshold and areaLiving >250 and GSfactor>fitThreshold:
            fitness = distFactor+ XXareasFactor + WRareaFactor + RLareaFactor + totalAreaFactor + GSfactor
            self.fitness = round(fitness,2)
        else:
            self.fitness = 0
        
    def dispalyText(self, id):
        loc1 = [self.originIndiv[0], self.originIndiv[1]-10, self.originIndiv[2]] 
        myText1 = rs.AddText(str(id), loc1, 5)
        rs.ObjectColor(myText1, [100,100,100])
        loc2 = [self.originIndiv[0], self.originIndiv[1]-3, self.originIndiv[2]] 
        myText2 = rs.AddText(str(self.fitness), loc2, 2)
        rs.ObjectColor(myText2, [255,0,0])
        return myText1, myText2
        
    def drawLiving(self, coordCA):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        pt2 = [pt1[0] + self.values[0] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.values[0] + 3, pt1[1] + self.values[1] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.values[1] + 3, pt1[2]]
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        pt6 = [pt1[0] + self.values[0] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        pt7 = [pt1[0] + self.values[0] + 3, pt1[1] + self.values[1] + 3, pt1[2] + FLOORHEIGHT]
        pt8 = [pt1[0], pt1[1] + self.values[1] + 3, pt1[2] + FLOORHEIGHT]
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        livingBox =  rs.AddBox(pts)
        return livingBox
        
    def drawWorking(self, coordCA):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        pt2 = [pt1[0] + self.values[2] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.values[2] + 3, pt1[1] + self.values[3] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.values[3] + 3, pt1[2]]
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        pt6 = [pt1[0] + self.values[2] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        pt7 = [pt1[0] + self.values[2] + 3, pt1[1] + self.values[3] + 3, pt1[2] + FLOORHEIGHT]
        pt8 = [pt1[0], pt1[1] + self.values[3] + 3, pt1[2] + FLOORHEIGHT]
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        workingBox =  rs.AddBox(pts)
        return workingBox
        
    def drawResting(self, coordCA):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        pt2 = [pt1[0] + self.values[4] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.values[4] + 3, pt1[1] + self.values[5] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.values[5] + 3, pt1[2]]
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        pt6 = [pt1[0] + self.values[4] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        pt7 = [pt1[0] + self.values[4] + 3, pt1[1] + self.values[5] + 3, pt1[2] + FLOORHEIGHT]
        pt8 = [pt1[0], pt1[1] + self.values[5] + 3, pt1[2] + FLOORHEIGHT]
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        restingBox =  rs.AddBox(pts)
        return restingBox

class Neuron:
    
    def __init__(self, _pos, _vec, _limbo, _id, _winnersList, _dist2winner, _closestWInner, _colour):
        self.pos = _pos
        self.vec = _vec
        self.guid = None
        self.limbo = _limbo
        self.id = _id
        self.isWinner = False
        self.fitness = 0
        self.winnersList = _winnersList
        self.dist2winner = _dist2winner
        self.closestWInner = _closestWInner
        self.colour = _colour
        self.grid = None

    def organise(self, neuron, input, i, winner, WINLEARN, LEARN, NEIGH):
        
        # Check if you're the winner or not...
        # If so adjust yourself according to WINLEARN
        if (self.id[0] == winner[0] and self.id[1] == winner[1]):
            
            self.isWinner = True
            
            # give a wiiner the colour of its input
            self.colour = input[i].colour
            
            
            for f in range(FNUM):
                dd = input[i].vec[f] - self.vec[f]
                self.limbo[f] = self.limbo[f] + dd * WINLEARN
                
        # If you were not the winner, check your distance in map 2d space
        # And adjust according to the distance and the LEARN value
        else:
            
            dist = m.sqrt(m.pow((self.id[0] - winner[0]),2) + m.pow((self.id[1] - winner[1]),2))
            #print dist, NEIGH
            # If we're close enough apply 'positive' feedback
            if (dist <= NEIGH) :
                for f in range(FNUM):
                    dd = input[i].vec[f] - self.vec[f] 
                    self.limbo[f] =  self.limbo[f] + dd*(LEARN/dist)
                
                self.winnersList.append(winner)
                self.dist2winner.append(dist)
                
                
                
            # Otherwise apply 'inhibitory' feedback
            else:
                for f in range(FNUM):
                    dd = input[i].vec[f] - self.vec[f] 
                    self.limbo[f] =  self.limbo[f] - dd*(LEARN/dist) *.2
                    
    def update(self, gen, statesCA, population, neuron):
        
        if (self.guid!=None): rs.DeleteObjects(self.guid)
        if (self.grid!=None): rs.DeleteObjects(self.grid)
        for f in range(FNUM):
            self.vec[f] = self.limbo[f]
            
        self.drawNeuronBodyplan(gen, statesCA)
        
        # find which winner is closest and give that neuron a colour that
        # represents the winner's cluster
        
        smallestDistance = 10000000
        bestID = 0
        if self.dist2winner != [] and self.winnersList != [] and self.isWinner == False:
            for i in range(len(self.dist2winner)):
                if(self.dist2winner[i] < smallestDistance):
                    closestID = i
                    smallestDistance = self.dist2winner[i]
                
            closestWinner = self.winnersList[closestID]
            
            # find the u and v indexes of the closest winner and
            # give its colour to the neuron
            cwU = closestWinner[0]
            cwV = closestWinner[1]
            
            col = neuron[cwU][cwV].colour
            self.colour = col
            rs.ObjectColor(self.guid,col)
        
        if(self.isWinner): 
            rs.ObjectColor(self.guid, self.colour)
            rad = CAunitsX*widthCA
            pos = [self.pos[0]+rad/2, self.pos[1]+rad/2, self.pos[2]]
            circle = rs.AddCircle(pos, rad*0.75)
            rs.ObjectColor(circle, self.colour)
            rs.ObjectLinetype(circle, "Dashed") 
        else: circle = None
        #if(self.isWinner): rs.ObjectColor(self.guid, [255,0,0])
        
        # Reset our winner status to false again
        self.isWinner = False
        return circle
        
    def drawNeuronBodyplan(self, gen, statesCA):
        area = 0
        guid = []
        grid = []
        originsCA = []
        originsCAmodel = []
        CAmodelGuid =[]
            
        
        n = 0
        m = 0
        for z in range (CAunitsZ):
            for y in range (CAunitsY):
                for x in range (CAunitsX):
                    
                    # move the origin for each CA unit by genes defined 2D vector
                    n += 2
                    coordCA = [self.pos[0]+(x*widthCA) + (self.vec[n + 4]/2), self.pos[1]+(y*widthCA) + (self.vec[n + 5]/2),z*FLOORHEIGHT]
                    originsCA.append(coordCA)
                    
                    planeOrigin = [self.pos[0]+(x*widthCA), self.pos[1]+(y*widthCA), z*FLOORHEIGHT]
                    # draw a rectangle of CA's grid for each unit on the ground
                    if z == 0:
                        myPlane = rs.PlaneFromFrame(planeOrigin, [widthCA,0,0], [0,widthCA,z*FLOORHEIGHT])
                        rect = rs.AddRectangle(myPlane, widthCA, widthCA)
                        rs.ObjectColor(rect, [80,80,80])
                        grid.append(rect)
                        
                    # creates a display line between the origing of the unit#s grid rectangle
                    # and an origin of the 3D box of the unit
                    #m += 1
                    #if statesCA[m-1] != "void" and self.vec[n + 4]!=0 and self.vec[n + 5]!=0:
                        #line = rs.AddLine(planeOrigin,coordCA)
                        #rs.ObjectColor(line, [0,255,255])
        self.grid = grid[:]
        # goes through every unit of every individual and draws the appropriate
        # geometry depending on the state of the unit
        for i in range (len(statesCA)):
            
            coordCA = originsCA[i]
            
            if statesCA[i] == "living":
                livingBox = self.drawNeuronLiving(coordCA)
                guid.append(livingBox)
                
            if statesCA[i] == "working":
                workingBox = self.drawNeuronWorking(coordCA)
                guid.append(workingBox)
                
            if statesCA[i] == "resting":
                restingBox = self.drawNeuronResting(coordCA)
                guid.append(restingBox)
                
        self.guid = guid[:]
        
        # Assess the fitness: proximity of the boxes' centroids
        # within Moore neighborhood and min intersection volume
        # list originsCA[] has all origins of this individual's boxes. 
        #self.assessNeuronFitness(gen)
        
    def assessNeuronFitness(self, gen):
        
        # fitness according to the proximity of the proportion of the box to 
        # Golden Section Ratio defined as a global variable GSratio
        GSfactor = 0
        
        # checks the ration of the width vs length of Living CA unit
        # and adds to fitness factor GSfactor depending on this ratio
        pt1 = [0, 0, 0]
        pt2 = [pt1[0] + self.vec[0] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.vec[0] + 3, pt1[1] + self.vec[1] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.vec[3] + 3, pt1[2]]
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioLiving = dst1/dst2
        else: ratioLiving = dst2/dst1
        GSfactor += 10/abs(ratioLiving-GSratio)
        
        # check the floor area of the Living CA unit
        pts = [pt1, pt2, pt3, pt4]
        srf = rs.AddSrfPt(pts)
        areaLiving = rs.Area(srf)
        rs.DeleteObject(srf)
        
        # checks the ration of the width vs length of Working CA unit
        # and adds to fitness factor GSfactor depending on this ratio
        pt1 = [0, 0, 0]
        pt2 = [pt1[0] + self.vec[2] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.vec[2] + 3, pt1[1] + self.vec[3] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.vec[3] + 3, pt1[2]]
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioWorking = dst1/dst2
        else: ratioWorking = dst2/dst1
        GSfactor += 10/abs(ratioWorking-GSratio)
        
        # check the floor area of the WOrking CA unit
        pts = [pt1, pt2, pt3, pt4]
        srf = rs.AddSrfPt(pts)
        areaWorking = rs.Area(srf)
        rs.DeleteObject(srf)
        
        # checks the ration of the width vs length of Resting CA unit
        # and adds to fitness factor GSfactor depending on this ratio
        pt1 = [0, 0, 0]
        pt2 = [pt1[0] + self.vec[4] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.vec[4] + 3, pt1[1] + self.vec[5] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.vec[5] + 3, pt1[2]]
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioResting = dst1/dst2
        else: ratioResting = dst2/dst1
        GSfactor +=10/abs(ratioResting-GSratio)
        
        # check the floor area of the Resting CA unit
        pts = [pt1, pt2, pt3, pt4]
        srf = rs.AddSrfPt(pts)
        areaResting = rs.Area(srf)
        rs.DeleteObject(srf)
        
        distances = 0
        areas = 0
        XXfactor = 0
        XXareasFactor = 0
        totalAreaFactor = 0
        distFactor = 0
        objects = []
        # fitness criteria keeps the neighboring boxes as close as possible 
        # maintaining the initial spatial arrangement 
        for z in range (CAunitsZ):
            for y in range (CAunitsY):
                for x in range (CAunitsX):
                    
                    # check the area of the CA unit and add it to the total area
                    index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                    boxThis = self.guid[index-1]
                    totalAreaFactor += rs.SurfaceArea(boxThis)[0]
                    
                    if x != 0 and y != 0 and x != CAunitsX-1 and y != CAunitsY - 1:
                        # determines its own box, its neighboring boxes and their centroids
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                        boxThis = self.guid[index-1]
                        if boxThis is not None: centroidThis = rs.SurfaceVolumeCentroid(boxThis)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x + 1
                        boxS = self.guid[index-1]
                        if boxThis is not None: centroidS = rs.SurfaceVolumeCentroid(boxS)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x + 2
                        boxSE = self.guid[index-1]
                        if boxThis is not None: centroidSE = rs.SurfaceVolumeCentroid(boxSE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 2
                        boxE = self.guid[index-1]
                        if boxThis is not None: centroidE = rs.SurfaceVolumeCentroid(boxE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x + 2
                        boxNE = self.guid[index-1]
                        if boxThis is not None: centroidNE = rs.SurfaceVolumeCentroid(boxNE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x + 1
                        boxN = self.guid[index-1]
                        if boxThis is not None: centroidN = rs.SurfaceVolumeCentroid(boxN)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x
                        boxNW = self.guid[index-1]
                        if boxThis is not None: centroidNW = rs.SurfaceVolumeCentroid(boxNW)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x
                        boxW = self.guid[index-1]
                        if boxThis is not None: centroidW = rs.SurfaceVolumeCentroid(boxW)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x
                        boxSW = self.guid[index-1]
                        if boxThis is not None: centroidSW = rs.SurfaceVolumeCentroid(boxSW)[0]
                        
                        # works out the sum of the distances between the neighbouring units
                        if centroidS is not None and centroidThis is not None: dist1 = rs.Distance(centroidThis,centroidS)
                        if centroidSE is not None and centroidThis is not None:dist2 = rs.Distance(centroidThis,centroidSE)
                        if centroidE is not None and centroidThis is not None:dist3 = rs.Distance(centroidThis,centroidE)
                        if centroidNE is not None and centroidThis is not None:dist4 = rs.Distance(centroidThis,centroidNE)
                        if centroidN is not None and centroidThis is not None:dist5 = rs.Distance(centroidThis,centroidN)
                        if centroidNW is not None and centroidThis is not None:dist6 = rs.Distance(centroidThis,centroidNW)
                        if centroidW is not None and centroidThis is not None:dist7 = rs.Distance(centroidThis,centroidW)
                        if centroidSW is not None and centroidThis is not None:dist8 = rs.Distance(centroidThis,centroidSW)
                        distances = dist1+dist2+dist3+dist4+dist5+dist6+dist7+dist8
                        distFactor += distances
                        
                        # works out the sum of the intersection areas of the neighbouring units
                        THISxS = rs.BooleanIntersection(boxThis,boxS, False)
                        if (THISxS != [] and THISxS is not None):
                            XXareasFactor += rs.SurfaceArea(THISxS)[0]
                            objects.append(THISxS)
                            #XXfactor += 100
                            
                        THISxSE = rs.BooleanIntersection(boxThis,boxSE, False)
                        if (THISxSE != [] and THISxSE is not None):
                            XXareasFactor += rs.SurfaceArea(THISxSE)[0]
                            objects.append(THISxSE)
                            #XXfactor += 100
                        
                        THISxE = rs.BooleanIntersection(boxThis,boxE, False)
                        if (THISxE != [] and THISxE is not None):
                            XXareasFactor += rs.SurfaceArea(THISxE)[0]
                            objects.append(THISxE)
                            #XXfactor += 100
                            
                        THISxNE = rs.BooleanIntersection(boxThis,boxNE, False)
                        if (THISxNE != [] and THISxNE is not None):
                            XXareasFactor += rs.SurfaceArea(THISxNE)[0]
                            objects.append(THISxNE)
                            #XXfactor += 100
                            
                        THISxN = rs.BooleanIntersection(boxThis,boxN, False)
                        if (THISxN != [] and THISxN is not None):
                            XXareasFactor += rs.SurfaceArea(THISxN)[0]
                            objects.append(THISxN)
                            #XXfactor += 100
                            
                        THISxNW = rs.BooleanIntersection(boxThis,boxNW, False)
                        if (THISxNW != [] and THISxNW is not None):
                            XXareasFactor += rs.SurfaceArea(THISxNW)[0]
                            objects.append(THISxNW)
                            #XXfactor += 100
                            
                        THISxW = rs.BooleanIntersection(boxThis,boxW, False)
                        if (THISxW != [] and THISxW is not None):
                            XXareasFactor += rs.SurfaceArea(THISxW)[0]
                            objects.append(THISxW)
                            #XXfactor += 100
                            
                        THISxSW = rs.BooleanIntersection(boxThis,boxSW, False)
                        if (THISxSW != [] and THISxSW is not None):
                            XXareasFactor += rs.SurfaceArea(THISxSW)[0]
                            objects.append(THISxSW)
                            #XXfactor += 100
                            
                        if objects != []:
                            rs.DeleteObjects(objects)
                        
                        
        if distFactor != 0: distFactor = 17000*CAunitsZ/distFactor
        if XXareasFactor  != 0: XXareasFactor = 150000*CAunitsZ/XXareasFactor
        totalAreaFactor = totalAreaFactor*0.017/CAunitsZ
        WRareaFactor = areaWorking/areaResting*110
        RLareaFactor = areaResting/areaLiving*110
        if GSfactor > 200: GSfactor = 200
        #print distFactor, XXareasFactor, totalAreaFactor, GSfactor, WRareaFactor, RLareaFactor
        # In order to gain some fitness an individual (or a neuron) must have 
        # the components of the fitness factor defined accepted level. 
        # If one of the Fitness Factor constituents is below the 
        # defined threshold, its total fitness is written down to zero.
        if selectionChoice == 2 or selectionChoice == 3: 
            fitThreshold = gen*(FitnCoevRate) + 50
        else: fitThreshold = 0
        if distFactor>fitThreshold and XXareasFactor>fitThreshold and totalAreaFactor>fitThreshold and RLareaFactor>fitThreshold and WRareaFactor>fitThreshold and areaLiving > 250 and GSfactor>fitThreshold:
            fitness = distFactor+ XXareasFactor + WRareaFactor + RLareaFactor + totalAreaFactor + GSfactor
            self.fitness = round(fitness,2)
        else:
            self.fitness = 0
        
    def dispalyNeuronText(self, id):
        loc1 = [self.pos[0], self.pos[1]-10, self.pos[2]] 
        myText = rs.AddText(str(id), loc1, 5)
        rs.ObjectColor(myText, [100,100,100])
        loc2 = [self.pos[0], self.pos[1]-3, self.pos[2]] 
        myText = rs.AddText(str(self.fitness), loc2, 2)
        rs.ObjectColor(myText, [255,0,0])
        
    def drawNeuronLiving(self, coordCA):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        pt2 = [pt1[0] + self.vec[0] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.vec[0] + 3, pt1[1] + self.vec[1] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.vec[1] + 3, pt1[2]]
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        pt6 = [pt1[0] + self.vec[0] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        pt7 = [pt1[0] + self.vec[0] + 3, pt1[1] + self.vec[1] + 3, pt1[2] + FLOORHEIGHT]
        pt8 = [pt1[0], pt1[1] + self.vec[1] + 3, pt1[2] + FLOORHEIGHT]
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        livingBox =  rs.AddBox(pts)
        return livingBox
        
    def drawNeuronWorking(self, coordCA):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        pt2 = [pt1[0] + self.vec[2] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.vec[2] + 3, pt1[1] + self.vec[3] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.vec[3] + 3, pt1[2]]
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        pt6 = [pt1[0] + self.vec[2] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        pt7 = [pt1[0] + self.vec[2] + 3, pt1[1] + self.vec[3] + 3, pt1[2] + FLOORHEIGHT]
        pt8 = [pt1[0], pt1[1] + self.vec[3] + 3, pt1[2] + FLOORHEIGHT]
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        workingBox =  rs.AddBox(pts)
        return workingBox
        
    def drawNeuronResting(self, coordCA):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        pt2 = [pt1[0] + self.vec[4] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.vec[4] + 3, pt1[1] + self.vec[5] + 3, pt1[2]]
        pt4 = [pt1[0], pt1[1] + self.vec[5] + 3, pt1[2]]
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        pt6 = [pt1[0] + self.vec[4] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        pt7 = [pt1[0] + self.vec[4] + 3, pt1[1] + self.vec[5] + 3, pt1[2] + FLOORHEIGHT]
        pt8 = [pt1[0], pt1[1] + self.vec[5] + 3, pt1[2] + FLOORHEIGHT]
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        restingBox =  rs.AddBox(pts)
        return restingBox

class Input:
    
    def __init__(self, _pos, _vec, _guid, _colour):
        self.pos = _pos
        self.vec = _vec
        self.guid = _guid
        self.colour = _colour
    
    def findWinner(self, neuron,population):
        
        win_dif = 100000
        winner = []
        for u in range(int(round(len(population)*1.5))):
            for v in range(int(round(len(population)*1.5))):
                difference = 0
                
                # Eucliden Distance in feature space:
                for f in range(FNUM):
                    difference += (m.pow((self.vec[f] - neuron[u][v].vec[f]),2)) 
                difference = m.sqrt(difference)
                
                if (difference < win_dif):
                    win_dif = difference
                    winner = [u,v]
        
        # Return 2d index of winner on map
        return winner

def main():

    # The main list of individuals
    population = []
    oldPop = []
    
    rs.Command("SelAll")
    rs.Command("Delete")
    
    rs.AddLayer("fitness curves")
    # Setup a text file for data
    myFile = open('fitnessHistory.txt', 'w')
    
    # Initialise GA
    for i in range(initPOPCOUNT):
        colour = [0,0,0]
        population.append(Individual(i, colour))
        
    # Run the process
    runGA(population, oldPop, myFile)
    
    # Close the text file
    myFile.close()

def runGA(population, oldPop, myFile):
    
    BetwGens = 0
    # generate two lists that contain all possible cobinations of genes and
    # their corresponding values. These will be used in ReverseDecode function
    # to convert self.values of SOM neurons into chromosomes:
    list0 = []
    list1 = []
    bestPts = []
    allGeneslist = binaryList(geneLength)
    for m in range (geneLength):
        list0.append(0)
        list1.append(1)
    allGeneslist.append(list0)
    allGeneslist.append(list1)
    allValueslist = binaryDecode(allGeneslist)
            
    # calculate a random gene decode number to be used for the creations
    # of the initial SOM
    decodeNum = 6
    
    ####################################
    #########     CA model    ##########
    ####################################
    
    # run CA for population[i]; generate two lists containing info for each CA unit: 
    # originsCA[] and statesCA[] and pass this info to drawBodyplan function.
    # In this algorithm the lists are given already
    statesCA = []
    for z in range (CAunitsZ):
        for y in range (CAunitsY):
            for x in range (CAunitsX):
                k = r.random()
                if k > 10 and (x == 0 or y == 0 or x == CAunitsX-1 or y == CAunitsY - 1):
                    statesCA.append(statesCAall[3]) # creates void cell on outer layer of the CA model
                else:
                    s = r.randrange(0,3)
                    statesCA.append(statesCAall[s]) # assigns states to other cells
                    
    
    
    #####################################
    ##########   GA Body Plan ########### 
    #####################################
    
    EVOLUTION = True
    while(EVOLUTION == True):
        newPopcount = len(population)
        for g in range(GENERATIONS):
            print "generation", g+1,":"
            myFile.write("Generation: ")
            myFile.write(str(g+1) + "\n")
            # Reset values
            totalFitness = 0
            uvCurves = []
            uPoints = []
            uPointsInd = []
            neuron = []
            input = [] # Inputs (samples)
            allIndivNeurons = []
            rs.EnableRedraw(False)
            finished = False
            
            oldPopcount = newPopcount
            newPopcount = len(population)
            
            if newPopcount > 1:
                # sets the radius according to the SOM size, that in its turn depends 
                # on the length of each generation
                UMAX = oldPopcount # Map U size of next generations
                VMAX = oldPopcount # Map V size of next generations
                    
                # calculates the distance along Y between generations
                BetwGens = (VMAX + 2)* 1.5 * (CAunitsY*widthCA + widthCA*2) + BetwGens
                step = round(200/newPopcount)-10
                # Create the generation
                for i in range(newPopcount):
                    # Look at the current population. Sum up all of the fitness values.
                    # checks if an indiv has fitness
                    population[i].decode()
                    population[i].drawBodyplan(i, g, finished, statesCA, BetwGens)
                    
                    # record fitness values as points at certain heights above individuals
                    # Fitness Surface will use the points to visualise how the fitness changes in SOM
                    x = population[i].originIndiv[0] + CAunitsX*widthCA/2
                    y = population[i].originIndiv[1] + CAunitsY*widthCA/2
                    z = population[i].originIndiv[2] - 300 + population[i].fitness/5
                    upt = rs.AddPoint(x,y,z)
                    uPointsInd.append(upt)
                        
                    rs.EnableRedraw(False)
                    rs.ZoomExtents()
                    if g == 0:
                        colour = [30+i*step,30+(newPopcount-i)*step,200]
                        population[i].colour = colour
                        rs.ObjectColor(population[i].guid, colour)
                        if population[i].fitness > 0:
                            # check with the designer weather to keep the fit individual
                            rs.SelectObjects(population[i].guid)
                            rs.ZoomSelected()
                            rs.UnselectAllObjects()
                            choice = rs.GetInteger("keep this original individual? If yes, enter 1, if not, enter 2")
                            if choice == 1:
                                myText1, myText2 = population[i].dispalyText(i)
                                rs.ZoomExtents()
                            else: 
                                HandPickingIndiv(population, colour, i, g, finished, statesCA, BetwGens)
                        else:
                            HandPickingIndiv(population, colour, i, g, finished, statesCA, BetwGens)
                    else: myText1, myText2 = population[i].dispalyText(i)
                    
                    # colour is given to each individual only in first generation. 
                    # The colours of the individuals of the following generations inherit in parts from their parents
                    
                    rs.ObjectColor(population[i].guid, population[i].colour)
                        
                ###############################
                #########     SOM   ###########
                ###############################
                
                # After the individuals are generated, initialise the neural map that 
                # later will be trained to achieve parameters close to the individuals of the current generation
                rs.EnableRedraw(False)
                for u in range(int(round(len(population)*1.5))):
                    vDom = []
                    for v in range(int(round(len(population)*1.5))):
                        # generate initial vector parameters for each individual in the map 
                        vec = []
                        for i in range(FNUM):
                            # the vectors of initial map neurons can be either zero or any 
                            # number from the decode list. If they are all zeroes, 
                            # then as the map trains it is easier to observe the "growth"
                            # the model as it tries to match an input
                            vecParam = 0 # r.randrange(0, decodeNum)
                            vec.append(vecParam)
                        
                        pos = [u*uSPACE, v*vSPACE + BetwGens + widthCA*CAunitsY*2, 0]
                        limbo = vec[:]
                        id =[u,v]
                        dist = 0
                        winnersList = []
                        dist2winner = []
                        closestWInner = []
                        colour = [0,0,0]
                        objNeuron = Neuron(pos, vec, limbo, id, winnersList, dist2winner,closestWInner, colour)
                        vDom.append(objNeuron)
                    neuron.append(vDom)
                rs.EnableRedraw(False)
                
                # Initialise the inputs
                rs.EnableRedraw(False)
                for i in range(len(population)):
                    pos = population[i].originIndiv[:]
                    vec = population[i].values[:]
                    guid = population[i].guid[:]
                    colour = population[i].colour
                    
                    objInput = Input(pos, vec, guid, colour)
                    input.append(objInput)
                rs.EnableRedraw(False)
                
                rs.EnableRedraw(True)
                rs.ZoomExtents()
                
                # train neurons on the map
                runSOM(neuron, input, statesCA, g, population, UMAX, VMAX)
                
                # take all neurons which fitness is above zero, convert them to 
                # individuals and append theem to the list allIndivNeurons
                i = 0
                
                for v in range(int(round(len(population)*1.5))):
                    uPoints = []
                    for u in range(int(round(len(population)*1.5))):
                        
                        # assess neurons' fitness
                        neuron[u][v].assessNeuronFitness(g)
                        
                        # record fitness values as points at certain heights above neurons
                        # Fitness Surface will use the points to visualise how the fitness changes in SOM
                        x = neuron[u][v].pos[0] + CAunitsX*widthCA/2
                        y = neuron[u][v].pos[1] + CAunitsY*widthCA/2
                        z = neuron[u][v].pos[2] - 300 + neuron[u][v].fitness/5
                        upt = rs.AddPoint(x,y,z)
                        uPoints.append(upt)
                        
                        if neuron[u][v].fitness != 0:
                            colour = [0,0,0]
                            allIndivNeurons.append(Individual(i, colour))
                            allIndivNeurons[i].values = neuron[u][v].vec[:]
                            allIndivNeurons[i].originIndiv = neuron[u][v].pos[:]
                            allIndivNeurons[i].fitness = neuron[u][v].fitness
                            allIndivNeurons[i].guid = neuron[u][v].guid[:]
                            allIndivNeurons[i].colour = neuron[u][v].colour
                            allIndivNeurons[i].grid = neuron[u][v].grid
                            
                            # Display the index as text
                            neuron[u][v].dispalyNeuronText(i)
                            allIndivNeurons[i].id = i
                            # Reverse decode from values to chromosome for each neuron of the SOM
                            # of each generation
                            allIndivNeurons[i].chromosome = []
                            for p in range (len(allIndivNeurons[i].values)):
                                for b in range (len(allValueslist)):
                                    # each neuron's value is rounded up to the closest even number
                                    # so a binary chromosome can be decoded from it
                                    roundedValue = closestEven(allIndivNeurons[i].values[p])
                                    allIndivNeurons[i].values[p] = roundedValue
                                    if allIndivNeurons[i].values[p] == allValueslist[b]:
                                        for k in range (geneLength):
                                            # gene by gene, bit by bit, creates a binary chromosome decoded from neuron's values
                                            allIndivNeurons[i].chromosome.append(allGeneslist[b][k])
                            i += 1
                    uCrv = rs.AddCurve(uPoints,1)
                    rs.DeleteObjects(uPoints)
                    uvCurves.append(uCrv)
                    rs.ObjectLayer(uCrv, "fitness curves")
                #fitnSurf = rs.AddLoftSrf(uvCurves)
                
                #######################################################
                ###########   GA: Selection and Crossover   ###########
                #######################################################
                
                rs.EnableRedraw(True)
                # CLUSTERS
                # a. separate the list allIndivNeurons into lists of  individuals that
                # form clusters and add an original "teaching" individual from the 
                # current generation (distinction of neurons by their colours)
                # b. calculate total fitness for each cluster and store it in the list
                # self.clusterFitness for each individual in the generation
                for i in range (len(population)):
                    population[i].clusterIndList = []
                    population[i].clusterFitness = 0
                    
                parents = []
                clustersLists(allIndivNeurons, population, g, statesCA, BetwGens, parents)
                
                #SELECTION
                if (g != GENERATIONS-1):
                    
                    for i in range (len(population)):
                        clusterPop = population[i].clusterIndList[:]
                        
                        # GOLDBERG ROULTETTE SELECTION among fittest.
                        # spin the wheel once to select one future parent from each cluster
                        if selectionChoice == 1:
                            if len(clusterPop) == 1:
                                parent = clusterPop[0]
                            if len(clusterPop) > 1:
                                parentIndex = roulette(clusterPop, population[i].clusterFitness)
                                parent = clusterPop[parentIndex]
                            if len(clusterPop) == 0:
                                print "cluster has no individuals"
                            # mark the parents on the map
                            markParents(parent)
                            parents.append(parent)
                            
                        # RANDOM OPTIMISED SELECTION among fittest
                        # filter the cluster with the min fitness cut-off limit,
                        # generate couples and pick one randomly from each cluster
                        if selectionChoice == 2 or selectionChoice == 3:
                            
                            if len(clusterPop) != 0:
                                totClFit = 0
                                ln = len(clusterPop)
                                for s in range (ln):
                                    totClFit = totClFit + clusterPop[s].fitness
                                avFit = totClFit/ln
                                minFit = minFitLevel*avFit/100 + avFit
                                tempNIList = []
                                for j in range (ln):
                                    if clusterPop[j].fitness >= minFit:
                                        tempNIList.append(clusterPop[j])
                                        
                                # if original individual has fitness above minFit
                                # make it part of the cluster & give it its own cluster id
                                if population[i].fitness > minFit:
                                    if len(tempNIList) != 0:
                                        ind = len(tempNIList)-1
                                        lastID = tempNIList[ind].id + 1
                                    else:
                                        lastID = 0
                                    population[i].id = lastID
                                    
                                    loc = [population[i].originIndiv[0] + 20, population[i].originIndiv[1]-10, population[i].originIndiv[2]] 
                                    txt = "cluster id", str(lastID)
                                    myText = rs.AddText(txt, loc, 5)
                                    rs.ObjectColor(myText, population[i].colour)
                                    
                                    population[i].clusterIndList.append(population[i])
                                    allIndivNeurons.append(population[i])
                                    tempNIList.append(population[i])
                                    population[i].clusterFitness += population[i].fitness
                                        
                                    
                                clusterPop = tempNIList[:]
                                ln = len(clusterPop)
                                # if there are two or more fit enough couples in the cluster
                                if ln >= 2:
                                    
                                    if selectionChoice == 2:
                                        # creates a list of couples from the current cluster population
                                        couplesList = []
                                        couple = []
                                        tempList = clusterPop[:]
                                        ln1 = int(round((ln-0.5)/2))
                                        for j in range (ln1):
                                            ln2 = len(tempList)-1
                                            ind = r.randrange(0,ln2)
                                            couple.append(tempList[ind])
                                            tempList.pop(ind)
                                            if ln2 != 1:
                                                ind = r.randrange(0,ln2-1)
                                            else: ind = 0
                                            couple.append(tempList[ind])
                                            tempList.pop(ind)
                                            couplesList.append(couple)
                                            couple = []
                                            
                                        # pick a randon couple from the couples list
                                        coupleIndex = r.randrange(0,len(couplesList))
                                        dad = couplesList[coupleIndex][0]
                                        mum = couplesList[coupleIndex][1]
                                        
                                    # ARTIFICIAL SELECTION
                                    # filter the cluster with the min fitness cutoff limit,
                                    # if necessary apply the elimination criteria, and manually pick the number of
                                    # candidates from each cluster
                                    if selectionChoice == 3:
                                        for t in range (len(clusterPop)):
                                            rs.SelectObjects(clusterPop[t].guid)
                                            
                                        rs.ZoomSelected()
                                        
                                        mumId = rs.GetInteger("please choose mum's id from the selected models")
                                        dadId = rs.GetInteger("please choose dad's id from the selected models")
                                        
                                        rs.UnselectAllObjects()
                                        for ind in range (len(clusterPop)):
                                            if clusterPop[ind].id == mumId: 
                                                mum = clusterPop[ind]
                                            if clusterPop[ind].id == dadId: 
                                                dad = clusterPop[ind]
                                        
                                        rs.ZoomExtents()
                                    # mark the parents on the map
                                    #parents.append(dad)
                                    parents.append(mum)
                                
                                # if there is one fit enough individual in the cluster
                                if ln == 1:
                                    parent = clusterPop[0]
                                    parents.append(parent)
                                # if there are no fit enough individuals in the cluster
                                if ln == 0:
                                    # create a fresh random individual with the fitness above a min fitness
                                    parent = createFreshInd(minFit,population,i,allIndivNeurons,g, statesCA, BetwGens, parents)
                                    parents.append(parent)
                                    
                                    # record fitness values as points at certain heights above individuals
                                    # Fitness Surface will use the points to visualise how the fitness changes in SOM
                                    x = parent.originIndiv[0] + CAunitsX*widthCA/2
                                    y = parent.originIndiv[1] + CAunitsY*widthCA/2
                                    z = parent.originIndiv[2] - 300 + parent.fitness/5
                                    upt = rs.AddPoint(x,y,z)
                                    uPointsInd.append(upt)
                    
                            else: 
                                minFit = 0
                                parent = createFreshInd(minFit,population,i,allIndivNeurons,g, statesCA, BetwGens, parents)
                                parents.append(parent)
                                
                                # record fitness values as points at certain heights above individuals
                                # Fitness Surface will use the points to visualise how the fitness changes in SOM
                                x = parent.originIndiv[0] + CAunitsX*widthCA/2
                                y = parent.originIndiv[1] + CAunitsY*widthCA/2
                                z = parent.originIndiv[2] - 300 + parent.fitness/5
                                upt = rs.AddPoint(x,y,z)
                                uPointsInd.append(upt)
                                    
                    # PARENTS CROSSOVER
                    # parents are chosen from the GA population and its SOM.
                    # However the offsprings are replacing individuals from the GA's generation
                    # so the next SOMap is build based on the evolved generation
                    newPop = []
                    
                    # couples are formed randomly from the list of the parents and crossed over
                    # making sure that the number of offsprings does not exceed
                    # max allowed POPmax
                    noParents = len(parents)
                    lnth = int(noParents/2)
                    parentsTemp = parents[:]
                    count  = 0
                    for q in range (lnth):
                        if len(newPop) <= POPmax:
                            count  = count + 1
                            ln = len(parentsTemp)
                            ind = r.randrange(0,ln)
                            dad = parentsTemp[ind]
                            parentsTemp.pop(ind)
                            markParents(dad)
                            
                            ln = len(parentsTemp)
                            ind = r.randrange(0,ln)
                            mum = parentsTemp[ind]
                            parentsTemp.pop(ind)
                            markParents(mum)
                            
                            for j in range (len(parents)):
                                if parents[j] == dad: dad.id = j
                                if parents[j] == mum: mum.id = j
                                    
                            # append all offsprings to the temp new population list
                            offspring1, offspring2 = crossover(dad.id, mum.id, parents)
                            newPop.append(offspring1)
                            newPop.append(offspring2)
                        
                        
                # Display the fittest among all individuals and neurons
                if len(allIndivNeurons) > 0:
                    bestFitness, totFitness = showBest(allIndivNeurons, myFile, statesCA,g, bestPts)
                    aveFitness = totFitness/len(allIndivNeurons)
                
                print "the average fitness of the generation and its SOM is", aveFitness
                print "the best fitness is ", bestFitness
                print "there are", len(allIndivNeurons), "fit individuals"
                #print "there are", len(newPop), "parents"
                if len(parents) == 4: print "The crossover is performed only between the individuals of the current generation", g + 1
                
                
                myFile.write("    the average fitness of the generation and its SOM is: ")
                myFile.write(str(aveFitness) + "\n")
                myFile.write("    number of fit individuals: ")
                myFile.write(str(len(allIndivNeurons)) + "\n")
                myFile.write("    number of parents: ")
                myFile.write(str(len(parents)) + "\n")
                
                
                if totFitness  == 0:
                    print "Evolution died out"
                    EVOLUTION = False
                    
                # MUTATION
                #if selectionChoice == 1:
                    #for j in range(len(newPop)):
                        #if r.random()< MUTATION_RATE:
                            #newPop[j].mutate()
                            
                # copy the temp new population list to the original population list
            if (g != GENERATIONS-1): 
                population = newPop[:]
            else: EVOLUTION = False
                
            # draws a fitness curve of the individuals of the current generation
            uCrv = rs.AddCurve(uPointsInd,1)
            rs.DeleteObjects(uPointsInd)
            uvCurves.append(uCrv)
            rs.ObjectLayer(uCrv, "fitness curves")
                    
            rs.EnableRedraw(True)
            rs.ZoomExtents()
            
    bestPts[0][1] = bestPts[0][1] - widthCA
    bestPts[len(bestPts)-1][1] = bestPts[len(bestPts)-1][1] + CAunitsY *widthCA + widthCA
    rs.AddCurve(bestPts,1)
    for i in range(len(bestPts)):
        bestPts[i][0] = bestPts[i][0] + CAunitsY*widthCA + widthCA*2
    rs.AddCurve(bestPts,1)

def HandPickingIndiv(population, colour, i, g, finished, statesCA, BetwGens):
    if population[i].guid is not None: rs.DeleteObjects(population[i].guid)
    if population[i].grid is not None: rs.DeleteObjects(population[i].grid)
    fitFound = False
    while fitFound == False:
        individual = Individual(i, colour)
        individual.decode()
        individual.drawBodyplan(i, g, finished, statesCA, BetwGens)
        myText1, myText2 = individual.dispalyText(i)
        objs = [myText1, myText2]
        
        rs.EnableRedraw(True)
        if individual.fitness > 850:
            rs.ZoomExtents()
            # check with the designer weather to keep the new individual
            rs.SelectObjects(objs)
            rs.SelectObjects(individual.guid)
            rs.SelectObjects(individual.grid)
            rs.ZoomSelected()
            rs.UnselectAllObjects()
            choice = rs.GetInteger("keep this new individual? If yes, enter 1, if not, enter 2")
            if choice == 1:
                fitFound = True
                population[i] = individual
                population[i].colour = colour
            else: 
                rs.DeleteObjects(objs)
                rs.DeleteObjects(individual.guid)
                rs.DeleteObjects(individual.grid)
                
        else:
                rs.DeleteObjects(objs)
                rs.DeleteObjects(individual.guid)
                rs.DeleteObjects(individual.grid)
    
def markParents(parent):
    rad = CAunitsX*widthCA
    pos = [parent.originIndiv[0]+rad/2, parent.originIndiv[1]+rad/2, parent.originIndiv[2]]
    circle = rs.AddCircle(pos, rad*0.8)
    hatch = rs.AddHatch(circle, rs.CurrentHatchPattern())
    rs.ObjectColor(circle, parent.colour)
    R = (255 - parent.colour[0])* 0.7 + parent.colour[0]
    G = (255 - parent.colour[1])* 0.7 + parent.colour[1]
    B = (255 - parent.colour[2])* 0.7 + parent.colour[2]
    if hatch is not None: rs.ObjectColor(hatch, [R,G,B])

def clustersLists(allIndivNeurons, population,g, statesCA, BetwGens, parents):
    minFit = 0
    
    # separate the list allIndivNeurons into lists of  individuals that
    # form clusters and add an original "teaching" individual from the 
    # current generation (distinction of neurons by their colours)
    
    for i in range (len(population)):
        for j in range (len(allIndivNeurons)):
            if population[i].colour == allIndivNeurons[j].colour:
                population[i].clusterIndList.append(allIndivNeurons[j])
                
                # calculate total fitness for each cluster and store it in the list
                # self.clusterFitness for each individual in the generation
                population[i].clusterFitness += allIndivNeurons[j].fitness
                
        # if the individual of the current pop has fitness then make it a part of its own cluster 
        # and give it its own cluster id
        if population[i].fitness > minFit:
            population[i].clusterIndList.append(population[i])
            allIndivNeurons.append(population[i])
            population[i].clusterFitness += population[i].fitness
    #
    #for i in range (len(population)):
    # if there are no fit models in the cluster create a brand new individual
    # that have some fitness and make it part of the cluster. 
    # position it alongside the original individuals of the current population
        #if len(population[i].clusterIndList) == 0:
            # add an individual from the current generation to each clusters list
            #createFreshInd(minFit, population,i, allIndivNeurons,g,statesCA, BetwGens, parents)
            
        # print "there is/are", len(population[i].clusterIndList), "fit individual/s in cluster", i
    
def createFreshInd(minFit,list,id,allIndivNeurons,g, statesCA, BetwGens, parents):
    # creates fresh random individual with the fitness above the specified minFit level
    # if the number of the parents does exceed the specified limit POPmax
    fitFound = False
    while fitFound == False:
        colour = [r.randrange(100,200),r.randrange(100,200),r.randrange(170,200)]
        finished = False
        freshID = len(list)
        freshInd = Individual(freshID, colour)
        freshInd.decode()
        freshInd.drawBodyplan(freshID, g, finished, statesCA, BetwGens)
        if freshInd.fitness > minFit:
            myText1, myText2 = freshInd.dispalyText(freshID)
            list[id].clusterIndList.append(freshInd)
            allIndivNeurons.append(freshInd)
            list.append(freshInd)
            fitFound = True
        else: 
            if freshInd.guid is not None: rs.DeleteObjects(freshInd.guid)
            if freshInd.grid is not None: rs.DeleteObjects(freshInd.grid)
    rs.ZoomExtents()
    return freshInd
    
def runSOM(neuron, input, statesCA, g, population, VMAX, UMAX):
  
    
    # Initialise the parameters
    WINLEARN = 0.98 # Winner learning strength
    LEARN = 0.95    # Others learning strength
    RADIUS = m.sqrt(m.pow((UMAX*uSPACE),2) + m.pow((VMAX*vSPACE),2))
    NEIGH = RADIUS
    CONVERGED = False
    cycles  = 0
    win = []
    closestWinner = []
    objects = []
    # Now keep going until system has converged
    while(CONVERGED == False):
        for u in range(int(round(len(population)*1.5))):
            for v in range(int(round(len(population)*1.5))):
                neuron[u][v].winnersList = []
                neuron[u][v].dist2winner = []
                neuron[u][v].closestWInner = []
        # 1. Find winner and organise
        for i in range(len(population)):
            win = input[i].findWinner(neuron, population)
            for u in range(int(round(len(population)*1.5))):
                for v in range(int(round(len(population)*1.5))):
                    neuron[u][v].organise(neuron, input, i, win, WINLEARN, LEARN, NEIGH)
        
        # 2. Update map
        rs.EnableRedraw(False)
        if objects != []: rs.DeleteObjects(objects)
        objects = []
        for u in range(int(round(len(population)*1.5))):
            for v in range(int(round(len(population)*1.5))):
                circle = neuron[u][v].update(g, statesCA, population, neuron)
                if circle != None: objects.append(circle)
                
        # 3. Update parameters
        cycles += 1
        WINLEARN = WINLEARN * (1 - (cycles / 600)) #0.98
        LEARN = LEARN * (1 - (cycles / 400)) #0.95
        NEIGH = RADIUS * (1 - (cycles / 100)) #0.95
        
        if WINLEARN < WINLEARN_RATE: CONVERGED = True
        
        rs.EnableRedraw(True)
        
        #print WINLEARN
        rs.ZoomExtents()

def binaryList(n):
    list = []
    for perm in getPerms(n):
        gene = map(int,perm)
        list.append(gene)
    return list

def getPerms(n):
    for i in getCandidates(n):
        for perm in set(permutations(i)):
            yield ''.join(perm)

def getCandidates(n):
    for i in range(1, n):
        res = "1" * i + "0" * (n - i)
        yield res

def binaryDecode(allGeneslist):
    counter = 0
    localList = []
    
    for g in range(len(allGeneslist)):
        thisValue = 0
        for i in range(geneLength):
            if allGeneslist[g][i] == 1:
                thisValue += m.pow(2, geneLength-i)
        localList.append(thisValue)
        
    return localList

def closestEven(decimal):
    
    c = round(decimal)
    d = c/2
    if d.is_integer():
        return c
    else: 
        if decimal > c:
            c = c+1
            return c
        else:
            c = c - 1
            return c

def crossover(mumIndex, dadIndex, oldPop):
    Dcol = oldPop[dadIndex].colour
    Mcol = oldPop[mumIndex].colour
    
    # Make a copy of ourselves
    dad = Individual(dadIndex, Dcol)
    mum = Individual(mumIndex, Mcol)
    
    dad.chromosome = oldPop[dadIndex].chromosome[:]
    mum.chromosome = oldPop[mumIndex].chromosome[:]
        
        
    # Single point splice (not right at the ends)
    splice = r.randrange(1, dad.chromLength-1)

    # Get the left and right bits for the dad
    parent01_left = dad.chromosome[0:splice]
    parent01_right = dad.chromosome[splice:dad.chromLength]
    
    # Get the left and right bits for the mum
    parent02_left = mum.chromosome[0:splice]
    parent02_right = mum.chromosome[splice : mum.chromLength]
    
    # Now make the children and update the chromosomes for mum and dad
    # Essentially, mum and dad turn into their children - ahem...
    dad.chromosome = parent01_left + parent02_right
    mum.chromosome = parent02_left + parent01_right
    
    # offsprings inherit the averaged colours from their parents 
    # split in a randomly chosen proportion
    R = (dad.colour[0] + mum.colour[0])/2
    G = (dad.colour[1] + mum.colour[1])/2
    B = (dad.colour[2] + mum.colour[2])/2
    dColSplice = r.random()
    mColSplice = 1 - dColSplice
    
    dad.colour = [R*dColSplice, G*dColSplice, B]
    mum.colour = [R*mColSplice, G*mColSplice, B]
    
    # Return these new offspring
    return dad, mum

def roulette(oldPop, totalFitness):

    # Goldberg's Roulette Wheel (or pie chart) as described by Mitchell, 
    # Introduction to Genetic Algorithms, p.166
    
    # First find a position on the pie chart
    myRandom = r.random()*totalFitness;
    fitSum = 0.0;

    # Now keep cycling through the pie until you get the correct member
    for i in range(len(oldPop)):
        fitSum += oldPop[i].fitness
        if(fitSum > myRandom):
            return i

def showBest(allIndivNeurons, myFile, statesCA, gen, bestPts):
    totFitness = 0
    bestFitness = 0
    bestID = 0
    for i in range(len(allIndivNeurons)):
        if(allIndivNeurons[i].fitness > bestFitness):
            bestID = i
            bestFitness = allIndivNeurons[i].fitness
        totFitness += allIndivNeurons[i].fitness
    for i in range (len(allIndivNeurons[bestID].guid)):
        unit = allIndivNeurons[bestID].guid[i]
        
        if statesCA[i] == "living":
            rs.ObjectColor(unit, [204,51,51])
        if statesCA[i] == "working":
            rs.ObjectColor(unit, [51,51,204])
        if statesCA[i] == "resting":
            rs.ObjectColor(unit, [51,204,51])
        
        start =allIndivNeurons[bestID].originIndiv
        end = [-210, 1000+ gen* (CAunitsY *widthCA + 80),0]
        transl = rs.VectorSubtract(end, start)
        rs.CopyObject(unit, transl)
        pt = [end[0]- widthCA, end[1], end[2] - 300 + allIndivNeurons[bestID].fitness/5]
        bestPts.append(pt)
        
    for i in range (len(allIndivNeurons[bestID].grid)):
        unit = allIndivNeurons[bestID].grid[i]
        start =allIndivNeurons[bestID].originIndiv
        end = [-210, 1000+ gen* (CAunitsY *widthCA + 80),0]
        transl = rs.VectorSubtract(end, start)
        rs.CopyObject(unit, transl)
        
    # display text
    loc1 = [end[0], end[1]-10, end[2]] 
    myText = rs.AddText(str(gen), loc1, 5)
    rs.ObjectColor(myText, [100,100,100])
    loc2 = [end[0], end[1]-3, end[2]] 
    myText = rs.AddText(str(allIndivNeurons[bestID].fitness), loc2, 2)
    rs.ObjectColor(myText, [255,0,0])
        
    # Write to the text file
    myFile.write("    the best fitness is: ")
    myFile.write(str(allIndivNeurons[bestID].fitness) + "\n")
    return bestFitness, totFitness

if __name__=="__main__":
    main()