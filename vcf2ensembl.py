#!/bin/python
#22 May 2017 - Adam Scott - 
 
from biomine.variant import variant
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
	ref = variant.nullCheck( ref )
	alt = variant.nullCheck( alt )
	ensFields.append( ref + "/" + alt )
	ensFields.append( "+" )
	ensFields.append( ID )
	return ensFields

def makeID( chrom , pos , ref , alt ):
	return ':'.join( [ chrom , str( pos ) , ref , alt ] )

def removeOverlap( var ):
	var.removeOverlapFromReferenceAndAlternate( )
	return [ var.start , var.stop , var.reference , var.alternate ]

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
		#print( fields )
		chrom = str( fields[0] )
		pos = int( fields[1] )
		ref = fields[3].upper()
		alt = fields[4].upper()
		ensFields = [ str( chrom ) ]
		var = variant(  chromosome = chrom , \
						reference = ref , \
						alternate = alt , \
						start = pos , \
						stop = pos \
					)
		ID = makeID( chrom , pos , ref , alt )
		if len( ref ) == 1 and len( alt ) == 1: #is snv
			ensFields = buildEnsemblLine( chrom , pos , pos , ref , alt , ID )
		else:
			[ start , stop , ref , alt ] = removeOverlap( var )
			ensFields = buildEnsemblLine( chrom , start , stop , ref , alt , ID )
		o.write( '\t'.join( ensFields ) )
		o.write( "\n" )
	f.close()
	o.close()

if __name__ == "__main__":
    main( sys.argv[1:] )
