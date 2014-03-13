Title: Редкая проблема с GRUB 0.97 и resize2fs.
Slug: bug-in-grub-legacy
Category: Администрирование
Date: 2011-07-05 19:24
Source: False

При клонировании образа виртуальной машины наткнулся на интересную проблему:

    
    
    # grub --device-map=/boot/grub/device.map 
    grub> root (hd0,0) 
    grub> setup (hd0) 
    Checking if "/boot/grub/stage1" exists... no 
    Checking if "/grub/stage1" exists... 
    Error 15: File not found 
    # grub-install --root-directory=/ /dev/vda 
    The file /boot/grub/stage1 not read correctly 
    

Суть проблемы состоит в том, что в CentOS по умолчанию файловая система должна
использовать размер inode 128 бит, а новые версии e2fsprogs (1.40.5)
используют размер inode 256 бит для улучшения работы ext4 файловой системы.

Из man:

    
    
    -I inode-size 
    Specify the size of each inode in bytes. mke2fs creates 256-byte inodes by default.In kernels after 2.6.10 and some earlier vendor kernels it is possible to utilize inodes larger than 128 bytes to store extended attributes for improved performance. The inode-size value must be a power of 2 larger or equal to 128. The larger the inode-size the more space the inode table will consume, and this reduces the usable space in the filesystem and can also negatively impact performance. Extended attributes stored in large inodes are not visible with older kernels, and such filesystems will not be mountable with 2.4 kernels at all. It is not possible to change this value after the filesystem is created.
    

К слову, то что там написано - не совсем правда, mke2fs считывает информацию
из конфигурационного файла /etc/mke2fs.conf и при определённых условиях может
менять размер inode, для небольших разделов может выставлять размер inode 128
бит.

Из man следует, что размер inode нельзя поменять не пересоздав файловую
систему заново.

Специально для libguestfs был написан [патч][1], который позволяет передавать
mke2fs размер inode:

    
    
    $ guestfish
    ><fs> add-drive test.img 1G #for small images by default used 128 bit
    ><fs> run
    ><fs> part-disk /dev/vda mbr
    ><fs> mkfs ext3 /dev/vda1
    ><fs> tune2fs-l /dev/vda1 | grep "Inode size"
    Inode size: 256
    ><fs> mkfs-opts ext3 /dev/vda1 inode:128
    ><fs> tune2fs-l /dev/vda1 | grep "Inode size"
    Inode size: 128
    

   [1]: http://git.annexia.org/?p=libguestfs.git;a=commit;h=24fb2c1255f751dad98dd1739b3ed3a52ce06f70
