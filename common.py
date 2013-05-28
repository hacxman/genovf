from string import Template
import sys
import os
from VMDKstream import convert_to_stream
from operator import add
import json
import hashlib
from importlib import import_module


def generate_manifest(files, outdir=''):
  with open(os.path.join(outdir, 'MANIFEST.MF'), 'w+') as fout:
    # hashlib is stupid so we can't use map :(
    mf = generate_manifest_data(files) 
    fout.write(mf)

def generate_manifest_data(files):
  mf = ''
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

  return mf

def convert_images_to_vmdk(files, outpath):
  ofils = []
  for f in files:
    foutname = os.path.join(outpath, os.path.basename(f)+'.vmdk')
    sys.stdout.write('Converting {0} to {1}\n'.format(f, foutname))
    convert_to_stream(f, foutname)

    ofils.append(foutname)

  sys.stdout.write('Converting done.\n')
  return ofils

def construct_refs(intpl, filenames):
  idx = 1
  orefs = [] # output File Referencies fragments for OVF
  for fin in filenames:
    size = os.stat(fin).st_size
    sparsesize = os.stat(fin).st_blocks*512

    d = {'vmdkname': fin, 'fileid': 'file'+str(idx), 'filemaxsize': str(size)}
    tpl = Template(intpl)
    orefs.append(tpl.substitute(d))

  return orefs

def construct_disks(intpl, filenames):
  idx = 1
  orefs = [] # output Disk Section fragments for OVF
  for fin in filenames:
    size = os.stat(fin).st_size
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


