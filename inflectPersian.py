# -*- coding: utf-8 -*-
"""
.. module:: inflexPersian
    :platform: Unix
    :synopsis: Generator of various inflections for Persian verbs and nouns for Persian LMS system

"""
import sys
import codecs
import json
import sys
import re
from PersianPipeline import *


def readLUs(fPath, srcFlag, lemmaHash):

		
    fle = codecs.open(fPath, "r", "utf-8")
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
                    pastList = inflectVerbs(lu, True) 
                elif lu.endswith("_ts"):
                    lu = lu.replace("_ts","")
                    presList = inflectVerbs(lu, False) 
                elif lu.endswith("_n"):
                    lu = lu.replace("_n","")
                    pluralList = inflectNouns(lu) 


                
            # if lu is already seen            
            if lu in luHash:
                if conc not in luHash[lu]:
                    luHash[lu].append(conc)
                # we have already recorded this concept for this lu

            else:
                luHash[lu] = [conc]
            
            # store all past inflections
            for pi in pastList:
                # store the lemma
                if pi not in lemmaHash:
                    lemmaHash[pi] = lu
                # if already seen            
                if pi in luHash:
                    if conc not in luHash[pi]:
                        luHash[pi].append(conc)
                    # we have already recorded this concept for this lu
                else:
                    luHash[pi] = [conc]
                    
            # store all present inflections
            for ti in presList:
                if ti not in lemmaHash:
                    lemmaHash[ti] = lu
                
                # if already seen            
                if ti in luHash:
                    if conc not in luHash[ti]:
                        luHash[ti].append(conc)
                    # we have already recorded this concept for this lu
                else:
                    luHash[ti] = [conc]
            

            # store all plural noun inflections
            for pn in pluralList:               
                if pn not in lemmaHash:
                    lemmaHash[pn] = lu
                
                # if already seen            
                if pn in luHash:
                    if conc not in luHash[pn]:
                        luHash[pn].append(conc)
                    # we have already recorded this concept for this lu
                else:
                    luHash[pn] = [conc]

            
    return luHash


def inflectNouns(n):
    infs = []
    infs.append(n + u"ها")
    infs.append(n + u"های")
    infs.append(n + u"هایی")
    infs.append(n + u"\u200c" + u"ها")
    infs.append(n + u"\u200c" + u"های")
    infs.append(n + u"\u200c" + u"هایی")
    """
    for t in infs:
        out.write(t + "--")
    """
    return infs
    
def inflectVerbs(stem, isPast):
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

def main():
    pass
    
if __name__ == "__main__":
    main()

