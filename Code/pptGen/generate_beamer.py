#!/usr/bin/env python3

from pptGen_models import readData, readPData, readData2, TeiText

bemaer_path = '../../beamers/'

beamer_start = r"\documentclass{beamer} \usepackage[utf8]{inputenc} \usepackage{datetime}" + "\n"
doc_start = r"\begin{document}"+ "\n" + r"\frame{\titlepage}" + "\n"
doc_end = r"\end{document}"
frame_start = r"\begin{frame}" + " \n "
frame_end = r"\end{frame}" + "\n"

def gen_titleElem(p: TeiText):
    return r"\title{"+p.title+"}" + "\n"

def gen_authorElem(p: TeiText):
    return r"\author{"+p.author+"}" + "\n"

def gen_institute(p: TeiText):
    return "\institute{ShareLaTeX}" + "\n"

def gen_frame(title, elements):
    frame_title = r"\frametitle{"+title+"}"
    frame = frame_start + frame_title + " \n " + r"\begin{itemize} " + "\n"
    for e in elements:
        frame = frame + r"\item " + e +"\n"
    frame = frame + r"\end{itemize}" + "\n" 
    frame = frame + frame_end

    return frame

def gen_beamertex(p: TeiText):
    beamer = beamer_start + gen_titleElem(p) + gen_authorElem(p) + gen_institute(p) + doc_start
    beamer = beamer + gen_frame(p.title, ["This is the first slide", "Testing this out", "Making three things"])
    beamer = beamer + doc_end

    return beamer

def write_beamer_to_file(p: TeiText, beamer: str):
    f= open(bemaer_path + p.id + ".tex","w+")
    f.write(beamer)
    f.close()


p = readPData('0000-0000-0000_0_paper.tei.xml')
beamer = gen_beamertex(p)
write_beamer_to_file(p, beamer)







