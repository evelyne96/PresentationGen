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

def gen_pres_titleElem(title: str):
    return r"\title{"+title+"}" + "\n"

def gen_authorElem(p: TeiText):
    return r"\author{"+p.author+"}" + "\n"

def gen_pres_authorElem(author: str):
    return r"\author{"+author+"}" + "\n"

def gen_institute(p: TeiText):
    return "\institute{ShareLaTeX}" + "\n"

def gen_pres_institute(institute: str):
    return r"\institute{"+institute+"}" + "\n"

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

def gen_pres_frame(title, content):
    frame_title = r"\frametitle{"+title+"}"
    frame = frame_start + frame_title 
    for (firstP, secondP) in content:
        if firstP == None:
            for e in secondP:
                frame = frame + " \n " + r"\begin{itemize} " + "\n"
                frame = frame + r"\item " + e +"\n"
                frame = frame + r"\end{itemize}" + "\n" 
        else:
            frame = frame + " \n " + r"\begin{itemize} " + "\n"
            frame = frame + r"\item " + firstP +"\n"
            for e in secondP:
                frame = frame + " \n " + r"\begin{itemize} " + "\n"
                frame = frame + r"\item " + e +"\n"
                frame = frame + r"\end{itemize}" + "\n" 
            frame = frame + r"\end{itemize}" + "\n" 
    frame = frame + frame_end

    return frame


def gen_pres_beamertex(title: str, author: str, institute: str, frames):
    beamer = beamer_start + gen_pres_titleElem(title) + gen_pres_authorElem(author) + gen_pres_institute(institute) + doc_start
    for (title, content) in frames:
        beamer = beamer + gen_pres_frame(title, content)
    beamer = beamer + doc_end

    return beamer

def write_beamer_to_file(fileName: str, beamer: str):
    f= open(bemaer_path + fileName + ".tex","w+")
    f.write(beamer)
    f.close()


# p = readPData('0000-0000-0000_0_paper.tei.xml')
# beamer = gen_beamertex(p)
# write_beamer_to_file(p.id, beamer)

beamer = gen_pres_beamertex("Machine Learning", "Will Black", "Institute of Science", 
[ ("First Frame",  [("title",["ONE", "TWO", "THREe"]), (None, ["First", "Second"])])
])

write_beamer_to_file("test", beamer)






