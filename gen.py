#!/usr/bin/python

from string import Template
import sys
import os
from VMDKstream import convert_to_stream
from operator import add
import json
import hashlib

tpltypes = {'vsphere': 'vsphere.xml.tpl'}

reftpl = '<File ovf:href="$vmdkname" ovf:id="$fileid" ovf:size="$filemaxsize"/>'
disktpl = '<Disk ovf:capacity="$capacity" ovf:capacityAllocationUnits="byte" ovf:diskId="$diskid" ovf:fileRef="$fileid" ovf:format="http://www.vmware.com/interfaces/specifications/vmdk.html#streamOptimized" ovf:populatedSize="$populsize"/>'
diskitemtpl = '''
      <Item>
        <rasd:AddressOnParent>$idx</rasd:AddressOnParent>
        <rasd:ElementName>Hard disk $idx</rasd:ElementName>
        <rasd:HostResource>ovf:/disk/$diskid</rasd:HostResource>
        <rasd:InstanceID>$instanceid</rasd:InstanceID>
        <rasd:Parent>3</rasd:Parent>
        <rasd:ResourceType>17</rasd:ResourceType>
        <vmw:Config ovf:required="false" vmw:key="backing.writeThrough" vmw:value="false"/>
      </Item>'''

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


def convert_images(files, outpath):
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



def doit(tplname, outname, inputimages, proffile):
  with open(tplname) as ftpl:
    tpl = Template(ftpl.read())

    refs = construct_refs(reftpl, inputimages)
    disks = construct_disks(disktpl, inputimages)
    hwdisks = construct_hw_disks(diskitemtpl, disks)

    d = {'cpucount': 1,
         'filereferencies': reduce(add, refs, ''), 
         'disksection': reduce(add, disks, ''),
         'hwdiskitems': reduce(add, hwdisks, '')}

    with open(proffile) as prof:
      hwcfg = json.load(prof)
    d.update(hwcfg)

    outtpl = tpl.substitute(d)

    with open(outname, 'w+') as ofil:
      ofil.write(outtpl)

    sys.stdout.write('Wrote {0}.\n'.format(outname))
    generate_manifest(inputimages + [outname])
    sys.stdout.write('Wrote MANIFEST.MF.\n')

def showusage():
  sys.stderr.write('''usage: ./gen.py [-t TYPE] [-o OUTFILE] [-c] [-h] -p profile.json -i IMAGE1 IMAGE2...
      where
        -t TYPE is one of: vsphere(default)
        -o OUTFILE is output OVF name (default output.ovf)
        -c convert raw imgs to streamable VMDKs
        -i specifies list of input disk imgs
        -p specifies HW profile
        -h shows this help\n''')

if __name__ == '__main__':
  typ = 'vsphere'
  outfile = 'output.ovf'
  cvt = False
  inputimages = []

  if '-t' in sys.argv:
    typ = sys.argv[sys.argv.index('-t')+1]
    if typ not in tpltypes.keys():
      sys.stderr.write('{0} is unsupported, supported -t options are {1}\n'.format(typ, tpltypes.keys()))
  if '-o' in sys.argv:
    outfile = sys.argv[sys.argv.index('-o')+1]
  if '-c' in sys.argv:
    cvt = True
  if '-h' in sys.argv:
    showusage()
    exit(1)
  if '-i' in sys.argv:
    argidx = sys.argv.index('-i')+1
    for inf in sys.argv[argidx:]:
      if not inf.startswith('-'): 
        inputimages.append(inf)
      else:
        break
  else:
    sys.stderr.write('-i argument is mandatory. exitting.\n')
    exit(2)

  if '-p' in sys.argv:
    proffile = sys.argv[sys.argv.index('-p')+1]
  else:
    sys.stderr.write('-p argument is mandatory. exitting.\n')
    exit(2)


  if cvt:
    inputimages = convert_images(inputimages, '.')

  doit(tpltypes[typ], outfile, inputimages, proffile)
