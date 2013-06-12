import common
from common import create_archive

__all__ = ['construct_fragments', 'construct_manifest', 'convert_images',
           'create_archive', 'template_name']

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

import module_locator
template_name = os.path.join(module_locator.module_path(), 'vsphere.xml.tpl')

def construct_fragments(origimages, inputimages):
  refs = construct_refs(reftpl, origimages, inputimages)
  disks = construct_disks(disktpl, origimages, inputimages)
  hwdisks = construct_hw_disks(diskitemtpl, disks)

  return {'filereferencies': refs,
          'disksection': disks,
          'hwdiskitems': hwdisks}

def construct_manifest(files, outdir):
  common.generate_manifest(files, outdir)

def convert_images(files, outpath):
  return common.convert_images_to_vmdk(files, outpath)
