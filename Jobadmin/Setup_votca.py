#!/usr/bin/python
import numpy as np
import sys
import subprocess as sp
import os
import errno
import shutil
import re
import argparse 
import lxml.etree as lxml
from __tools__ import MyParser
from __tools__ import cd
from __tools__ import query_yes_no
from __xtpAtom__ import atom
from __xtpMolecule__ import molecule





parser=MyParser(description="Environment to do run multiple votca calculations")
parser.add_argument("--suffix",type=str,default="",help="Suffix to append to foldernames")
parser.add_argument("--jobfile",type=str,required=True,help="File with paths to grofiles")
parser.add_argument("--template",type=str,required=True,help="Folder, from which to take optionfiles from")
parser.add_argument("--mapfile",type=str,default="system.xml",help="Name of mapfile. Default:system.xml")
parser.add_argument("--sqlfile",type=str,default="system.sql",help="Name of mapfile. Default:system.sql")
parser.add_argument("--neighbourlist", action='store_const', const=1, default=0,help="Make neighbourlist")
parser.add_argument("--createdirs", action='store_const', const=1, default=0,help="Create directories")
parser.add_argument('-p',"--map", action='store_const', const=1, default=0,help="Map system")
parser.add_argument("--iexcitoncl", action='store_const', const=1, default=0,help="Calculate exciton coupling in classical limit")
parser.add_argument("--ianalyze", action='store_const', const=1, default=0,help="Run ianalyze")
parser.add_argument("--izindo", action='store_const', const=1, default=0,help="Run izindo")
parser.add_argument('--einternal', action='store_const', const=1, default=0,help="Run einternal")
parser.add_argument('--xqmmm', action='store_const', const=1, default=0,help="Run xqmmm")
parser.add_argument('--eanalyze', action='store_const', const=1, default=0,help="Run eanalyze")
parser.add_argument("--ewald", action='store_const', const=1, default=0,help="Use ewald only write,read and local work")
parser.add_argument("--zmultipole",action='store_const', const=1, default=0,help="Run zmultipole")
parser.add_argument("--sub",action='store_const', const=1, default=0,help="Run on cluster")
parser.add_argument("--local",action='store_const', const=1, default=0,help="Run locally")
parser.add_argument("--write",action='store_const', const=1, default=0,help="Write jobfile")
parser.add_argument("--read",action='store_const', const=1, default=0,help="Read jobfile")
parser.add_argument("--kmc", action='store_const', const=1, default=0,help="Run kmc")
parser.add_argument("--egwbse", action='store_const', const=1, default=0,help="Run egwbse")
parser.add_argument("--igwbse", action='store_const', const=1, default=0,help="Run igwbse")
parser.add_argument("--stateserver", action='store_const', const=1, default=0,help="Run stateserver")
parser.add_argument("--kmcjobfile", type=str,default="jobset.csv",help=".csv File in which the kmc jobs are stored")
parser.add_argument("--tprfile", default="topol.tpr",help="Name of tpr file. Default=topol.tpr")


args=parser.parse_args()








