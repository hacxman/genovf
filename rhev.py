import common
import uuid
import os
import time
import subprocess
import sys
from operator import add
from common import create_archive
from string import Template

__all__ = ['construct_fragments', 'construct_manifest', 'convert_images',
           'create_archive', 'template_name', 'postprocess_ovf']

diskitemtpl = '''
      <Item>
        <rasd:Caption>Hard Disk $idx</rasd:Caption>
        <rasd:InstanceId>$instanceid</rasd:InstanceId>
        <rasd:ResourceType>17</rasd:ResourceType>
        <rasd:HostResource>$diskid</rasd:HostResource>
        <rasd:Parent>00000000-0000-0000-0000-000000000000</rasd:Parent>
        <rasd:Template>00000000-0000-0000-0000-000000000000</rasd:Template>
        <rasd:ApplicationList></rasd:ApplicationList>
        <rasd:StorageId>c256eb74-a127-48d5-9321-a6bbcf354326</rasd:StorageId>
        <rasd:StoragePoolId>b9bb11c2-f397-4f41-a57b-7ac15a894779</rasd:StoragePoolId>
        <rasd:CreationDate>$$exportdate</rasd:CreationDate>
        <rasd:LastModified>$$exportdate</rasd:LastModified>
        <Type>disk</Type>
        <Device>disk</Device>
        <rasd:Address></rasd:Address>
        <BootOrder>0</BootOrder>
        <IsPlugged>true</IsPlugged>
        <IsReadOnly>false</IsReadOnly>
        <Alias></Alias>
      </Item>'''
reftpl = '<File ovf:href="$vmdkname" ovf:id="$fileid" ovf:size="$filemaxsize"/>'
disktpl = '<Disk ovf:capacity="$capacity" ovf:capacityAllocationUnits="byte" ovf:diskId="$diskid" ovf:fileRef="$fileid" ovf:format="http://www.vmware.com/interfaces/specifications/vmdk.html#streamOptimized" ovf:populatedSize="$populsize"/>'

import module_locator
template_name = os.path.join(module_locator.module_path(), 'rhev.xml.tpl')

def construct_hw_disks(intpl, diskids):
  idx = 0
  orefs = []
  for did in diskids:
    print did
    idx = did.find('images/')
    diskid = did[idx+len('images/'):]
    instid  = diskid[diskid.find('/')+1:]

    d = {'idx': idx, 'diskid': diskid, 'instanceid': instid} #17+idx}
    tpl = Template(intpl)
    orefs.append(tpl.substitute(d))
  return orefs

def set_export_date(data):
  print type(data)
  return Template(data).substitute({'exportdate':
    time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())})

def construct_fragments(origimages, inputimages, outdir):
#  old = common.construct_hw_disks
#  common.construct_hw_disks = construct_hw_disks
  output = common.construct_fragments(origimages,
      inputimages, reftpl, disktpl, diskitemtpl, outdir,
      construct_hw_disks=construct_hw_disks)
#  common.construct_hw_disks = old

#  output = set_export_date(output)
  return output

#def construct_fragments(origimages, inputimages):
#  return common.construct_fragments(origimages,
#      inputimages, reftpl, disktpl, diskitemtpl)

def construct_manifest(files, outdir):
  #TODO: we need to construct metafile
  #      question is if we need it for each image
  return None

def construct_metafile(fimg, fmeta, img_idx, dom_idx):
  metafile=""

  #TODO: we should know dom_idx in advance
  #      which is not possible unless you're oracle
  #      and a crystal ball owner. many thanks to
  #      standards adherers out there.
  metafile += "DOMAIN=" + dom_idx + "\n"
  # saved template has VOLTYPE=SHARED
  metafile += "VOLTYPE=LEAF\n"
  metafile += "CTIME=" + str(time.time()) + "\n"
  # saved template has FORMAT=COW
#  if self.qcow_size:
  metafile += "FORMAT=COW\n"
#  else:
#      metafile += "FORMAT=RAW\n"
  metafile += "IMAGE=" + img_idx + "\n"
  metafile += "DISKTYPE=1\n"
  metafile += "PUUID=00000000-0000-0000-0000-000000000000\n"
  metafile += "LEGALITY=LEGAL\n"
  metafile += "MTIME=" + str(time.time()) + "\n"
  metafile += "POOL_UUID=" + '00000000-0000-0000-0000-000000000000' + "\n"
  # assuming 1KB alignment
  
  metafile += "SIZE=" + str(os.stat(fimg).st_size) + "\n"
  metafile += "TYPE=SPARSE\n"
  metafile += "DESCRIPTION=Created by genovf\n"
  #[MaS[MaS[MaS[MaS[MaS[MaS[M`S[M`S[M`S[M`S[M#S

  with open(fmeta, 'w+') as f:
    f.write(metafile)
  return fmeta


def convert_images(files, outpath):
  grp_uuidx = str(uuid.uuid1())
  imgdir = os.path.join(outpath, 'images', grp_uuidx)

  os.makedirs(imgdir)
  onames = []
  mfiles = []
  for fname in files:
    img_uuidx = str(uuid.uuid1())

    foutname = os.path.join(imgdir, str(img_uuidx))
    moutname = os.path.join(imgdir, str(img_uuidx)+'.meta')
    onames.append(foutname)
    mfiles.append(moutname)

    sys.stdout.write('Converting {0} to {1}\n'.format(fname, foutname))
    subprocess.check_output(['qemu-img', 'convert', '-O', 'qcow2', fname, foutname])

    # TODO: fix zeroed uuid
    construct_metafile(foutname, moutname, img_uuidx, '00000000-0000-0000-0000-000000000000')

  return [files, onames, mfiles]

def postprocess_ovf(data):
  return set_export_date(data)

def write_ovf(ovfname, outtpl, outpath):
  '''
  doc taken from ovirt-image-uploader
  The image uploader can be used to list export storage domains and upload OVF files to
  export storage domains. This tool only supports OVF files created by oVirt engine.  OVF archives should have the
  following characteristics:
  1. The OVF archive must be created with gzip compression.
  2. The archive must have the following internal layout:
      |-- images
      |   |-- <Image Group UUID>
      |        |--- <Image UUID (this is the disk image)>
      |        |--- <Image UUID (this is the disk image)>.meta
      |-- master
      |   |---vms
      |       |--- <UUID>
      |             |--- <UUID>.ovf
  '''
  # ovfname is ignored atm and is used in vsphere module

  uuidx = str(uuid.uuid1())
  ovfdir = os.path.join(outpath, 'master/vms/', uuidx)
  outname = os.path.join(ovfdir, str(uuidx)+'.ovf')

  os.makedirs(ovfdir)
  with open(outname, 'w+') as ofil:
    ofil.write(outtpl)

  return outname

