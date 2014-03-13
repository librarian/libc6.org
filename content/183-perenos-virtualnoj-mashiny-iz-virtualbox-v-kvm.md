Title: Перенос виртуальной машины из Virtualbox в KVM
Slug: perenos-virtualnoj-mashiny-iz-virtualbox-v-kvm
Category: Виртуализация
Date: 2013-02-11 14:31
Source: False

В русскоязычном сегменте сети этой информации нет (либо я не нашёл, искал-то я недолго), так что позволю себе адаптировать и расширить эту [англоязычную заметку](http://slashsda.blogspot.ru/2012/03/migrate-from-virtualbox-to-kvm.html) на понятный мне язык.

Итак по пунктам: у нас есть файлик vdi от VirtualBox, нужно запустить виртуальную машину в KVM с virtio драйверами.

1\. Сконвертируем vdi в raw (или qcow2, кому как нравится):

    qemu-img convert windows.vdi windows.img

2\. Скачиваем iso образ с [virtio драйверами](http://alt.fedoraproject.org/pub/alt/virtio-win/latest/images/bin/)

3\. Скачиваем iso образ с [Hiren's boot cd](http://www.hirensbootcd.org/download/)
    
4\. Создадим виртуальную машину с вот такими устройствами (test.img это просто файл, например размера 1Мб):

    <disk type='file' device='disk'>
      <driver name='qemu' type='raw'/>
      <source file='/path-to/windows.img'/>
      <target dev='hda' bus='ide'/>
      <address type='drive' controller='0' bus='0' target='0' unit='0'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='/path-to/some.iso'/>
      <target dev='hdc' bus='ide'/>
      <readonly/>
      <address type='drive' controller='0' bus='0' target='0' unit='1'/>
    </disk>
    <disk type='file' device='disk'>
      <driver name='qemu' type='raw'/>
      <source file='/path-to/test.img'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </disk>

5\. Подключаем вместо some.iso, сначала Hirens boot cd. Это такая маленькая виртуальная машина с XP (я не уверен, что это легально, но уж как есть). Там запускаем HBCD Menu -> Programs -> Registry -> Fix hard disk controller -> T -> C:\Windows -> M. Так мы сбросим, как я понимаю, привязку системы к конкретному типу дисков.

6\. Подключаем iso с virtio драйверами и устанавливаем обнаруженные устройства: сетевую карту и диск (мы специально подключили test.img, чтобы Windows увидела новое устройство).

7\. Выключаем виртуальную машину, удаляем из конфигурационного файла iso и test.img. Приводим конфигурационный файл основного диска к такому виду:

    <disk type='file' device='disk'>
      <driver name='qemu' type='raw'/>
      <source file='/path-to/windows.img'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </disk>

8\. Запускаем виртуальную машину и радуемся возросшей производительности.
