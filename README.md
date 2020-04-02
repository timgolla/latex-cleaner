# latex-cleaner
A small tool for creating a "clean" copy of a directory containing a latex document with dependent files.
Copies all relevant files  to the output folder. Removes commented out parts of the .tex files. By default, the output folder gets the name of the input folder with a "_cleaned" suffix.
What it does:
1. It collects all filenames in the input folder.
2. It scans all .tex files, removes comments (can be deactivated) and writes them to the output folder.
3. Scans if filenames of the other files in the input folder have been mentioned in the .tex files. If so, copy. Ignores extensions.
4. Optionall it can eliminate subdirectories by renaming files in subdirectories to give them unique names, copying them to the root directory and changing the references in the .tex files.

Known limitations: 
- Currently assumes that all includes are relative to the input folder.
- "False positives" are possible, due to multiple reasons:
  - Only the filenames without extensions are tested.
  - Only a simple test, whether the filename is mentioned in the text is performed. 

Warning: no warranties whatsoever. Use at your own risk. Make backups!

## Usage
python latex_cleaner.py inputdir

## Background: 
I found that other tools didn't copy all files necessery for my project. I thus wrote this small tool, which copies all the files for me, but tends to have more false positives.
