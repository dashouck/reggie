PROJECT=Reggie_John-Houck
TEX=pdflatex
BIBTEX=bibtex $(PROJECT)
BUILDTEX=$(TEX) $(PROJECT).tex
PDFFILE=$(PROJECT).pdf

all:
	$(BUILDTEX)
	$(BUILDTEX)
	$(BUILDTEX)
	$(MAKE) clean
	open $(PDFFILE)

clean:
	rm -f *.fdb_latexmk *.fls *.gz *.dvi *.log *.bak *.aux *.bbl *.blg *.idx *.ps *.eps *.toc *.out *~
