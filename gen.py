#!/usr/bin/python

from string import Template
import sys
import os
from VMDKstream import convert_to_stream
from operator import add
import json
import hashlib
from importlib import import_module
from itertools import izip_longest

tpltypes = {'vsphere': 'vsphere.xml.tpl'}

converters = {'vsphere': 'vsphere', 'rhev': 'rhev'}


#def doit(tplname, outname, inputimages, proffile, typ):
#  with open(tplname) as ftpl:
#    tpl = Template(ftpl.read())
#
#    refs = construct_refs(reftpl, inputimages)
#    disks = construct_disks(disktpl, inputimages)
#    hwdisks = construct_hw_disks(diskitemtpl[typ], disks)
#
#    d = {'cpucount': 1,
#         'filereferencies': reduce(add, refs, ''),
#         'disksection': reduce(add, disks, ''),
#         'hwdiskitems': reduce(add, hwdisks, '')}
#
#    with open(proffile) as prof:
#      hwcfg = json.load(prof)
#    d.update(hwcfg)
#
#    outtpl = tpl.substitute(d)
#
#    with open(outname, 'w+') as ofil:
#      ofil.write(outtpl)
#
#    sys.stdout.write('Wrote {0}.\n'.format(outname))
#    generate_manifest(inputimages + [outname])
#    sys.stdout.write('Wrote MANIFEST.MF.\n')
#
def doit2(mod, outname, (origimages, inputimages, otherf),
          proffile, outdir, make_archive):
  with open(mod.template_name) as ftpl:
    tpl = Template(ftpl.read())

    f = mod.construct_fragments(origimages, inputimages)
    map(lambda x: reduce(add, f[x], ''), f.keys())
    print f

    with open(proffile) as prof:
      hwcfg = json.load(prof)
    f.update(hwcfg)
    outtpl = tpl.substitute(f)
    ovf_name = mod.write_ovf(outname, outtpl, outdir)

  img_meta_paired = filter(lambda _x: _x is not None,
      reduce(lambda _u, (_v, _w): _u + [_v, _w],
          izip_longest(inputimages, otherf), []))

#  print outname, [ovf_name] + img_meta_paired]
  if make_archive:
    mod.create_archive(outname+'.ova', [ovf_name] + img_meta_paired)
  print outname+'.ova'


def showusage():
  sys.stderr.write('''usage: ./gen.py [-t TYPE] [-o OUTFILE] [-c] [-h] -p profile.json -i IMAGE1 IMAGE2...
      where
        -t TYPE is one of: vsphere(default), rhev
        -o OUTFILE is output OVF name (default output.ovf)
        -O OUTDIR is output directory (default .)
        -c convert raw imgs to target format (streamable VMDK, QCOW2; depends on -t)
        -i specifies list of input disk imgs
        -p specifies HW profile
        -a tar results to obtain OVA (archive) intead of OVF + rest
        -h shows this help\n''')

if __name__ == '__main__':
  typ = 'vsphere'
  outfile = 'output.ovf'
  cvt = False
  inputimages = []
  outdir = '.'
  make_archive = False

  if '-t' in sys.argv:
    typ = sys.argv[sys.argv.index('-t')+1]
    if typ not in converters.keys():
      sys.stderr.write('{0} is unsupported, supported -t options are {1}\n'.format(typ, converters.keys()))
  if '-o' in sys.argv:
    outfile = sys.argv[sys.argv.index('-o')+1]
  if '-O' in sys.argv:
    outdir = sys.argv[sys.argv.index('-O')+1]
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

  if '-a' in sys.argv:
    make_archive = True

  mod = import_module(converters[typ])
  if cvt:
    origimages, inputimages, otherf = mod.convert_images(inputimages, outdir)

  doit2(mod, outfile, (origimages, inputimages, otherf),
        proffile, outdir, make_archive)
  #exit(1987)

  #doit(tpltypes[typ], outfile, inputimages, proffile, typ)
