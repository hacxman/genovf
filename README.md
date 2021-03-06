genovf
======

Generates OVF from template, HW profile and set of supplied RAW/VMDK images

HOWTO
=====
1. [Getting OVF](#getting-ovf)
2. [Replacing KS in OZ](#replacing-ks)
3. [Build stop after no disk activity](#build-stop-after-no-disk-activity)

<h2 id="getting-ovf">Getting OVF</h2>

You need to have working Imagefactory and OZ installation.

$ sudo imagefactory base_image template.tdl

or, set pythonpath for Imagefactory or OZ

```bash
$ sudo PYTHONPATH=IMAGAFACTORYPATH:OZPATH python ./imagefactory base_image template.tdl
```

Note the UUID

```bash
$ sudo imagefactory target_image --id UUID vsphere
```

Note the UUID.

The you can abuse this tool. Image is stored in /var/log/imagefactory/storage/TARGET_UUID.body
Make it available somehow, by copying, chmodding, etc...
Resulting image is RAW so we need to convert it. Current version saves converted VMDK image
to current directory.

Example HW profile:
```bash
$ cat vsphere.json
```
```JSON
{
"vmname": "testvm",
"virtualhwfamily": "vmx-04",
"cpucount": 2,
"ramsize": 4096
}
```

Which is almost self describing, maybe except virtualhwfamily, but it should be sufficent to leave it
as is.

```bash
$ ./genovf -c -o output.ovf -p profile.json -i /var/log/imagefactory/storage/TARGET_UUID.body
```

You should obtain output.ovf, MANIFEST.MF and TARGET_UUID.body.vmdk.
(Easiest) way to move it to Windows vSphere machine is to use some python3 magic

Move it to ./tmp and invoke there

```bash
$ python3 -m http.server 8000
```

Now you can rdesktop to vSphere and download vmdk, manifest and ovf
together to new directory. Go to File/Deploy OVF Template and target it on
the OVF file. vSphere treats whole dir as a OVF "package".

Hopefully it will work.

<h2 id="2">Replacing KS</h2>

OZ's KS templates are in oz/oz/auto. I've edited rhel-6-jeos.ks (it depends on your OS of choice).
My adjustments dealt with logvols. It's pretty simple to do it and you might find handy having
some KS from anaconda for example. Rest is the same is in 1).

<h2 id="3">Build stop after no disk activity</h2>
It might happen that you'll get smaller images than you wanted. In that case you
either need to edit TDL and add
```XML
<disk><size>YOURSIZE</size></disk>
```

OR If it won't help you can edit default value for size in generate_diskimage function in
oz/oz/Guest.py.
