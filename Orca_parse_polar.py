#!/usr/bin/env python
import numpy as np;
import sys;
import string;
import numpy.linalg as lg
import argparse as ap

atb=1.88971616463

parser=ap.ArgumentParser(description="Parse polarisation from Gaussian logfile")
parser.add_argument("-f","--logfile", help="Gaussian logfile")
args=parser.parse_args()
inputfile=args.logfile


check=False
        
with open (inputfile,"r") as f:
    for line in f:
        
        if "The raw cartesian tensor" in line :
            check=True
            
        if check==True:
            line=f.next();
            polarstring=(line.split());
            print polarstring
            xx=float(polarstring[0])
            line=f.next();
            polarstring=(line.split());
            print polarstring
            xy=float(polarstring[0])
            yy=float(polarstring[1])
            line=f.next();
            polarstring=(line.split());
            print polarstring
            xz=float(polarstring[0])
            yz=float(polarstring[1])
            zz=float(polarstring[2])
            polartensor=np.array([[xx,xy,xz],[xy,yy,yz],[xz,yz,zz]])
            break
                        
    
if check==False:
        print "There is no polarisability in file. Leaving"
        sys.exit()

else:
        polartensorangstrom=polartensor/(atb**3)
        polartensorangstromdiag=np.diag(lg.eigvalsh(polartensorangstrom))
        print "Convert to tensor"
        print "xx, xy, xz, yy, yz, zz"
        print "{0:4.4f} {1:4.4f} {2:4.4f} {3:4.4f} {4:4.4f} {5:4.4f}".format(polartensor[0,0],polartensor[0,1],polartensor[0,2],polartensor[1,1],polartensor[1,2],polartensor[2,2])
        print "Polarisability tensor in A^3, non diagonal"
        print "xx, xy, xz, yy, yz, zz"
        print "{0:4.4f} {1:4.4f} {2:4.4f} {3:4.4f} {4:4.4f} {5:4.4f}".format(polartensorangstrom[0,0],polartensorangstrom[0,1],polartensorangstrom[0,2],polartensorangstrom[1,1],polartensorangstrom[1,2],polartensorangstrom[2,2])
        print "Diagonal tensor in A^3"
        print "xx, xy, xz, yy, yz, zz"
        print "{0:4.4f} 0.0 0.0 {1:4.4f} 0.0 {2:4.4f}".format(polartensorangstromdiag[0,0],polartensorangstromdiag[1,1],polartensorangstromdiag[2,2])

        








