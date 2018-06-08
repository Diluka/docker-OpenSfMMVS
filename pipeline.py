#!/usr/bin/python
#! -*- encoding: utf-8 -*-
#
# Created by @FlachyJoe
#
# this script is for easy use of OpenMVG and OpenMVS
#
#usage: SfM_MyPipeline.py input_dir output_dir
#                         [-h] [-f FIRST_STEP] [-l LAST_STEP] [--0 0 [0 ...]]
#                         [--1 1 [1 ...]] [--2 2 [2 ...]] [--3 3 [3 ...]]
#                         [--4 4 [4 ...]] [--5 5 [5 ...]] [--6 6 [6 ...]]
#                         [--7 7 [7 ...]] [--8 8 [8 ...]] [--9 9 [9 ...]]
#                         [--10 10 [10 ...]] [--11 11 [11 ...]]
#
#Photogrammetry reconstruction with these steps :
#	0. Intrinsics analysis	extract_metadata
#	1. Detect features		opensfm detect_features
#	2. Match features		opensfm match_features
#	3. Create tracks	opensfm create_tracks
#	4. Reconstruct	opensfm reconstruct
#	5. Mesh	opensfm mesh
#	6. Undistort	opensfm undistort
#	7. Export to openMVS	opensfm export_openmvs
#	8. Densify point cloud	OpenMVS/DensifyPointCloud
#	9. Reconstruct the mesh	OpenMVS/ReconstructMesh
#	10. Refine the mesh		OpenMVS/RefineMesh
#	11. Texture the mesh	OpenMVS/TextureMesh
#
#positional arguments:
#  input_dir             the directory which contains the pictures set.
#  output_dir            the directory which will contain the resulting files.
#
#optional arguments:
#  -h, --help            show this help message and exit
#  -f FIRST_STEP, --first_step FIRST_STEP
#                        the first step to process
#  -l LAST_STEP, --last_step LAST_STEP
#                        the last step to process
#
#Passthrough:
#  Option to be pass to command lines (remove - in front of option names)
#  e.g. --1 p ULTRA to use the ULTRA preset in openMVG_main_ComputeFeatures


import commands
import os
import subprocess
import sys

# Indicate the openMVG and openMVS binary directories
OPENSFM_BIN = "/opt/OpenSfM/bin"
OPENMVS_BIN = "/usr/local/bin/OpenMVS"

DEBUG=False

## HELPERS for terminal colors
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
NO_EFFECT, BOLD, UNDERLINE, BLINK, INVERSE, HIDDEN = (0,1,4,5,7,8)

#from Python cookbook, #475186
def has_colours(stream):
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # guess false in case of error
        return False
has_colours = has_colours(sys.stdout)

def printout(text, colour=WHITE, background=BLACK, effect=NO_EFFECT):
        if has_colours:
                seq = "\x1b[%d;%d;%dm" % (effect, 30+colour, 40+background) + text + "\x1b[0m"
                sys.stdout.write(seq+'\r\n')
        else:
                sys.stdout.write(text+'\r\n')

## OBJECTS to store config and data in

class ConfContainer(object):
    """Container for all the config variables"""
    pass

conf=ConfContainer()

class aStep:
    def __init__(self, info, cmd, opt):
        self.info = info
        self.cmd = cmd
        self.opt = opt

