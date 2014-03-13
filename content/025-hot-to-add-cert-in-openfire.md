Title: Как добавить сертификат в Openfire.
Slug: hot-to-add-cert-in-openfire
Category: Администрирование
Date: 2011-12-09 19:22
Source: False

Я либо что-то не вкурил, но стандартный keytool категорически отказывался нормально импортировать сертификаты.

Итак, представляю проверенный, извращенский способ:

1\. Нужно сконвертировать SSL cертификат в DER формат:



    openssl pkcs8 -topk8 -nocrypt -in cert.key -inform PEM -out cert-key.der -outform DER
    openssl x509 -in cert.crt -inform PEM -out cert-crt.der -outform DER



2\. Скачать сорцы класса Java, заменить в них строку аутентификации хранилища (по дефолту в openfire это *changeit*) и скомпилировать в класс:



    wget http://www.agentbob.info/agentbob/80/version/default/part/AttachmentData/data/ImportKey.java

    // change this if you want another password by default
    String keypass = "changeit";
    // change this if you want another alias by default
    String defaultalias = "changeit";

    javac ImportKey.java



3\. Создаём хранилище для сертификатов:



    java ImportKey cert-key.der cert-crt.der



4\. Делаем бэкапы текущего хранилища:


    
    cp /etc/openfire/security/keystore /etc/openfire/security/keystore.bkp
    cp /etc/openfire/security/truststore /etc/openfire/security/truststore.bkp



5\. Копируем полученный файл вместо текущего хранилища и перезапускаем openfire


    
    cp keystore.ImportKey /etc/openfire/security/keystore
    invoke-rc.d openfire restart
    


На этом всё.
