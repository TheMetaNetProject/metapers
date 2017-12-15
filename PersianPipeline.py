#!/usr/bin/python
#  -*- coding: utf-8 -*-

import sys
import codecs
import json
import sys, logging, pprint
import re
from nltk.tag.stanford import POSTagger
from behmalt import MaltParser
sys.stdout = codecs.getwriter("utf8")(sys.stdout)


class PersianPipeline:

	def __init__(self, posTagModelPath, posTaggerPath, parserModelPath, workingDir):
		
		try:
			self.posTagger = POSTagger(posTagModelPath, posTaggerPath,"UTF-8")
			print "pos tagger is loaded"
		except:
			print "Error in loading POS tagger"
		
		try:
			self.parser = MaltParser(tagger=None, mco = parserModelPath, working_dir= workingDir)
			print "parser is loaded"
		except:
			print "Error in loading the MALT Parser"

	
	# tokenizes, fixes some of the detached affixes
	def preprocess(self, s):
		# remove the diacritics
		drs = s
		for c in range(1611, 1619):
			drs = drs.replace(unichr(c),"")
		
		# tokenize the sentence
		ts = self.seperatePuncs(drs)
		# fix the affixes
		afs = self.fixAffixes(ts)
		
		# replace slashes and pounds and underlines
		afs= afs.replace("#","-")
		afs= afs.replace("/","-")
		afs = afs.replace("_","-")
		return afs

	
	# tokenize a persian sentence
	def seperatePuncs(self, s):
		
		s = re.sub(ur"([\[{\(\\`\"‚„†‡‹‘’“”•\.–—›««])", r"\1 ", s)
		s = re.sub(ur"([\]}\'\`\"\),;:!\?\%‚„…†‡‰‹‘’“”•–—›»\.])", r" \1", s)
		# persian specific
		s = re.sub(ur"([،؛؟،\.])", r" \1 ", s)
		s = s.replace("  ", " ")
		return s
	
	

	def fixAffixes(self, sent):
		suffList = [u"ها", u"های"]
		sSent = sent.split(" ")
		newTokSent = []
		sentLen = len(sSent)
		i = 0
		while i < sentLen:

			if sSent[i] in suffList:
				print "+++ Affix problem got fixed"
				# attach the suffix to the previous word
				newTokSent[-1] = newTokSent[-1] + u"\u200c" + sSent[i]
			else:
				newTokSent.append(sSent[i])
			i += 1
		return " ".join(newTokSent)

	
		
	def posTagASentence(self, sent):
		try:
			sent = sent.replace("/","-")
			posSent = self.posTagger.tag(sent.split())
			return posSent
		except:
			return None
		
	
				
	# Function reads in a POS tagged sentence (list) and if there are two adjacent verbs, it attaches them together and make them one word.
	def attachPerCompounds(self, posSent):
			
		prFlag = False
		ct = senCt = prCt = 0
		i = 0
		senCt += 1
		pos = wd = outWd = ""
		sentLen = len(posSent)
		newPOSSent = []
		while i < sentLen - 1:
			ct += 1
			tok = posSent[i]
			nexTok = posSent[i+1]
			(wd, pos) = tok
			(nwd, npos) = nexTok
			outWd = wd 
			if pos == "V":
				if npos == "V":
					prFlag = True
					outWd = wd + '^' + nwd
					pos = "V"
					i += 1
			# attaching the "mi" prefix for present continious form
			if npos == "V" and wd.strip() == u"می":		
				prFlag = True
				outWd = u"می" + u"\u200c" + nwd
				pos = "V"
				i += 1
				#print "the mi case "
				#t.write("outWd:" + outWd + "\n")
				
				
			newPOSSent.append((outWd, pos))
			i += 1
		
		# don't forget the last word (if not processed)
		if i < sentLen:
			ct += 1
			tok = posSent[-1]
			newPOSSent.append(tok)
			
		# counting the lines with compound verbs patterns
		if prFlag:
			prCt += 1
		#print prCt
		
		#t.write(newPOSSent[-2][0] + "--" + newPOSSent[-1][0] + "\n")
		return newPOSSent
################################################################
		
		
	def parseATaggedSentence(self, tSent):
		try:
			compTSent = self.attachPerCompounds(tSent)
			depParse = self.parser.tagged_parse(compTSent)
			return depParse
		except:
			print "Error in parsing a sentence!"
			return None
		
	def parseASentence(self, sent):
		pass
		

def main():
	
	posModPath = "/u/metanet/persianCode/PersianPipeline/models/persian-train.model"
	posJar = "/u/metanet/nlptools/stanford-postagger-full-2014-06-16/stanford-postagger.jar"
	#parserModPath = "test"
	parseModPath = "PerParseModelWithCompoundTerms"
	#parserPath = "/u/metanet/nlptools/maltparser-1.8/"
	workDir = "./" 
	ct = 0

	sampleF = codecs.open(sys.argv[1], "r", "utf-8")
	# instantiating the persian pipeline with path to the parser and pos tagger and their models
	pPipeline = PersianPipeline(posModPath, posJar, parseModPath, workDir)
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
		taggedLine = pPipeline.posTagASentence(tokLine)
		print "tagged", 
		
		parsedLine = pPipeline.parseATaggedSentence(taggedLine)
		# make the compounds more readable
		pl = parsedLine.to_conll(10).replace("^", " ")
		print "parsed"
		outFile.write(pl + "\n")
		

if __name__ == "__main__":
    status = main()

