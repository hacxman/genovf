genovf
======

Generates OVF from template, HW profile and set of supplied RAW/VMDK images

HOWTO
=====
1) Getting OVF
2) Replacing KS in OZ

1) Getting OVF

You need to have working Imagefactory and OZ installation.

$ sudo imagefactory base_image template.tdl

or, set pythonpath for Imagefactory or OZ

$ sudo PYTHONPATH=IMAGAFACTORYPATH:OZPATH python ./imagefactory base_image template.tdl

Note the UUID

$ sudo imagefactory target_image --id UUID vsphere

Note the UUID.

The you can abuse this tool. Image is stored in /var/log/imagefactory/storage/TARGET_UUID.body
Make it available somehow, by copying, chmodding, etc...
Resulting image is RAW so we need to convert it. Current version saves converted VMDK image
to current directory.

Example HW profile:
$ cat vsphere.json
{
"vmname": "testvm",
"virtualhwfamily": "vmx-04",
"cpucount": 2,
"ramsize": 4096
}

Which is almost self describing, maybe except virtualhwfamily, but it should be sufficent to leave it
as is.

$ ./genovf -c -o output.ovf -p profile.json -i /var/log/imagefactory/storage/TARGET_UUID.body

You should obtain output.ovf, MANIFEST.MF and TARGET_UUID.body.vmdk.
(Easiest) way to move it to Windows vSphere machine is to use some python3 magic

Move it to ./tmp and invoke there

$ python3 -m http.server 8000

Now you can rdesktop to vSphere and download vmdk, manifest and ovf
together to new directory. Go to File/Deploy OVF Template and target it on
the OVF file. vSphere treats whole dir as a OVF "package".

Hopefully it will work.

2) Replacing KS

OZ's KS templates are in oz/oz/auto. I've edited rhel-6-jeos.ks (it depends on your OS of choice).
My adjustments dealt with logvols. It's pretty simple to do it and you might find handy having
some KS from anaconda for example. Rest is the same is in 1).
