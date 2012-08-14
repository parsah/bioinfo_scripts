
# Helpful script to convert a SAM file into a fastq file as well as filter
# sequences having a particular chromosome character

import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='SAM to fastq conversion script')
	parser.add_argument('-in', help='Input SAM file [n/a]', metavar='', required=True)
	parser.add_argument('-ignore', help='Ignore particular chromosome []', metavar='',
					default='', type=str) # by default, ignore reads not mapping to reference	
	args = vars(parser.parse_args()) # parse args and render it useful for manipulation 	
	ignore_char, infile = args['ignore'], args['in'] # set user-provided params
	
	for line in open(infile): # parse file and iterate through its entries
		line = line.strip().split('\t') # SAM files are tab-delimited
		if len(line) > 9:
			header, chrom, seq, qual = line[0], line[2], line[9], line[10]
			# If no ignore character is provided, print entire enty. Also,
			# if the ignore character does not equal the current chromosome
			# character, ignore the entry (as it is desired to be ignored)
			if ignore_char == '' or ignore_char != chrom:
				fastq_str = '@'+header+'\n'+seq+'\n+\n'+qual
				print chrom
				