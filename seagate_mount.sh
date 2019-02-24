MOUNT_POINT=/media/Seagate2To/

if [ $# -gt 0 -a "$1" == "-u" ]; then	
	echo umount $MOUNT_POINT
	mountpoint -q $MOUNT_POINT && sudo umount $MOUNT_POINT
	exit
fi

mountpoint -q $MOUNT_POINT || sudo mount -t cifs //192.168.0.1/"Seagate Backup Plus Drive 2To"  $MOUNT_POINT
