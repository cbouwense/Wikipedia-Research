import pandas as pd
import numpy as np
import sys, re
from difflib import SequenceMatcher
import re, math
from collections import Counter

class TextDiff:
    def __init__(self, source, target):
        """source = source text - target = target text"""
        self.nl = u"<NL>"
        self.delTag = u"[-%s-]"
#         self.delTag = u"%s"
        self.insTag = u"{+%s+}"
#         self.insTag = u"%s"
        self.source = source.replace(u"\n", u"\n%s" % self.nl).split()
        self.target = target.replace(u"\n", u"\n%s" % self.nl).split()
        self.deleteCount, self.insertCount, self.replaceCount = 0, 0, 0
        self.diffText = None
        self.cruncher = SequenceMatcher(None, self.source,
                                     self.target)
        self._buildDiff()

    def _buildDiff(self):
        """Create a tagged diff."""
        outputList = []
        for tag, alo, ahi, blo, bhi in self.cruncher.get_opcodes():
            if tag == 'replace':
                # Text replaced = deletion + insertion
                outputList.append(self.delTag % u" ".join(self.source[alo:ahi]))
                outputList.append(self.insTag % u" ".join(self.target[blo:bhi]))
                self.replaceCount += 1
            elif tag == 'delete':
                # Text deleted
                outputList.append(self.delTag % u" ".join(self.source[alo:ahi]))
                self.deleteCount += 1
            elif tag == 'insert':
                # Text inserted
                outputList.append(self.insTag % u" ".join(self.target[blo:bhi]))
                self.insertCount += 1
        diffText = u" ".join(outputList)
        #diffText = " ".join(diffText.split())
        self.diffText = diffText.replace(self.nl, u"\n")
    
    def getStats(self):
        "Return a tuple of stat values."
        return (self.insertCount, self.deleteCount, self.replaceCount)

    def getDiff(self):
        "Return the diff text."
        return self.diffText

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

WORD = re.compile(r'\w+')
def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)