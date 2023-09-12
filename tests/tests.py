#!/usr/bin/env python
import os
import sys
import re
import time
import hashlib
import tempfile
from killableprocess import *
from multiprocessing import *

PYEXE = "python"

# Fix path of script to be absolute.
sys.argv[0] = os.path.abspath(sys.argv[0])

# Import m2z modules
sys.path.append(
  os.path.join(os.path.dirname(sys.argv[0]),"../src")
)

from m2zutils import *

# Import testing modules
sys.path.append(
  os.path.join(os.path.dirname(sys.argv[0]),"src/")
)

from pyPdf import PdfFileWriter, PdfFileReader 

# Force data to be written to file. 
def hard_write(f,data):
  print >> f, data
  f.flush()
  os.fsync(f)

# Combine a list of PDFs into a single file. 
# Only combines the first page of each PDF. 
def combine_plots(pdf_list,out_file):
  output = PdfFileWriter()
  for pdf in pdf_list:
    if not os.path.isfile(pdf):
      continue
  
    try:
      pdfobj = PdfFileReader(file(pdf,"rb"))
      output.addPage(pdfobj.getPage(0))
    except:
      print >> sys.stderr, "\nError combining PDF %s\n" % pdf

  out_stream = file(out_file,"wb")
  output.write(out_stream)
  out_stream.close()

# Given a directory, give a list of all files 
# in all directories underneath. 
def walk_flat(path):
  files = []
  for i in os.walk(path):
    real_path = os.path.realpath(i[0])
    for f in i[2]:
      full_file = os.path.join(real_path,f)
      files.append(full_file)
  
  return files

# Get the size of a file as a long. 
def getFileSize(file):
  return os.stat(file).st_size

# Filter a list of files down to only those with a PDF file extension. 
def filterPDF(file_list):
  p = re.compile("\.pdf",re.I)
  return filter(lambda x: p.search(x) != None,file_list)

# Class for watching a directory tree for file creations/deletions/changes. 
class FileSystemWatcher():
  def __init__(self,dir,recursive=False):
    self.dir = dir
    self.snap_start = None
    self.snap_end = None
    self.recursive = recursive
  
    if not os.path.isdir(dir):
      raise ValueError, "Error: dir %s does not exist." % str(dir)

  # Start watching the file system below self.dir for changes. 
  def start(self):
    if self.recursive:
      self.snap_start = walk_flat(self.dir)
    else:
      self.snap_start = os.listdir(self.dir)
 
    self.snap_end = None; # clear out end snapshot
  
  # Stop watching. 
  def end(self):
    if self.recursive:
      self.snap_end = walk_flat(self.dir)
    else:
      self.snap_end = os.listdir(self.dir)

  # Find files that were created between start/end. 
  def find_new(self):
    return sorted(list(set(self.snap_end).difference(set(self.snap_start))))
      
  # Find files that were deleted between start/end. 
  def find_removed(self):
    return sorted(list(set(self.snap_start).difference(set(self.snap_end))))

  # Find files whose modification times changed between start/end. 
  def find_mod_changed(self):
    pass

