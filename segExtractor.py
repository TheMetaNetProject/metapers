# -*- coding: utf-8 -*-
"""
.. module:: segExtractor
    :platform: Unix
    :synopsis: metaphor segment extractor for Persian LMS system

Extracts metaphor segments from sentences using precomputed language model data.

"""
import codecs
import os
import sys
import random
import processParseTree
# readinLM
def readLM(lmPath):
    """
    Read a language model into a dictionary.
    """
    lmFile = codecs.open(lmPath)
    lmHash = {}
    while 1:
        lmLine = lmFile.readline()
        if not lmLine or lmLine.strip() == "":
            break
        tokList = lmLine.split("\t")

        try:
            prob = float(tokList[0])
        except:
            print lmLine
            print tokList
        #print prob
        ngr = tokList[1] 

        lmHash[ngr.strip()] = prob
    return lmHash

###################################################
def readInLex(lexPath):
    """
    Loads a lexicon into a dictionary and returns the dictionary
    """
    lexFile = open(lexPath)
    lexHash = {}
    while 1:
        lex = lexFile.readline()
        if not lex:
            break
        lex = lex.strip()
        if lex not in lexHash:
            lexHash[lex] = 1
    return lexHash
#########################################
def analyzeMozafs(posSent, srcHash, tgtHash, mozList):
    """
    Reads in a pos tagged sentence, the source and target lexicons 
    (dictionaries) and the list of extracted ezaafeh constructions 
    (extracted from the sentences.  The method analyzes the ezaafeh construct
    using the source and target lexicons and decides if the construct 
    is potentially metaphoric.
    """
    [wd,pos] = [prevWd,prevPos] = ["",""]

    srcList = []
    tgtList = []
    for moz in mozList:
        #print moz
        tokMoz = moz.split()
        srcWds = []
        tgtWds = []
        # bigram moz in which there is a tgt word, just take them
        if len(tokMoz) == 2 and tokMoz[1] in tgtHash:
            
            #print "bigram moz", moz
            #if tokMoz[1] in ["ثروت", "فقر", "مالیات", "مالیاتها", "مالیاتهای", "ثروتها", "ثروتهای"]:
            #    print "UUUUUUUUUUUUUUUUUUUUpdating lexicon", tokMoz[0], "--", moz
            #    srcHash[tokMoz[0]] = 1
            srcList.append(tokMoz[0])
            tgtList.append(tokMoz[1])
            continue

        # revisit
        for tok in tokMoz:
            # if not seen a target word and see a source word
            if not tgtWds and tok in srcHash:
                srcWds.append(tok)
            # if seen a source word and now see a target word
            if srcWds and tok in tgtHash:
                tgtWds.append(tok)
        # if seen both target and source words
        if srcWds and tgtWds:
            tgtList.extend(tgtWds)
            srcList.extend(srcWds)
        # buggy
        # elif srcWds:
        #    srcList.append(moz)
        #elif tgtWds:
        #    tgtList.append(moz)
    # there is something in both lists
    if srcList and tgtList:
        return [srcList, tgtList]
    return None
####################################################################

# remove sub-phrases of longer phrase from a list
def removeExtraPieces(l):
    i = 0
    rList = []
    for i in range(len(l)):
        for j in range(i+1, len(l)):
            if l[i] in l[j] and i not in rList:
                rList.append(i)
            if l[j] in l[i] and j not in rList:
                rList.append(j)
    newL = []
    for i in range(len(l)):
        if l[i] not in rList:
            newL.append(l[i])
    return newL

####################################################################
def locateMetSeg(pl, srcLUHash, tgtLUHash, out):
    extrs = [[],[],[],[],[]]
    pl = pl.to_conll(10).replace("^", " ")
    mozList = processParseTree.extractMOZ(pl)
    mozList = removeExtraPieces(mozList)
    tosList = processParseTree.extractTosifiPhrase(pl)
    tosList = removeExtraPieces(tosList)
    vbList = processParseTree.extractVerb(pl)
    vbList = removeExtraPieces(vbList)
    subList = processParseTree.extractSubjObj(pl, True)
    subList = removeExtraPieces(subList)
    objList = processParseTree.extractSubjObj(pl, False)
    objList = removeExtraPieces(objList)
    allSegLists = [mozList, tosList, vbList, subList, objList]
    
    # look for a moz or a sub-phrase of it in src and tgt LU hashes
    h = -1
    for segList in allSegLists:
        h += 1
        for seg in segList:
            #out.write("typs is " + str(h) + " and seg is:")
            #out.write(seg)
            #out.write("\n")
            tokSeg = seg.split()
            srcMatch = []
            tgtMatch = []
            # looping on the length of the subsegment: 1 to len(seg)
            for i in range(1,1+len(tokSeg)):
                # looping on the start point of the subsegement            
                for j in range(0, len(tokSeg)-i+1):
                    # a sub-segment
                    subSeg = " ".join(tokSeg[j:j+i])
                    if subSeg and subSeg in srcLUHash:
                        #print "found a src sub-seg in the source LUs"
                        srcMatch.append(subSeg)
                        
                    if subSeg and subSeg in tgtLUHash:
                        #print "found a tgt sub-seg in the target LUs"
                        tgtMatch.append(subSeg)
            if srcMatch != [] and tgtMatch != []:
                extrs[h].append([seg, srcMatch, tgtMatch])
    return extrs
    
##############################################
def findLUsInSent(sent, luList):
    sentList = sent.split()
    extList = []
    for lu in luList:
        spaceCt = lu.strip().count(" ")
        # for single term LUs, look in the tokenized list
        if spaceCt == 0:
            if lu in sentList:
                
                extList.append(lu)
            
        # for compound LUs, look in the actual sentence
        elif sent.find(lu.strip()) > -1:
            extList.append(lu)
            
            
    return extList
        
###################################################
def combineSrcTgt(src, tgt, sent):
    sent =sent.encode("utf-8")
    srcInx = sent.find(src)
    tgtInx = sent.find(tgt)
    start = min(srcInx, tgtInx)
    end = 0
    if srcInx < tgtInx:
        # if target is not very far from source, the get the maximum span      
        if tgtInx < (srcInx + len(src) +5):
            end = tgtInx + len(tgt)
            #print "@@@@@@", sent[start:end]
            return sent[start:(end)].decode('utf-8')
    
    else:
        if srcInx < (tgtInx + len(tgt) + 5):
            end = srcInx + len(src)
            return sent[start:end].decode('utf-8')

    return None

###################################################
def main():
    repDir = sys.argv[2]
    inFile = codecs.open(sys.argv[1],"r",'utf-8')


if __name__ == "__main__":
    main()

