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
    tex_files_in = []
    tex_files_out = []
    other_files_in = []
    other_files_out = []
    tex_exts = []
    for ext in args.tex_exts:
        tex_exts.append(ext.lower())
    for root, dirs, files in os.walk(args.inputdir):
        reldir = os.path.relpath(root, start=args.inputdir)
        for file in files:
            current_filename_in = os.path.join(reldir, file)
            current_filename_in = current_filename_in.replace("\\", "/")
            current_filename_in = current_filename_in.lstrip("./")
            current_filename_out = current_filename_in
            if args.remove_subdirs:
                current_filename_out = current_filename_out.replace("/","_")
            myf, ext = os.path.splitext(current_filename_in)
            if (ext.lower() in tex_exts):
                tex_files_in.append(current_filename_in)
                tex_files_out.append(current_filename_out)
            else:
                other_files_in.append(current_filename_in)
                other_files_out.append(current_filename_out)
    tex_contents = []
    all_files_in = tex_files_in + other_files_in
    all_files_in = sorted(all_files_in,key=len)[::-1]
    all_files_out = tex_files_out + other_files_out
    all_files_out = sorted(all_files_out,key=len)[::-1]
    for i in range(len(tex_files_in)):
        texfilename = os.path.join(args.inputdir, tex_files_in[i])
        f = open(texfilename, "r", errors=args.errors)
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
            tex_contents.append(cleanedstring)
        else:
            tex_contents.append(f.read())
        if args.remove_subdirs:
            for j in range(len(all_files_in)):
                fin, ext = os.path.splitext(all_files_in[j])
                fout, ext = os.path.splitext(all_files_out[j])
                tex_contents[i] = tex_contents[i].replace(fin,fout)
        f.close()
    used = np.zeros(len(other_files_in), dtype=bool)
    notfound = np.ones(len(other_files_in), dtype=bool)
    for i in range(len(other_files_out)):
        myf, ext = os.path.splitext(other_files_out[i])
        kp = False
        for pref in args.keep_prefixes:
            if myf.startswith(pref):
                kp = True
        for e in args.keep_exts:
            e = e.lower()
            if ext.lower().endswith(e):
                kp = True
        for s in tex_contents:
            if kp or myf in s:
                used[i] = True
                notfound[i] = False
                break
    other_files_in = np.array(other_files_in)
    other_files_out = np.array(other_files_out)
    print("\nused files:")
    used_files_in = other_files_in[used]
    used_files_out = other_files_out[used]
    print(used_files_in)
    print("\nunused files:")
    unusedfiles = other_files_in[notfound]
    print(unusedfiles)
    for i in range(len(used_files_in)):
        f = used_files_out[i]
        outfilename = os.path.join(args.outputdir, f)
        os.makedirs(os.path.dirname(outfilename), exist_ok=True)
        shutil.copy2(os.path.join(
            args.inputdir, used_files_in[i]), outfilename)
    for i in range(len(tex_files_in)):
        outfilename = os.path.join(args.outputdir, tex_files_out[i])
        os.makedirs(os.path.dirname(outfilename), exist_ok=True)
        if not args.keep_comments:
            outfile = open(outfilename, "w")
            outfile.write(tex_contents[i])
            outfile.close()
        else:
            shutil.copy2(os.path.join(args.inputdir, texfilename), outfilename)


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
    parser.add_argument("--remove_subdirs", action="store_true",
                        help="Copy all relevant files into the root directory, renames the respective files and changes the includes accordingly.")
    parser.add_argument("--errors", default=None,
                        help="How to handle read errors. See the documentation of Python's open.")
    args = parser.parse_args()
    latex_clean(args)


if __name__ == "__main__":
    main()
