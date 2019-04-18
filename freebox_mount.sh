MOUNT_POINT=/media/freebox/

if [ $# -gt 0 -a "$1" == "-u" ]; then	
	echo umount $MOUNT_POINT
	mountpoint -q $MOUNT_POINT && sudo umount $MOUNT_POINT
	exit
fi

mountpoint -q $MOUNT_POINT || sudo mount -t cifs -o guest,vers=1.0 //192.168.0.1/"Disque dur"  $MOUNT_POINT
