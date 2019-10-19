#!/usr/bin/env python

# Xibalba - VPN monitor tool and Internet Kill Switch
# Written by eif0.
# Licenced under GPLv3
# Report Xibalba bugs to eif0@hush.com


# Deps: 
#   - zenity
#   - python-geoip
#   - wget
#   - man
#   - less
#   - iptables
#   - iptables-restore
#   - iptables-save
#   - git



try:
    import sys

except:
    print("\n\nExecution error:\n\n  >> No python module named 'sys', please install it before running Xibalba.\n\n")
    quit()
    
if sys.version_info >= (3, 0):
    print("\n\nYou're running python3\n\nWe don't have a python3 port yet. Please run Xibalba with python2\n\n")
    sys.exit(2)

else:

    class color:
       PURPLE = '\033[95m'
       CYAN = '\033[96m'
       DARKCYAN = '\033[36m'
       BLUE = '\033[94m'
       GREEN = '\033[92m'
       YELLOW = '\033[93m'
       RED = '\033[91m'
       BOLD = '\033[1m'
       UNDERLINE = '\033[4m'
       END = '\033[0m'

    try:
        from collections import Counter
        from subprocess import Popen, PIPE
        import os
        import sys
        import re
        import getopt
        import datetime
        import threading
        import subprocess
        import time
        import pygtk
        import gtk
        import gobject
        import getpass
        import os.path
        import urllib
        import GeoIP

    except:
        e = sys.exc_info()[1]
        print("\n\nPython execution error: "+color.BOLD+str(e)+color.END+", please install it before running Xibalba.")
        print("\n\nPlease check Xibalba's python modules deps and install the one missing in your system:\n\n  - subprocess\n  - os\n  - sys\n  - re\n  - getopt\n  - datetime\n  - threading\n  - subprocess\n  - time\n  - pygtk\n  - gtk\n  - gobject\n  - getpass\n  - os.path\n  - urllib\n  - geoip\n\n")
        sys.exit(2)

    def which(program):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None

    if (getpass.getuser() != "root"):
        alldeps = ["wget", "zenity", "python2", "man", "less", "git"]
    else:
        alldeps = ["wget", "zenity", "python2", "man", "less", "git", "iptables", "iptables-save", "iptables-restore"]
        
    for dep in alldeps:
        if (which(dep) == None):
            print("\n\nWARNING: Xibalba needs '"+color.BOLD+dep+color.END+"' to be installed in your system.\n\nPlease install '"+color.BOLD+dep+color.END+"' and try to run Xibalba again.\n\n")
            sys.exit(2)

    gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)



    try:
        pygtk.require('2.0')
    except:
        print("\n\nIt looks like you don't have gtk2 installed.\n\nWe don't have gtk3 support yet.\n\nPlease install gtk2 libs before running Xibalba again.\n\n")
        sys.exit(2)

    gtk.gdk.threads_init()

    global logpath
    global connectionname
    global uuid
    global cycle
    global parcialtime
    global surfshark
    global killswitch
    global restoremode
    global wasconnected
    global reconnections
    global ip
    global country
    global version
    global oldrelease
    global latest
    global checkcount
    global connectedonstartup
    global surfshark_connected

    oldrelease = False

    version = "0.5.4"

    surfshark = False
    surfshark_connected = False
    connectedonstartup = False
    logpath = "/tmp/xibalba.log"
    connectionname = ""
    word = ""
    uuid = ""
    cycle = 30
    parcialtime = 0
    killswitch = False
    wasconnected = False
    restoremode = False
    reconnections = 0
    country = ""
    ip = "NO AVAILABLE"
    latest = "0.0"
    checkcount = 0


    def looper():
        global uuid
        global parcialtime
        global killswitch
        global wasconnected
        global reconnections
        global ip
        global country
        global version
        global oldrelease
        global latest
        global checkcount
        global connectedonstartup
        global surfshark_connected

        print("\nStarting Xibalba...\n")


        logcommand = "touch "+logpath
        os.system(logcommand)

        try:
            latest = urllib.urlopen('https://raw.githubusercontent.com/eif0/xibalba/master/VERSION').read().split()[0]
        except:
            latest = "0.0"
        
        if (latest > version):
            oldrelease = True
            updateinfo = "zenity --warning --text='There is an update available!\n\nPlease go to UPDATES option in the menu.'"
            os.system(updateinfo)
        elif (latest < version):
            updateinfo = "zenity --warning --text='There is an update available!\n\nPlease go to UPDATES option in the menu.'"
            os.system(updateinfo)



        if (latest > version):
            oldrelease = True


        if (surfshark == True):
            grepcommand = "surfshark-vpn status"



        else:
            namecounter = sum(1 for w in connectionname.lower().split())

            grepcommand = "nmcli con show --active | grep \""+connectionname+"\""

            time.sleep(3)
            app.update_icon()


            p = Popen(grepcommand, shell=True, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            word = ""

            if ((namecounter > 1) and (out != "")): 
                try:
                    for i in range(namecounter):
                        word = word+out.split()[i]
                        if i < namecounter-1:
                            word = word+" "
                except:
                    print("\n"+color.BOLD+"ERROR: "+color.END+"It looks like you wrote bad your connection name/label. Please check your ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] parameter\n\n\n"+color.BOLD+color.UNDERLINE+"REMINDER:\n\n"+color.END+" - If the connection name/label has more than one word, you should put it between double quotation marks (\" \")\n - This param is case sensitive!\n\n")
                    if (killswitch):
                        print(color.BOLD+"HINT:"+color.END+"\n\n - To protect you from leaks, the Internet Kill Switch only works when you "+color.UNDERLINE+"run Xibalba while connected to the VPN"+color.END+"\n\n")
                    gtk.main_quit()
            elif (out != ""):
                try:
                    word = out.split()[0]
                except:
                    print("\n"+color.BOLD+"ERROR: "+color.END+"It looks like you wrote bad your connection name/label. Please check your ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] parameter\n\n\n"+color.BOLD+color.UNDERLINE+"REMINDER:\n\n"+color.END+" - If the connection name/label has more than one word, you should put it between double quotation marks (\" \")\n - This param is case sensitive!\n\n")
                    gtk.main_quit()
                    sys.exit(2)
            elif (uuid != ""): # If 'out' is empty and 'uuid' not -> the VPN should try to connect at startup
                if (killswitch):
                    print(color.BOLD+"HINT:"+color.END+"\n\n - To protect you from leaks, the Internet Kill Switch only works when you "+color.UNDERLINE+"run Xibalba while connected to the VPN"+color.END+"\n\n")
                    gtk.main_quit()
                upcommand = "nmcli con up uuid "+uuid+" > /dev/null"
                logmsg = "WARNING: VPN disconnected, trying to connect at startup...\n\n"
                reconnections = reconnections + 1
                app.update_icon("disconnected")
                app.icon.set_tooltip("WARNING: VPN disconnected, trying to connect...")
                logfile = open(logpath, "a")
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d	%H:%M:%S")
                logfile.write(timestamp+"\n")
                logfile.write(logmsg)
                logfile.close()
                
                time.sleep(1)
                os.system(upcommand)
                time.sleep(2)            
                switchmsg = "zenity --warning --text='Your VPN is disconnected!\n\nTrying to connect at Xibalba startup...\n\n'"
                os.system(switchmsg)

                grepcommand = "nmcli con show --active | grep \""+connectionname+"\""
                p = Popen(grepcommand, shell=True, stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                if (out == ""):
                    print("\n\n"+color.BOLD+color.UNDERLINE+"ERROR:"+color.END+" Failed to connect to your VPN!\n\n"+color.BOLD+color.UNDERLINE+"HINT:"+color.END+" Are you sure your ["+color.BOLD+"-c"+color.END+", "+color.BOLD+"--connection"+color.END+"] and ["+color.BOLD+"-u"+color.END+", "+color.BOLD+"--uuid"+color.END+"] params are OK?\n\n\n"+color.BOLD+color.UNDERLINE+"REMINDER:\n\n"+color.END+" - If the connection name/label has more than one word, you should put it between double quotation marks (\" \")\n - This param is case sensitive!\n\n")
                    switchmsg = "zenity --warning --text='Failed to connect to your VPN!\n\nAre you sure your [-c, --connection] and [-u, --uuid] params are OK?\n\n'"
                    os.system(switchmsg)
                    gtk.main_quit()
                    sys.exit(2)                    
                else:
                    connectedonstartup = True
                    namecounter = sum(1 for w in connectionname.lower().split())
                    if (namecounter > 1):
                        try:
                            for i in range(namecounter):
                                word = word+out.split()[i]
                                if i < namecounter-1:
                                    word = word+" "
                        except:
                            print("\n"+color.BOLD+"ERROR: "+color.END+"It looks like you wrote bad your connection name/label. Please check your ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] parameter\n\n\n"+color.BOLD+color.UNDERLINE+"REMINDER:\n\n"+color.END+" - If the connection name/label has more than one word, you should put it between double quotation marks (\" \")\n - This param is case sensitive!\n\n")
                            gtk.main_quit()   
                            sys.exit(2)             
                            
                    else:
                        try:
                            word = out.split()[0]
                        except:
                            print("\n"+color.BOLD+"ERROR: "+color.END+"It looks like you wrote bad your connection name/label. Please check your ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] parameter\n\n\n"+color.BOLD+color.UNDERLINE+"REMINDER:\n\n"+color.END+" - If the connection name/label has more than one word, you should put it between double quotation marks (\" \")\n - This param is case sensitive!\n\n")
                            gtk.main_quit()
                            sys.exit(2)
                            
            else: 

                print("-----------------------------------------------------------------\n")
                print("--   "+color.BOLD+color.UNDERLINE+"EXECUTION FAILED WHILE IDENTIFYING YOUR VPN INFORMATION"+color.END+"   --\n")
                print("-----------------------------------------------------------------\n\n")
                print(color.BOLD+"NEED SOME HELP ?"+color.END+"\n")
                print(" - If you are running this script while your VPN "+color.BOLD+color.UNDERLINE+"is active"+color.END+" and connected: You should use only ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] parameter (["+color.BOLD+"-u"+color.END+', '+color.BOLD+"--uuid"+color.END+"] is also welcome, but not mandatory)\n")
                print(" - If you are running this script while your VPN "+color.BOLD+color.UNDERLINE+"is not active"+color.END+": You should use ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] and ["+color.BOLD+"-u"+color.END+', '+color.BOLD+"--uuid"+color.END+"] parameters (both are mandatory)\n\n")
                print(color.BOLD+color.UNDERLINE+"REMINDER:\n\n"+color.END+" - If the connection name/label has more than one word, you should put it between double quotation marks (\" \")\n - ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] param is case sensitive!\n\n")
                print("\n\n         >> For full documentation and help, use ["+color.BOLD+"-h"+color.END+', '+color.BOLD+"--help"+color.END+"] parameter <<\n\n")

                gtk.main_quit()
                sys.exit(2)

        while True:
            p = Popen(grepcommand, shell=True, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()

            checkcount = checkcount+1


            if (surfshark):
                if ("Connected to Surfshark VPN" in out):
                    surfshark_connected = True
                    connectionname = "Surfshark"
                    word = ""
                else:
                    surfshark_connected = False
                    connectionname = "Surfshark"
                    word = ""


     
            try:
                ip = urllib.urlopen('http://myexternalip.com/raw').read().split()[0]
            except:
                ip = "NO AVAILABLE"
                country = ""

            if (ip != "NO AVAILABLE"):
                try:
                    country = " ["+gi.country_code_by_addr(ip)+"]"
                except:
                    country = " [N/A] "

            if (surfshark == True and surfshark_connected == False):



                logmsg = "WARNING: Surfshark VPN is disconnected.\n\n"
                app.update_icon("disconnected")
                app.icon.set_tooltip("WARNING: VPN disconnected.\nIP: "+ip+country)
                logfile = open(logpath, "a")
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d	%H:%M:%S")
                logfile.write(timestamp+"\n")
                logfile.write(logmsg)
                logfile.close()
                morezinfo = ""

                disconnectionzmsg = "zenity --warning --text='WARNING: Your VPN is DOWN!'"
                os.system(disconnectionzmsg)


            else:
                if ((out == "") and (uuid == "")) or (connectionname == ""):

                    if (killswitch):
                        print("\n"+color.BOLD+"ERROR:"+color.END+" You're not connected to a VPN\n\n\n"+color.BOLD+"HINT:"+color.END+"\n\n  - To protect you from leaks, the Internet Kill Switch only works when you run Xibalba while connected to the VPN\n  - If you're already connected to the VPN, please check if you wrote it's name/label right in the ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] parameter\n")
                        print("\n"+color.BOLD+color.UNDERLINE+"REMINDER:\n\n"+color.END+" - If the connection name/label has more than one word, you should put it between double quotation marks (\" \")\n - ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] param is case sensitive!\n\n")
                        gtk.main_quit()
                        sys.exit(2)


                    print("-----------------------------------------------------------------\n")
                    print("--   "+color.BOLD+color.UNDERLINE+"EXECUTION FAILED WHILE IDENTIFYING YOUR VPN INFORMATION"+color.END+"   --\n")
                    print("-----------------------------------------------------------------\n\n")
                    print(color.BOLD+"NEED SOME HELP ?"+color.END+"\n")
                    print(" - If you are running this script while your VPN "+color.BOLD+color.UNDERLINE+"is active"+color.END+" and connected: You should use only ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] parameter (["+color.BOLD+"-u"+color.END+', '+color.BOLD+"--uuid"+color.END+"] is also welcome, but not mandatory)\n")
                    print(" - If you are running this script while your VPN "+color.BOLD+color.UNDERLINE+"is not active"+color.END+": You should use ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] and ["+color.BOLD+"-u"+color.END+', '+color.BOLD+"--uuid"+color.END+"] parameters (both are mandatory)\n\n")
                    print(color.BOLD+color.UNDERLINE+"REMINDER:\n\n"+color.END+" - If the connection name/label has more than one word, you should put it between double quotation marks (\" \")\n - ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] param is case sensitive!\n\n")
                    print("\n\n         >> For full documentation and help, use ["+color.BOLD+"-h"+color.END+', '+color.BOLD+"--help"+color.END+"] parameter <<\n\n")
                    gtk.main_quit()
                    sys.exit(2)
                elif (out == "") and (connectionname == "") and (uuid == ""):
                    print("It looks like you wrote bad your connection name/label ("+color.BOLD+"-c"+color.END+" param)\n\n")
                    gtk.main_quit()
                elif (out != ""):
                    if (surfshark == False):
                        uuid = out.split()[namecounter]

                if (surfshark == False):
                    upcommand = "nmcli con up uuid "+uuid+" > /dev/null"
                else:
                    upcommand = "echo"
	            

            if surfshark:
                if (connectionname in out) and ("Connected to Surfshark VPN" in out):
                    surfshark_connected = True
                    word = ""

            if (((connectionname in out) and (out != "") and (surfshark_connected == False)) or (surfshark_connected == True)):
                if (((connectionname == word) and (len(uuid)==36)) or surfshark_connected):

                    logmsg = "VPN already connected! :)\n\n"
                    app.update_icon("connected")
                    app.icon.set_tooltip("VPN OK!\nIP: "+ip+country)
                    logfile = open(logpath, "a")
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d	%H:%M:%S")
                    logfile.write(timestamp+"\n")
                    logfile.write(logmsg)
                    logfile.close()
                    wasconnected = True
                elif ((word == "") and (connectedonstartup == False) and surfshark == False):
                    print("\n"+color.BOLD+"ERROR: "+color.END+"It looks like you wrote bad your connection name/label. Please check your ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] parameter\n\n\n"+color.BOLD+color.UNDERLINE+"REMINDER:\n\n"+color.END+" - If the connection name/label has more than one word, you should put it between double quotation marks (\" \")\n - This param is case sensitive!\n\n")
                    gtk.main_quit()
                elif (connectedonstartup):
                    print ("TESTING")
                    
                
            else:
                if (killswitch):
                    if (wasconnected):
                        print("Internet Kill Switch ACTIVATED!\nShutting Down all network traffic...\n")
                        print("In order to browse the internet again after this switch gets activated, you have to run Xibalba with ["+color.BOLD+"-r"+color.END+', '+color.BOLD+"--restorenetwork"+color.END+"] flag\n\n")

                        os.system("iptables-save > /tmp/user-iptables")
                        os.system("iptables -F")
                        os.system("iptables -P INPUT DROP")
                        os.system("iptables -P OUTPUT DROP")
                        os.system("iptables -P FORWARD DROP")

                        time.sleep(1)
                        logmsg = "WARNING: Internet Kill Switch ACTIVATED!. Shutting Down all network traffic...\n\n"
                        logfile = open(logpath, "a")
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d      %H:%M:%S")
                        logfile.write(timestamp+"\n")
                        logfile.write(logmsg)
                        logfile.close()
                        switchmsg = "zenity --warning --text='Internet Kill Switch ACTIVATED!.\n\nNow you are secure.\n\nXibalba stopped all your network traffic.\n\nNumber of successful checks before activation: "+str(checkcount-1)+"'"
                        os.system(switchmsg)
                    else:
                        print("\n"+color.BOLD+"ERROR:"+color.END+" You're not connected to a VPN\n\n\n"+color.BOLD+"HINT:"+color.END+"\n\n - To protect you from leaks, the Internet Kill Switch only works when you "+color.UNDERLINE+"run Xibalba while connected to the VPN"+color.END+"\n\n\n"+color.BOLD+color.UNDERLINE+"REMINDER:"+color.END+"\n\n - If you're already connected to the VPN, please check if you wrote it's name/label right in the ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] parameter\n - If the connection name/label has more than one word, you should put it between double quotation marks (\" \")\n - ["+color.BOLD+"-c"+color.END+', '+color.BOLD+"--connection"+color.END+"] param is case sensitive!\n\n")

                    gtk.main_quit()
                    sys.exit(2)

                logmsg = "WARNING: VPN disconnected, trying to reconnect...\n\n"
                reconnections = reconnections + 1
                app.update_icon("disconnected")
                app.icon.set_tooltip("WARNING: VPN disconnected, trying to reconnect...\nIP: "+ip+country)
                logfile = open(logpath, "a")
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d	%H:%M:%S")
                logfile.write(timestamp+"\n")
                logfile.write(logmsg)
                logfile.close()
            
                time.sleep(1)
                os.system(upcommand)
                time.sleep(2)
                if (wasconnected):
                    morezinfo = "\n\nReconnection number: #"+str(reconnections)+"  \n\n"
                else:
                    morezinfo = ""

                disconnectionzmsg = "zenity --warning --text='WARNING: Your VPN is DOWN!\n\nXibalba is trying to reconnect... "+morezinfo+"'"
                os.system(disconnectionzmsg)


            for parcialtime in range(int(cycle)):
                try:
                    time.sleep(1)
                except:
                    gtk.main_quit()
                    sys.exit(2)



    class TrayIcon(object):

        UNKNOWN, DISCONNECTED, CONNECTED = range(3)
        icon_filename = {
            UNKNOWN: 'images/unknown.png',
            DISCONNECTED: 'images/disconnected.png',
            CONNECTED: 'images/connected.png',
        }


        def __init__(self):

            ### This is an alternate way to create icons (without using an own icon, using one of the default system icons instead)
            ### Actually the icon is created inside "update_icon()" function.
            
            #self.icon = gtk.StatusIcon()
            #self.icon.set_from_stock(gtk.STOCK_ABOUT)         
            
            self.location = os.path.dirname(os.path.realpath(__file__))
            self.state = self.UNKNOWN
            self.update_icon()
            self.icon.connect('activate', self.on_left_click)
            self.icon.connect('popup-menu', self.on_right_click)
            self.icon.set_tooltip("Gathering information...")
            self.icon.set_visible(True)

        @property
        def unknown(self):
            return self.state == self.UNKNOWN
        @property
        def connected(self):
            return self.state == self.CONNECTED
        @property
        def disconnected(self):
            return self.state == self.DISCONNECTED

        def on_right_click(self, icon, event_button, event_time):
            self.make_menu(event_button, event_time)

        def on_left_click(self, event):
            timeleft = int(cycle)-(parcialtime+1)
            if (app.state == 0):
                laststatus = "Gathering Information..."
            elif (app.state == 1):
                laststatus = "VPN Disconnected, trying to reconnect..."
            else:
                laststatus = "VPN OK!"

            if (killswitch == False):
                moreinfo = "\n\nReconnections so far: "+str(reconnections)
            else:
                moreinfo = ""

            
            self.message(connectionname+"\n\nLast Status: "+laststatus+" ["+str(parcialtime+1)+" seconds ago]\n\nLast IP: "+ip+country+"\n\nNumber of Status Checks: "+str(checkcount)+moreinfo+"\n\nNext Check: "+str(timeleft)+" seconds left") 


        def message(self, data=None):
            msg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, data)
            ### To give some format to the gtk windows (bold in this case)
            #msg.set_markup("<b>%s</b>" % data)
            #msg.format_secondary_markup(data)
            msg.run()
            msg.destroy()

        
        def check_updates(self, widget, data=None):
            #self.message(data)
            if (version != latest):
                msg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, data)
            else:
                msg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, data)
            response = msg.run()

            if str(response) == "-8":   ### '-8' is the value of the "YES" button in the dialog

                print("\n\nXibalba is being updated...\n\n")
                pathname = os.path.dirname(sys.argv[0])
                os.system("git --git-dir="+os.path.abspath(pathname)+"/.git --work-tree="+os.path.abspath(pathname)+" checkout HEAD^ -q -f")
                os.system("git --git-dir="+os.path.abspath(pathname)+"/.git --work-tree="+os.path.abspath(pathname)+" pull origin master -q")

                ###ALTERNATE WAY OF REVERTING CHANGES (replace of 'git checkout HEAD')
                #os.system("git --git-dir="+os.path.abspath(pathname)+"/.git --work-tree="+os.path.abspath(pathname)+" reset --hard -q")

                print("\n\nTHE UPDATE PROCESS WAS SUCCESSFUL!\n\nNew version: "+color.BOLD+latest+color.END+"\n\nXibalba is stopping...\n\nPlease run Xibalba again to start the new version installed.\n\n\n")

                #updatemsg = "THE UPDATE PROCESS WAS SUCCESSFUL!\n\nNew version installed: "+latest+"\n\n\nXibalba will close...\n\nPlease run Xibalba again to start the new version installed.\n\n\n\nHINT: We also downloaded a bundle for you!\n      You can find the (.zip) file in:   /tmp/xibalba-latest.zip\n\n"
                updatemsg = "THE UPDATE PROCESS WAS SUCCESSFUL!\n\nNew version installed: "+latest+"\n\n"
                self.message(updatemsg)
                msg.destroy()

                updatemsg = "\nDo you want to download also a bundle with the sources?\n"   ##   You can find the (.zip) file in:   /tmp/xibalba-latest.zip\n\n"
                bundlemsg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO, updatemsg)
                downloadresponse = bundlemsg.run()
                
                if str(downloadresponse) == "-8":   ### '-8' is the value of the "YES" button in the dialog
                    if (os.path.isfile("/tmp/xibalba-latest.zip")):
                        os.system("rm -f /tmp/xibalba-latest.zip")
                    os.system("wget -r -q https://github.com/eif0/xibalba/archive/master.zip -O /tmp/xibalba-latest.zip")
                    os.system("chmod 777 /tmp/xibalba-latest.zip")
                    self.message("\nDOWNLOAD SUCCESSFUL!\n\nYou can find the (.zip) bundle file in:   /tmp/xibalba-latest.zip\n\n")
                bundlemsg.destroy()
                self.message("\nXibalba will close...\n\nRun Xibalba again to start "+latest+" version\n\n")
                gtk.main_quit()
                sys.exit(2)    

            msg.destroy()
            


        def show_monit_info_dialog(self, widget, data=None):
            self.message(data)

        def close_app(self, widget):
            gtk.main_quit()


        def show_about_dialog(self, widget):
            about_dialog = gtk.AboutDialog()
            about_dialog.set_destroy_with_parent (True)
            about_dialog.set_icon_name ("Xibalba")
            about_dialog.set_name('Xibalba')
            about_dialog.set_version(version)
            about_dialog.set_copyright("GPLv3 - 2015 | @eif0")
            about_dialog.set_comments(("VPN monitor tool and Internet Kill Switch"))
            about_dialog.set_authors(['eif0 <eif0@hush.com>'])
            about_dialog.run()
            about_dialog.destroy()





        def make_menu(self, event_button, event_time):
            menu = gtk.Menu()



            #add monit info item
            monitinfo = gtk.MenuItem("VPN Info")
            monitinfo.show()
            menu.append(monitinfo)
            if (killswitch):
                killstatus = "ON"
            else:
                killstatus = "OFF"
            
            if (surfshark):
                connectionname = "Surfshark"
                word = ""
                uuid = "N/A"            	

            monitinfo.connect("activate", self.show_monit_info_dialog, "MONITORING STATUS:\n\nVPN Name: "+connectionname+"\nVPN uuid: "+uuid+"\n\nCheck Cycle: "+str(int(cycle))+" seconds\n\nInternet Kill Switch: "+killstatus+"\n\nLog File: "+logpath)

            # show about dialog
            about = gtk.MenuItem("About")                       # Label
            about.show()                                        # Make it Visible
            menu.append(about)                                  # Add to menu
            about.connect('activate', self.show_about_dialog)   # Action on click


            # add check for updates dialog
            updates = gtk.MenuItem("Updates")
            updates.show()
            menu.append(updates)
            if (oldrelease):
                updates.connect('activate', self.check_updates, 'You are running:  Xibalba '+version+'\nThe last stable version is '+latest+'\n\n\nYou can manually download the latest stable version from:\n\n    https://github.com/eif0/xibalba\n\n\n\n Do you want to auto-update your running version now?')
            elif (version == latest):
                updates.connect('activate', self.check_updates, 'You are running:  Xibalba '+version+'\n\nYour version is up to date :)')
            else:
                updates.connect('activate', self.check_updates, 'THERE IS SOMETHING WEIRD GOING ON HERE!\n\nYou are running:  Xibalba '+version+'\nThe last stable version is '+latest+'\n\n\n> > You have an issue with your Xibalba version < <\n\n\nYou can manually download the latest stable version from:\n\n    https://github.com/eif0/xibalba\n\n\n\n Do you want to auto-update your running version now?')

            # add quit item
            quit = gtk.MenuItem("Quit")
            quit.show()
            menu.append(quit)
            quit.connect('activate', self.close_app)





            # make the icon menu/popup run when clicked
            menu.popup(None, None, gtk.status_icon_position_menu, event_button, event_time, self.icon)



           

        def update_icon(self, status="unknown",addr="0.0.0.0"):
            
            if status == "unknown":
                self.state = self.UNKNOWN
            elif status == "connected":
                self.state = self.CONNECTED
            else:
                self.state = self.DISCONNECTED
                
            #gobject.timeout_add(30000, self.update_icon)
            
            fn = self.icon_filename[self.state]         
            path = os.path.join(self.location, fn)
            assert os.path.exists(path), 'File not found: %s' % path
            if hasattr(self, 'icon'):
                self.icon.set_from_file(path)
            else:
                self.icon = gtk.status_icon_new_from_file(path)



        def main(self):
            ### All PyGTK applications must have a gtk.main(). Control ends here and waits for an event to occur (like a key press or mouse event).
            #gobject.timeout_add(30000, self.update_icon)
            gtk.main()




    if __name__ == "__main__":

        try:    
            opts, extra = getopt.getopt(sys.argv[1:], 't:l:c:u:hkrLVs', ['timeloop=','logfile=','connection=','uuid=','help','killswitch','restorenetwork','license','changelog','surfshark'])    
            if (extra != []):
                print("\n\nIt looks like you have added some non-valid params...\n\n")
                print("REMINDER ABOUT ["+color.BOLD+"-c "+color.END+', '+color.BOLD+"--connection"+color.END+"] PARAM:\n\n - If the connection name/label has more than one word, you should put it between double quotation marks (\" \")\n - This param is case sensitive!\n\n")
                sys.exit(2)
        except:
            err = sys.exc_info()[1]
            print("\nWARNING: "+color.BOLD+color.UNDERLINE+str(err)+color.END)
            print("\nFor full documentation and help, use ["+color.BOLD+"-h"+color.END+', '+color.BOLD+"--help"+color.END+"] parameter\n\n")
            sys.exit(2)
        
        


        
        for code,param in opts:
            if code in ["-h","--help"]:
                pathname = os.path.dirname(sys.argv[0])
                os.system("man "+os.path.abspath(pathname)+"/MANPAGE")
                sys.exit(2)
            else:

                if code in ["-V","--changelog"]:
                    pathname = os.path.dirname(sys.argv[0])
                    os.system("less "+os.path.abspath(pathname)+"/CHANGELOG")
                    sys.exit(2)
                if code in ["-L","--license"]:
                    pathname = os.path.dirname(sys.argv[0])
                    os.system("less "+os.path.abspath(pathname)+"/LICENSE")
                    sys.exit(2)
                if code in ["-l","--logfile"]:
                    logpath = param
                if code in ["-c","--connection"]:
                    connectionname = param
                if code in ["-u","--uuid"]:
                    uuid = param
                if code in ["-t","--timeloop"]:
                    cycle = float(param)
                if code in ["-s","--surfshark"]:
                	surfshark = True
                if code in ["-k","--killswitch"]:
                    killswitch = True
                    if ((os.path.isfile("/tmp/user-iptables")) and (getpass.getuser() == "root")):
                        print("\n\nIt looks like the Internet Kill Switch was activated recently, and you didn't restore your original network configuration yet.\n\nIn order to run Xibalba with the Internet Kill Switch mode again, you need to have your original iptables rules running (and not the blocking rules created when the switch went ON)\n\n")
                        print(color.BOLD+color.UNDERLINE+"HINT:"+color.END)
                        print("\n - In order to browse the internet again after this switch gets activated, you have to run Xibalba with ["+color.BOLD+"-r"+color.END+', '+color.BOLD+"--restorenetwork"+color.END+"] flag\n\n")
                        sys.exit(2)                    


                if code in ["-r","--restorenetwork"]:

                    restoremode = True

                    user = getpass.getuser()


                    if ((restoremode) and (user != "root")):
                        print("\n\nTo run Xibalba with ["+color.BOLD+"-r"+color.END+', '+color.BOLD+"--restorenetwork"+color.END+"] flag, you need to be root.\n\nXibalba needs to restore the iptables rules you used to have before the Internet Kill Switch activation, and to do this it needs some OS administrative rights.\n\n")
                        sys.exit(2)


                    logmsg = "INFO: Internet Kill Switch effects have been REVERTED!. You can browse the internet freely without a VPN again.\n\n"
                    logfile = open(logpath, "a")
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d      %H:%M:%S")
                    logfile.write(timestamp+"\n")
                    logfile.write(logmsg)
                    logfile.close()


                    os.system("touch /tmp/user-iptables")
                    os.system("iptables-restore < /tmp/user-iptables")
                    print("\nRestoring your network configuration...\n")
                    os.system("rm -f /tmp/user-iptables")
                    time.sleep(1)
                    print("The Internet Kill Switch effects have been reverted!\nNow you can browse the internet normally without a VPN.\n\n")
                    sys.exit(2)
                                    

        if (os.path.isfile("/tmp/user-iptables")):
            print("\n\nIt looks like the Internet Kill Switch was activated recently, and you didn't restore your original network configuration yet.\n\nIn order to run Xibalba again, you need to have your original iptables rules running (and not the blocking rules created when the switch went ON)\n\n")
            print(color.BOLD+color.UNDERLINE+"HINT:"+color.END)
            print("\n - In order to browse the internet again after this switch gets activated, you have to run Xibalba with ["+color.BOLD+"-r"+color.END+', '+color.BOLD+"--restorenetwork"+color.END+"] flag. -root required-\n\n")
            sys.exit(2)

        user = getpass.getuser()



        if ((killswitch) and (user != "root")):
            print("\nTo run Xibalba with Internet Kill Switch mode, you need to be root.\n\nTo prevent leaks, Internet Kill Switch apply some blocking iptables rules when detecting a VPN disconnection (and to do this, Xibalba need OS administrative rights)\n\n")
            sys.exit(2)
        


        
        ### looper() runs in a diffrent thread. If I don't do this, the infinite "while" loop inside looper() don't allow the system to escape and continue the execution flow, and app.main() and gtk.main() never run.
        thread = threading.Thread(target=looper) 
        thread.daemon = True
        thread.start()
       
        
     
        app = TrayIcon()
        app.main()

