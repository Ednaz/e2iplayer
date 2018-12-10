#!/bin/sh
cp $1/iptvupdate/custom/xxx.sh $2/iptvupdate/custom/xxx.sh
status=$?
if [ $status -ne 0 ]; then
	echo "Неустранимая ошибка. Файл $0 не может быть скопирован, ошибка[$status]."
	exit 1
fi
cp $1/hosts/hostXXX.py $2/hosts/
cp $1/icons/logos/XXXlogo.png $2/icons/logos/
cp $1/icons/PlayerSelector/XXX*.png $2/icons/PlayerSelector/ 
status=$?
if [ $status -ne 0 ]; then
	echo "Внимание. Мы не смогли скопировать XXX, ошибка[$status]."
else
	echo "Копирование XXX OK"
fi
if [ -x /usr/bin/fullwget ] ; then
	/usr/bin/fullwget --no-check-certificate https://gitlab.com/iptv-host-xxx/iptv-host-xxx/repository/master/archive.tar.gz -q -O /tmp/iptv-host-xxx.tar.gz
	if [ -s /tmp/iptv-host-xxx.tar.gz ] ; then
		tar -xzf /tmp/iptv-host-xxx.tar.gz -C /tmp 
		cp -r -f /tmp/iptv-host-xxx-master*/IPTVPlayer/icons/PlayerSelector/* $2/icons/PlayerSelector/
		cp -r -f /tmp/iptv-host-xxx-master*/IPTVPlayer/icons/logos/* $2/icons/logos/
		cp -r -f /tmp/iptv-host-xxx-master*/IPTVPlayer/iptvupdate/custom/* $2/iptvupdate/custom/
		cp -r -f /tmp/iptv-host-xxx-master*/IPTVPlayer/hosts/* $2/hosts/
		rm -r -f /tmp/iptv-host-xxx*
		if [ -e $2/icons/PlayerSelector/XXX100 ] ; then
			mv $2/icons/PlayerSelector/XXX100 $2/icons/PlayerSelector/XXX100.png
			mv $2/icons/PlayerSelector/XXX120 $2/icons/PlayerSelector/XXX120.png
			mv $2/icons/PlayerSelector/XXX135 $2/icons/PlayerSelector/XXX135.png
			echo "Переименование файла png OK"
		fi
		echo "Загрузка XXX tar.gz OK"
	else
		echo "Внимание, загрузка XXX tar.gz не удалась"
	fi
fi
echo "Выполнение $0 окончено успешно."
exit 0