# Class responsible for running a set of Tests. 
class TestSuite():
  def __init__(self,bin,args,run_dir,log_file="log_file.txt",multi=5):
    self.bin = find_systematic(bin)
    
    if args != None:
      self.bin += " " + " ".join(args)
    
    self.run_dir = find_systematic(run_dir)
    self.tests = []
    self.log = log_file
    self.multi = multi
    if not os.path.isdir(self.run_dir):
      raise ValueError, "Error: dir %s is not a directory." % str(run_dir)

  def add_test(self,test):
    test.id = len(self.tests)
    self.tests.append(test)

  def run_all(self):
    cwd = os.getcwd()

    print "Running %i tests.." % len(self.tests)
    
    # Try to change to run directory. 
    os.chdir(self.run_dir)
 
    # Create directory to work within.
    work_dir = time.strftime("%Y-%m-%d_%H-%M-%S")
    os.mkdir(work_dir)
    os.chdir(work_dir); 

    # Setup log file if requested. 
    log_file = None
    if self.log:
      log_file = os.path.join(os.getcwd(),self.log)
      proc_manager = Manager()
      log_lock = proc_manager.Lock()
    else:
      raise ValueError, "Error: must give a log file name by log_file= parameter."

    for test in self.tests:
      if test.bin == None:
        test.bin = self.bin
     
      if log_file != None:
        test.out_file = log_file
        test.out_lock = log_lock

    # Run tests.
    test_results = {}
    all_pdfs = []
    finished_tests = []
    if self.multi > 1:
      pool = Pool(self.multi,maxtasksperchild=1)
      proc_results = []
      for test in self.tests:
        proc_results.append(pool.apply_async(test))
      
      print "Waiting for tests to terminate.."
      pool.close()
      pool.join()

      for presult in proc_results:
        test_done = presult.get()

        finished_tests.append(test_done)
        all_pdfs.extend(test_done.pdfs)

        for r in test_done.results:
          test_results.setdefault(test_done.id,[]).append(r)
    else:
      for test in self.tests:
        test_done = test()

        finished_tests.append(test_done)
        all_pdfs.extend(test_done.pdfs)

        for r in test_done.results:
          test_results.setdefault(test_done.id,[]).append(r)

    # Combine PDFs. 
    out_name = "allpdfs_" + time.strftime("%Y-%m-%d_%H-%M-%S") + ".pdf"
    combine_plots(all_pdfs,out_name)

    # Combine gold standard plots. 
    gold_list = []
    for test in finished_tests:
      if test.gold_standard != None and test.gold_standard != "":
        gold_list.append(test.gold_standard)
        for p in test.pdfs:
          gold_list.append(p)

    if len(gold_list) > 0:
      gold_out = "gold_" + time.strftime("%Y-%m-%d_%H-%M-%S") + ".pdf"
      combine_plots(gold_list,gold_out)

    # Change back to original directory. 
    os.chdir(cwd)

    # Write out summary of test results. 
    for i in xrange(len(test_results)):
      result = test_results[i]
      test = self.tests[i]
      
      log = open(log_file,"a")

      hard_write(log,"Test [%i] - %s:" % (i,test.title))
      for r in result:
        hard_write(log,"Result:")
        hard_write(log,"|-  Pass: [%s]" % str(r['pass']))
        hard_write(log,"|-  Message: %s" % str(r['msg']))
        hard_write(log,"|-  File: %s" % ("NA" if not r.has_key('file') else str(r['file'])))
        hard_write(log,"-------")
  
      hard_write(log,"")

      log.close()

