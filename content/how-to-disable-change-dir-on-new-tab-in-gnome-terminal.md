Title: Как убрать сохранение текущей директории в Gnome Terminal.
Slug: how-to-disable-change-dir-on-new-tab-in-gnome-terminal
Category: Администрирование
Date: 2012-02-11 19:21
Source: False

Иногда приходится работать с Gnome Terminal и меня очень сильно раздражает ситуация, когда в зайдёшь директорию, сделаешь новый таб и внезапно оказываешься в той же директории, в то время как все навыки въевшиеся за всё время требуют в качестве рабочей директории - домик пользователя.

Как обычно такие проблемы решаются патчем меняющем одну строку:

    --- gnome-terminal-2.30.2.orig/src/terminal-screen.c
    +++ gnome-terminal-2.30.2/src/terminal-screen.c
    @@ -1492,7 +1492,7 @@ terminal_screen_launch_child_cb (Termina
       update_records = terminal_profile_get_property_boolean (profile, TERMINAL_PROFILE_UPDATE_RECORDS);
     
       if (priv->initial_working_directory)
    -    working_dir = priv->initial_working_directory;
    +    working_dir = g_get_home_dir ();
       else
         working_dir = g_get_home_dir ();

Я не берусь утверждать, что патч на текущий момент корректно решает проблему, но он это делает.

Собирается всё так:

    apt-get source gnome-terminal
    cd gnome-terminal*
    vim src/terminal-screen.c
    debuild -i -us -uc
    dpkg -i ../gnome-terminal*deb

Можно взять готовый пакет для Debian Squeeze amd64 здесь ([1][1], [2][2]).

[1]: http://i.libc6.org/media/opensource/gnome-terminal_2.30.2-1_amd64.deb
[2]: http://i.libc6.org/media/opensource/gnome-terminal-data_2.30.2-1_all.deb