class stepsStore :
    def __init__(self):
        self.steps_data=[
            [   "Intrinsics analysis",
                os.path.join(OPENSFM_BIN, "opensfm"),
                ["extract_metadata", "%input_dir%"] ],
            [   "Detect features",
                os.path.join(OPENSFM_BIN,"opensfm"),
                ["detect_features", "%input_dir%"] ],
            [   "Match features",
                os.path.join(OPENSFM_BIN, "opensfm"),
                ["match_features", "%input_dir%"] ],
            [   "Create tracks",
                os.path.join(OPENSFM_BIN, "opensfm"),
                ["create_tracks", "%input_dir%"] ],
            [   "Reconstruct",
                os.path.join(OPENSFM_BIN, "opensfm"),
                ["reconstruct", "%input_dir%"] ],
            [   "Mesh",
                os.path.join(OPENSFM_BIN, "opensfm"),
                ["mesh", "%input_dir%"] ],
            [   "Undistort",
                os.path.join(OPENSFM_BIN, "opensfm"),
                ["undistort", "%input_dir%"] ],
            [   "Export to openMVS",
                os.path.join(OPENSFM_BIN, "opensfm"),
                ["export_openmvs", "%input_dir%"] ],
            [   "Densify point cloud",
                os.path.join(OPENMVS_BIN,"DensifyPointCloud"),
                ["scene.mvs", "-w","%mvs_dir%"]],
            [   "Reconstruct the mesh",
                os.path.join(OPENMVS_BIN,"ReconstructMesh"),
                ["scene_dense.mvs", "-w","%mvs_dir%"]],
            [   "Refine the mesh",
                os.path.join(OPENMVS_BIN,"RefineMesh"),
                ["scene_dense_mesh.mvs", "-w","%mvs_dir%"]],
            [   "Texture the mesh",
                os.path.join(OPENMVS_BIN,"TextureMesh"),
                ["scene_dense_mesh_refine.mvs", "-w","%mvs_dir%"]]
            ]

    def __getitem__(self, indice):
        return aStep(*self.steps_data[indice])

    def length(self):
        return len(self.steps_data)

    def apply_conf(self, conf):
        """ replace each %var% per conf.var value in steps data """
        for s in self.steps_data :
            o2=[]
            for o in s[2]:
                co=o.replace("%input_dir%",conf.input_dir)
                co=co.replace("%mvs_dir%",conf.mvs_dir)
                o2.append(co)
            s[2]=o2

steps=stepsStore()

## ARGS
import argparse
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="Photogrammetry reconstruction with these steps : \r\n"+
        "\r\n".join(("\t%i. %s\t %s" % (t, steps[t].info, steps[t].cmd) for t in range(steps.length())))
    )
parser.add_argument('input_dir', help="the directory wich contains the pictures set.")
parser.add_argument('-f','--first_step', type=int, default=0, help="the first step to process")
parser.add_argument('-l','--last_step', type=int, default=11, help="the last step to process" )

group = parser.add_argument_group('Passthrough',description="Option to be passed to command lines (remove - in front of option names)\r\ne.g. --1 p ULTRA to use the ULTRA preset in openMVG_main_ComputeFeatures")
for n in range(steps.length()) :
    group.add_argument('--'+str(n), nargs='+')

parser.parse_args(namespace=conf) #store args in the ConfContainer

## FOLDERS

def mkdir_ine(dirname):
    """Create the folder if not presents"""
    if not os.path.exists(dirname):
        os.mkdir(dirname)

#Absolute path for input and ouput dirs
conf.input_dir=os.path.abspath(conf.input_dir)
conf.output_dir=conf.input_dir

if not os.path.exists(conf.input_dir):
    sys.exit("%s : path not found" % conf.input_dir)


conf.matches_dir = os.path.join(conf.output_dir, "matches")
conf.mvs_dir = os.path.join(conf.output_dir, "openmvs")

mkdir_ine(conf.mvs_dir)

steps.apply_conf(conf)

## WALK
print "# Using input dir  :  %s" % conf.input_dir
print "# First step  :  %i" % conf.first_step
print "# Last step :  %i" % conf.last_step
for cstep in range(conf.first_step, conf.last_step+1):
    printout("#%i. %s" % (cstep, steps[cstep].info), effect=INVERSE)

    opt=getattr(conf,str(cstep))
    if opt is not None :
        #add - sign to short options and -- to long ones
        for o in range(0,len(opt),1):
            if len(opt[o])>1:
                opt[o]='-'+opt[o]
            opt[o]='-'+opt[o]
    else:
        opt=[]

    #Remove steps[cstep].opt options now defined in opt
    for anOpt in steps[cstep].opt :
		if anOpt in opt :
			idx=steps[cstep].opt.index(anOpt)
			if DEBUG :
				print '#\t'+'Remove '+ str(anOpt) + ' from defaults options at id ' + str(idx)
			del steps[cstep].opt[idx:idx+2]

    cmdline = [steps[cstep].cmd] + steps[cstep].opt + opt

    if not DEBUG :
        pStep = subprocess.Popen(cmdline)
        pStep.wait()
    else:
        print '\t'+' '.join(cmdline)
