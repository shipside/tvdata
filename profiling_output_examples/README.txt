
Source: http://stackoverflow.com/questions/582336/how-can-you-profile-a-python-script

@Maxy's comment on this answer helped me out enough that I think it deserves its own answer: I already had cProfile-generated .pstats files and I didn't want to re-run things with pycallgraph, so I used gprof2dot, and got pretty svgs:

$ sudo apt-get install graphviz
$ git clone https://code.google.com/p/jrfonseca.gprof2dot/ gprof2dot
$ ln -s "$PWD"/gprof2dot/gprof2dot.py ~/bin
$ cd $PROJECT_DIR
$ gprof2dot.py -f pstats profile.pstats | dot -Tsvg -o callgraph.svg
