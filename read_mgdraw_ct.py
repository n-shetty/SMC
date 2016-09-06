#!/usr/bin/env python

''' Reads mgdraw standard output (binary) and exports its data in ascii files.

	The script takes as argument a standard mgdraw binary file obtained with 
	fluka (when USERDUMP was called without modifying mgdraw user routine).
	
	The files created by this script are.... (DESCRIPTION MISSING)

	(EXAMPLE OF SCRIPT USSAGE MISSING)

	IMPORTANT: (NOTHING OF IMPORTANCE)
'''
import sys
import numpy as np
import struct
from time import sleep

__author__ = "Leonel Morejon"
__copyright__ = "None"
__credits__ = [""]
__license__ = ""
__version__ = "1.0.1"
__maintainer__ = "Leonel Morejon"
__email__ = "leonel.morejon@eli-beamlines.eu"
__status__ = "Prototype"


#-------------------------------------------
# Every chunk in the mgdraw file is padded front and back by a 4byte number 
# containing the size in bytes of the chunk whithin the padding

# Every first chunk is made of 28bytes: 5 single precision numbers (4byte each)
# padded front and back by a 4byte integer equal to 20

# Every second chunk will also be padded by integers stating its size, and its
# information depends on the first integer (after pad) of the first chunk

record=[] # listing the cases in order of appearance on the file
filename = 'colltape_for_testing'

format1 = 'IiiiffI'

Case1_list, Case2_list, Case3_list = [], [], []

with open(filename,'rb') as f:
	chunkA = f.read(28)
	
	while chunkA:		
		padA, case, i1, i2, f0, f1, padA = struct.unpack(format1, chunkA)

		chunk_size, = struct.unpack('I', f.read(4)) # in bytes
		chunkB = f.read(chunk_size + 4) # plus 4 'cause of the tail pad
		padB, = struct.unpack('I',chunkB[-4:])

		if padB != chunk_size: # cross checking: head and tail pad should match
			print "ERROR reading the file: head vs tail pad missmatch in "\
				"FORTRAN chunk at position ",f.tell()," in file ",filename
			sys.exit()

		if case > 0: 	# Case 1: continuous energy deposition 
			NTRACK, MTRACK, JTRACK, ETRACK, WTRACK = case, i1, i2, f0, f1

			# (XTRACK(I), YTRACK(I), ZTRACK(I), I = 0, NTRACK), ...
			# ... (DTRACK(J), J = 1, MTRACK), CTRACK

			lenXYZTRACK = 3 * ( NTRACK + 1 )
			XYZTRACK = struct.unpack(lenXYZTRACK*'f', chunkB[:4*lenXYZTRACK])
			XYZTRACK = [ [XYZTRACK[i], XYZTRACK[i+1], XYZTRACK[i+2]] 
				for i in range(0,NTRACK+1,3)]

			lenDTRACK = MTRACK
			DTRACK = struct.unpack(lenDTRACK*'f', chunkB[4*lenXYZTRACK:4*-2])

			CTRACK, = struct.unpack('f', chunkB[-8:-4])

			Case1_list.append([[NTRACK, MTRACK, JTRACK, ETRACK, WTRACK, CTRACK], 
				XYZTRACK, [i for i in DTRACK] ])

			record.append(1)

		elif case == 0: # Case 2: point energy deposition 
			ICODE, JTRACK, ETRACK, WTRACK = i1, i2, f0, f1
			
			XSCO, YSCO, ZSCO, RULL = struct.unpack('4f',chunkB[:-4])

			Case2_list.append([ICODE,JTRACK,ETRACK,WTRACK,XSCO,YSCO,ZSCO,RULL])
			
			record.append(2)

		elif case < 0: 	# Case 3: source particles
			NCASE, NPFLKA, NSTMAX, TKESUM, WEIPRI = -case, i1, i2, f0, f1
			
			# (ILOFLK(I), ETOT(I), WTFLK(I), XFLK(I), YFLK(I), ZFLK(I), ...
			# ... TXFLK(I), TYFLK(I), TZFLK(I), I = 1, NPFLKA )

			lenFLKLIST = NPFLKA
			FLKLIST = struct.unpack(lenFLKLIST*'i8f', chunkB[:-4])
			Case3_list.append([[NCASE, NPFLKA, NSTMAX, TKESUM, WEIPRI], 
				[i for i in FLKLIST]])

			record.append(3)


		chunkA = f.read(28) # read next chunkA in file

print record[:10]

# print Case3_list[0],Case3_list[1]
# print Case1_list[0],Case1_list[1],Case1_list[2]
# print Case2_list[:8]

# finding primaries with NPFLKA greater than one
# for i in range(0,len(Case3_list),2):
	# if Case3_list[i][1] > 1:
		# print Case3_list[i]

# for i in range(1,len(Case3_list),2):
	# if len(Case3_list[i]) > 1:
		# print Case3_list[i]

