import common
import uuid
import os
import time
import subprocess
import sys
from operator import add

diskitemtpl = '''
      <Item>
        <rasd:Caption>
        b57db30f-070f-4173-bf6a-333ae9a247b0_Disk1</rasd:Caption>
        <rasd:InstanceId>
        92001497-5161-4233-9e91-0bf07d1d46b5</rasd:InstanceId>
        <rasd:ResourceType>17</rasd:ResourceType>
        <rasd:HostResource>
        f8da1407-601a-4751-bd87-ac32e70c7a86/92001497-5161-4233-9e91-0bf07d1d46b5</rasd:HostResource>
        <rasd:Parent>
        00000000-0000-0000-0000-000000000000</rasd:Parent>
        <rasd:Template>
        00000000-0000-0000-0000-000000000000</rasd:Template>
        <rasd:ApplicationList></rasd:ApplicationList>
        <rasd:StorageId>
        c256eb74-a127-48d5-9321-a6bbcf354326</rasd:StorageId>
        <rasd:StoragePoolId>
        b9bb11c2-f397-4f41-a57b-7ac15a894779</rasd:StoragePoolId>
        <rasd:CreationDate>2013/05/23 19:31:52</rasd:CreationDate>
        <rasd:LastModified>2013/05/23 19:31:54</rasd:LastModified>
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

def construct_fragments(inputimages):
  refs = common.construct_refs(reftpl, inputimages)
  disks = common.construct_disks(disktpl, inputimages)
  hwdisks = common.construct_hw_disks(diskitemtpl, disks)

  return {'filereferencies': reduce(add, refs, ''),
          'disksection': reduce(add, disks, ''),
          'hwdiskitems': reduce(add, hwdisks, '')}

def construct_manifest(files, outdir):
  #TODO: we need to construct metafile
  #      question is if we need it for each image
  pass

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
  metafile += "EOF\n"

  with open(fmeta, 'w+') as f:
    f.write(metafile)
#  return metafile


def convert_images(files, outpath):
  grp_uuidx = str(uuid.uuid1())
  imgdir = os.path.join(outpath, 'images', grp_uuidx)

  os.makedirs(imgdir)
  onames = []
  for fname in files:
    img_uuidx = str(uuid.uuid1())

    foutname = os.path.join(imgdir, str(img_uuidx))
    moutname = os.path.join(imgdir, str(img_uuidx)+'.meta')
    onames.append(foutname)

    sys.stdout.write('Converting {0} to {1}\n'.format(fname, foutname))
    subprocess.check_output(['qemu-img', 'convert', '-O', 'qcow2', fname, foutname])

    # TODO: fix zeroed uuid
    construct_metafile(foutname, moutname, img_uuidx, '00000000-0000-0000-0000-000000000000')

  return files

def write_ovf(outtpl, outpath):
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

  uuidx = str(uuid.uuid1())
  ovfdir = os.path.join(outpath, 'master/vms/', uuidx)
  outname = os.path.join(ovfdir, str(uuidx)+'.ovf')

  os.makedirs(ovfdir)
  with open(outname, 'w+') as ofil:
    ofil.write(outtpl)

