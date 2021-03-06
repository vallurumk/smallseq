from __future__ import division
from collections import defaultdict
import os
import argparse, dr_tools
import pylab as P

"""
collapse multi mirnas only, keep the rest of table intact
"""

def safe_mkdir(path):
	if not os.path.exists(path):
		os.mkdir(path)
		os.chmod(path, 0o774)


def collapse_mirnas(molc_file):
	gene2molc = {}
	gene2trid = {}
	trid2gene = {}
	with open(o.out_molc_files, 'w') as outfh:
		for line in open(molc_file, 'r'):
			if line.startswith('#'):
				print >> outfh, line[:-1]

			else:
				p = line.strip('\n').split('\t')
				trans_ids = p[1]; genename = p[0]
				gene2trid[genename] = trans_ids

				if genename.startswith("hsa"): #selects only mirbase mirnas from the expression table
					molc_counts = map(float, p[2:])
					zeros = [0]*len(molc_counts)			
					gene2molc[genename] = [i+j for i,j in zip(gene2molc.get(genename, zeros), molc_counts)]
				else:
					print >> outfh, line[:-1]
				
		for gene in gene2molc:
			print >> outfh, dr_tools.join(gene, gene2trid[gene], [round(m, 2) for m in gene2molc[gene]])

			

if '__main__' == __name__:
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--in_molc_files', default='counts_molc_preCollapse.txt')
	parser.add_argument('-o', '--out_molc_files', default='counts_molc.txt')
	o = parser.parse_args()

	"""
	call function
	"""
	collapse_mirnas(o.in_molc_files)
		
		








