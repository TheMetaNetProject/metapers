#!/usr/bin/python
#  -*- coding: utf-8 -*-

import sys
import codecs
import json
import sys
# import logging, pprint
import re
#from nltk.tag.stanford import POSTagger
#from nltk.parse.behmalt import MaltParser
from PersianPipeline import *

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
def readLUs(fle, out, srcFlag):
	luHash = {}
	while True:
		line = fle.readline()
		if not line:
			break
		lList = line.split("\t")
		conc = lList[0]
		
		if srcFlag:
			lus = lList[-1]
		else:
			lus = lList[2]
		pastList = []
		presList = []
		
		for c in range(1611, 1619):
			lus = lus.replace(unichr(c),"")
		
		luList = lus.split(",")
		"""
		if srcFlag:
			print len(luList)
			out.write("tgt LU List is:" + luList[0])
		
		"""
		for lu in luList:
			pastList = []
			presList = []
			pluralList = []
			lu = lu.strip()
			if lu.find("_") > -1:
				# infinitive form:
				if lu.endswith("_i"):
					lu = lu.replace("_i","")
				elif lu.endswith("_ps"):
					lu = lu.replace("_ps","")
					pastList = inflectVerbs(out, lu, True) 
				elif lu.endswith("_ts"):
					lu = lu.replace("_ts","")
					presList = inflectVerbs(out, lu, False) 
				elif lu.endswith("_n"):
					lu = lu.replace("_n","")
					pluralList = inflectNouns(out, lu) 


				
			# if lu is already seen			
			if lu in luHash:
				if conc not in luHash[lu]:
					luHash[lu].append(conc)
				# we have already recorded this concept for this lu

			else:
				luHash[lu] = [conc]
			
			# store all past inflections
			for pi in pastList:
				# if already seen			
				if pi in luHash:
					if conc not in luHash[pi]:
						luHash[pi].append(conc)
					# we have already recorded this concept for this lu
				else:
					luHash[pi] = [conc]
					
			# store all present inflections
			for ti in presList:
				# if already seen			
				if ti in luHash:
					if conc not in luHash[ti]:
						luHash[ti].append(conc)
					# we have already recorded this concept for this lu
				else:
					luHash[ti] = [conc]
			

			# store all plural noun inflections
			for pn in pluralList:
				# if already seen			
				if pn in luHash:
					if conc not in luHash[pn]:
						luHash[pn].append(conc)
					# we have already recorded this concept for this lu
				else:
					luHash[pn] = [conc]

			
	return luHash

def locateLUsInSent(out, luList, sent):
	sentList = sent.split()
	for lu in luList:
		spaceCt = lu.strip().count(" ")
		# for single term LUs, look in the tokenized list
		if spaceCt == 0:
			if lu in sentList:
				out.write("found-s:" + lu + "\n")
		# for compound LUs, look in the actual sentence
		elif sent.find(lu.strip()) > -1:
			out.write("found-c:" + lu + "\n")
		

def inflectNouns(out, n):
	infs = []
	infs.append(n + u"ها")
	infs.append(n + u"های")
	infs.append(n + u"هایی")
	infs.append(n + u"\u200c" + u"ها")
	infs.append(n + u"\u200c" + u"های")
	infs.append(n + u"\u200c" + u"هایی")
	for t in infs:
		out.write(t + "--")
	return infs
	
