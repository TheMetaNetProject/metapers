1. Set the following system parameters:

PYTHONPATH .:/u/metanet/nlptools/nltk-3.0.0b1
JAVAHOME /usr/lib/jvm/jre-1.7.0-oracle.x86_64/bin/java
MALTPARSERHOME /u/metanet/nlptools/maltparser-1.8/

2. The PersianMetaphorExtractor constructor uses the following default directory as its working one: '/u/metanet/extraction/persian/lms2/'
You can overwrite that by specifying your own path.  Your new working dir needs to hold the following symbolic links:
PerParseModelWithCompoundTerms.mco -> /u/metanet/persianCode/PersianPipeline/models/PerParseModelWithCompoundTerms.mco
LUList.src.txt -> /u/metanet/extraction/persian/lms2/LUList.src.txt
LUList.tgt.txt -> /u/metanet/extraction/persian/lms2/LUList.tgt.txt

