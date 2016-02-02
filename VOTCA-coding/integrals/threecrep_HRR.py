#!/usr/bin/env python

import itertools
import sys

orb2ang={"s":0,"p":1,"d":2,"f":3,"g":4,"h":5,"i":6}
ang2orb={0:"s",1:"p",2:"d",3:"f",4:"g",5:"h",6:"i"}
coordinates={'x','y','z'}

#Right now thi  script can only give you recursion for (ab,c) b=s type recursion formulas

def componentsorbital(angular,orbital):
        if angular==0:
                realcombos=['s']
        else:
                coordinates={'x','y','z'}
                realcombos=[]
                combos = itertools.combinations_with_replacement(coordinates, angular)
                for combo in combos:
                        
                        realcombos.append(orbital+''.join(combo))   
        return realcombos



def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False       

def getinput():
        orbital=raw_input("Enter orbital ")
        if orbital not in orb2ang:
                print 'enter either s,p,d,f,g'
                orbital=getinput()
        else:
                print orbital        
        return orbital

def getinputm():
        m=raw_input("Enter m ")
        if RepresentsInt(m)==False:
                print 'm must be an integer'
                m=getinputm()
        else:
                print m        
        return int(m)


def com2vec(components):
        vectors=[]
        for component in components:     
                vectors.append([component.count('x'),component.count('y'),component.count('z')])
        return vectors

def vec2com(vector):
        angular=sum(vector)
        if angular==0:
                components=ang2orb[angular]
        else:
                components='x'*vector[0]+'y'*vector[1]+'z'*vector[2] 
    
        return components
        
        

def mincoordinates(vector):
        minval=min(x for x in vector if x > 0)
        ind = [i for i, v in enumerate(vector) if v == minval]
        return ind[0]





def tc(vectorA,vectorB,vectorC):
        

       
        if all(xyz>=0 for xyz in vectorA) and all(xyz>=0 for xyz in vectorB) and all(xyz>=0 for xyz in vectorC):
                threecenter="R[Cart::{0}][Cart::{1}][Cart::{2}]".format(vec2com(vectorA),vec2com(vectorB),vec2com(vectorC))
        else:
                threecenter=''
        return threecenter

def tcold(vectorA,vectorB,vectorC,m):
        if all(xyz>=0 for xyz in vectorA) and all(xyz>=0 for xyz in vectorB)and all(xyz>=0 for xyz in vectorC):
                #threecenter="R[Cart::{0}][Cart::{1}][Cart::{2}][{3}]".format(vec2com(vectorA),vec2com(vectorB),vec2com(vectorC),m)
                threecenter="R_temp[Cart::{0}][Cart::{2}][{3}]".format(vec2com(vectorA),vec2com(vectorB),vec2com(vectorC),m)
        else:
                threecenter=''
        return threecenter




def check(N,string):
    if N>0:
        return string
    else:
        return ""




def printstructure(orbitalA,orbitalB,orbitalC):
    angularA=orb2ang[orbitalA]   
    angularB=orb2ang[orbitalB]
    angularC=orb2ang[orbitalC]
    
 
    
    print '//Integral {} - {} - {}'.format(orbitalA,orbitalB,orbitalC)

    if angularB > 0 and angularC >0 and angularA>0:
        print "if (_lmax_beta>{0} && _lmax_alpha>{1} && _lmax_gamma>{2}){{".format(angularB-1,angularA-1,angularC-1)
    elif angularA>0 and angularB>0:
        print "if (_lmax_beta>{0} && _lmax_alpha>{1}){{".format(angularB-1,angularA-1)
    elif angularC>0 and angularB>0:
        print "if (_lmax_beta>{0} && _lmax_gamma>{1}){{".format(angularB-1,angularC-1)
    elif angularA>0 and angularC>0:
        print "if (_lmax_alpha>{0} && _lmax_gamma>{1}){{".format(angularA-1,angularC-1)
    elif angularA>0:
        print "if (_lmax_alpha>{0}){{".format(angularA-1)
    elif angularB>0:
        print "if (_lmax_beta>{0}){{".format(angularB-1)
    elif angularC>0:
        print "if (_lmax_beta>{0}){{".format(angularC-1)
    componentsA=componentsorbital(angularA,orbitalA)
    componentsB=componentsorbital(angularB,orbitalB)
    componentsC=componentsorbital(angularC,orbitalC)
    print ""
    
    vectorsA=com2vec(componentsA)
    vectorsB=com2vec(componentsB)  
    vectorsC=com2vec(componentsC)  
    for vectorC in vectorsC:    
        for vectorB in vectorsB:
            for vectorA in vectorsA:

                if all(xyz==0 for xyz in vectorB):
                    print tc(vectorA,vectorB,vectorC)+"="+tcold(vectorA,vectorB,vectorC,0)+";"
               
                else:        
                    vectorAp1=list(vectorA)
                    vectorBm1=list(vectorB)
                    ind=mincoordinates(vectorB)
                    vectorAp1[ind]=vectorAp1[ind]+1
                    vectorBm1[ind]=vectorBm1[ind]-1
                    firstsecondterm="{1}+amb{0}*{2}".format(ind,tc(vectorAp1,vectorBm1,vectorC),tc(vectorA,vectorBm1,vectorC))
                    print tc(vectorA,vectorB,vectorC)+"="+firstsecondterm+";"
    if (angularB+angularA+angularC) > 0:
        print "}"
    print "//------------------------------------------------------"
    print ""



#orbitalB=getinput()
maxA=sys.argv[1]
maxB=sys.argv[2]
maxC=sys.argv[3]
#m=int(getinputm())
#print orbitalA
#print orbitalB


angularsA=range(orb2ang[maxA]+orb2ang[maxB]+1)
angularsB=range(orb2ang[maxB]+1)
angularsC=range(orb2ang[maxC]+1)
#for angularindex in range(mmax):
#    print componentsorbital(angularindex,ang2orb[angularindex])

for angularB in angularsB:
    for angularC in angularsC:
        for angularA in angularsA:
            if (angularA+angularB)<=(orb2ang[maxA]+orb2ang[maxB]):
                printstructure(ang2orb[angularA],ang2orb[angularB],ang2orb[angularC])
            




                
                          
                        

             











		
			