class votcafolder(object):
	
	def __init__(self,name,template,grofile):
		self.name=name
		self.path=os.path.join(os.getcwd(),name)
		self.template=os.path.abspath(template)
		self.sql=os.path.join(self.path,args.sqlfile)
		self.optfiles=os.path.join(self.path,"OPTIONFILES/")
		self.map=os.path.join(self.path,args.mapfile)
		self.grofile=grofile

	def setupdir(self,tprfile):
		os.mkdir(self.path)
		os.mkdir(os.join.path(self.path,"MP_FILES"))
		sp.call("cp {}/MP_FILES/* {}/MP_FILES".format(self.template,self.path),shell=True)
		sp.call("ln -s {}/QC_FILES {}/QC_FILES".format(self.template,self.path),shell=True)
		os.mkdir(os.path.join(self.path,"MD_FILES"))
		os.mkdir(self.optfiles)
		shutil.copy(os.path.join(self.template,"MD_FILES/"+tprfile),os.path.join(self.path,"MD_FILES"))	   
		shutil.copy(self.grofile,os.path.join(self.path,"MD_FILES"))
		print "Creating {}".format(self.name)

	def mapsystem(self,mapfile,tprfile):	 
		shutil.copyfile(os.path.join(self.template,mapfile),self.map)
		tprfile=os.path.join(self.path,"MD_FILES/"+os.path.basename(tprfile))
		grofile=os.path.join(self.path,"MD_FILES/"+os.path.basename(self.grofile))	   
		with cd(self.path):
			print "Mapping {}".format(self.name)
			#print "xtp_map -s {} -t {} -c {} -f {} ".format(os.path.join(self.path,mapfile),tprfile,grofile,self.sql)
			sp.check_output("xtp_map -s {} -t {} -c {} -f {} > map.log".format(self.map,tprfile,grofile,self.sql),shell=True,stderr=sp.STDOUT)
			sp.check_output("xtp_dump -e trajectory2pdb -f {}".format(self.sql),shell=True,stderr=sp.STDOUT)

	def readoptionfile(self,name,calcname=None):
		if calcname==None:
			calcname=name
		templatefile=os.path.join(self.template,"OPTIONFILES/"+name+".xml")
		parser=lxml.XMLParser(remove_comments=True)
		tree = lxml.parse(templatefile,parser)
		root = tree.getroot()	  
		for i in root:
			if i.tag!=calcname:
				root.remove(i)  
		return root

	def writeoptionfile(self,root,name):
		optionfile=os.path.join(self.optfiles,name+".xml")
		with open(optionfile, 'w') as f:
			f.write(lxml.tostring(root, pretty_print=True))

	def neighborlist(self):
		name="xneighborlist"
		self.writeoptionfile(self.readoptionfile(name),name)
		#print "xtp_run -e {} -o OPTIONFILES/{}.xml -f {}".format(name,name,os.path.basename(self.sql))
		with cd(self.path):
			print "Setting up neighborlist for {}".format(self.name)
			sp.check_output("xtp_run -e {} -o OPTIONFILES/{}.xml -f {} > neighborlist.log".format(name,name,os.path.basename(self.sql)),shell=True,stderr=sp.STDOUT)

	def einternal(self):
		name="xeinternal"
		self.writeoptionfile(self.readoptionfile(name),name)
		with cd(self.path):
			print "Importing internal energies for {}".format(self.name)
			sp.check_output("xtp_run -e {} -o OPTIONFILES/{}.xml -f {}".format(name,name,os.path.basename(self.sql)),shell=True,stderr=sp.STDOUT)

	def iexcitoncl(self):	   
		name="iexcitoncl"
		jobfile=os.path.join(self.path,"{}.jobs".format(name))
		mpsfile=os.path.join(self.path,"mps.tab".format(name))
		
		if args.write:
			root=self.readoptionfile(name)
			for entry in root.iter(name):		   
				entry.find("mapping").text=self.map
				entry.find("emp_file").text=mpsfile
				entry.find("job_file").text=jobfile
			self.writeoptionfile(root,name)
			with cd(self.path):
				print "Writing iexcitoncl jobfile for {}".format(self.name)
				sp.check_output("xtp_parallel -e {} -o  OPTIONFILES/{}.xml -f {} -j write -s 0 > iexcitoncl.log".format(name,name,os.path.basename(self.sql)),shell=True,stderr=sp.STDOUT)
		if args.local:	
			with cd(self.path):
				print "Running iexcitoncl locally for {}".format(self.name)		
				sp.check_output("xtp_parallel -e {} -o  OPTIONFILES/{}.xml -f {} -j run -c 20000 -t 4 -s 0 >> iexcitoncl.log".format(name,name,os.path.basename(self.sql)),shell=True,stderr=sp.STDOUT)
		if args.read:
			with cd(self.path):
				print "Reading iexcitoncl jobfile for {}".format(self.name)		
				sp.check_output("xtp_parallel -e {} -o  OPTIONFILES/{}.xml -f {} -j read >> iexcitoncl.log".format(name,name,os.path.basename(self.sql)),shell=True,stderr=sp.STDOUT)

	def ianalyze(self):
		name="xianalyze"
		self.writeoptionfile(self.readoptionfile(name),name)
		with cd(self.path):
			print "Running xianalyze for {}".format(self.name)
			sp.check_output("xtp_run -e {} -o OPTIONFILES/{}.xml -f {} -s 0 > ianalyze.log".format(name,name,os.path.basename(self.sql)),shell=True)

	def izindo(self):
			name="izindo"
			self.writeoptionfile(self.readoptionfile(name),name)
			with cd(self.path):
				print "Running izindo for {}".format(self.name)
				sp.check_output("xtp_run -e {} -o OPTIONFILES/{}.xml -f {} -t 4 > izindo.log".format(name,name,os.path.basename(self.sql)),shell=True)

	def xqmmm(self):
			name="xqmmm"
			root=self.readoptionfile(name)
			for entry in root.iter(name):		   
				dftoptions=entry.find("dftpackage").text
				shutil.copyfile(os.path.join(self.template,dftoptions),os.path.join(self.path,dftoptions))
				gwbse=entry.find("gwbse").text
				gwbseoptions=gwbse.find("gwbse_options").text
				shutil.copyfile(os.path.join(self.template,gwbseoptions),os.path.join(self.path,gwbseoptions))
				entry.find("job_file").text=os.path.join(self.path,jobfile)
			self.writeoptionfile(root,name)
			with cd(self.path):
				print "Running xqmmm for {}".format(self.name)
				sp.check_output("xtp_parallel -e {} -o OPTIONFILES/{}.xml -f {} -t 1 -c 1 -s 0 > xqmmm.log".format(name,name,os.path.basename(self.sql)),shell=True)

	def stateserver(self):
		name="stateserver"
		self.writeoptionfile(self.readoptionfile(name),name)
		with cd(self.path):
			print "Creating mps.tab file for {}".format(self.name)
			sp.call("xtp_run -e {} -o OPTIONFILES/{}.xml -f {} -s 0 > stateserver.log".format(name,name,os.path.basename(self.sql)),shell=True,stderr=sp.STDOUT)
	

	def egwbse(self):

		if args.write:
			name="egwbse"
			jobfile="egwbse.jobs"
			root=self.readoptionfile(name)
			for entry in root.iter(name):		   
				dftoptions=entry.find("dftpackage").text
				shutil.copyfile(os.path.join(self.template,dftoptions),os.path.join(self.path,dftoptions))
				gwbseoptions=entry.find("gwbse_options").text
				shutil.copyfile(os.path.join(self.template,gwbseoptions),os.path.join(self.path,gwbseoptions))
				entry.find("job_file").text=os.path.join(self.path,jobfile)
				try:
					espoptions=entry.find("esp_options").text
					shutil.copyfile(os.path.join(self.template,espoptions),os.path.join(self.path,espoptions))
				except:
					print "Running without espfits"
			self.writeoptionfile(root,name)
			with cd(self.path):
				print "Running egwbse to write jobfile {} for {}".format(jobfile,self.name)
				sp.check_output("xtp_parallel -e {} -o OPTIONFILES/{}.xml -f {} -j write -s 0 > egwbse.log".format(name,name,os.path.basename(self.sql)),shell=True)

		elif args.local:
			name="egwbselocal"
			calcname="egwbse"
			self.writeoptionfile(self.readoptionfile(name,calcname=calcname),name)
			with cd(self.path):
				print "Running egwbse locally for {}".format(self.name)
				sp.call("xtp_parallel -e gwbse -o OPTIONFILES/{}.xml -f {} -s 0 -t 1 -c 4 > egwbselocal.log".format(name,os.path.basename(self.sql)),shell=True)


		elif args.read:
			name="egwbse"
			jobfile="egwbse.jobs"
			with cd(self.path):
				print "Running egwbse to read jobfile {} for {}".format(jobfile,self.name)
				sp.check_output("xtp_parallel -e {} -o OPTIONFILES/{}.xml -f {} -j read >> egwbse.log".format(name,name,os.path.basename(self.sql)),shell=True)



	def igwbse(self):

		if args.write:
			name="igwbse"
			jobfile="igwbse.jobs"
			root=self.readoptionfile(name)
			for entry in root.iter(name):		   
				dftoptions=entry.find("dftpackage").text
				shutil.copyfile(os.path.join(self.template,dftoptions),os.path.join(self.path,dftoptions))
				gwbseoptions=entry.find("gwbse_options").text
				shutil.copyfile(os.path.join(self.template,gwbseoptions),os.path.join(self.path,gwbseoptions))
				couplingoptions=entry.find("bsecoupling_options").text
				shutil.copyfile(os.path.join(self.template,couplingoptions),os.path.join(self.path,couplingoptions))
				entry.find("job_file").text=os.path.join(self.path,jobfile)
			self.writeoptionfile(root,name)
			with cd(self.path):
				print "Running igwbse to write jobfile {} for {}".format(jobfile,self.name)
				sp.check_output("xtp_parallel -e {} -o OPTIONFILES/{}.xml -f {} -j write -s 0 > igwbse.log".format(name,name,os.path.basename(self.sql)),shell=True)

		elif args.local:
			name="igwbselocal"
			calcname="igwbse"
			self.writeoptionfile(self.readoptionfile(name,calcname=calcname),name)
			with cd(self.path):
				print "Running igwbse locally for {}".format(self.name)
				sp.call("xtp_parallel -e gwbse -o OPTIONFILES/{}.xml -f {} -s 0 -t 1 -c 4 > igwbselocal.log".format(name,os.path.basename(self.sql)),shell=True)


		elif args.read:
			name="igwbse"
			jobfile="igwbse.jobs"
			with cd(self.path):
				print "Running igwbse to read jobfile {} for {}".format(jobfile,self.name)
				sp.check_output("xtp_parallel -e {} -o OPTIONFILES/{}.xml -f {} -j read >> igwbse.log".format(name,name,os.path.basename(self.sql)),shell=True)
			

	def ewald(self):

		if args.write:
			name='stateserver'
			self.writeoptionfile(self.readoptionfile(name),name)
			with cd(self.path):
				print "Running stateserver for ewald for {}".format(self.name)
				sp.check_output("xtp_run -e {} -o OPTIONFILES/{}.xml -f {} -s 0 > stateserver.log".format(name,name,os.path.basename(self.sql)),shell=True)

			name="xjobwriter"
			self.writeoptionfile(self.readoptionfile(name),name)

			with cd(self.path):
				print "Running xjobwriter for ewald for {}".format(self.name)
				sp.check_output("xtp_run -e {} -o OPTIONFILES/{}.xml -f {} -s 0 > jobwriter.log".format(name,name,os.path.basename(self.sql)),shell=True)
				sp.call("mv xjobwriter.mps.chrg.xml ewald.jobs",shell=True)

		elif args.read:
			name="ewaldparser"
			with cd(self.path):
				print "Running ewaldparser for ewald for {}".format(self.name)
				sp.call("xtp_parseewald.py -j ewald.jobs -f {}".format(os.path.basename(self.sql)),shell=True)

		elif args.local:
   
			name="ewaldlocal"
			calcname="ewald"
			self.writeoptionfile(self.readoptionfile(name,calcname=calcname),name)
			with cd(self.path):
				print "Running ewald locally for {}".format(self.name)
				sp.call("xtp_parallel -e pewald3d -o OPTIONFILES/{}.xml -f {} -s 0 -t 4 -c 128 > ewaldlocal.log".format(name,os.path.basename(self.sql)),shell=True)
				sp.call("xtp_parseewald.py -j ewald.jobs -f {}".format(os.path.basename(self.sql)),shell=True)

	def eanalyze(self):
		name="xeanalyze"
		
		self.writeoptionfile(self.readoptionfile(name),name)
		with cd(self.path):
			print "Running xeanalyze for {}".format(self.name)
			sp.check_output("xtp_run -e {} -o OPTIONFILES/{}.xml -f {} -s 0 > eanalyze.log".format(name,name,os.path.basename(self.sql)),shell=True)
			

	def zmultipole(self):
		
		if args.local or args.sub:
			name="zmultipole"  
			self.writeoptionfile(self.readoptionfile(name),name)
			with cd(self.path):
				if args.local:		   
					print "Running zmultipole for {}".format(self.name)
					sp.check_output("xtp_run -e {} -o OPTIONFILES/{}.xml -f {} -t 4 > zmultipole_local.log".format(name,name,os.path.basename(self.sql)),shell=True)
				elif args.sub:
					print "Running zmultipole for {} on cluster".format(self.name)  
					sp.check_output("xtp_jobstarterPARALLEL.py -o OPTIONFILES/{}.xml -f {} --sub  > zmultipole_cluster.log".format(name,os.path.basename(self.sql)),shell=True)

		elif args.read:
			name="eimport"
			self.writeoptionfile(self.readoptionfile(name),name)
			with cd(self.path):
				print "Importing site energies from directory ZMULTIPOLE for {}".format(self.name)
				sp.call("cat ZMULTIPOLE/*.dat > zmultipole.dat",shell=True)
				sp.check_output("xtp_run -e {} -o OPTIONFILES/{}.xml -f {}  > zmultipole_read.log".format(name,name,os.path.basename(self.sql)),shell=True)
				
		   

	def kmc(self):
		jobfile=args.kmcjobfile
		p = re.compile('([-+]?([0-9]*\.[0-9]+|[0-9]+))K\_')
		
		temp=p.search(self.name)
		#print self.name
		if temp==None:
			Temperature=300
		else:
			Temperature=float(temp.group(1))
		if args.read:
			with cd(self.path):
				sp.call("xtp_kmc_jobresults.py --jobset {} --jobfolder kmc_jobs".format(jobfile),shell=True)
				print re.sub(".csv","_results.csv",jobfile)
				sp.call("xtp_kmc_jobresults_mobility.py --csv {}".format(re.sub(".csv","_results.csv",jobfile)),shell=True)
		else:
			print "Temperature set to {} for {}".format(Temperature,self.name)
			shutil.copyfile(os.path.join(self.template,jobfile),os.path.join(self.path,jobfile))
			with cd(self.path):
				if args.sub:
					print "Running kmc for {} at T={}K".format(self.name,Temperature)
					sp.call("xtp_kmc_jobstarterPARALLEL.py -j {} -c parse -sub -T {}".format(jobfile,Temperature),shell=True)
				
	

