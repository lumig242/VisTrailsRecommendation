###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
# Finds all .py files recursively in current directory (.)
# and updates 2007 year with 2008 in the file header. 
import re
import os
new_copyright = ["## Copyright (C) 2011-2014, NYU-Poly.\n"]

re_copyright = re.compile(r"\s+## Copyright \(C\) 2011-2014, NYU-Poly\.\s+")
line_copyright = re.compile(r"## Copyright \(C\) 2011-2014, NYU-Poly\.")
IGNORE_LIST = ["update_copyright_year.py"]
files = []
for (path, dnames, fnames) in os.walk('.'):
    for fn in fnames:
        if fn not in IGNORE_LIST and fn.endswith(".py"):
            files.append(os.path.join(path, fn))

print len(files), " files found"
count = 0
for fname in files:
    fin = open(fname)
    lines = fin.readlines()
    fin.seek(0)
    all_lines = fin.read()
    fin.close()
    if re_copyright.search(all_lines) > 0:
        #Search through the first lines because sometimes it's not exactly in the second line:
        for i in [2,3,4,5]:
            if line_copyright.search(lines[i]) > 0:
                print "Updating: %s"%fname
                newlines = lines[:i]
                newlines.extend(new_copyright)
                cropped = lines[i+1:] #Replace by i+1 when it is to update just the year.
                newlines.extend(cropped)
                fout = file(fname, 'w')
                fout.writelines(newlines)
                fout.close()
                count += 1
                break

print count, " files updated"
