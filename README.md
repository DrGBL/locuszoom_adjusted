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
wget https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/wgEncodeGencodeAttrsV44.txt.gz
wget https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/knownGene.txt.gz
printf "geneName\tname\tchrom\tstrand\ttxStart\ttxEnd\tcdsStart\tcdsEnd\texonCount\texonStarts\texonEnds\n" > refFlat_protein_coding.txt
zcat knownGene.txt.gz | \
  sort - > knownGene_sorted.txt
zcat wgEncodeGencodeAttrsV44.txt.gz | \
  grep protein_coding | \
  join -1 4 -2 1 -o 1.2,1.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,2.10 - knownGene_sorted.txt | \
  tr " " \\t >> refFlat_protein_coding.txt
rm knownGene.txt.gz knownGene_sorted.txt wgEncodeGencodeAttrsV44.txt.gz


wget http://csg.sph.umich.edu/locuszoom/download/recomb-hg38.tar.gz
tar -xzvf recomb-hg38.tar.gz
sed 's|^chr||g' recomb-hg38/genetic_map_GRCh38_merged.tab | \
  sed 's|^om|chr|g' | \
  sed 's|recomb_rate|recomb|g' | \
  sed 's|pos_cm|cm_pos|g' > recomb-hg38/genetic_map_GRCh38_merged.mod.tab
rm recomb-hg38/genetic_map_GRCh38_merged.tab
mv recomb-hg38/genetic_map_GRCh38_merged.mod.tab recomb-hg38/genetic_map_GRCh38_merged.tab

dbmeister.py --db name_of_your_database.db --snp_pos my_snp_pos_file.txt 
dbmeister.py --db name_of_your_database.db --trans refsnp_trans.txt
dbmeister.py --db name_of_your_database.db --refflat refFlat_protein_coding.txt
dbmeister.py --db name_of_your_database.db --recomb_rate recomb-hg38/genetic_map_GRCh38_merged.tab

```

After this you can run locuszoom normally using the new .db file. Please refer to the original locus zoom git and the wiki it links to for full instructions.
