from string import Template
import sys
import os
from VMDKstream import convert_to_stream
from operator import add
import json
import hashlib
from importlib import import_module
import tarfile

def construct_fragments(origimages, inputimages,
    reftpl, disktpl, diskitemtpl):
  refs = construct_refs(reftpl, origimages, inputimages)
  disks = construct_disks(disktpl, origimages, inputimages)
  hwdisks = construct_hw_disks(diskitemtpl, disks)

  return {'filereferencies': reduce(add, refs, ''),
          'disksection': reduce(add, disks, ''),
          'hwdiskitems': reduce(add, hwdisks, '')}

def construct_manifest(files, outdir=''):
  fname = os.path.join(outdir, 'MANIFEST.MF')

  with open(fname, 'w+') as fout:
    # hashlib is stupid so we can't use map :(
    mf = generate_manifest_data(files, outdir)
    fout.write(mf)
  return fname

def generate_manifest_data(files, outdir):
  mf = ''
  #fixup path so it will have trailing slash
  cwd = os.getcwd()
  outdir = os.path.join(outdir, '')
  outdirslen = len(outdir)
  files = map(lambda fil: fil[outdirslen:], files)

  os.chdir(outdir)

  for img in files:
    sys.stdout.write('Calculating hash for {0}\n'.format(img))
    with open(img, 'rb') as fin:
      digest = hashlib.sha256()
      while True:
        r = fin.read(1024*1024)
        if r == '':
          break
        digest.update(r)

      digest_str = digest.hexdigest()
      mf += "SHA256(%s)= %s\n" % (img, digest_str)

  os.chdir(cwd)
  return mf

def convert_images_to_vmdk(files, outpath):
  ofils = []
  os.makedirs(outpath)
  for f in files:
    foutname = os.path.join(outpath, os.path.basename(f)+'.vmdk')
    sys.stdout.write('Converting {0} to {1}\n'.format(f, foutname))
    convert_to_stream(f, foutname)

    ofils.append(foutname)

  sys.stdout.write('Converting done.\n')
  return [files, ofils, []]

def construct_refs(intpl, origimages, filenames):
  idx = 1
  orefs = [] # output File Referencies fragments for OVF
  for ofin, fin in zip(origimages, filenames):
    size = os.stat(ofin).st_size
    sparsesize = os.stat(fin).st_blocks*512

    d = {'vmdkname': fin, 'fileid': 'file'+str(idx), 'filemaxsize': str(size)}
    tpl = Template(intpl)
    orefs.append(tpl.substitute(d))

  return orefs

def construct_disks(intpl, origimages, filenames):
  idx = 1
  orefs = [] # output Disk Section fragments for OVF
  for ofin, fin in zip(origimages, filenames):
    size = os.stat(ofin).st_size
    sparsesize = os.stat(fin).st_blocks*512

    d = {'capacity': str(size), 'diskid': 'vmdisk'+str(idx),
         'fileid': 'file'+str(idx), 'populsize': str(sparsesize)}
    tpl = Template(intpl)
    orefs.append(tpl.substitute(d))

  return orefs

def construct_hw_disks(intpl, diskids):
  idx = 0
  orefs = [] # output Disk Section fragments for OVF
  for did in diskids:
    d = {'idx': idx, 'diskid': 'vmdisk'+str(idx+1), 'instanceid': 17+idx}
    #TODO: this instanceid thingy needs systematic fix
    #      17 is magical number

    tpl = Template(intpl)
    orefs.append(tpl.substitute(d))

  return orefs

def create_archive(outfile, files, gzipit=True, stripandcwd=True):
  mode = 'w' if not gzipit else 'w|gz'

  with tarfile.open(outfile, mode) as tar:
    for x in files:
      if stripandcwd:
        cwd = os.getcwd()
        dirname = os.path.dirname(x)
        name = os.path.basename(x)
        os.chdir(dirname)
      else:
        name = x

      tar.add(name)

      if stripandcwd:
        os.chdir(cwd)
    #map(lambda x: tar.add(x), files)
