import rhinoscriptsyntax as rs
import random as r
import math as m
from itertools import permutations

##################################
######  Amina Bakunowicz    ######
######      Thesis          ######
######       Day 16         ######
######     CA growing GA    ######
######         SOM          ######
######      Artificial      ######
######      Selection       ######
##################################

# Short description: 

# Global Variables for GA
initPOPCOUNT = rs.GetInteger("please enter the number of individuals?", 2, 2, 50)
GENERATIONS = rs.GetInteger("evolve over how many generations?", 1, 1, 500)
selectionChoice = 2 #rs.GetInteger("Selection type: if Goldberg Roulette, enter 1; if random, enter 2", 1, 1, 2)
geneLength = 4
MUTATION_RATE = 0.2
CROSSOVER_RATE = 1.0
FitnCoevRate = 2 # % by which a fitness componenet threshold should grow by with each egneration
minFitLevel = 5 # min % of the fitness of the best individual that a potential parent should possess in order to become a parent

FLOORHEIGHT = 8

# Globals for CA

CAunitsX = 4 # Number of CA units along X
CAunitsY = 4 # Number of CA units along Y
CAunitsZ = 24 # Number of CA units along Z

widthCA = 20 #width of the CA unit

statesCAall = ["living", "working", "resting"]
GSratio = 1.618
POPmax = initPOPCOUNT * 2 # max size of a generation

# Global Variables for SOM

