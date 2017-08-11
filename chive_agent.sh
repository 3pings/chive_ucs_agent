#! /bin/bash

echo
echo "###############################################"
echo "Thank you for using the CHIVE Demo Application."
echo "This script will install the chive agent aci app"
echo "###############################################"
echo

echo "Press Enter to continue..."
read confirm
echo

echo "Please enter the IP ADDRESS of your APIC : "
read myapic_ip

echo "Please enter the USERNAME for your APIC : "
read myapic_usr

echo "Please enter the PASSWORD of your APIC : "
read -s myapic_pwd

echo
echo "The IP address of your APIC is : ${myapic_ip}"
echo "The USERNAME is                : ${myapic_usr}"
echo
echo "Press Enter to continue..."
read confirm

python ./app/chive_agent_aci.py $myapic_ip,$myapic_usr,$myapic_pwd