def inflectVerbs(out, stem, isPast):
		infs = []
		persSuffs = [u"م", u"ی", u"د", u"یم", u"ید", u"ند"]
		persSuffs2 = [u"ام", u"ای", u"است", u"ایم", u"اید", u"اند"]
		persSuffs3 = [u"بودم", u"بودی", u"بود", u"بودیم", u"بودید", u"بودند", u"باشم", u"باشی", u"باشد", u"باشیم", u"باشید", u"باشند"]
		stemStart = stemStart = ""
		stemEnd = stem
		stemEnd = stem
		
		# compound verbs
		if stem.count(" ") > 0:
			# break the stem 
			bStem = stem.split()
			stemStart = " ".join(bStem[:-1])
			stemEnd = bStem[-1]
		
			
		for suff in persSuffs:
			if isPast:
				infs.append(stemStart + " " + u"خواه" + suff + u"\u200c" + stemEnd)
				infs.append(stemStart + " " + u"خواه" + suff + u" " + stemEnd )
				
				# add the suffix prooun to all except the third person
				if suff != u"د":
					infs.append(stem + suff)	
					infs.append(stemStart + " " + u"می" + stemEnd + suff)
					infs.append(stemStart + " " + u"می" + u"\u200c" + stemEnd + suff)	
					infs.append((u"داشت" + suff + " " + stemStart + " " + u"می" + stemEnd + suff).replace("  ", " "))
					infs.append(stemStart + " " + u"می" + u"\u200c" + stemEnd + suff)
					infs.append((u"داشت" + suff + " " + stemStart + " " + u"می" + u"\u200c" + stemEnd + suff).replace("  ", " "))
				else:
					infs.append(stemStart + " " + u"می" + stemEnd)
					infs.append(stemStart + " " + u"می" + u"\u200c" + stemEnd)	
					infs.append((u"داشت"  + " " + stemStart + " " + u"می" + stemEnd).replace("  ", " "))
					infs.append(stemStart + " " + u"می" + u"\u200c" + stemEnd)
					infs.append((u"داشت"  + " " + stemStart + " " + u"می" + u"\u200c" + stemEnd).replace("  ", " "))

				
			else:
				infs.append(stemStart + " " + u"ب" + stemEnd + suff)
				infs.append(stemStart + " " + u"می" + stemEnd + suff)
				infs.append(stemStart + " " + u"می" + u"\u200c" + stemEnd + suff)
				infs.append((u"دار" + suff + " " + stemStart + " " + u"می" + stemEnd + suff).replace("  ", " "))					
				infs.append(stemStart + " " + u"می" + u"\u200c" + stemEnd + suff)
				infs.append((u"دار" + suff + " " + stemStart + " " + u"می" + u"\u200c" + stemEnd + suff).replace("  ", " "))
				
				
		# for present and past participles (maazi naqli and mazi baeed) 
		if isPast:
			for suff in persSuffs2:
				infs.append(stem + u"ه\u200c" + suff)
		
			for suff in persSuffs3:
				infs.append(stem + u"ه\u200c" + suff)
		"""
		for inf in infs:
			out.write(inf + "--")
		out.write("\n")
		"""
		return infs
	
posModPath = "/u/metanet/persianCode/PersianPipeline/persian-train.model"
posJar = "/u/metanet/nlptools/stanford-postagger-full-2014-06-16/stanford-postagger.jar"
#parserModPath = "test"
parseModPath = "PerParseModelWithCompoundTerms"
parserPath = "/u/metanet/nlptools/maltparser-1.8/"
	
ct = 0

sampleF = codecs.open(sys.argv[1], "r", "utf-8")
# instantiating the persian pipeline with path to the parser and pos tagger and their models
pPipeline = PersianPipeline(posModPath, posJar, parseModPath, parserPath)
outPath = sys.argv[2]
outFile = codecs.open(outPath, "w", "utf-8")

srcLUFile = codecs.open(sys.argv[3],"r", "utf-8",)
tgtLUFile = codecs.open(sys.argv[4],"r", "utf-8",)

			
print "reading src LUs"
srcLUHash = readLUs(srcLUFile, outFile, True)
print "reading tgt LUs"
tgtLUHash = readLUs(tgtLUFile, outFile, False)
srcLUList = srcLUHash.keys()
tgtLUList = tgtLUHash.keys()

print "size of src LU List:", len(srcLUList)
print "size of tgt LU List:", len(tgtLUList)

while True:
	#if True:
	#	break
	ct += 1
	line = sampleF.readline()
	if not line:
		break
	outFile.write("sentence " + str(ct) + "\n") 
	
	#tokLine = pPipeline.seperatePuncs(line)  
	#tokLine = pPipeline.fixAffixes(tokLine)
	tokLine = pPipeline.preprocess(line) 
	outFile.write(tokLine)
	outFile.write("checking src terms\n")
	locateLUsInSent(outFile, srcLUList, tokLine)
	outFile.write("checking tgt terms\n")
	locateLUsInSent(outFile, tgtLUList, tokLine)
		
	"""
	taggedLine = pPipeline.posTagASentence(tokLine)
	print "==> tagged ==>", 
	
	
	parsedLine = pPipeline.parseATaggedSentence(taggedLine)
	print "parsed ==>",
	# make the compounds more readable
	pl = parsedLine.to_conll(10).replace("^", " ")
	"""

	