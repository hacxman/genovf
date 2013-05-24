<?xml version='1.0' encoding='utf-8'?>
<ovf:Envelope xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/1/"
xmlns:rasd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData"
xmlns:vssd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
ovf:version="3.1.0.0">
  <References>
    $filereferencies
    <Nic ovf:id="bbf8fe7f-983e-4763-b6f5-b3a358eeae55" />
  </References>
  <Section xsi:type="ovf:NetworkSection_Type">
    <Info>List of networks</Info>
    <Network ovf:name="Network 1" />
  </Section>
  <Section xsi:type="ovf:DiskSection_Type">
    <Info>List of Virtual Disks</Info>
    $disksection
    <Disk ovf:diskId="92001497-5161-4233-9e91-0bf07d1d46b5"
    ovf:size="50" ovf:actual_size="1"
    ovf:vm_snapshot_id="00000000-0000-0000-0000-000000000000"
    ovf:parentRef=""
    ovf:fileRef="f8da1407-601a-4751-bd87-ac32e70c7a86/92001497-5161-4233-9e91-0bf07d1d46b5"
    ovf:format="http://www.gnome.org/~markmc/qcow-image-format.html"
    ovf:volume-format="COW" ovf:volume-type="Sparse"
    ovf:disk-interface="VirtIO" ovf:boot="true"
    ovf:disk-alias="b57db30f-070f-4173-bf6a-333ae9a247b0_Disk1"
    ovf:wipe-after-delete="false" />
  </Section>
  <Content ovf:id="out" xsi:type="ovf:VirtualSystem_Type">
    <Name>$vmname</Name>
    <TemplateId>5cd8d241-c38b-4a8d-b06d-bd18fbff333b</TemplateId>
    <Description>$vmname - description</Description>
    <Domain></Domain>
    <CreationDate>2013/05/23 19:30:39</CreationDate>
    <ExportDate>2013/05/23 21:46:36</ExportDate>
    <IsAutoSuspend>false</IsAutoSuspend>
    <TimeZone></TimeZone>
    <Origin>0</Origin>
    <VmType>1</VmType>
    <default_display_type>0</default_display_type>
    <default_boot_sequence>1</default_boot_sequence>
    <Section ovf:id="5cd8d241-c38b-4a8d-b06d-bd18fbff333b"
    ovf:required="false"
    xsi:type="ovf:OperatingSystemSection_Type">
      <Info>Guest Operating System</Info>
      <Description>OtherLinux</Description>
    </Section>
    <Section xsi:type="ovf:VirtualHardwareSection_Type">
      <Info>1 CPU, 512 Memeory</Info>
      <System>
        <vssd:VirtualSystemType>ENGINE
        3.1.0.0</vssd:VirtualSystemType>
      </System>
      <Item>
        <rasd:Caption>$cpucount virtual cpu</rasd:Caption>
        <rasd:Description>Number of virtual CPU</rasd:Description>
        <rasd:InstanceId>1</rasd:InstanceId>
        <rasd:ResourceType>3</rasd:ResourceType>
        <rasd:num_of_sockets>1</rasd:num_of_sockets>
        <rasd:cpu_per_socket>1</rasd:cpu_per_socket>
      </Item>
      <Item>
        <rasd:Caption>$ramsize MB of memory</rasd:Caption>
        <rasd:Description>Memory Size</rasd:Description>
        <rasd:InstanceId>2</rasd:InstanceId>
        <rasd:ResourceType>4</rasd:ResourceType>
        <rasd:AllocationUnits>MegaBytes</rasd:AllocationUnits>
        <rasd:VirtualQuantity>$ramsize</rasd:VirtualQuantity>
      </Item>
      $hwdiskitems
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
      </Item>
      <Item>
        <rasd:Caption>Ethernet adapter on rhevm</rasd:Caption>
        <rasd:InstanceId>
        bbf8fe7f-983e-4763-b6f5-b3a358eeae55</rasd:InstanceId>
        <rasd:ResourceType>10</rasd:ResourceType>
        <rasd:ResourceSubType>3</rasd:ResourceSubType>
        <rasd:Connection>rhevm</rasd:Connection>
        <rasd:Name>eth0</rasd:Name>
        <rasd:speed>1000</rasd:speed>
        <Type>interface</Type>
        <Device>bridge</Device>
        <rasd:Address></rasd:Address>
        <BootOrder>0</BootOrder>
        <IsPlugged>true</IsPlugged>
        <IsReadOnly>false</IsReadOnly>
        <Alias></Alias>
      </Item>
      <Item>
        <rasd:Caption>USB Controller</rasd:Caption>
        <rasd:InstanceId>3</rasd:InstanceId>
        <rasd:ResourceType>23</rasd:ResourceType>
        <rasd:UsbPolicy>DISABLED</rasd:UsbPolicy>
      </Item>
      <Item>
        <rasd:Caption>Graphical Controller</rasd:Caption>
        <rasd:InstanceId>
        684a4364-295a-4b21-936e-e30350dd3cdb</rasd:InstanceId>
        <rasd:ResourceType>20</rasd:ResourceType>
        <rasd:VirtualQuantity>1</rasd:VirtualQuantity>
        <Type>video</Type>
        <Device>cirrus</Device>
        <rasd:Address></rasd:Address>
        <BootOrder>0</BootOrder>
        <IsPlugged>true</IsPlugged>
        <IsReadOnly>false</IsReadOnly>
        <Alias></Alias>
        <SpecParams>
          <vram>65536</vram>
        </SpecParams>
      </Item>
    </Section>
  </Content>
</ovf:Envelope>
