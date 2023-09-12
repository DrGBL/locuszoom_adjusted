# 1.4 (May 1, 2017)

## Bug fixes

*  Ignore quotations in trait name in GWAS catalog
*  Fix plotting BED tracks when region contains no white segments
*  Check for both PDF and SVG files when creating plots
*  Fix EPACTS file not retaining user added columns
*  Fix for when color column would accidentally become a factor
*  Fix for when --flank specified as a plain integer (bp)
*  Fix invalid directory names on Windows
*  Fix for latest gridExtra package
*  Allow p-values of 0 when --no-transform given
*  Fix for titles with multiple lines
*  Corrected error message when results file contains both rsID and chr:pos IDs
*  Order of BED tracks plotted is preserved
*  Fix URLs for lzupdate for EBI catalog and GENCODE data

## Changes

*  There is no longer a default --build, --source, or --pop. You must at least specify --build, along with a suitable LD option (or --no-ld). There were too many instances of users accidentally running with the wrong build. 
*  A warning message will be given when tabix index does not exist for an EPACTS results file
*  Slightly better error messages when issues arise querying the sqlite tables
*  PLINK will use --noweb now

## New data

*  1000G phase 3 from Nov 2014 now included, use --source 1000G_Nov2014, both --build hg19 and --build hg38 are available
*  Database now also contains hg38 coordinates, though we are missing recombination rates mapped to GRCh38. See https://github.com/statgen/locuszoom-standalone/issues/1

## Features added

*  Generate SVG with format=svg
*  Allow ignoring FILTER when using VCF to calculate LD (--ignore-vcf-filter)
*  Highlight multiple regions of gene track by giving multiple hiStart/hiEnd as comma separated values
*  New title argument for specifying titles in expression notation, e.g. expr_title="paste(italic(TCF7L2),' rs7903146')"
*  Highlight a specific gene with hiRequiredGene=T, highRequiredGeneColor="red",requiredGene="TCF7L2"
*  Highlight a particular isoform of a gene with showIso=T requiredGene=ENST00000349937 hiRequiredGene=T
*  Allow multiple required genes, e.g. requiredGene="GENE1,GENE2,GENE3"
*  Select a GENCODE tag to filter by when creating table in DB (example: use only GENCODE basic)

# 1.3 (June 20, 2014)

## Bug fixes

*  Fix for R 3.1's strange idea to change how read.table works in regards to converting obviously numeric columns into char/factors if precision loss was detected. This caused locuszoom to fail completely with a cryptic (for users) error message regarding an operation being meaningless for factors
*  Previously, only variants with the format rs# or chr#:### were allowed, now variants without chr (e.g. #:####) are also allowed
*  Isoform names were not appearing when showIso=T
*  requiredGene sometimes did not work correctly with isoforms, or when the required gene was not available in the region
*  Fixed very old bug where isoforms would not be plotted at all in certain cases
*  Fixed bug when plotting within 1 gene containing 0 exons in the plotting region selected
*  Fixed min/max p-value on second page of PDF
*  warnMissingGenes was mistakenly disabled - is now re-enabled by default (this shows the warning to the right of the genes when there are too many genes to plot)
*  Fixed bzipped files not being detected properly
*  Fixed when users give variants named "RS####" instead of "rs####"

## Backward compatibilty issues

*  Use of built-in annotations (from the .db file) is disabled now by default. These were very old, with no plans of bringing them up to date. Users were likely already using custom annotations with their files. If you however had modified your database previously to use the var_annot table, and still would like to pull annotations from it, use --enable-db-annot

## Features added

*  lzupdate.py script to automatically create/update a database file. This script will download data from UCSC/NCBI/GENCODE, format it appropriately, and insert it into a sqlite3 file that can be used with locuszoom. 
*  lzupdate.py can also generate an updated GWAS catalog (use --gwas-cat)
*  Database provided with release has been updated as of June 20, 2014
*  Can now use different tables for gene information, e.g. --gene-table gencode or --gene-table refFlat. GENCOE is also now included in the database by default
*  Added support for tabix indexes with EPACTS files
*  Allow reading from STDIN instead of directly from a file (use --metal - or --epacts -). This may be useful if you have your own fast method (perhaps tabix, or something else) of selecting out the region you wish to plot. For example: tabix -h <file> 1:1-100 | locuszoom --metal - --refgene TCF7L2 ... Note that you can tabix index METAL files, but you'll need to add a chr and pos column yourself, bgzip it, and then have tabix index it. 
*  Added drawing of multiple horizontal significance lines, use signifLine="5e-08,1e-10" for example. Can also change each line's width and color using signifLineColor="red,blue" or signifLineWidth="2,4"
*  Added support for plotting BED tracks. Use --bed-tracks <BED file> to add tracks below plot, 1 track per label in the label column of the BED file
*  Change color of each marker arbitrarily by specifying a column in your association results containing a color name or hex code, then tell locuszoom the column by using colorCol="name_of_col". This disables showing color by LD. 
*  Can provide a JSON file mapping from specific chromosome names to individual VCF files to use when calculating LD (just provide the JSON file directly to --ld-vcf) 
*  Added options to control the names of EPACTS columns, as the format is still in flux slightly (--epacts-chrom-col, --epacts-beg-col, --epacts-end-col, --epacts-pval-col) 
*  Can specify a GWAS catalog file now directly with --gwas-cat, rather than providing the name of a built-in catalog. The built-in catalogs are still available as well

