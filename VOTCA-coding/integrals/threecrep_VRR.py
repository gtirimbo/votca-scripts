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



def tc(vectorA,vectorB,vectorC,m):
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

def bracketterm1(vector1,vector2,vector3,m,N):
        bracketterm=check(N,'+{0}*rzeta*({1}-gfak*{2})'.format(N,tc(vector1,vector2,vector3,m),tc(vector1,vector2,vector3,m+1)))    
        return bracketterm

def bracketterm2(vector1,vector2,vector3,m,N):
        bracketterm=check(N,'+{0}/_decay_gamma*({1}-cfak*{2})'.format(N,tc(vector1,vector2,vector3,m),tc(vector1,vector2,vector3,m+1)))    
        return bracketterm


def printstructure(orbitalA,orbitalC,m):
    if m<0:
        print ""
    else:
        angularA=orb2ang[orbitalA]
        orbitalB="s"
        angularB=orb2ang[orbitalB]
        angularC=orb2ang[orbitalC]
        
        if (angularA==0 and angularB==0 and angularC==0):
            #print "//omitting s-s-s"
            return
        
        print '//Integral {} - {} - {} - m{}'.format(orbitalA,orbitalB,orbitalC,m)
        if m>0:
            print "if (_mmax >{} ){{".format(m)
        if angularA>0 and angularC>0:
            print "if (_lmax_alpha>{0} && _lmax_gamma>{1}){{".format(angularA-1,angularC-1)
        elif angularA>0:
            print "if (_lmax_alpha>{0}){{".format(angularA-1)
        elif angularC>0:
            print "if (_lmax_gamma>{0}){{".format(angularC-1)
        componentsA=componentsorbital(angularA,orbitalA)
        componentsB=componentsorbital(angularB,orbitalB)
        componentsC=componentsorbital(angularC,orbitalC)

        vectorsA=com2vec(componentsA)
        vectorsB=com2vec(componentsB)  
        vectorsC=com2vec(componentsC)  
        
        for vectorA in vectorsA:
            for vectorB in vectorsB:
                for vectorC in vectorsC:
                    vectorAm1=list(vectorA)
                    vectorCm1=list(vectorC)

                    if angularA >= angularC:      
                        ind=mincoordinates(vectorA)
                        vectorAm1[ind]=vectorAm1[ind]-1
                        vectorCm1[ind]=vectorCm1[ind]-1
                        vectorAm2=list(vectorA)
                        vectorAm2[ind]=vectorAm2[ind]-2
                        firstsecondterm="pma{0}*{1}+wmp{0}*{2}".format(ind,tc(vectorAm1,vectorB,vectorC,m),tc(vectorAm1,vectorB,vectorC,m+1))
                        thirdfourthterm=bracketterm1(vectorAm2,vectorB,vectorC,m,vectorAm2[ind])
                        #fifthsixthterm NOT IN USE RIGHT NOW
                        lastterm=check(vectorC[ind],'+0.5/_decay*{0}*{1}'.format(vectorC[ind],tc(vectorAm1,vectorB,vectorCm1,m+1)))
                    else:
                        ind=mincoordinates(vectorC)
                        vectorAm1[ind]=vectorAm1[ind]-1
                        vectorCm1[ind]=vectorCm1[ind]-1
                        vectorCm2=list(vectorC)
                        vectorCm2[ind]=vectorCm2[ind]-2
                        firstsecondterm="wmc{0}*{1}".format(ind,tc(vectorA,vectorB,vectorCm1,m+1))
                        thirdfourthterm=bracketterm2(vectorA,vectorB,vectorCm2,m,vectorCm2[ind])
                        lastterm=check(vectorA[ind],'+0.5/_decay*{0}*{1}'.format(vectorA[ind],tc(vectorAm1,vectorB,vectorCm1,m+1)))
                    
                    print tc(vectorA,vectorB,vectorC,m)+"+="+firstsecondterm+thirdfourthterm+lastterm+";"
        if angularA>0 or angularC>0 :
            print "}"
        if m>0:
            print "}"
        print "//------------------------------------------------------"
        print ""


maxA=sys.argv[1]
#orbitalB=getinput()

maxC=sys.argv[2]
#m=int(getinputm())
#print orbitalA
#print orbitalB


angularsA=range(orb2ang[maxA]+1)
angularsC=range(orb2ang[maxC]+1)
mmax=orb2ang[maxA]+orb2ang[maxC]
#print mmax
#for angularindex in range(mmax):
#    print componentsorbital(angularindex,ang2orb[angularindex])
for angularA in angularsA:
    for angularC in angularsC:
        mrange=range(mmax-angularA-angularC+1)
    
        for m in mrange:
            #print "{} - {} - m{}".format(ang2orb[angularA],ang2orb[angularC],m)
            
            printstructure(ang2orb[angularA],ang2orb[angularC],m)
            




                
                          
                        

             











		
			