class votcabundle(object):

	def __init__(self):
		self.listofpaths=[]
		self.joblist=[]

	def read(self,grofiles):	   
		with open(grofiles,"r") as f:
			lines=f.readlines()
			for line in lines:
				if line[0]=="#":
					continue
				path=line.split('\n')[0]
				if not os.path.isabs(path):
					directory=os.path.dirname(os.path.abspath(grofiles))
					path=os.path.join(directory,path)
				self.listofpaths.append(path)
			 
					


	def setupjobs(self):
		print "Working in the following folders:" 
		for path in self.listofpaths:
			name=os.path.splitext(os.path.basename(path))[0]+args.suffix
			print name
			self.joblist.append(votcafolder(name,args.template,path))
		print ""
		answer=query_yes_no("Proceed?")
		if answer==False:
			print "Shutting down"
			sys.exit(2)

	def createdirs(self):
		for job in self.joblist:
			job.setupdir(args.tprfile)			

	def mapjobs(self):
		for job in self.joblist:
			job.mapsystem(args.mapfile,args.tprfile)

	def neighborlists(self):
		for job in self.joblist:
			job.neighborlist()

	def excitons(self):
		for job in self.joblist:
			job.iexcitoncl()

	def ianalyze(self):
		for job in self.joblist:
			job.ianalyze()

	def stateserver(self):
		for job in self.joblist:
			job.stateserver()	

	def ewald(self):
		for job in self.joblist:
			job.ewald()

	def egwbse(self):
		for job in self.joblist:
			job.egwbse()

	def igwbse(self):
		for job in self.joblist:
			job.igwbse()


	def einternal(self):
		for job in self.joblist:
			job.einternal()

	def eanalyze(self):
		for job in self.joblist:
			job.eanalyze()


	def kmc(self):
		for job in self.joblist:
			job.kmc()

	def zmultipole(self):
		for job in self.joblist:
			job.zmultipole()
	def izindo(self):
		for job in self.joblist:
			job.izindo()


bundle=votcabundle()
bundle.read(args.jobfile)
bundle.setupjobs()
if args.createdirs:
	bundle.createdirs()
if args.map:
	bundle.mapjobs()
if args.neighbourlist:
	bundle.neighborlists()
if args.stateserver:
	bundle.stateserver()
if args.einternal:
	bundle.einternal()
if args.iexcitoncl:
	bundle.excitons()
if args.izindo:
	bundle.izindo()
if args.ianalyze:
	bundle.ianalyze()
if args.ewald:
	bundle.ewald()
if args.egwbse:
	bundle.egwbse()
if args.igwbse:
	bundle.igwbse()
if args.zmultipole:
	bundle.zmultipole()
if args.xqmmm:
	bundle.xqmmm()
if args.eanalyze:
	bundle.eanalyze()
if args.kmc:
	bundle.kmc()

	
		
