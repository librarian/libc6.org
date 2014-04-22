Title: Сборка i386 ядра на amd64 системе.
Slug: compiling-i386-kernel-on-amd64
Category: Администрирование
Date: 2011-10-15 19:24
Source: False

Для сборки i386 ядра на amd64 системе нужно сделать немного симлинков и запустить сборку с определёнными параметрами:


    # ln -s /usr/bin/ar /usr/bin/i386-ar
    # ln -s /usr/bin/gcc /usr/bin/i386-gcc
    # ln -s /usr/bin/ld /usr/bin/i386-ld
    # ln -s /usr/bin/nm /usr/bin/i386-nm
    # ln -s /usr/bin/objcopy /usr/bin/i386-objcopy
    # ln -s /usr/bin/objdump /usr/bin/i386-objdump
    # ln -s /usr/bin/strip /usr/bin/i386-strip    
    # ln -s /usr/bin/objcopy /usr/bin/i386objcopy 
    # ln -s /usr/bin/objdump /usr/bin/i386objdump 
    # ls -l /usr/bin/i386-*


Ядро конфигурируем и собираем командами:


    $ make-kpkg --cross-compile=i386 --arch=i386 --config=menuconfig configure
    $ make-kpkg --cross-compile=i386 --arch=i386 --rootcmd fakeroot  --initrd  kernel_image kernel_headers
