from string import Template
import sys
import os

tpltypes = {'vsphere': 'vsphere.xml.tpl'}

def doit(tplname, outname):
  with open(tplname) as ftpl:
    tpl = Template(ftpl.read())
    d = {'cpucount': 10000}

    outtpl = tpl.substitute(d)

    with open(outname, 'w+') as ofil:
      ofil.write(outtpl)

    os.stdout.write('{0} wrote.'.format(outname))

def showusage():
  os.stderr.write('''usage: ./gen.py [-t TYPE] [-o OUTFILE] [-h]
      where
        -t TYPE is one of: vsphere(default)
        -o OUTFILE is output OVF name (default output.ovf)
        -h shows this help
      ''')

if __name__ == '__main__':
  typ = 'vsphere'
  outfile = 'output.ovf'

  if '-t' in sys.argv:
    typ = sys.argv[sys.argv.index('-t')+1]
    if typ not in tpltypes.keys():
      os.stderr.write('{0} is unsupported, supported -t options are {1}'.format(typ, tpltypes.keys()))
  if '-o' in sys.argv:
    outfile = sys.argv[sys.argv.index('-o')+1]
  if '-h' in sys.argv:
    showusage()
    exit(1)

  doit(tpltypes[typ], outfile)
