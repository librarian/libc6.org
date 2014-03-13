Title: Рингтоны для Apple iPhone/iPod длительностью более 40 секунд.
Slug: ringtony-dlya-apple-iphoneipod-dlitelnostyu-bolee-40-sekund
Category: Разное
Date: 2010-06-23 19:27
Source: False

Для загрузки полноценных рингтонов (более 40 секунд) нам понадобится программа
iPhone Browser. Перед тем как начать загружать рингтоны, вначале сделаем их.

Для тех кто не знает как, ниже представлено видео. Далее подключаем телефон и
запускаем программу iPhone Browser. Перейдём в директорию "var -mobile-Media-
iTunes_Control-Ringtones", где должны находиться рингтоны. Загружаем их сюда.
После их загрузки нам нужно прописать их в плейлисте рингтонов на телефоне.
Для этого перейдём в папку "var-mobile-Media-iTunes_Control-iTunes". В этой
папке хранится файл Ringtones.plist в котором прописаны все рингтоны.
Содержимое файла лично у меня выглядит так:

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Ringtones</key>
        <dict>
          ....... (тут прописываются рингтоны)
        </dict>
    </dict>
    </plist>

Код для занесения рингтона в плейлист в общем виде выглядит так:

    
    <key>Имя_файла.m4r</key>
    <dict>
        <key>GUID</key><string>Идентификатор</string>
        <key>Name</key><string>Имя рингтона</string>
        <key>Total Time</key><integer>Длительность_рингтона</integer>
    </dict>

**Теперь об этих параметрах.**

  * "Имя_файла.m4r" должно совпадать с именем соответствующего рингтона.
  * Идентификатор состоит из 16 символов латинского алфавита и цифр. Он уникален, т.е. не должен совпадать с идентификаторами других рингтонов. Указывается произвольно.
  * Имя рингтона указываете любое. Имено оно будет отображаться у вас в телефоне.
  * Длительность_рингтона указывается в милисекундах. Но этот параметр ни на что не влияет и не уникален. По сути прописываете любое число, но меньше 39000. Если параметр будет больше 39 секунд, то рингтон не будет отображаться в списке рингтонов на телефоне.

Для примера приведу содержимое своего файла Ringtones.plist, в котором
прописаны 2 рингтона:

    
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Ringtones</key>
        <dict>
            <key>Without you.m4r</key>
            <dict>
                <key>GUID</key><string>F6E2696248042DC4</string>
                <key>Name</key><string>Ocean Drive -- Without you</string>
                <key>Total Time</key><integer>2675</integer>
            </dict>
            <key>New divide.m4r</key>
            <dict>
                <key>GUID</key><string>451B362C65573E43</string>
                <key>Name</key><string>Linkin Park -- New Devide</string>
                <key>Total Time</key><integer>22761</integer>
            </dict>
        </dict>
    </dict>
    </plist>

**Полезные программы:**

  * [iTunes 8][1]   (P.s. iTunes 9 уже не позволяет создавать рингтоны) 
  * [iPhone Browser 1.9.3][2]
  * [Total Commander][3]

Внимание!!! При синхронизации телефона с айтюнсом плейлист рингтонов
стирается. Поэтому после каждой синхронизации придётся постоянно загружать
файл "Ringtones.plist". Пока что эту проблему не решил, но в процессе решения
=).

**Создание рингтонов для iPhone/iPod**
**Загрузка рингтонов на iPhone/iPod длит. >40 секунд**

   [1]: http://appldnld.apple.com.edgesuite.net/content.info.apple.com/iTunes8/061-6166.20090311.znt32/iTunesSetup.exe
   [2]: http://code.google.com/p/iphonebrowser/downloads/list
   [3]: http://wincmd.ru/download.php?id=totalcmd
