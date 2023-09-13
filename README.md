# locuszoom_adjusted
A slight adjustment to locuszoom to easily use whatever reference you want (no more rsids!)

Original locuszoom code can be obtained from this repository: https://github.com/statgen/locuszoom-standalone

*** Instructions ***

Use the following code to build the new locuszoom reference, as was done for the plots in https://www.medrxiv.org/content/10.1101/2023.06.26.23291885v1 .

In this case I use hg38. Once that's done you can use the locuszoom function in the bin folder.

```my_snp_pos_file.txt``` is a tsv file with the following header: ```snp     chr     pos```, where snp is the variant ID.

```refsnp_trans.txt``` is a tsv file with the following header: ```rs_orig rs_current```, where both columns are the same variant ID.

All other files are created to downloaded using the code below.

```
cd /path/to/your/directory/

#build new reference
wget https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/refFlat.txt.gz
gzip -d refFlat.txt.gz
printf "geneName\tname\tchrom\tstrand\ttxStart\ttxEnd\tcdsStart\tcdsEnd\texonCount\texonStarts\texonEnds\n" > refFlat_header.txt
cat ${pathOut}refFlat_header.txt ${pathOut}refFlat.txt > ${pathOut}refFlat_new.txt
awk 'FNR==NR {a[$2]; next} $1 in a' protein_coding_genes.tsv refFlat_new.txt | cat refFlat_header.txt - > refFlat_protein_coding.txt

wget http://csg.sph.umich.edu/locuszoom/download/recomb-hg38.tar.gz
tar -xzvf ${pathOut}recomb-hg38.tar.gz
sed 's|^chr||g' recomb-hg38/genetic_map_GRCh38_merged.tab | \
  sed 's|^om|chr|g' | \
  sed 's|recomb_rate|recomb|g' | \
  sed 's|pos_cm|cm_pos|g' > recomb-hg38/genetic_map_GRCh38_merged.mod.tab
rm ${pathOut}recomb-hg38/genetic_map_GRCh38_merged.tab
mv ${pathOut}recomb-hg38/genetic_map_GRCh38_merged.mod.tab recomb-hg38/genetic_map_GRCh38_merged.tab

dbmeister.py --db ${pathOut}bangladesh.db --snp_pos ${pathOut}my_snp_pos_file.txt 
dbmeister.py --db ${pathOut}bangladesh.db --trans ${pathOut}refsnp_trans.txt
dbmeister.py --db ${pathOut}bangladesh.db --refflat ${pathOut}refFlat_protein_coding.txt
dbmeister.py --db ${pathOut}bangladesh.db --recomb_rate ${pathOut}recomb-hg38/genetic_map_GRCh38_merged.tab

```
