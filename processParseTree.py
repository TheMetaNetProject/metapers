#!/usr/bin/python
#  -*- coding: utf-8 -*-

import sys
import codecs
import json
import sys, logging, pprint
import re
from nltk.tag.stanford import POSTagger
from behmalt import MaltParser
from PersianPipeline import *

sys.stdout = codecs.getwriter("utf8")(sys.stdout)

# extracts MOZ patterns from the the tree 

def extractSubjObj(p, isSubj):
	pList = p.split("\n")
	senLen = len(pList)
	sFlag = oFlag = False
	start = end = 0
	phrList = []
	i = -1
	j = k = 0
	
	while i < senLen -2:
		i += 1
		pL = pList[i]		
		[cIx, cWd, nn1, cPos, nn2, nn3, cHd, cRle, nn4, nn5] = pL.split("\t")
		
		#if tFlag and cPos:
		if isSubj and cRle == "SBJ":
			 sFlag = True
			 sSeg = cWd 
			 start = int(cIx)
			 end = start
		elif cRle == "OBJ":
			 oFlag = True
			 oSeg = cWd 
			 start = int(cIx)
			 end = start
		j = start - 1
		k = end - 1

		if oFlag:
			# go through the start of the phrase and look back at the previous words
			while j > 0 and j > start -4:
				# the starting word of the tosifi phrase and its previous word
				[sIx, sWd, nn1, sPos, nn2, nn3, sHd, sRle, nn4, nn5] = pList[j].split("\t")
				[pIx, pWd, nn1, pPos, nn2, nn3, pHd, pRle, nn4, nn5] = pList[j-1].split("\t")
				  
				if pHd == sIx and pHd == cIx and pPos != "CONJ":
					oSeg = pWd + " " + oSeg
				else:
					break
				j -= 1
			#out.write("ophr:" + oSeg + "\n")
			# add the verb to the end of the object phrase
			oSeg = oSeg + " " + pList[int(cHd)-1].split("\t")[1] 
			
			phrList.append(oSeg)
			oFlag = False
		elif sFlag:	
			while k < senLen-2 and k < end + 2:
				# the end word of the tosifi phrase
				[eIx, eWd, nn1, ePos, nn2, nn3, eHd, eRle, nn4, nn5] = pList[k].split("\t")
				# the word after the end word
				[aIx, aWd, nn1, aPos, nn2, nn3, aHd, aRle, nn4, nn5] = pList[k+1].split("\t")
				if (aHd == eIx or aHd == cIx) and aPos != "CONJ":
					sSeg =  sSeg + " " + aWd
				else:
					break
				k += 1
			#out.write("sphr:" + sSeg + "\n")
			
			# add the verb to the end of the subject phrase
			sSeg = sSeg + " " + pList[int(cHd)-1].split("\t")[1]
			phrList.append(sSeg)
			sFlag = False
	return phrList
		
def extractObj(p, out):
	pass

def extractVerb (p):
	pList = p.split("\n")
	senLen = len(pList)
	vFlag = False
	vList = []
	i = 0
	j = 0
	while i < senLen -1:
		pL = pList[i]		
		[cIx, cWd, nn1, cPos, nn2, nn3, cHd, cRle, nn4, nn5] = pL.split("\t")
		
		#if tFlag and cPos:
		if cPos == "V":
			 vFlag = True
			 vSeg = cWd 
			 start = int(cIx)
			 end = start
		if vFlag:
			# go through the start of the phrase and look back at the previous words
			j = start - 1
		
			while (j > 0) and j > (start - 8):
				# the starting word of the verb phrase and its previous word
				[sIx, sWd, nn1, sPos, nn2, nn3, sHd, sRle, nn4, nn5] = pList[j].split("\t")
				  
				if cIx == sHd and (sPos == "N" or ((int(sIx) == (start - 1)) and (sPos == "ADJ"))):
					vSeg = sWd + " " + vSeg
				j -= 1
			# done with expansion. time to write and reset
			#out.write("vphr:" + vSeg + "\n")
			vList.append(vSeg)
			vSeg = ""
			vFlag = False
			
		i += 1
	return vList

