Title: Баг в libvirt 0.9.11+ на хост системах с процессорами AMD Magny Cours
Slug: bug-v-libvirt-0911-na-host-sistemah-s-processorami-amd-magny-cours
Category: Администрирование
Date: 2012-05-28 14:53
Source: False

Недавно натолкнулся на такой баг: обновил libvirt до 0.9.11 на одной из систем. После этого при перезагрузке виртуальной машины стала появляться такая ошибка:

    $ virsh start guest
    error: Failed to start domain guest
    error: internal error cannot set CPU affinity on process 0: Invalid argument

Виртуальная машина запустилась после того как из конфига была удалено следующее:

    -<vcpu placement='static' cpuset='19'>1</vcpu> 
    +<vcpu>1</vcpu> 

После этого я сделал:


    $ virsh vcpupin guest
    VCPU: CPU Affinity
    ----------------------------------
       0: 0-11
    
    $ virsh vcpuinfo guest
    VCPU:           0
    CPU:            N/A
    State:          N/A
    CPU time        N/A
    CPU Affinity:   yyyyyyyyyyyy

То есть libvirt видит только половину ядер. После небольшого исследования был найдет виновник: макрос VIR_NODEINFO_MAXCPUS(nodeinfo). Он возвращал всего 12 ядер, вместо 24.

А вот виновником этого уже является файл src/nodeinfo.c, а именно строки:

        /* Parse core */
        core = parse_core(cpu);
        if (!CPU_ISSET(core, &core_mask)) {
            CPU_SET(core, &core_mask);
            nodeinfo->cores++;
        }

        /* Parse socket */
        sock = parse_socket(cpu);
        if (!CPU_ISSET(sock, &socket_mask)) {
            CPU_SET(sock, &socket_mask);
            nodeinfo->sockets++;
        }

Судя по всему разработчики libvirt не учли на тот момент, что есть особенные процессоры AMD (Opteron например), у которых в одном корпусе может быть два процессора.

Баг исправляет коммит [nodeinfo: Get the correct CPU number on AMD Magny Cours platform](http://libvirt.org/git/?p=libvirt.git;a=patch;h=10d9038b744a69c8d4bd29c2e8c012a097481586). Хотя он выглядит больше как некий хак.

Ждём 0.9.13, где этот патч будет в комплекте, а пока можно наложить ручками.

Я у себя вернулся обратно на 0.9.8, однако есть досадный баг, что после обновления виртуальные машины, которые были  запущены (или перезагружены) - обнаруживаются libvirt как выключенные. Выполнение virsh qemu-attach не приводит к желаемому результату.