# 1.2 (May 9, 2013)

## Bug fixes

*  dbmeister.py would complain about not being able to find which
*  which() would fail if a dir on the user's PATH did not exist
*  SQL queries for variant annotations and other tables were run even if the tables did not exist
*  locuszoom now tries to find Rscript and run locuszoom.R accordingly, rather than assuming Rscript was located in /usr/bin/ (can also now change RSCRIPT_PATH in conf file)

## Features added

*  support for March 2012 1000G for computing LD (ASN, AFR, EUR, AMR)
*  lifted over variant annotations from hg18 to hg19
*  updated SNP positions and gene boundaries from snp137 and latest refFlat (as of 2013-01-22)
*  added support for plotting LD with multiple reference SNPs
*  plot credible sets of SNPs from fine-mapping results as a separate track
*  plot GWAS catalog SNPs as a separate track
*  calculate LD from VCF files
*  load EPACTs result files directly

# 1.1 (June 20, 2011)

## Bug fixes

*  hitspec with blank lines would cause crash 
*  hitspec with alternative line endings (unix, windows, etc.) would cause crash
*  hitspec without proper number of columns would crash, proper warning now issued
*  if a SNP's position could not be found when processing hitspec file, program would crash instead of skipping it
*  program would crash if sqlite was not available, now issues proper warning
*  genes would not be displayed at all in the event that all genes in region could not be fit into track below plot
*  if a reference SNP was given as chr:pos but existed in LD files as rs# (or vice versa), plot would be entirely gray 
*  better support for 1000G SNPs (all SNPs are converted to chr/pos internally as a result) 
*  SNPs in hitspec file that were from an earlier genome build were not being translated into the current genome build (instead, it would complain about not finding a position) 
*  users running R 2.13.0 would get a crash regarding a missing library include
*  fixed issue where some gzipped files would cause a crash 

## Features added

*  support for hg19 (for 1000G populations, hapmap will no longer be provided)
*  support for metabochip LD 
*  added --no-ld option, will force locuszoom to skip calculating LD
*  added a warning when metal file contains both rsID and chr:pos SNP names to make sure user selects proper genome build

## Features removed

*  removed the --hits option, this was no longer used and is superseded by --hitspec
*  removed support for pre-computed LD (this was not being maintained, bloated the code, and often was a "cache miss") 
*  (CSG internal version) removed SQL database connections, now runs entirely from sqlite database

# 1.0.3 (Dec 1, 2010)

*  fixed bug where metal files with p-values only within the range [0.1,1] were double -log10 transformed
*  fixed bug in dbmeister.py where indices were not being created after inserting a new snp_pos table, resulting in absurdly long runtimes
*  fixed bug where user supplied database would cause a crash in certain instances (especially forcing offline mode with --offline 1) 
*  changed how gzip/bzip2 files are detected (no longer depends on file extension) 

# 1.0.2 (Sept 27, 2010)

*  added LD files for 1000G June 2010 release
*  added additional populations to LD files for 1000G Aug 2009 (now includes YRI and CHB+JPT). 
*  added support for automatically converting between 1000G chr:pos format and rs# format for SNPs when a difference exists between the user's association results file and LD genotype files (try to use rs# naming if possible, as this is less error prone)
*  fixed bug in LD cache where a reference SNP with no LD able to be computed would cause a crash
*  fixed bug where blank lines in the user's association results file would cause a crash
*  changed --ld to allow for both relative and absolute paths
*  changed error message to read "locuszoom.R" instead of previous "metal2zoom.R"

# 1.0.1 (June 10, 2010)

*  fixed crash if user's python was not compiled with bz2 support
*  fixed --cache None, this will now properly skip creating a LD cache file

# 1.0:

*  initial release