def extractMOZ(p):
	mozList = []
	pList = p.split("\n")
	senLen = len(pList)
	dHash = {x:[] for x in range(senLen)}
	wdList = ["root"]
	mozSeg = ""
	endMoz = ""
	try:
		for pLine in pList[:(senLen-1)]:
			#print pLine
			spPLine = pLine.split("\t")
			inx = int(spPLine[0])
			wd = spPLine[1]
			pos = spPLine[3]
			head = int(spPLine[6])
			dHash[inx].append(head) 
			role = spPLine[7]
			wdList.append(wd)
			if role == "MOZ": 
					# check if the previous word is dependent on this word
					if mozSeg == "" and inx > 2 and (inx -1) in dHash[inx-2]:
						mozSeg =  wdList[inx-2]
					mozSeg = mozSeg + " " + wdList[head]
					mozSeg = mozSeg.strip() 
			else:
				if mozSeg != "":
					mozSeg += " " + wdList[-2]
					
					#out.write("Moz:" + mozSeg + "\n")
					mozList.append(mozSeg)
					mozSeg = ""
		return mozList
	except:
		return []

def extractTosifiPhrase(p):
	pList = p.split("\n")
	senLen = len(pList)
	tsSeg = ""
	tFlag = False
	i = 0
	j = 0
	tosList = []
	while i < senLen -2:
		pL = pList[i]
		nL = pList[i+1]
		
		[cIx, cWd, nn1, cPos, nn2, nn3, cHd, cRle, nn4, nn5] = pL.split("\t")
		[nIx, nWd, nn1, nPos, nn2, nn3, nHd, nRle, nn4, nn5] = nL.split("\t")
		#if tFlag and cPos:
		if cPos == "N" and nPos == "ADJ":
			 tFlag = True
			 tsSeg = cWd + " " + nWd
			 start = int(cIx)
			 end = int(nIx)
		if tFlag:
			# go through the start of the phrase and look back at the previous words
			j = start - 1
			k = end - 1
			while j > 0 and j > start -4:
				# the starting word of the tosifi phrase and its previous word
				[sIx, sWd, nn1, sPos, nn2, nn3, sHd, sRle, nn4, nn5] = pList[j].split("\t")
				[pIx, pWd, nn1, pPos, nn2, nn3, pHd, pRle, nn4, nn5] = pList[j-1].split("\t")
				  
				if sHd == pIx and pPos != "CONJ":
					tsSeg = pWd + " " + tsSeg
				else:
					break
				j -= 1
			
			while k < senLen-2 and k < end + 2:
				# the end word of the tosifi phrase
				[eIx, eWd, nn1, ePos, nn2, nn3, eHd, eRle, nn4, nn5] = pList[k].split("\t")
				# the word after the end word
				[aIx, aWd, nn1, aPos, nn2, nn3, aHd, aRle, nn4, nn5] = pList[k+1].split("\t")
				if aHd == eIx or aHd == cIx and aPos == "CONJ":
					tsSeg =  tsSeg + " " + aWd
				else:
					break
				k += 1
				
			# done with expansion. time to write and reset
			#out.write("tphr:" + tsSeg + "\n")
			tosList.append(tsSeg)
			tsSeg = ""
			tFlag = False
			
		i += 1
	return tosList		


def main():
	sys.stdout = codecs.getwriter("utf8")(sys.stdout)
	
		
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
	
	
	while True:
		ct += 1
		line = sampleF.readline()
		if not line:
			break
		print "sentence ", ct,
		
		#tokLine = pPipeline.seperatePuncs(line)  
		#tokLine = pPipeline.fixAffixes(tokLine)
		tokLine = pPipeline.preprocess(line) 
		outFile.write(tokLine)
		taggedLine = pPipeline.posTagASentence(tokLine)
		print "==> tagged ==>", 
		
		parsedLine = pPipeline.parseATaggedSentence(taggedLine)
		print "parsed ==>",
		# make the compounds more readable
		pl = parsedLine.to_conll(10).replace("^", " ")
		#extractMOZ(pl, outFile)
		#extractTosifiPhrase(pl, outFile)
		#extractVerb(pl, outFile)
		#extractSubjObj(pl, outFile, True)
		print "phrases are extracted"
		outFile.write(pl + "\n")
	
if __name__ == "__main__":
    main()
