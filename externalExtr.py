#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: externalExtr
    :platform: Unix
    :synopsis: Language Model System (LMS) linguistic metaphor extractor for Persian.

Language Model System (LMS) linguistic metaphor extractor for Persian.  Uses lexicons,
unigram, bigram, and trigram frequency data which is stored by default in

``/u/metanet/extraction/persian``

This path can be changes via a initialization parameter.

"""
import segExtractor
import json
import sys, logging, pprint
import codecs
import re
import os
import random
from PersianPipeline import *
import inflectPersian
import processParseTree

REPDIR = '/u/metanet/extraction/persian/lms2/'

# the script reads in a json file, calls the extractor and generates a new
# json file (with a '.lms' extension and adds the extracted LMs to the output
# file.
# python externalExtr.py inputJsonFile

class PersianMetaphorExtractor:
    """
    The class is the main interface for Persian Metaphor Extraction.
    It includes methods for loading various lexicons and the complete
    pipeline for preprocessing, metaphor extraction, and output
    generation, and allows for the overhead of loading resources
    to be paid at initialization time.
    """
    def __init__(self, repDir=None, verbose=False):
        """
        :param repDir: path to distributional statistical data
        :type repDir: str
        :param verbose: flag for verbose messages
        :type verbose: bool
        """
        global REPDIR
        self.logger = logging.getLogger(__name__)
        # for pos tagger
        if repDir:
            self.repDir = repDir
        else:
            self.repDir= REPDIR

	print self.repDir
        self.verbose = verbose
        #B#self.fpOne = codecs.open(self.repDir + '/bigramProb.txt','r','utf-8').read()
        #B#self.fpTwo = codecs.open(self.repDir + '/lexProb.txt','r','utf-8').read()
        
        # read in the LM
        #B#self.triModel = self.readLM(self.repDir + "/cleanTextCorp-UPEC-PerTB.trigram")
        #B#self.bigModel = self.readLM(self.repDir + "/cleanTextCorp-UPEC-PerTB.bigrams")
        #B#self.uniModel = self.readLM(self.repDir + "/cleanTextCorp-UPEC-PerTB.unigrams.sortCleaned")
        
        #B#self.tgtHash = self.readInLex(self.repDir + "/tgtLexExt3.txt")
        #B#self.srcHash = self.readInLex(self.repDir + "/srcLexExt3.txt")
        
        posModPath = "/u/metanet/persianCode/PersianPipeline/models/persian-train.model"
        posJar = "/u/metanet/nlptools/stanford-postagger-full-2014-06-16/stanford-postagger.jar"
        parseModPath = "PerParseModelWithCompoundTerms"
        parserPath = "/u/metanet/nlptools/maltparser-1.8/"
        self.lemHash = {}
        self.srcHash = inflectPersian.readLUs("/u/metanet/extraction/persian/lms2/LUList.src.txt", True, self.lemHash)
        self.tgtHash = inflectPersian.readLUs("/u/metanet/extraction/persian/lms2/LUList.tgt.txt", False, self.lemHash)
        self.srcLUList = self.srcHash.keys()
        self.tgtLUList = self.tgtHash.keys()
        self.stopList = [u"آن", u"ان", u"این", u"آنها", u"آنان", u"من", u"تو", u"او", u"ما", u"شما", u"ایشان", u"در", u"انها"]

        # note: parser's working directory is repDir.  That's the place NLTK writes the temp parsing files
        # We need to have a symbolic link from that working directory to the actual persian parse model (*.mco)
        self.perPipeline = PersianPipeline(posModPath, posJar, parseModPath, self.repDir)
        print "done with loading the persian pipeline"
        #print len(self.srcHash)
        self.mozList = []
        
    ###################################################
    # prepare the hash for writing the element info into json
    def prepElement(self, elem, sent, infHash, isSrc):
        """
        Prepares a dictionary for writing an element into a json object.
        """
        elemDict = {}
        #start = unicode(sent).find(elem)
        #end = start + len(elem)
        elemDict["start"] = 0#start
        elemDict["end"] = 1#end
        elemDict["form"] = elem

	if isSrc:
		if elem in self.srcHash:
			elemDict["concept"] = self.srcHash[elem][0]
		else:
			print "Source Element was not count in the source Hash"
	else:
		if elem in self.tgtHash:
			elemDict["target"] = self.tgtHash[elem][0]
		else:
			print "Source Element was not count in the source Hash"
			
        if elem in infHash:
            elemDict["lemma"] = infHash[elem]
        else:
            elemDict["lemma"] = elem
        
        return elemDict

    ###################################################    
    def combineSrcTgt(self, src, tgt, sent):
        """
        Combines the extracted source and target segments and returns the
        metaphoric segment.
        """
        #sent =sent.encode("utf-8")
        srcInx = tgtInx = 0

        # locating the src tgt in the sentence
        srcTgtInx = sent.find (src + " " + tgt)
        tgtSrcInx = sent.find (tgt + " " + src)
        
        if srcTgtInx >= 0:
            srcInx = srcTgtInx
            tgtInx = srcTgtInx + len(src) + 1
        elif tgtSrcInx >= 0:
            tgtInx = tgtSrcInx
            srcInx = tgtSrcInx + len(tgt) + 1
        # if source and target are not next to each other, locate them separately
        else:
            srcInx = sent.find(src)
            tgtInx = sent.find(tgt)
        
        #srcInx = sent.find(src)
        #tgtInx = sent.find(tgt)
        start = min(srcInx, tgtInx)
        end = 0
        
        if srcInx < tgtInx:
            #print "src < tgt"
            # if target is not very far from source, the get the maximum span 
            if tgtInx < (srcInx + len(src) + 10):
                end = tgtInx + len(tgt)
                try: 
                    #print "@@@@@", sent[start:end]
                    return sent[start:(end)]#.decode('utf-8')
                except UnicodeDecodeError:
                    self.logger.error(u'unicode error in sentence: %s',sent)
        else:
            #print "tgt < src", srcInx, tgtInx, sent
            # if target is after source, return only the source
            if srcInx < (tgtInx + len(tgt) + 10):
                end = srcInx + len(src)
                try:
                    return sent[start:end]#.decode('utf-8')
                except UnicodeDecodeError:
                    self.logger.error(u'unicode error in sentence: %s',sent)
        return None
    

 
    ###################################################    

    def parse(self, jObj):
        print "calling the empty parse"
        return ""
    ##########################################################                
    def find_LMs(self, jObj):
        """
        A higher level method that reads in a json object (containing 
        a set of sentences, preprocesses, parses and extract metaphoric segments
        and write the results into a new a json object which will be returned 
        
        :param jObj: MetaNet JSON format structure
        :type jObj: dict
        :returns: MetaNet JSON format structure
        """
        randStr = str(random.randint(0, 100000))
        randStr = "1"
        out = codecs.open(self.repDir+ "/blog_" + randStr + ".txt","w", "utf-8")
        sents = jObj['sentences']
        # for all sentences, call the extracor to get metaphoric segments.
        # create an LM list and add each segment under the "name" field.
        ct = -1
        mFlag = False
        for snt in sents:
            mFlag = False
            # snt["lms"] = []
            ct += 1
            txt = snt["text"]
            sen = self.perPipeline.preprocess(txt)
            print "============== Sent", ct,"========================"
            out.write("Sent " + str(ct))
            out.write(sen + "\n")
            # call the extract method to find a list of metaphoric expressions  
            # returns empty list if nothing found
            #metList = segExtractor.oldExtract(txt,self.uniModel,self.bigModel,self.triModel,
            #                               self.srcHash, self.tgtHash, self.repDir,
            #                               self.fpOne, self.fpTwo, self.mozList[ct])
                        
            srcExtList = segExtractor.findLUsInSent(sen, self.srcHash)
            tgtExtList = segExtractor.findLUsInSent(sen, self.tgtHash)
            """
            for t in srcExtList:
                out.write("first src matching based on:") 
                out.write(t)
                out.write("\n")
            for t in tgtExtList:
                out.write("first tgt matching based on:") 
                out.write(t)
                out.write("\n")
            """
            
            metList = [srcExtList, tgtExtList]
            
            # metaphor list for this sentence            
            lmsList = []
            # if there is source and target terms, then parse the sentence and there are not same, parse the setence    
            if srcExtList and tgtExtList and ((len(srcExtList) != len(tgtExtList)) or ((srcExtList[0] != tgtExtList[0]))):
                print "there are src and target LUs"
                print "calling the pos tagger and the parser."
    
                taggedLine = self.perPipeline.posTagASentence(sen)
                if not taggedLine:
                    print "pos tagging failed, skipping the sentence!"
                    continue
		
                parsedLine = self.perPipeline.parseATaggedSentence(taggedLine)
                if not parsedLine:
                    print "pos tagging failed, skipping the sentence!"
                    continue
                print "parsed!"
                
                # get a list of extracts for different constructions (moz, tosifi, etc) along with the list of src and target segments for each 
                # extracted metaphor
                extracts = segExtractor.locateMetSeg(parsedLine, self.srcHash, self.tgtHash, out)
                 
                lmsDict = {}
                k = -1
                #print "size of extracts", len(extracts)
		
                for exSet in extracts:
                    if mFlag:
                        break
                    #print "size of exSet:", len(exSet)
                    for extr in exSet:
                        if mFlag:
                            break
                        if extr != []:
                            out.write("top:" + extr[0] + "\n")
                            lmsDict["name"] = extr[0]
                            lmsDict["seed"] = u'NA'
                            lmsDict["extractor"] = u'LMS2'
                            lmsDict["score"] = "0.5"
                            #extrSrc = extr[1][0]                        
                            #extrTgt = extr[2][0]
                            ys = 0
                            yt = 0
                            extrSrc = extrTgt = ""
                            # look for the match, skip the source of target LU matches if they're stop word.					
                            while (ys < len(extr[1])) and (yt < len(extr[2])):
                                #ys += 1
                                #yt += 1
                                out.write("seg:" + extr[0] + "\n")
                                out.write("src:" + extr[1][ys] + "\n")
                                out.write("tgt:" + extr[2][yt] + "\n")
                                extrSrc = extr[1][ys]
                                extrTgt = extr[2][yt]
                                if extrSrc in self.stopList:
                                    ys += 1
                                    continue
                                if extrTgt in self.stopList:
                                    yt += 1
                                    continue
                                if extrSrc == extrTgt:
                                    if (len(extr[1]) - ys) > (len(extr[2]) - yt):
                                        ys += 1
                                    else:
                                        yt += 1
                                    continue
                                else:
                                    out.write("found one metaphor, breaking")
                                    print "found one metaphor, breaking"
                                    break
                                    
                            # if we have both src and tgt segments, insert it into the json   
                            if extrSrc and extrTgt and extrSrc != extrTgt:   
                                srcElem = self.prepElement(extrSrc, sen, self.lemHash, True)
                                lmsDict["source"] = srcElem
                                
                                tgtElem = self.prepElement(extrTgt, sen, self.lemHash, False)
                                lmsDict["target"] = tgtElem
                                if (lmsDict not in lmsList) and srcElem != tgtElem:
                                    print "+++ adding to the LM LIST"
                                    mFlag = True
                                    lmsList.append(lmsDict)
                                else:
                                    print "rrrr Skipping a repetitive or an identical metaphor!" 
                            else:
                                print "----- couldn't form a metaphoric segment from this extract", 
                                print "source is:", len(extrSrc), "chars!",
                                print " and tgt is:", len(extrTgt), "chars!",
                                print "there were ", len(extr[1]), "in extracted src",  
                                print "and ", len(extr[2]), "in extracted tgt"
                                

                            
                               
            if len(lmsList) > 0:
                print "adding a list of ", len(lmsList), "LMs to the jobj"
                snt["lms"] = lmsList
            else:
                print "--- A sentence with no metaphor"            
        return jObj
    
    def writejson(self,jObj,fname):
        """
        Custom json writer to circumvent Persian-specific bugs in json handling.
        """
        jOut = codecs.open(fname,"w",encoding='utf-8')
        json.dump(jObj, jOut, encoding='utf-8')
	

def main():
    if len(sys.argv) < 2:
        print "use the following:"
        print "python externalExtr.py input-json-file"
        print "   e.g. \"python externalExtr.py TestInput-fa.json\""
        sys.exit()
    logging.basicConfig()


    rDir = '/u/metanet/persianCode/beh/code/sysOct2014/'
    jObj = json.load(file(sys.argv[1]), encoding='utf-8')
    filePath = sys.argv[1]
    fileName = filePath
    if filePath.find("/") > -1:
        fileName = filePath.split("/")[-1]
    
    # process and write
    pext = PersianMetaphorExtractor(rDir)
    #pext.parse(jObj)
    jObj = pext.find_LMs(jObj)
    pext.writejson(jObj,rDir + "/lms2." + fileName)
    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

