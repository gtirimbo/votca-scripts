#! /usr/bin/python



import sys
import os
import re
import getopt

# =========================================================
# INFO

def print_help():

    print """\

    PYHON EXEC "pycrop"

    Options ===========================================

    > I/O ---------------------------------------------
    -f              -- input file
    -o              -- output file
    
    > Mode --------------------------------------------
    -h              -- display this info
    -m              -- options include line, adjacent,
                       columns, rows, except 

    > Trigger -----------------------------------------
    --tstr           -- start string
    --tend           -- end string
    --this           -- starting this line (yes) or
                        next line (no, default)
    --tocc           -- occurrence of start string
                        at which trigger switches
    --tlen           -- number of lines for trigger
                        to be in active state
    
    > Criteria ----------------------------------------
    --cstr           -- string that has to occur in line
                        in order to be cropped
    --clen           -- length of line when split into
                        array
    --ctyp           -- type of entries, e.g. "s f f f"
                        for a string followed by three
                        floats
    --cnot           -- string that must NOT occur in
                        line in order to be cropped
    --cnum           -- number of lines that supposedly
                        meet the criteria
    --ccom           -- specify comment symbol in file

    > Processing --------------------------------------
    --pcol           -- columns to be returned, for
                        example "0 1 9"
    --pret           -- return string (string) or list
                        (list); currently not used
   
   
    COMMENTS ==========================================
    
    For import in python use function crop(argstr):
    i.e. from pycrop import crop(argstr)

            """
    sys.exit(0)






# =========================================================
# CLASS DEFINITIONS

class Trigger(object):
    def __init__(self):
        self.tstr = ''
        self.tend = ''
        self.this = False
        self.tocc = 1
        self.tlen = -1

        self.on  = False
        self.off = False

        self.tcount = 0    # ln count
        self.tocccount = 0 # occ count

    def trigger(self, ln):

        if self.tend != '' and self.on and self.tend in ln:
            self.off = True
            self.on = False
        if self.tcount == self.tlen:
            self.off = True
            self.on = False
            return ln, ln.split(), self.on
            
        if self.tstr in ln:
            self.tocccount += 1
            if self.tocccount == self.tocc:
                self.on = True
            else:
                pass        
        
        if self.on:
            self.tcount += 1

        return ln, ln.split(), self.on

    def countocc(self, infi):

        if self.tocc < 0:        
            intt = open(infi,'r')
            count = 0
            for ln in intt.readlines():
                if self.tstr in ln:
                    count += 1
                else:
                    pass
            self.tocccount = -count -1

            print "\n", count, "occurences of", self.tstr, "in", infi
            
        else:
            pass

class Check(object):
    def __init__(self):
        self.cstr = ''
        self.clen = -1
        self.ctyp = ''
        self.cnot = ''
        self.cnum = -1
        self.ccom = ''

        self.met  = False
        self.countall = 0
        self.countchk = 0
        
    def check(self, ln, Trigger):

        if not Trigger.on:
            return '', [], self.met
        
        self.met = False
        self.countall += 1

        if self.cnum != -1 and self.countchk == self.cnum:
            Trigger.on = False
            Trigger.off = True
            return '', [], self.met
        
        if ln.split() != []:
            if self.cstr in ln:
                pass
            else:
                return '', [], self.met

            if len(ln.split()) != self.clen and self.clen != -1:
                return '', [], self.met
            else:
                pass

            if self.cnot in ln and self.cnot != '':
                return '', [], self.met
            else:
                pass

            if self.ccom != '' and ln.split()[0][0] == self.ccom:
                return '', [], self.met
            else:
                pass

        else:
            return ln, ln.split(), True

        # If programme got up to here:
        self.met = True
        self.countchk += 1

        return ln, ln.split(), self.met


class Process(object):
    def __init__(self):
        self.pcol = []
        self.pret = 'string'
        
    def process(self, ln):

        outln = ''
        outlnsp = []
        
        # Process line split
        if self.pcol != []:
            lnsp = ln.split()
            for i in self.pcol:
                try:
                    outlnsp.append(lnsp[i])
                except IndexError:
                    outlnsp = []
                    break
        else:
            outlnsp = ln.split()
            pass
        
        # Process line string
        outln = ln

        return outln, outlnsp, self.pret


# =========================================================
# MODULE

