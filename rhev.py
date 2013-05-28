import common
import uuid
import os

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

template_name = 'rhev.xml.tpl'

def construct_fragments(inputimages):
  refs = common.construct_refs(reftpl, inputimages)
  disks = common.construct_disks(disktpl, inputimages)
  hwdisks = common.construct_hw_disks(diskitemtpl, disks)

  return {'filereferencies': refs,
          'disksection': disks,
          'hwdiskitems': hwdisks}

def construct_manifest(files, outdir):
  #TODO: we need to construct metafile
  #      question is if we need it for each image
  pass

def convert_images(files, outpath):
  return files

def write_ovf(outtpl, outpath):
  uuidx = str(uuid.uuid1())
  ovfdir = os.path.join(outpath, 'master/vms/', uuidx)
  outname = os.path.join(ovfdir, str(uuidx)+'.ovf')

  os.mkdir(ovfdir)
  with open(outname, 'w+') as ofil:
    ofil.write(outtpl)