class Test():
  def __init__(self,cmd_string,out_file=None,title="",timeout=-1,should_fail=False,delay=None,plot_title=None,plot_expr_title=None):
    # Set before execution:
    self.id = None; 
    self.title = title
    self.plot_title = plot_title
    self.plot_expr_title = plot_expr_title
    self.bin = None
    self.cmd = cmd_string
    self.run_cmd = None
    self.required_files = []
    self.timeout = timeout
    self.gold_standard = ""
    self.should_fail = should_fail
    self.delay = delay

    self.out_file = out_file
    self.out_lock = None

    # Set after execution: 
    self.files = []
    self.pdfs = []

  def add_required_file(self,file):
    self.required_files.append(find_systematic(file))

  def gold_std(self,file):
    self.gold_standard = find_systematic(file)

  def hash(self):
    return hashlib.md5(self.cmd + self.title + "".join(required_files))

  def __call__(self):
    return self.run()

  def run(self):
    if self.delay != None:
      time.sleep(self.delay)

    self.files = []
    self.pdfs = []

    # Create temporary directory to execute in. 
    orig_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp(dir=".")
    time.sleep(0.5)
    os.chdir(temp_dir)

    # Make sure required files exist. 
    for f in self.required_files:
      if not os.path.isfile(f):
        return [{'pass':False,'msg':"Required file missing: %s" % str(f)}]
    
    # Form command line. 
    run_cmd = None
    if self.bin:
      run_cmd = PYEXE + " " + self.bin + " " + self.cmd
    else:
      raise ValueError, "Bin not specified."

    # Was there a title?
    if self.plot_title is not None:
      if '"' in self.plot_title:
        run_cmd += " title=%s" % str(self.plot_title)
      else:
        run_cmd += " title=\"%s\"" % str(self.plot_title)
    elif self.plot_expr_title is not None:
      if '"' in self.plot_expr_title:
        run_cmd += " expr_title=%s" % str(self.plot_expr_title)
      else:
        run_cmd += " expr_title=\"%s\"" % str(self.plot_expr_title)
    else:
      run_cmd += " title=\"%s\"" % str(self.title)

    self.run_cmd = run_cmd
    print "[%i] %s -- %s" % (self.id,self.title,run_cmd)

    # Start watching directories below the run directory for changes. 
    watcher = FileSystemWatcher(dir=".",recursive=True)
    watcher.start()

    # Run the test. 
    proc_stream = tempfile.NamedTemporaryFile("r+")
    proc = Popen(run_cmd,shell=True,stdout=proc_stream,stderr=proc_stream)
    retcode = proc.wait(timeout=self.timeout)
    watcher.end()

    print "[%i] %s -- finished!" % (self.id,self.title)
    
    # Get output from process. 
    proc_stream.seek(0)
    proc_string = proc_stream.read()
    proc_stream.close();    

    # Test results stored here. 
    results = []; 

    # Did the program catch an error? 
    caught_error = re.compile("error",re.I).search(proc_string)
    if caught_error != None:
      if self.should_fail:
        results.append({'pass':True,'msg':"Error was detected by program."})
      else:
        results.append({'pass':False,'msg':"An error was detected by the program."})
    else:
      if self.should_fail:
        results.append({'pass':False,'msg':"Test was expected to fail, but no error message was detected."})
        
    # Were any tracebacks generated? 
    traceback = re.compile("Traceback").search(proc_string)
    if traceback != None:
      if self.should_fail:
        results.append({'pass':False,'msg':"Test failed as expected, but traceback was detected."})
      else:
        results.append({'pass':False,'msg':"A traceback was detected."});        

    # Check for PDF creation. 
    self.files = watcher.find_new()
    self.pdfs = filterPDF(self.files)

    if len(self.pdfs) == 0:
      if not self.should_fail:
        results.append({'pass':False,'msg':"No PDF generated."})
    else:
      for pdf in self.pdfs:
        size = getFileSize(self.pdfs[0])
        if size > 0:
          results.append({'pass':True,'msg':"PDF success.",'file':pdf})
        else:
          results.append({'pass':False,'msg':"PDF generated, but file size was 0.",'file':file})

    self.results = results

    # Redirect output. 
    self.out_lock.acquire()
    print self.out_file
    with open(self.out_file,"a") as out:
      out.write("$ Test [%i]: %s\n" % (self.id,self.title))
      out.write(proc_string)
      out.write("\n")
    self.out_lock.release()

    return self

def create_tests(file):
  print "Creating test cases.."
  
  tests = []; 

  execfile(file)

  return tests

def main():
  test_cases = sys.argv[1]
  if not os.path.isfile(test_cases):
    sys.exit("Error: test case file does not exist!")

  test_list = create_tests(test_cases)
  
  print "Setting up tests.."
  suite = TestSuite(
    bin="src/m2zfast.py",
    args=[],
    run_dir="tests/results",
    log_file="log_file.txt",
    multi=16
   )

  print "Adding test cases to testing suites.."
  for test in test_list:
    suite.add_test(test)

  print "Executing tests.."
  suite.run_all()

if __name__ == "__main__":
  main()
