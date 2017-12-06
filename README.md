
## Smallseq data analysis pipeline
This repository provides scripts for analysis of data generated by single-cell small RNA sequencing protocol (Faridani/Abdullayev et al., 2016)


### Prerequisities
Install cutadapt, cgat (from https://github.com/CGATOxford/cgat/releases/tag/v0.2.7), UMI-tools (https://github.com/CGATOxford/UMI-tools), dr_tools.py and argparse.py (https://github.com/danielramskold/S3_species-specific_sequencing)


## Remove UMI from reads: 
First, remove the UMI sequences specifiying the sequence with correct number of Ns
```
maxRlen=40 #maximum read length to define a small RNA
minRlen=41 #minimum read length to define a precursor
nprocs=3 #number of processors to use
source ~/cgat-install/conda-install/bin/activate cgat-scripts
python ../src/remove_umi_from_fastq_v4.py -d rawdata -o rawdata_noUMI -u NNNNNNNN -p $nprocs
```

## Remove adapters and CA from the beginning of each read from all samples
```
for sample in `ls rawdata`; do mkdir -p rawdata_final/$sample; done
mkdir cmds
ls rawdata_final | xargs -I% echo 'cutadapt -a file:../adapters/cutadapt_3prime.fa -e 0.1 -O 1 -u 2 --quiet --minimum-length 18 -o rawdata_final/%/%.fastq rawdata_noUMI/%/%_umiTrim.fq' > cmds/RemoveAdaptors.sh
cat cmds/RemoveAdaptors.sh | parallel -P $nprocs -n 1
```

## Mapping reads to the reference human genome (hg38) with the following STAR options
```
for sample in `ls rawdata`; do mkdir -p starout/$sample; done
ls rawdata_final | xargs -I% echo 'STAR   --runThreadN 10   --genomeDir /mnt/kauffman/sandberglab/star_index/hg38_ERCC_mirnaERCC_v2   --readFilesIn rawdata_final/%/%.fastq      --readFilesCommand -      --outSAMstrandField intronMotif   --outFilterMultimapNmax 50   --outFilterScoreMinOverLread 0   --outFilterMatchNmin 18   --outFilterMatchNminOverLread 0   --outFilterMismatchNoverLmax 0.04   --alignIntronMax 1 --outFileNamePrefix starout/%/' > cmds/map.sh
cat cmds/map.sh | parallel -P $nprocs -n 1
```

## Process alignment file and separate unique and multiple aligned reads
```
ls starout | xargs -I% echo 'samtools view -bS starout/%/Aligned.out.sam | samtools sort - starout/%/% && samtools index starout/%/%.bam' > cmds/ProcessSam.sh
cat cmds/ProcessSam.sh | parallel -P $nprocs -n 1
```

## Remove the clipped reads - i.e reads mapped via soft-clipping.  
```
python ../src/remove_softclipped_reads_parallelized_v3.py -i starout -o starout_clipped -p $nprocs -n 0 -t 3
```

## Extract reads with minimum ${maxRlen} nt read length (for details about cut-off see the methods section of Faridani/Abdullayev et al., 2016)
```
maxRlen=40 #maximum read length to define a small RNA
minRlen=41 #minimum read length to define a precursor
python ../src/subsample_bam_by_readlen_v2.py -d starout_clipped -o starout_max${maxRlen} -c ${maxRlen} -m max
ls starout_max${maxRlen}/*/*.bam | xargs -P $nprocs -n 1 samtools index 
```

## Remove PCR dublicates - aka creating absolute molecule counts
```
source ~/cgat-install/conda-install/bin/activate cgat-scripts
python ../src/remove_umi_dedup.py -d starout_max${maxRlen} -o starout_molc -p $nprocs
```

## Remove precursor reads. OBS: these reads are wrongly assigned as small RNAs, but they are actually coming from precursors.
```
python ../src/remove_reads_with_genomic_TGG.py -i starout_molc -o starout_molc_final -p $nprocs -x ${minRlen}
```

## Count molecules and merge into single file. Custom annotation file could also be used. Make sure it is in GenePred format. 
```
python ../src/count_smallrnas.py -i starout_molc_final -g ../annotations/combined_annots.gp -o counts_molc -p $nprocs
python ../src/merge_countsmallrnaoutput.py counts_molc.txt counts_molc/*/*_Count.txt
```

## Collapse multi miRNAs only, keep the rest of table intact
```
python ../src/collapse_mirnas_on_counts_molc.py -i counts_molc.txt -o counts_molc_final.txt
rm counts_molc.txt
```

```
The counts_molc_final.txt is a table containing molecule counts of all the RNA biotypes in the annotation table. If you get this file, it means the pipeline has been executed cprrectly.
```

## Citation

Please refer to the following article: (Faridani/Abdullayev et al., 2016)



