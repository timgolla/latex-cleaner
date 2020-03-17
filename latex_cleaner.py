# -*- coding: utf-8 -*-
"""
latex-cleaner
A small tool for creating a "clean" copy of a directory containing a latex document with dependent files.

@author: Tim Golla
"""

import argparse
import glob
import os
import re
import shutil

import numpy as np


def latex_clean(args):
    if args.outputdir is None:
        inputdir = args.inputdir.rstrip("/").rstrip("\\")
        args.outputdir = inputdir + "_cleaned"
    shutil.rmtree(args.outputdir, ignore_errors=True)
    os.makedirs(args.outputdir, exist_ok=True)
    tex_files = []
    other_files = []
    tex_exts = []
    for ext in args.tex_exts:
        tex_exts.append(ext.lower())
    for root, dirs, files in os.walk(args.inputdir):
        reldir = os.path.relpath(root, start=args.inputdir)
        for file in files:
            current_file = os.path.join(reldir, file)
            current_file = current_file.replace("\\", "/")
            current_file = current_file.lstrip("./")
            myf, ext = os.path.splitext(current_file)
            if (ext.lower() in tex_exts):
                tex_files.append(current_file)
            else:
                other_files.append(current_file)
    s = ""
    for i in range(len(tex_files)):
        texfilename = os.path.join(args.inputdir, tex_files[i])
        f = open(texfilename, "r", errors=args.errors)
        outfilename = os.path.join(args.outputdir, tex_files[i])
        os.makedirs(os.path.dirname(outfilename), exist_ok=True)
        if not args.keep_comments:
            cleanedstring = ""
            lines = f.readlines()
            for l in lines:
                if l.isspace():  # a wanted line break
                    cleanedstring += l
                else:
                    # replace everything after a percent sign with a newline
                    l = re.sub("%.*\n", "\n", l)
                    if not l.isspace():  # this check is necessary in order not to add unwanted line breaks
                        cleanedstring += l
            outfile = open(outfilename, "w")
            outfile.write(cleanedstring)
            outfile.close()
            s += cleanedstring
        else:
            s += f.read()
            shutil.copy2(os.path.join(args.inputdir, texfilename), outfilename)
        f.close()
    used = np.zeros(len(other_files), dtype=bool)
    notfound = np.ones(len(other_files), dtype=bool)
    for i in range(len(other_files)):
        myf, ext = os.path.splitext(other_files[i])
        kp = False
        for pref in args.keep_prefixes:
            if myf.startswith(pref):
                kp = True
        for e in args.keep_exts:
            e = e.lower()
            if ext.lower().endswith(e):
                kp = True
        if kp or myf in s:
            used[i] = True
            notfound[i] = False
    other_files = np.array(other_files)
    print("\nused files:")
    usedfiles = other_files[used]
    print(usedfiles)
    print("\nunused files:")
    unusedfiles = other_files[notfound]
    print(unusedfiles)
    for f in usedfiles:
        outfilename = os.path.join(args.outputdir, f)
        os.makedirs(os.path.dirname(outfilename), exist_ok=True)
        shutil.copy2(os.path.join(args.inputdir, f), outfilename)


def main():
    parser = argparse.ArgumentParser(description='Clean LaTex Directory')
    parser.add_argument("inputdir")
    parser.add_argument(
        "--outputdir", "-o", help="output directory. If not specified, it will create a ""clean"" subdirectory.", default=None)
    parser.add_argument("--keep_prefixes", "-k", default=[],
                        help="Keep all files that have the listed prefixes, including the directory name.")
    parser.add_argument("--keep_exts", "-e", default=[
        ".tex", ".sty", ".fd", ".bbx", ".cls", ".dtx", ".bst"], help="Keep all files that have the listed extensions.")
    parser.add_argument("--tex_exts", default=[
        ".tex"], help="Extensions of tex files - these are parsed for includes and always kept.")
    parser.add_argument("--keep_comments", action="store_true",
                        help="By default, remove all comments. This switch keeps them.")
    parser.add_argument("--errors", default=None,
                        help="How to handle read errors. See the documentation of Python's open.")
    args = parser.parse_args()
    latex_clean(args)


if __name__ == "__main__":
    main()