def crop(argstr):

    sopts = 'hf:o:m:'
    lopts = ['tstr=','tend=','this=','tocc=','tlen=',
             'cstr=','clen=','ctyp=','cnot=','cnum=','ccom=',
             'pcol=','pret=']
    try:
        opts, xargs = getopt.getopt(argstr.split(), sopts, lopts)
    except getopt.GetoptError, err:
        print "Unknown execute argument: ", str(err)
        sys.exit(2)    

    T = Trigger()
    C = Check()
    P = Process()

    for o in opts:
        # I/O
        if   o[0] == '-h':
            print_help()
        elif o[0] == '-f':
            infi = o[1]
        elif o[0] == '-o':
            outfi = o[1]
        # TRIGGER   
        elif 'tstr' in o[0]:
            T.tstr = o[1]
        elif 'tend' in o[0]:
            T.tend = o[1]
        elif 'this' in o[0]:
            T.this = True
        elif 'tocc' in o[0]:
            T.tocc = int(o[1])
        elif 'tlen' in o[0]:
            T.tlen = int(o[1])
        # CONTROLLER
        elif 'cstr' in o[0]:
            C.cstr = o[1]
        elif 'clen' in o[0]:
            C.clen = int(o[1])
        elif 'ctyp' in o[0]:
            C.ctyp = o[1]
        elif 'cnot' in o[0]:
            C.cnot = o[1]
        elif 'cnum' in o[0]:
            C.cnum = int(o[1])
        elif 'ccom' in o[0]:
            C.ccom = o[1]
        # PROCESSOR
        elif 'pcol' in o[0]:
            P.pcol = [ int(i)-1 for i in o[1].split() ]
            P.pret = 'list'
        elif 'pret' in o[0]:
            P.pret = o[1]
            
        else:
            pass



    try:
        if infi and outfi:
            pass
    except NameError:
        print "No input / output specified"
        sys.exit(0)
        


    T.countocc(infi) # Initialise trigger counts
    intt  = open(infi,'r')
    outtt = open(outfi,'w')

    for ln in intt.readlines():

        ln, lnsp, Tbool = T.trigger(ln)
        #print ln, lnsp, Tbool
        ln, lnsp, Cbool = C.check(ln, T)
        #print ln, lnsp, Cbool
        ln, lnsp, Ppret = P.process(ln)
        #print ln, lnsp, Ppret
        
        if Cbool and Tbool:
            if   Ppret == 'string':
                outstr = ln
            elif Ppret == 'list':
                outstr = ''
                for sp in lnsp:
                    outstr += str(sp) + ' '
                outstr += ' \n'
            outtt.write(outstr)

        else:
            pass

    intt.close()
    outtt.close()
    sys.exit(0)


# =========================================================
# MAIN

if __name__ == "__main__":

    sopts = 'hf:o:m:'
    lopts = ['tstr=','tend=','this=','tocc=','tlen=',
             'cstr=','clen=','ctyp=','cnot=','cnum=','ccom=',
             'pcol=','pret=']
    try:
        opts, xargs = getopt.getopt(sys.argv[1:], sopts, lopts)
    except getopt.GetoptError, err:
        print "Unknown execute argument: ", str(err)
        sys.exit(2)


    T = Trigger()
    C = Check()
    P = Process()

    for o in opts:
        # I/O
        if   o[0] == '-h':
            print_help()
        elif o[0] == '-f':
            infi = o[1]
        elif o[0] == '-o':
            outfi = o[1]
        # TRIGGER   
        elif 'tstr' in o[0]:
            T.tstr = o[1]
        elif 'tend' in o[0]:
            T.tend = o[1]
        elif 'this' in o[0]:
            T.this = True
        elif 'tocc' in o[0]:
            T.tocc = int(o[1])
        elif 'tlen' in o[0]:
            T.tlen = int(o[1])
        # CONTROLLER
        elif 'cstr' in o[0]:
            C.cstr = o[1]
        elif 'clen' in o[0]:
            C.clen = int(o[1])
        elif 'ctyp' in o[0]:
            C.ctyp = o[1]
        elif 'cnot' in o[0]:
            C.cnot = o[1]
        elif 'cnum' in o[0]:
            C.cnum = int(o[1])
        elif 'ccom' in o[0]:
            C.ccom = o[1]
        # PROCESSOR
        elif 'pcol' in o[0]:
            P.pcol = [ int(i)-1 for i in o[1].split() ]
            P.pret = 'list'
        elif 'pret' in o[0]:
            P.pret = o[1]
            
        else:
            pass



    try:
        if infi and outfi:
            pass
    except NameError:
        print "No input / output specified"
        sys.exit(0)
        


    T.countocc(infi) # Initialise trigger counts
    intt  = open(infi,'r')
    outtt = open(outfi,'w')

    for ln in intt.readlines():

        ln, lnsp, Tbool = T.trigger(ln)
        #print ln, lnsp, Tbool
        ln, lnsp, Cbool = C.check(ln, T)
        #print ln, lnsp, Cbool
        ln, lnsp, Ppret = P.process(ln)
        #print ln, lnsp, Ppret
        
        if Cbool and Tbool:
            if   Ppret == 'string':
                outstr = ln
            elif Ppret == 'list':
                outstr = ''
                for sp in lnsp:
                    outstr += str(sp) + ' '
                outstr += ' \n'
            outtt.write(outstr)

        else:
            pass

    intt.close()
    outtt.close()
    sys.exit(0)
                

        
        

        



        
        
                
    

    
        
