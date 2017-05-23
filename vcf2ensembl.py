#!/bin/python
#22 May 2017 - Adam Scott - 
 
import sys
import getopt

def usage():
	print """
vcf2ensembl : convert .vcf variants to ensembl format

USAGE: vcf2ensembl <input> <output>
<input>     .vcf file
<output>    .tsv file in Ensembl variant format
	"""

def checkInputs( args ):
	if len(args) != 2:
		usage();
		sys.exit()

def buildEnsemblLine( chrom , start , stop , ref , alt , ID ):
	ensFields = []
	ensFields.append( chrom )
	ensFields.append( str( start ) )
	ensFields.append( str( stop ) )
	ref = nullCheck( ref )
	alt = nullCheck( alt )
	ensFields.append( ref + "/" + alt )
	ensFields.append( "+" )
	ensFields.append( ID )
	return ensFields

def makeID( chrom , pos , ref , alt ):
	return ':'.join( [ chrom , str( pos ) , ref , alt ] )

def removeOverlap( pos , ref , alt ):
	start = pos
	stop = pos
	updatedRef = ""
	updatedAlt = ""
	loverlap = 0
	for i in range( 0 , min( [ len( ref ) , len( alt ) ] ) ):
		if ref[i] == alt[i]:
			loverlap = i
			next
		else:
			break
	if loverlap < len( ref ) - 1:
		updatedRef = ref[loverlap+1:]
	if loverlap < len( alt ) - 1:
		updatedAlt = alt[loverlap+1:]
	[ start , stop ] = getStartStop( pos , loverlap , updatedRef , updatedAlt )
	updatedRef = nullCheck( updatedRef )
	updatedAlt = nullCheck( updatedAlt )
	return [ start , stop , updatedRef , updatedAlt ]

def getStartStop( pos , loverlap , updatedRef , updatedAlt ):
	start = pos + loverlap + 1
	stop = pos
	if len( updatedRef ) < len( updatedAlt ) and len( updatedRef ) == 0: #insertion
		start -= 1
		stop = start + 1
	elif len( updatedRef ) > len( updatedAlt ) and len( updatedAlt ) == 0: #deletion
		stop = start + len( updatedRef ) - 1
	elif len( updatedRef ) > 0 and len( updatedAlt ) > 0: #complex
		stop = start + len( updatedAlt )
	else: #dunno
		print( "Unusual ref alt start stop: " + updatedRef + " " + updatedAlt + " " + str( start ) + " " + str( stop ) )
	return [ start , stop ]

def nullCheck( val ):
	if not val:
		val = "-"
	return val

def main( args ):
	checkInputs( args )

	try:
		f = open( args[0] , "r" )
	except IOError:
		print( "Cannot open input file" )

	try:
		o = open( args[1] , "w" )
	except IOError:
		print( "Cannot open output file" )

#read input file
	header = ""
	for line in f:
		if line[0] == "#":
			header += line
			continue
		fields = line.strip().split( "\t" )
		chrom = str( fields[0] )
		pos = int( fields[1] )
		ref = fields[3].upper()
		alt = fields[4].upper()
		ensFields = [ str( chrom ) ]
		ID = makeID( chrom , pos , ref , alt )
		if len( ref ) == 1 and len( alt ) == 1: #is snv
			ensFields = buildEnsemblLine( chrom , pos , pos , ref , alt , ID )
		else:
			[ start , stop , ref , alt ] = removeOverlap( pos , ref , alt )
			ensFields = buildEnsemblLine( chrom , start , stop , ref , alt , ID )
		o.write( '\t'.join( ensFields ) )
		o.write( "\n" )
	f.close()
	o.close()

if __name__ == "__main__":
    main( sys.argv[1:] )
