import common

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

template_name = 'vsphere.xml.tpl'

def construct_fragments(inputimages):
  refs = construct_refs(reftpl, inputimages)
  disks = construct_disks(disktpl, inputimages)
  hwdisks = construct_hw_disks(diskitemtpl, disks)

  return {'filereferencies': refs,
          'disksection': disks,
          'hwdiskitems': hwdisks}

def construct_manifest(files, outdir):
  common.generate_manifest(files, outdir)

def convert_images(files, outpath):
  return common.convert_images_to_vmdk(files, outpath)