FNUM = CAunitsX*CAunitsY*CAunitsZ * 2 + 6 # Number of the parameters in the neural vector and it equals to the number of genes
uSPACE = CAunitsX * widthCA + 50  # Neural grid U-direction Spacing
vSPACE = CAunitsY * widthCA + 50  # Neural grid V-direction Spacing
neuron = [] # Neurons (map)
input = []
WINLEARN_RATE = 0.4


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
        self.floors = []
        self.ellPts = []
        
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
        originsCA = []
        originsCAmodel = []
        CAmodelGuid =[]
        count = 0
        crvsLiving = []
        crvsWorking = []
        crvsResting = []
        floorCentroids = []
        newguid = []
        floors = []
        IndivEllPts = []
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
                    coordCA = [self.originIndiv[0]+(x*widthCA) + (self.values[n + 4]/2), self.originIndiv[1]+(y*widthCA) + (self.values[n + 5]/2), z*FLOORHEIGHT]
                    originsCA.append(coordCA)
                    
                    planeOrigin = [self.originIndiv[0]+(x*widthCA), self.originIndiv[1]+(y*widthCA), z*FLOORHEIGHT]
                    # draw a rectangle of CA's grid for each unit on the ground
                    if z == 0:
                        myPlane = rs.PlaneFromFrame(planeOrigin, [widthCA,0,0], [0,widthCA,z*FLOORHEIGHT])
                        rect = rs.AddRectangle(myPlane, widthCA, widthCA)
                        rs.ObjectColor(rect, [80,80,80])
                        rs.ObjectLayer(rect, "grid")
                    
                    # creates a display line between the origing of the unit#s grid rectangle
                    # and an origin of the 3D box of the unit
                    m += 1
                    #if statesCA[m-1] != "void" and self.values[n + 4]!=0 and self.values[n + 5]!=0:
                        #line = rs.AddLine(planeOrigin,coordCA)
                        #rs.ObjectColor(line, [0,255,255])
                
        # goes through every unit of every individual and draws an appropriate
        # geometry depending on the state of the unit
        for i in range (len(statesCA)):
            
            # displays original CA model 
            #if id ==0 and gen == 0:
                #coordCAmodel = originsCAmodel[i]
                #pt1 = [coordCAmodel[0], coordCAmodel[1], coordCAmodel[2]]
                #pt2 = [pt1[0] + widthCA, pt1[1], pt1[2]]
                #pt3 = [pt1[0] + widthCA, pt1[1] + widthCA, pt1[2]]
                #pt4 = [pt1[0], pt1[1] + widthCA, pt1[2]]
                #pt5 = [coordCAmodel[0], coordCAmodel[1], coordCAmodel[2] + FLOORHEIGHT]
                #pt6 = [pt1[0] + widthCA, pt1[1], pt1[2] + FLOORHEIGHT]
                #pt7 = [pt1[0] + widthCA, pt1[1] + widthCA, pt1[2] + FLOORHEIGHT]
                #pt8 = [pt1[0], pt1[1] + widthCA, pt1[2] + FLOORHEIGHT]
                #pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
                #CAmodelBox =  rs.AddBox(pts)
                #rs.MoveObject(CAmodelBox, [-1*(widthCA*CAunitsX + 150), 0,0])
                
                #if statesCA[i] == "living":
                    #rs.ObjectColor(CAmodelBox, [204,51,51])
                #if statesCA[i] == "working":
                    #rs.ObjectColor(CAmodelBox, [51,51,204])
                #if statesCA[i] == "resting":
                    #rs.ObjectColor(CAmodelBox, [51,204,51])
                #CAmodelGuid.append(CAmodelBox)
            
            coordCA = originsCA[i]
            # after each floor is formed, the curves between similar units are created
            if i == CAunitsX*CAunitsY * count or i == len(statesCA)-1:
                if count != 0:
                    if ptsLiving != []:
                        pt = ptsLiving[0]
                        ptsLiving.append(pt)
                        crvLiving = rs.AddCurve(ptsLiving)
                        crvLiving = rs.MoveObject(crvLiving, [0,0,-0.3])
                        crvsLiving.append(crvLiving)
                        
                    if ptsWorking != []:
                        pt = ptsWorking[0]
                        ptsWorking.append(pt)
                        crvWorking = rs.AddCurve(ptsWorking)
                        crvWorking = rs.MoveObject(crvWorking, [0,0,-0.3])
                        crvsWorking.append(crvWorking)
                        
                    if ptsResting != []:
                        pt = ptsResting[0]
                        ptsResting.append(pt)
                        crvResting = rs.AddCurve(ptsResting)
                        crvResting = rs.MoveObject(crvResting, [0,0,-0.3])
                        crvsResting.append(crvResting)
                    
                # empties lists of points with each floor of the model
                ptsLiving = []
                ptsWorking = []
                ptsResting = []
                count = count + 1
                
            if statesCA[i] == "living":
                livingBox = self.drawLiving(coordCA, ptsLiving)
                guid.append(livingBox)
                rs.ObjectLayer(livingBox, "boxes")
            if statesCA[i] == "working":
                workingBox = self.drawWorking(coordCA, ptsWorking)
                guid.append(workingBox)
                rs.ObjectLayer(workingBox, "boxes")
                
            if statesCA[i] == "resting":
                restingBox = self.drawResting(coordCA, ptsResting)
                guid.append(restingBox)
                rs.ObjectLayer(restingBox, "boxes")
                
        self.guid = guid[:]
        #rs.ObjectColor(self.guid, self.colour)
        
        # build bridges/connecting spaces between the corresponding units on each floor of each model
        wallsAll = []
        bridgesAll = []
        stateL = "living"
        stateW = "working"
        ststeR = "resting"
        wallsAll, bridgesAll = self.drawBridges(crvsLiving, wallsAll, bridgesAll, stateL)
        wallsAll, bridgesAll = self.drawBridges(crvsWorking, wallsAll, bridgesAll, stateW)
        wallsAll, bridgesAll = self.drawBridges(crvsResting, wallsAll, bridgesAll, ststeR)
        #for w in range(len(wallsAll)):
            #if wallsAll[w] is not None: newguid.append(wallsAll[w])
        for ba in range(len(bridgesAll)):
            if rs.IsSurface(bridgesAll[ba]): newguid.append(bridgesAll[ba])
            
        # find the edge units, find their floor surface centroids,
        for z in range (CAunitsZ):
            centroidsEdge = []
            for y in range (CAunitsY):
                for x in range (CAunitsX):
                    if x == 0 or y == 0 or x == CAunitsX-1 or y == CAunitsY - 1:
                        # determines its own box
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                        boxThis = self.guid[index-1]
                        centroidThis = rs.SurfaceVolumeCentroid(boxThis)[0]
                        #rs.AddPoint(centroidThis)
                        centroidsEdge.append(centroidThis)
            centroidsEdge.append(centroidsEdge[0])
                        
            
            # create a point that is center of the all units' centroids. 
            # Store them in the list floorCentroids[]
            lnth = len(centroidsEdge)
            xC = 0
            yC = 0
            zC = 0
            for ind in range (lnth):
                xC = xC + centroidsEdge[ind][0]
                yC = yC + centroidsEdge[ind][1]
                zC = zC + centroidsEdge[ind][2]
            xC = xC/lnth
            yC = yC/lnth
            zC = zC/lnth
            pt = [xC,yC,zC]
            floorCentroid = rs.AddPoint(pt)
            rs.ObjectLayer(floorCentroid, "centreline")
            sphere = rs.AddSphere(pt, 0.5)
            rs.ObjectLayer(sphere, "centreline")
            floorCentroids.append(floorCentroid)
            newguid.append(sphere)
            newguid.append(floorCentroid)
            
        if floorCentroids != []: 
            centrCrv = rs.AddCurve(floorCentroids,1)
            rs.ObjectLayer(centrCrv, "centreline")
        if centrCrv is not None: newguid.append(centrCrv)
        
        # from the each unit's floor surface centroid build a untit
        # of elliptical form 
        for z in range (CAunitsZ):
            for y in range (CAunitsY):
                for x in range (CAunitsX):
                    index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                    boxThis = self.guid[index-1]
                    centroidThis = rs.SurfaceVolumeCentroid(boxThis)[0]
                    
                    line = rs.AddLine(floorCentroids[z], centroidThis)
                    center = centroidThis
                    #rs.ObjectLayer(boxThis, "boxes")
                    if statesCA[index-1] == "living":
                        val1 = self.values[0]/2+3
                        val2 = self.values[1]/2+3
                        colour = [204,51,51]
                        newGuid,ceiling, ellipse, ellPts1, ellPts2, floor1, floor2, slab = self.newGuid(val1, val2, colour, line, center)
                        
                    if statesCA[index-1] == "working":
                        val1 = self.values[2]/2+3
                        val2 = self.values[3]/2+3
                        colour = [51,51,204]
                        newGuid,ceiling, ellipse, ellPts1, ellPts2,floor1, floor2, slab = self.newGuid(val1, val2, colour, line, center)
                        
                    if statesCA[index-1] == "resting":
                        val1 = self.values[4]/2+3
                        val2 = self.values[5]/2+3
                        colour = [51,204,51]
                        newGuid, ceiling, ellipse, ellPts1, ellPts2,floor1, floor2, slab = self.newGuid(val1, val2, colour, line, center)
                        
                    if newGuid is not None: newguid.append(newGuid)
                    if ceiling is not None: newguid.append(ceiling)
                    if floor1 is not None: newguid.append(floor1)
                    if floor2 is not None: newguid.append(floor2)
                    if slab is not None: newguid.append(slab)
                    if ellipse is not None: floors.append(ellipse)
                    
                    rs.ObjectLayer(ceiling, "slabs")
                    rs.ObjectLayer(newGuid, "walls")
                    IndivEllPts.append(ellPts1)
                    IndivEllPts.append(ellPts2)
        
        #self.ellPts = IndivEllPts[:]
        noUnits = len(IndivEllPts)
        pts4crvs = []
        crvsEll = []
        for noUn in range (CAunitsX*CAunitsY*2): # how many units on each floor
            for noPt in range (20): # how many points each ellipse is divided by
                for flr in range(CAunitsZ): # over how many floors
                    index = int(noUnits/(CAunitsZ)*(flr+1) - noUn - 1)
                    pt = IndivEllPts[index][noPt]
                    pts4crvs.append(pt)
                crv = rs.AddCurve(pts4crvs,2)
                crvsEll.append(crv)
                pts4crvs = []
                
            loft = rs.AddLoftSrf(crvsEll)
            if rs.IsSurface(loft): 
                newguid.append(loft)
                rs.ObjectLayer(loft, "tower")
                
            crvsAdd = [crvsEll[0], crvsEll[len(crvsEll)-1]]
            loft = rs.AddLoftSrf(crvsAdd)
            if rs.IsSurface(loft): 
                newguid.append(loft)
                rs.ObjectLayer(loft, "railing")
            rs.DeleteObjects(crvsEll)
            crvsEll = []
        
        self.newguid = newguid[:]
        self.floors = floors[:]
        
        
        # Assess the fitness: proximity of the boxes' centroids
        # within Moore neighborhood and min intersection volume
        # list originsCA[] has all origins of this individual's boxes. 
        self.assessFitness(gen, centrCrv)
        
        # Display the index as text
        self.dispalyText(id)
        
    def assessFitness(self, gen, centrCrv):
        
        # fitness according to the proximity of the proportion of the box to 
        # Golden Section Ratio defined as a global variable GSratio
        GSfactor = 0
        
        # checks the ration of the width vs length of Living CA unit
        # and adds to fitness factor GSfactor depending on this ratio
        pt1 = [0, 0, 0]
        pt2 = [pt1[0] + self.values[0] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.values[0] + 3, pt1[1] + self.values[1] + 3, pt1[2]]
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioLiving = dst1/dst2
        else: ratioLiving = dst2/dst1
        # checks the ration of the width vs length of Working CA unit
        # and adds to fitness factor GSfactor depending on this ratio
        pt1 = [0, 0, 0]
        pt2 = [pt1[0] + self.values[2] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.values[2] + 3, pt1[1] + self.values[3] + 3, pt1[2]]
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioWorking = dst1/dst2
        else: ratioWorking = dst2/dst1
        GSfactor += 7/abs(ratioWorking-GSratio)
        # checks the ration of the width vs length of Resting CA unit
        # and adds to fitness factor GSfactor depending on this ratio
        pt1 = [0, 0, 0]
        pt2 = [pt1[0] + self.values[4] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.values[4] + 3, pt1[1] + self.values[5] + 3, pt1[2]]
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioResting = dst1/dst2
        else: ratioResting = dst2/dst1
        GSfactor += 15/abs(ratioResting-GSratio)
        
        
        
        distances = 0
        areas = 0
        distFactor = 0
        objects = []
        ellipsesXXfactor = 0
        XXfactor = 0
        XXareasFactor = 0
        
        # fitness criteria keeps the neighboring boxes as close as possible 
        # maintaining the initial spatial arrangement 
        for z in range (CAunitsZ):
            for y in range (CAunitsY):
                for x in range (CAunitsX):
                    
                    index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                    # work out the total intersection area of ellipses
                    if index < len(self.floors)-2:
                        crv1 = self.floors[index]
                        crv2 = self.floors[index+1]
                        origin = self.originIndiv
                        ellipsesXXarea = self.Xarea(crv1, crv2, origin)
                        ellipsesXXfactor += ellipsesXXarea
                        
                    # check the area of the CA unit and add it to the total area
                    boxThis = self.guid[index-1]
                    
                    # find the distances between non-edge units and their Moore neighbors
                    if x != 0 and y != 0 and x != CAunitsX-1 and y != CAunitsY - 1:
                        # determines its own box, its neighboring boxes and their centroids
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                        boxThis = self.guid[index-1]
                        centroidThis = rs.SurfaceVolumeCentroid(boxThis)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x + 1
                        boxS = self.guid[index-1]
                        centroidS = rs.SurfaceVolumeCentroid(boxS)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x + 2
                        boxSE = self.guid[index-1]
                        centroidSE = rs.SurfaceVolumeCentroid(boxSE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 2
                        boxE = self.guid[index-1]
                        centroidE = rs.SurfaceVolumeCentroid(boxE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x + 2
                        boxNE = self.guid[index-1]
                        centroidNE = rs.SurfaceVolumeCentroid(boxNE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x + 1
                        boxN = self.guid[index-1]
                        centroidN = rs.SurfaceVolumeCentroid(boxN)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x
                        boxNW = self.guid[index-1]
                        centroidNW = rs.SurfaceVolumeCentroid(boxNW)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x
                        boxW = self.guid[index-1]
                        centroidW = rs.SurfaceVolumeCentroid(boxW)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x
                        boxSW = self.guid[index-1]
                        centroidSW = rs.SurfaceVolumeCentroid(boxSW)[0]
                        
                        # works out the sum of the distances between the neighbouring units
                        dist1 = rs.Distance(centroidThis,centroidS)
                        dist2 = rs.Distance(centroidThis,centroidSE)
                        dist3 = rs.Distance(centroidThis,centroidE)
                        dist4 = rs.Distance(centroidThis,centroidNE)
                        dist5 = rs.Distance(centroidThis,centroidN)
                        dist6 = rs.Distance(centroidThis,centroidNW)
                        dist7 = rs.Distance(centroidThis,centroidW)
                        dist8 = rs.Distance(centroidThis,centroidSW)
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
                        
                        
        centrCrvLen = rs.CurveLength(centrCrv)
        # work out the final values of fitness factor components
        centrCrvFactor = 2000/centrCrvLen
        if distFactor != 0: distFactor = 90000/distFactor
        if XXareasFactor  != 0: XXareasFactor = 100000/XXareasFactor
        if ellipsesXXfactor != 0: ellipsesXXfactor = 90000/ellipsesXXfactor
        
        # print distFactor, XXareasFactor, ellipsesXXfactor, GSfactor, centrCrvFactor
        
        # In order to gain some fitness an individual (or a neuron) must have 
        # the components of the fitness factor defined accepted level. 
        # If one of the Fitness Factor constituents is below the 
        # defined threshold, its total fitness is written down to zero.
        if selectionChoice == 2: 
            fitThreshold = gen*FitnCoevRate + 40
        else: fitThreshold = 0
        if distFactor>fitThreshold and XXareasFactor>fitThreshold and XXareasFactor>fitThreshold and XXareasFactor>fitThreshold and centrCrvFactor>fitThreshold:
            fitness = distFactor + XXareasFactor + ellipsesXXfactor + GSfactor + centrCrvFactor
            self.fitness = round(fitness,2)
        else:
            self.fitness = 0
            
    def drawBridges(self, crvs, wallsAll, bridgesAll, state):
        
        lnth = len(crvs)
        for lb in range(lnth):
            if rs.IsCurve(crvs[lb]): 
                #pts = rs.CurvePoints(crvs[lb])
                #path = ([0,0,pts[0][2]],[0,0,pts[0][2]+FLOORHEIGHT+0.3])
                #walls = rs.ExtrudeCurve(crvs[lb],path)
                #wallsAll.append(walls)
                #rs.ObjectLayer(walls, "walls")
                Bridge = rs.AddPlanarSrf(crvs[lb])
                if len(Bridge) != 0:
                    for sf in range(len(Bridge)): 
                        if rs.IsSurface(Bridge[sf]): 
                            bridgesAll.append(Bridge[sf])
                            rs.ObjectLayer(Bridge[sf], "bridges")
                            if state == "living":
                                rs.ObjectColor(Bridge[sf],[204,51,51])
                            if state == "working":
                                rs.ObjectColor(Bridge[sf],[51,51,204])
                            if state == "resting":
                                rs.ObjectColor(Bridge[sf],[51,204,51])
        rs.DeleteObjects(crvs)
        return wallsAll,  bridgesAll
        
    def Xarea(self, crv1, crv2, origin):
        if rs.IsCurve(crv1) and rs.IsCurve(crv2):
            CxC = rs.CurveBooleanIntersection(crv2, crv1)
            crvs = [crv1,crv2]
            rs.DeleteObjects(crvs)
            if len(CxC) != 0:
                for indCxC in range (len(CxC)):
                    if rs.IsCurve(CxC[indCxC]):
                        srf = rs.AddPlanarSrf(CxC[indCxC])
                        for indSrf in range (len(srf)):
                            if rs.IsSurface(srf[indSrf]):
                                XXarea = rs.SurfaceArea(srf)[0]
                                rs.ObjectLayer(srf, "XXareas")
                            else: XXarea = 0
                        rs.DeleteObjects(CxC[indCxC])
                    else: XXarea = 0
            else: XXarea = 0
        else: XXarea = 0
        return XXarea
        
    def dispalyText(self, id):
        loc1 = [self.originIndiv[0], self.originIndiv[1]-10, self.originIndiv[2]] 
        myText = rs.AddText(str(id), loc1, 5)
        rs.ObjectColor(myText, [100,100,100])
        loc2 = [self.originIndiv[0], self.originIndiv[1]-3, self.originIndiv[2]] 
        myText = rs.AddText(str(self.fitness), loc2, 2)
        rs.ObjectColor(myText, [255,0,0])
        
    def newGuid(self, val1, val2, colour, line, center):
        lineExt1 = rs.ExtendCurveLength(line, 0, 1, val1)
        pts1 = rs.DivideCurve(lineExt1,2,False,True)
        ptCA1 = pts1[2]
        #rs.AddPoint(pts1[2])
        
        lineExt2 = rs.ExtendCurveLength(line, 0, 1, val2)
        lineExt2Perp = rs.RotateObject(lineExt2, center, 90, [0,0,1], True)
        pts2 = rs.DivideCurve(lineExt2Perp,2,False,True)
        ptCA2 = pts2[2]
        #rs.AddPoint(ptCA2)
        
        ellipse = rs.AddEllipse3Pt(center, ptCA1, ptCA2)
        ellipse = rs.MoveObject(ellipse, [0,0, FLOORHEIGHT/2])
        ellipse = rs.RotateObject(ellipse, center, 90, [0,0,1], False)
        ellPts1 = rs.DivideCurve(ellipse,20,False,True)

        
        ellipse2 = rs.MoveObject(ellipse, [0,0, -1 * FLOORHEIGHT])
        ellPts2 = rs.DivideCurve(ellipse2,20,False,True)

        
        floor1 = rs.AddPlanarSrf(ellipse)
        rs.ObjectLayer(floor1, "slabs")
        ellipse = rs.MoveObject(ellipse, [0,0, -0.3])
        floor2 = rs.AddPlanarSrf(ellipse)
        rs.ObjectLayer(floor2, "slabs")
        path = rs.AddLine([0,0,center[2]-FLOORHEIGHT/2-0.3],[0,0,center[2]-FLOORHEIGHT/2+2.5])
        walls = rs.ExtrudeCurve(ellipse, path)
        rs.ObjectLayer(walls, "railing")
        ceiling = rs.CopyObject(floor1, [0,0, FLOORHEIGHT])
        path = rs.AddLine([0,0,center[2]-FLOORHEIGHT/2],[0,0,center[2]+FLOORHEIGHT/2])
        newGuid = rs.ExtrudeCurve(ellipse, path)
        rs.ObjectColor(newGuid, colour)
        
        TBdeleted = [line, lineExt1, lineExt2, lineExt2Perp, path]
        rs.DeleteObjects(TBdeleted)
        
        if r.random()<0.6:
            TBdeleted = [floor1, floor2, walls]
            rs.DeleteObjects(TBdeleted)
            rs.HideObject(ellipse)
        
        return newGuid, ceiling, ellipse, ellPts1, ellPts2, floor1, floor2, walls
    
    def drawLiving(self, coordCA, ptsLiving):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        ptsLiving.append(pt1)
        pt2 = [pt1[0] + self.values[0] + 3, pt1[1], pt1[2]]
        ptsLiving.append(pt2)
        pt3 = [pt1[0] + self.values[0] + 3, pt1[1] + self.values[1] + 3, pt1[2]]
        ptsLiving.append(pt3)
        pt4 = [pt1[0], pt1[1] + self.values[1] + 3, pt1[2]]
        ptsLiving.append(pt4)
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        #ptsLiving.append(pt5)
        pt6 = [pt1[0] + self.values[0] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        #ptsLiving.append(pt6)
        pt7 = [pt1[0] + self.values[0] + 3, pt1[1] + self.values[1] + 3, pt1[2] + FLOORHEIGHT]
        #ptsLiving.append(pt7)
        pt8 = [pt1[0], pt1[1] + self.values[1] + 3, pt1[2] + FLOORHEIGHT]
        #ptsLiving.append(pt8)
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        livingBox =  rs.AddBox(pts)
        rs.ObjectColor(livingBox, [204,51,51])
        return livingBox
        
        
    def drawWorking(self, coordCA, ptsWorking):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        ptsWorking.append(pt1)
        pt2 = [pt1[0] + self.values[2] + 3, pt1[1], pt1[2]]
        ptsWorking.append(pt2)
        pt3 = [pt1[0] + self.values[2] + 3, pt1[1] + self.values[3] + 3, pt1[2]]
        ptsWorking.append(pt3)
        pt4 = [pt1[0], pt1[1] + self.values[3] + 3, pt1[2]]
        ptsWorking.append(pt4)
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        #ptsWorking.append(pt5)
        pt6 = [pt1[0] + self.values[2] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        #ptsWorking.append(pt6)
        pt7 = [pt1[0] + self.values[2] + 3, pt1[1] + self.values[3] + 3, pt1[2] + FLOORHEIGHT]
        #ptsWorking.append(pt7)
        pt8 = [pt1[0], pt1[1] + self.values[3] + 3, pt1[2] + FLOORHEIGHT]
        #ptsWorking.append(pt8)
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        workingBox =  rs.AddBox(pts)
        rs.ObjectColor(workingBox, [51,51,204])
        return workingBox
        
    def drawResting(self, coordCA, ptsResting):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        ptsResting.append(pt1)
        pt2 = [pt1[0] + self.values[4] + 3, pt1[1], pt1[2]]
        ptsResting.append(pt2)
        pt3 = [pt1[0] + self.values[4] + 3, pt1[1] + self.values[5] + 3, pt1[2]]
        ptsResting.append(pt3)
        pt4 = [pt1[0], pt1[1] + self.values[5] + 3, pt1[2]]
        ptsResting.append(pt4)
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        #ptsResting.append(pt5)
        pt6 = [pt1[0] + self.values[4] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        #ptsResting.append(pt6)
        pt7 = [pt1[0] + self.values[4] + 3, pt1[1] + self.values[5] + 3, pt1[2] + FLOORHEIGHT]
        #ptsResting.append(pt7)
        pt8 = [pt1[0], pt1[1] + self.values[5] + 3, pt1[2] + FLOORHEIGHT]
        #ptsResting.append(pt8)
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        restingBox =  rs.AddBox(pts)
        rs.ObjectColor(restingBox, [51,204,51])
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
        self.floors = []
        self.newguid = []

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
        
        if (self.guid !=None): rs.DeleteObjects(self.guid)
        if (self.newguid != []): rs.DeleteObjects(self.newguid)
        if (self.floors != []): rs.DeleteObjects(self.floors)
        
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
        newguid = []
        floors = []
        originsCA = []
        originsCAmodel = []
        CAmodelGuid =[]
            
        count = 0
        crvsLiving = []
        crvsWorking = []
        crvsResting = []
        floorCentroids = []
        
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
                    
                    # creates a display line between the origing of the unit#s grid rectangle
                    # and an origin of the 3D box of the unit
                    #m += 1
                    #if statesCA[m-1] != "void" and self.vec[n + 4]!=0 and self.vec[n + 5]!=0:
                        #line = rs.AddLine(planeOrigin,coordCA)
                        #rs.ObjectColor(line, [0,255,255])
                
        # goes through every unit of every individual and draws the appropriate
        # geometry depending on the state of the unit
        for i in range (len(statesCA)):
            
            coordCA = originsCA[i]
            
            # after each floor is formed, the curves between similar units are created
            if i == CAunitsX*CAunitsY * count or i == len(statesCA)-1:
                if count != 0:
                    if ptsNeuronLiving != []:
                        pt = ptsNeuronLiving[0]
                        ptsNeuronLiving.append(pt)
                        crvLiving = rs.AddCurve(ptsNeuronLiving)
                        #srf = rs.AddPlanarSrf(crvLiving)
                        #rs.ObjectColor(srf, [204,51,51])
                        crvsLiving.append(crvLiving)
                        
                    if ptsNeuronWorking != []:
                        pt = ptsNeuronWorking[0]
                        ptsNeuronWorking.append(pt)
                        crvWorking = rs.AddCurve(ptsNeuronWorking)
                        #srf = rs.AddPlanarSrf(crvWorking)
                        #rs.ObjectColor(srf, [51,51,204])
                        crvsWorking.append(crvWorking)
                        
                    if ptsNeuronResting != []:
                        pt = ptsNeuronResting[0]
                        ptsNeuronResting.append(pt)
                        crvResting = rs.AddCurve(ptsNeuronResting)
                        #srf = rs.AddPlanarSrf(crvResting)
                        #rs.ObjectColor(srf, [51,204,51])
                        crvsResting.append(crvResting)
                    
                # empties lists of points with each floor of the model
                ptsNeuronLiving = []
                ptsNeuronWorking = []
                ptsNeuronResting = []
                #crvsLiving = []
                #crvsWorking = []
                #crvsResting = []
                count = count + 1
                
            if statesCA[i] == "living":
                livingBox = self.drawNeuronLiving(coordCA, ptsNeuronLiving)
                guid.append(livingBox)
                
            if statesCA[i] == "working":
                workingBox = self.drawNeuronWorking(coordCA, ptsNeuronWorking)
                guid.append(workingBox)
                
            if statesCA[i] == "resting":
                restingBox = self.drawNeuronResting(coordCA, ptsNeuronResting)
                guid.append(restingBox)
                
        self.guid = guid[:]
        
        livingSpace = rs.AddLoftSrf(crvsLiving)
        if livingSpace is not None:
            rs.ObjectColor(livingSpace, [204,51,51])
            rs.DeleteObjects(crvsLiving)
            newguid.append(livingSpace)
            
        
        workingSpace = rs.AddLoftSrf(crvsWorking)
        if workingSpace is not None:
            rs.ObjectColor(workingSpace, [51,51,204])
            rs.DeleteObjects(crvsWorking)
            newguid.append(workingSpace)
        
        restingSpace = rs.AddLoftSrf(crvsResting)
        if restingSpace is not None:
            rs.ObjectColor(restingSpace, [51,204,51])
            rs.DeleteObjects(crvsResting)
            newguid.append(restingSpace)
            
        # find the edge units, find their floor surface centroids,
        for z in range (CAunitsZ):
            centroidsEdge = []
            for y in range (CAunitsY):
                for x in range (CAunitsX):
                    if x == 0 or y == 0 or x == CAunitsX-1 or y == CAunitsY - 1:
                        # determines its own box
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                        boxThis = self.guid[index-1]
                        centroidThis = rs.SurfaceVolumeCentroid(boxThis)[0]
                        #rs.AddPoint(centroidThis)
                        centroidsEdge.append(centroidThis)
                        
            # create a point that is center of the all units' centroids. 
            # Store them in the list floorCentroids[]
            lnth = len(centroidsEdge)
            xC = 0
            yC = 0
            zC = 0
            for ind in range (lnth):
                xC = xC + centroidsEdge[ind][0]
                yC = yC + centroidsEdge[ind][1]
                zC = zC + centroidsEdge[ind][2]
            xC = xC/lnth
            yC = yC/lnth
            zC = zC/lnth
            pt = [xC,yC,zC]
            floorCentroid = rs.AddPoint(pt)
            sphere = rs.AddSphere(pt, 0.5)
            floorCentroids.append(floorCentroid)
        # from the each unit's floor surface centroid build a untit
        # of elliptical form facing
        for z in range (CAunitsZ):
            for y in range (CAunitsY):
                for x in range (CAunitsX):
                    index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                    boxThis = self.guid[index-1]
                    centroidThis = rs.SurfaceVolumeCentroid(boxThis)[0]
                    
                    line = rs.AddLine(floorCentroids[z], centroidThis)
                    center = centroidThis
                    rs.HideObject(boxThis)
                    if statesCA[index-1] == "living":
                        val1 = self.vec[0]/2+3
                        val2 = self.vec[1]/2+3
                        colour = [204,51,51]
                        newGuid, floor, ceiling, ellipse = self.newNeuronGuid(val1, val2, colour, line, center)
                        
                        
                    if statesCA[index-1] == "working":
                        val1 = self.vec[2]/2+3
                        val2 = self.vec[3]/2+3
                        colour = [51,51,204]
                        newGuid, floor, ceiling, ellipse = self.newNeuronGuid(val1, val2, colour, line, center)
                        
                    if statesCA[index-1] == "resting":
                        val1 = self.vec[4]/2+3
                        val2 = self.vec[5]/2+3
                        colour = [51,204,51]
                        newGuid, floor, ceiling, ellipse = self.newNeuronGuid(val1, val2, colour, line, center)
                        
                    newguid.append(newGuid)
                    newguid.append(ceiling)
                    newguid.append(floor)
                    newguid.append(sphere)
                    floors.append(ellipse)
        
        self.newguid = newguid[:]
        self.floors = floors[:]
        # Assess the fitness: proximity of the boxes' centroids
        # within Moore neighborhood and min intersection volume
        # list originsCA[] has all origins of this individual's boxes
        # and intersection of floor slabs of the CA units
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
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioLiving = dst1/dst2
        else: ratioLiving = dst2/dst1
        # checks the ration of the width vs length of Working CA unit
        # and adds to fitness factor GSfactor depending on this ratio
        pt1 = [0, 0, 0]
        pt2 = [pt1[0] + self.vec[2] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.vec[2] + 3, pt1[1] + self.vec[3] + 3, pt1[2]]
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioWorking = dst1/dst2
        else: ratioWorking = dst2/dst1
        GSfactor += 7/abs(ratioWorking-GSratio)
        # checks the ration of the width vs length of Resting CA unit
        # and adds to fitness factor GSfactor depending on this ratio
        pt1 = [0, 0, 0]
        pt2 = [pt1[0] + self.vec[4] + 3, pt1[1], pt1[2]]
        pt3 = [pt1[0] + self.vec[4] + 3, pt1[1] + self.vec[5] + 3, pt1[2]]
        dst1 = rs.Distance(pt1,pt2)
        dst2 = rs.Distance(pt2,pt3)
        if dst1>=dst2: ratioResting = dst1/dst2
        else: ratioResting = dst2/dst1
        GSfactor += 7/abs(ratioResting-GSratio)
        
        distances = 0
        areas = 0
        distFactor = 0
        objects = []
        CAlen = len(self.floors)
        # fitness criteria keeps the neighboring boxes as close as possible 
        # maintaining the initial spatial arrangement 
        for z in range (CAunitsZ):
            for y in range (CAunitsY):
                for x in range (CAunitsX):
                    
                    index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                    # work out the total intersection area of ellipses
                    if index < CAlen-2:
                        crv1 = self.floors[index]
                        crv2 = self.floors[index+1]
                        origin = self.pos
                        #XXarea = self.Xarea(crv1, crv2, origin)
                        #print XXarea
                    
                    # find the distances between non-edge units and their Moore neighbors
                    
                    boxThis = self.guid[index-1]
                    
                    if x != 0 and y != 0 and x != CAunitsX-1 and y != CAunitsY - 1:
                        # determines its own box, its neighboring boxes and their centroids
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 1
                        boxThis = self.guid[index-1]
                        centroidThis = rs.SurfaceVolumeCentroid(boxThis)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x + 1
                        boxS = self.guid[index-1]
                        centroidS = rs.SurfaceVolumeCentroid(boxS)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x + 2
                        boxSE = self.guid[index-1]
                        centroidSE = rs.SurfaceVolumeCentroid(boxSE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x + 2
                        boxE = self.guid[index-1]
                        centroidE = rs.SurfaceVolumeCentroid(boxE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x + 2
                        boxNE = self.guid[index-1]
                        centroidNE = rs.SurfaceVolumeCentroid(boxNE)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x + 1
                        boxN = self.guid[index-1]
                        centroidN = rs.SurfaceVolumeCentroid(boxN)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y+1) * CAunitsX + x
                        boxNW = self.guid[index-1]
                        centroidNW = rs.SurfaceVolumeCentroid(boxNW)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + y * CAunitsX + x
                        boxW = self.guid[index-1]
                        centroidW = rs.SurfaceVolumeCentroid(boxW)[0]
                        
                        index = (CAunitsX*CAunitsY)*z + (y-1) * CAunitsX + x
                        boxSW = self.guid[index-1]
                        centroidSW = rs.SurfaceVolumeCentroid(boxSW)[0]
                        
                        # works out the sum of the distances between the neighbouring units
                        dist1 = rs.Distance(centroidThis,centroidS)
                        dist2 = rs.Distance(centroidThis,centroidSE)
                        dist3 = rs.Distance(centroidThis,centroidE)
                        dist4 = rs.Distance(centroidThis,centroidNE)
                        dist5 = rs.Distance(centroidThis,centroidN)
                        dist6 = rs.Distance(centroidThis,centroidNW)
                        dist7 = rs.Distance(centroidThis,centroidW)
                        dist8 = rs.Distance(centroidThis,centroidSW)
                        distances = dist1+dist2+dist3+dist4+dist5+dist6+dist7+dist8
                        distFactor += distances
                        
                        
                        
        if distFactor != 0: distFactor = 9000*CAunitsZ/distFactor
        
        #print distFactor, XXareasFactor, totalAreaFactor
        
        #print distFactor, XXareasFactor # totalAreaFactor # , XXfactor # GSfactor,
        # In order to gain some fitness an individual (or a neuron) must have 
        # the components of the fitness factor defined accepted level. 
        # If one of the Fitness Factor constituents is below the 
        # defined threshold, its total fitness is written down to zero.
        if selectionChoice == 2: 
            fitThreshold = gen*(0.3*FitnCoevRate)
        else: fitThreshold = 0
        if distFactor>(25+ fitThreshold): # and XXareasFactor>(10 + fitThreshold) and totalAreaFactor>(15 + fitThreshold):#totalAreaFactor>(20 + gen*(0.20*FitnCoevRate)):## and GSfactor>50
            fitness = distFactor #+ XXareasFactor + totalAreaFactor #  + GSfactor
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
        
    def drawNeuronLiving(self, coordCA, ptsNeuronLiving):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        ptsNeuronLiving.append(pt1)
        pt2 = [pt1[0] + self.vec[0] + 3, pt1[1], pt1[2]]
        ptsNeuronLiving.append(pt2)
        pt3 = [pt1[0] + self.vec[0] + 3, pt1[1] + self.vec[1] + 3, pt1[2]]
        ptsNeuronLiving.append(pt3)
        pt4 = [pt1[0], pt1[1] + self.vec[1] + 3, pt1[2]]
        ptsNeuronLiving.append(pt4)
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        pt6 = [pt1[0] + self.vec[0] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        pt7 = [pt1[0] + self.vec[0] + 3, pt1[1] + self.vec[1] + 3, pt1[2] + FLOORHEIGHT]
        pt8 = [pt1[0], pt1[1] + self.vec[1] + 3, pt1[2] + FLOORHEIGHT]
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        livingBox =  rs.AddBox(pts)
        return livingBox
        
    def drawNeuronWorking(self, coordCA, ptsNeuronWorking):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        ptsNeuronWorking.append(pt1)
        pt2 = [pt1[0] + self.vec[2] + 3, pt1[1], pt1[2]]
        ptsNeuronWorking.append(pt2)
        pt3 = [pt1[0] + self.vec[2] + 3, pt1[1] + self.vec[3] + 3, pt1[2]]
        ptsNeuronWorking.append(pt3)
        pt4 = [pt1[0], pt1[1] + self.vec[3] + 3, pt1[2]]
        ptsNeuronWorking.append(pt4)
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        pt6 = [pt1[0] + self.vec[2] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        pt7 = [pt1[0] + self.vec[2] + 3, pt1[1] + self.vec[3] + 3, pt1[2] + FLOORHEIGHT]
        pt8 = [pt1[0], pt1[1] + self.vec[3] + 3, pt1[2] + FLOORHEIGHT]
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        workingBox =  rs.AddBox(pts)
        return workingBox
        
    def drawNeuronResting(self, coordCA, ptsNeuronResting):
        
        pt1 = [coordCA[0], coordCA[1], coordCA[2]]
        ptsNeuronResting.append(pt1)
        pt2 = [pt1[0] + self.vec[4] + 3, pt1[1], pt1[2]]
        ptsNeuronResting.append(pt2)
        pt3 = [pt1[0] + self.vec[4] + 3, pt1[1] + self.vec[5] + 3, pt1[2]]
        ptsNeuronResting.append(pt3)
        pt4 = [pt1[0], pt1[1] + self.vec[5] + 3, pt1[2]]
        ptsNeuronResting.append(pt4)
        pt5 = [coordCA[0], coordCA[1], coordCA[2] + FLOORHEIGHT]
        pt6 = [pt1[0] + self.vec[4] + 3, pt1[1], pt1[2] + FLOORHEIGHT]
        pt7 = [pt1[0] + self.vec[4] + 3, pt1[1] + self.vec[5] + 3, pt1[2] + FLOORHEIGHT]
        pt8 = [pt1[0], pt1[1] + self.vec[5] + 3, pt1[2] + FLOORHEIGHT]
        pts = [pt1, pt2, pt3, pt4, pt5, pt6, pt7, pt8]
        restingBox =  rs.AddBox(pts)
        return restingBox
        
    def newNeuronGuid(self, val1, val2, colour, line, center):
        lineExt1 = rs.ExtendCurveLength(line, 0, 1, val1)
        pts1 = rs.DivideCurve(lineExt1,2,False,True)
        ptCA1 = pts1[2]
        #rs.AddPoint(pts1[2])
        
        lineExt2 = rs.ExtendCurveLength(line, 0, 1, val2)
        lineExt2Perp = rs.RotateObject(lineExt2, center, 90, [0,0,1], True)
        pts2 = rs.DivideCurve(lineExt2Perp,2,False,True)
        ptCA2 = pts2[2]
        #rs.AddPoint(ptCA2)
        
        ellipse = rs.AddEllipse3Pt(center, ptCA1, ptCA2)
        ellipse = rs.MoveObject(ellipse, [0,0, -FLOORHEIGHT/2])
        ellipse = rs.RotateObject(ellipse, center, 90, [0,0,1], False)
        floor = rs.AddPlanarSrf(ellipse)
        ceiling = rs.CopyObject(floor, [0,0, FLOORHEIGHT])
        path = rs.AddLine([0,0,center[2]-FLOORHEIGHT/2],[0,0,center[2]+FLOORHEIGHT/2])
        newGuid = rs.ExtrudeCurve(ellipse, path)
        rs.ObjectColor(newGuid, colour)
        
        TBdeleted = [line, lineExt1, lineExt2, lineExt2Perp, path, ellipse]
        rs.DeleteObjects(TBdeleted)
        
        
        return newGuid, floor, ceiling, ellipse
        
    def Xarea(self, crv1, crv2, origin):
        if rs.IsCurve(crv1) and rs.IsCurve(crv2):
            CxC = rs.CurveBooleanIntersection(crv2, crv1)
            crvs = [crv1,crv2]
            rs.DeleteObjects(crvs)
            print CxC
            #if CxC != None:
                #if rs.IsCurve(CxC):
                    #srf = rs.AddPlanarSrf(CxC)
                    #if rs.IsSurface(srf):
                        #XXarea = rs.SurfaceArea(srf)[0]
                    #else: XXarea = 0
                #else: XXarea = 0
            #else: XXarea = 0
        XXarea = 0
        return XXarea

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
    
    # Setup a text file for data
    myFile = open('fitnessHistory.txt', 'w')
    rs.AddLayer("railing")
    rs.AddLayer("tower")
    rs.AddLayer("boxes")
    rs.AddLayer("walls")
    rs.AddLayer("slabs")
    rs.AddLayer("grid")
    rs.AddLayer("bridges")
    rs.AddLayer("centreline")
    rs.AddLayer("XXareas")
    
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
            neuron = []
            input = [] # Inputs (samples)
            allIndivNeurons = []
            rs.EnableRedraw(True)
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
                    population[i].decode()
                    population[i].drawBodyplan(i, g, finished, statesCA, BetwGens)
                    
                    # colour is given to each individual only in first generation. 
                    # The colours of the individuals of the following generations inherit in parts from their parents
                    if g == 0:
                        colour = [30+i*step,30+(newPopcount-i)*step,200]
                        population[i].colour = colour
            rs.EnableRedraw(True)
            #rs.ZoomExtents()
            EVOLUTION = False
                    #rs.ObjectColor(population[i].guid, population[i].colour)
                        
#                ###############################
#                #########     SOM   ###########
#                ###############################
#                
#                # After the individuals are generated, initialise the neural map that 
#                # later will be trained to achieve parameters close to the individuals of the current generation
#                rs.EnableRedraw(False)
#                for u in range(int(round(len(population)*1.5))):
#                    vDom = []
#                    for v in range(int(round(len(population)*1.5))):
#                        # generate initial vector parameters for each individual in the map 
#                        vec = []
#                        for i in range(FNUM):
#                            vecParam = r.randrange(0, decodeNum)
#                            vec.append(vecParam)
#                        
#                        pos = [u*uSPACE, v*vSPACE + BetwGens + widthCA*CAunitsY*2, 0]
#                        limbo = vec[:]
#                        id =[u,v]
#                        dist = 0
#                        winnersList = []
#                        dist2winner = []
#                        closestWInner = []
#                        colour = [0,0,0]
#                        objNeuron = Neuron(pos, vec, limbo, id, winnersList, dist2winner,closestWInner, colour)
#                        vDom.append(objNeuron)
#                    neuron.append(vDom)
#                rs.EnableRedraw(False)
#                
#                # Initialise the inputs
#                rs.EnableRedraw(False)
#                for i in range(len(population)):
#                    pos = population[i].originIndiv[:]
#                    vec = population[i].values[:]
#                    guid = population[i].guid[:]
#                    colour = population[i].colour
#                    
#                    objInput = Input(pos, vec, guid, colour)
#                    input.append(objInput)
#                rs.EnableRedraw(False)
#                
#                rs.EnableRedraw(True)
#                rs.ZoomExtents()
#                
#                # train neurons on the map
#                runSOM(neuron, input, statesCA, g, population, UMAX, VMAX)
#                
#                # take all neurons which fitness is above zero, convert them to 
#                # individuals and append theem to the list allIndivNeurons
#                i = 0
#                for v in range(int(round(len(population)*1.5))):
#                    for u in range(int(round(len(population)*1.5))):
#                        # assess neurons' fitness
#                        neuron[u][v].assessNeuronFitness(g)
#                        if neuron[u][v].fitness != 0:
#                            colour = [0,0,0]
#                            allIndivNeurons.append(Individual(i, colour))
#                            allIndivNeurons[i].values = neuron[u][v].vec[:]
#                            allIndivNeurons[i].originIndiv = neuron[u][v].pos[:]
#                            allIndivNeurons[i].fitness = neuron[u][v].fitness
#                            allIndivNeurons[i].guid = neuron[u][v].guid[:]
#                            allIndivNeurons[i].colour = neuron[u][v].colour
#                            
#                            
#                            # Display the index as text
#                            neuron[u][v].dispalyNeuronText(i)
#                            allIndivNeurons[i].id = i
#                            # Reverse decode from values to chromosome for each neuron of the SOM
#                            # of each generation
#                            allIndivNeurons[i].chromosome = []
#                            for p in range (len(allIndivNeurons[i].values)):
#                                for b in range (len(allValueslist)):
#                                    # each neuron's value is rounded up to the closest even number
#                                    # so a binary chromosome can be decoded from it
#                                    roundedValue = closestEven(allIndivNeurons[i].values[p])
#                                    allIndivNeurons[i].values[p] = roundedValue
#                                    if allIndivNeurons[i].values[p] == allValueslist[b]:
#                                        for k in range (geneLength):
#                                            # gene by gene, bit by bit, creates a binary chromosome decoded from neuron's values
#                                            allIndivNeurons[i].chromosome.append(allGeneslist[b][k])
#                            i += 1
#                
#                #######################################################
#                ###########   GA: Selection and Crossover   ###########
#                #######################################################
#                
#                rs.EnableRedraw(True)
#                # CLUSTERS
#                # a. separate the list allIndivNeurons into lists of  individuals that
#                # form clusters and add an original "teaching" individual from the 
#                # current generation (distinction of neurons by their colours)
#                # b. calculate total fitness for each cluster and store it in the list
#                # self.clusterFitness for each individual in the generation
#                for i in range (len(population)):
#                    population[i].clusterIndList = []
#                    population[i].clusterFitness = 0
#                    
#                parents = []
#                clustersLists(allIndivNeurons, population, g, statesCA, BetwGens, parents)
#                
#                #SELECTION
#                if (g != GENERATIONS-1):
#                    
#                    for i in range (len(population)):
#                        clusterPop = population[i].clusterIndList[:]
#                        
#                        # GOLDBERG ROULTETTE SELECTION among fittest.
#                        # spin the wheel once to select one future parent from each cluster
#                        if selectionChoice == 1:
#                            if len(clusterPop) == 1:
#                                parent = clusterPop[0]
#                            if len(clusterPop) > 1:
#                                parentIndex = roulette(clusterPop, population[i].clusterFitness)
#                                parent = clusterPop[parentIndex]
#                            if len(clusterPop) == 0:
#                                print "cluster has no individuals"
#                            # mark the parents on the map
#                            markParents(parent)
#                            parents.append(parent)
#                            
#                        # RANDOM OPTIMISED SELECTION among fittest
#                        # filter the cluster with the min fitness cut-off limit,
#                        # generate couples and pick one randomly from each cluster
#                        if selectionChoice == 2 or selectionChoice == 3:
#                            
#                            if len(clusterPop) != 0:
#                                totClFit = 0
#                                ln = len(clusterPop)
#                                for s in range (ln):
#                                    totClFit = totClFit + clusterPop[s].fitness
#                                avFit = totClFit/ln
#                                minFit = minFitLevel*avFit/100 + avFit
#                                tempNIList = []
#                                for j in range (ln):
#                                    if clusterPop[j].fitness >= minFit:
#                                        tempNIList.append(clusterPop[j])
#                                        
#                                # if original individual has fitness above minFit
#                                # make it part of the cluster & give it its own cluster id
#                                if population[i].fitness > minFit:
#                                    if len(tempNIList) != 0:
#                                        ind = len(tempNIList)-1
#                                        lastID = tempNIList[ind].id + 1
#                                    else:
#                                        lastID = 0
#                                    population[i].id = lastID
#                                    
#                                    loc = [population[i].originIndiv[0] + 20, population[i].originIndiv[1]-10, population[i].originIndiv[2]] 
#                                    txt = "cluster id", str(lastID)
#                                    myText = rs.AddText(txt, loc, 5)
#                                    rs.ObjectColor(myText, population[i].colour)
#                                    
#                                    population[i].clusterIndList.append(population[i])
#                                    allIndivNeurons.append(population[i])
#                                    tempNIList.append(population[i])
#                                    population[i].clusterFitness += population[i].fitness
#                                        
#                                    
#                                clusterPop = tempNIList[:]
#                                ln = len(clusterPop)
#                                # if there are two or more fit enough couples in the cluster
#                                if ln >= 2:
#                                    
#                                    if selectionChoice == 2:
#                                        # creates a list of couples from the current cluster population
#                                        couplesList = []
#                                        couple = []
#                                        tempList = clusterPop[:]
#                                        ln1 = int(round((ln-0.5)/2))
#                                        for j in range (ln1):
#                                            ln2 = len(tempList)-1
#                                            ind = r.randrange(0,ln2)
#                                            couple.append(tempList[ind])
#                                            tempList.pop(ind)
#                                            if ln2 != 1:
#                                                ind = r.randrange(0,ln2-1)
#                                            else: ind = 0
#                                            couple.append(tempList[ind])
#                                            tempList.pop(ind)
#                                            couplesList.append(couple)
#                                            couple = []
#                                            
#                                        # pick a randon couple from the couples list
#                                        coupleIndex = r.randrange(0,len(couplesList))
#                                        dad = couplesList[coupleIndex][0]
#                                        mum = couplesList[coupleIndex][1]
#                                        
#                                    # ARTIFICIAL SELECTION
#                                    # filter the cluster with the min fitness cutoff limit,
#                                    # if necessary apply the elimination criteria, and manually pick the number of
#                                    # candidates from each cluster
#                                    if selectionChoice == 3:
#                                        for t in range (len(clusterPop)):
#                                            rs.SelectObjects(clusterPop[t].guid)
#                                            
#                                        rs.ZoomSelected()
#                                        
#                                        mumId = rs.GetInteger("please choose mum's id from the selected models")
#                                        dadId = rs.GetInteger("please choose dad's id from the selected models")
#                                        
#                                        rs.UnselectAllObjects()
#                                        for ind in range (len(clusterPop)):
#                                            if clusterPop[ind].id == mumId: 
#                                                mum = clusterPop[ind]
#                                            if clusterPop[ind].id == dadId: 
#                                                dad = clusterPop[ind]
#                                        
#                                        rs.ZoomExtents()
#                                    # mark the parents on the map
#                                    parents.append(dad)
#                                    parents.append(mum)
#                                
#                                # if there is one fit enough individual in the cluster
#                                if ln == 1:
#                                    parent = clusterPop[0]
#                                    parents.append(parent)
#                                # if there are no fit enough individuals in the cluster
#                                if ln == 0:
#                                    # create a fresh random individual with the fitness above a min fitness
#                                    parent = createFreshInd(minFit,population,i,allIndivNeurons,g, statesCA, BetwGens, parents)
#                                    parents.append(parent)
#                                    
#                            else: 
#                                minFit = 0
#                                parent = createFreshInd(minFit,population,i,allIndivNeurons,g, statesCA, BetwGens, parents)
#                                parents.append(parent)
#                                
#                    # PARENTS CROSSOVER
#                    # parents are chosen from the GA population and its SOM.
#                    # However the offsprings are replacing individuals from the GA's generation
#                    # so the next SOMap is build based on the evolved generation
#                    newPop = []
#                    
#                    # couples are formed randomly from the list of the parents and crossed over
#                    # making sure that the number of offsprings does not exceed
#                    # max allowed POPmax
#                    noParents = len(parents)
#                    lnth = int(noParents/2)
#                    parentsTemp = parents[:]
#                    count  = 0
#                    for q in range (lnth):
#                        if len(newPop) < POPmax:
#                            count  = count + 1
#                            ln = len(parentsTemp)
#                            ind = r.randrange(0,ln)
#                            dad = parentsTemp[ind]
#                            parentsTemp.pop(ind)
#                            markParents(dad)
#                            
#                            ln = len(parentsTemp)
#                            ind = r.randrange(0,ln)
#                            mum = parentsTemp[ind]
#                            parentsTemp.pop(ind)
#                            markParents(mum)
#                            
#                            for j in range (len(parents)):
#                                if parents[j] == dad: dad.id = j
#                                if parents[j] == mum: mum.id = j
#                                    
#                            # append all offsprings to the temp new population list
#                            offspring1, offspring2 = crossover(dad.id, mum.id, parents)
#                            newPop.append(offspring1)
#                            newPop.append(offspring2)
#                        
#                        
#                # Display the fittest among all individuals and neurons
#                if len(allIndivNeurons) > 0:
#                    bestFitness, totFitness = showBest(allIndivNeurons, myFile, statesCA)
#                    aveFitness = totFitness/len(allIndivNeurons)
#                
#                print "the average fitness of the generation and its SOM is", aveFitness
#                print "the best fitness is ", bestFitness
#                print "there are", len(allIndivNeurons), "fit individuals"
#                print "there are", len(newPop), "parents"
#                if len(parents) == 4: print "The crossover is performed only between the individuals of the current generation", g + 1
#                
#                
#                myFile.write("    the average fitness of the generation and its SOM is: ")
#                myFile.write(str(aveFitness) + "\n")
#                myFile.write("    number of fit individuals: ")
#                myFile.write(str(len(allIndivNeurons)) + "\n")
#                myFile.write("    number of parents: ")
#                myFile.write(str(len(parents)) + "\n")
#                
#                
#                if totFitness  == 0:
#                    print "Evolution died out"
#                    EVOLUTION = False
#                    
#                # MUTATION
#                #if selectionChoice == 1:
#                    #for j in range(len(newPop)):
#                        #if r.random()< MUTATION_RATE:
#                            #newPop[j].mutate()
#                            
#                # copy the temp new population list to the original population list
#            if (g != GENERATIONS-1): 
#                population = newPop[:]
#            else: EVOLUTION = False
#                
#                
#            rs.EnableRedraw(True)
#            rs.ZoomExtents()

                
def markParents(parent):
    rad = CAunitsX*widthCA
    pos = [parent.originIndiv[0]+rad/2, parent.originIndiv[1]+rad/2, parent.originIndiv[2]]
    circle = rs.AddCircle(pos, rad*0.8)
    hatch = rs.AddHatch(circle, rs.CurrentHatchPattern())
    rs.ObjectColor(circle, parent.colour)
    if hatch is not None: rs.ObjectColor(hatch, [220,220,220])

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
            list[id].clusterIndList.append(freshInd)
            allIndivNeurons.append(freshInd)
            list.append(freshInd)
            fitFound = True
        else: 
            rs.DeleteObjects(freshInd.guid)
            rs.DeleteObjects(freshInd.newguid)
            rs.DeleteObjects(freshInd.floors)
            
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

def showBest(allIndivNeurons, myFile, statesCA):
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
            
    # Write to the text file
    myFile.write("    the best fitness is: ")
    myFile.write(str(allIndivNeurons[bestID].fitness) + "\n")
    return bestFitness, totFitness

if __name__=="__main__":
    main()