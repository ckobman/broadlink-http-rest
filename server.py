from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import broadlink, configparser
import sys, getopt
import time, binascii
import netaddr
import settings
import signal
from os import path
from Crypto.Cipher import AES

class Server(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):

        if 'favicon' in self.path:
            return False

        self._set_headers()

        if 'learnCommand' in self.path:
            commandName = self.path.split('/')[2] 
            result = learnCommand(commandName)
            if result == False:
                self.wfile.write("Failed: No command learned")
            else:
                self.wfile.write("Learned: %s" % commandName)
       

	elif 'sp2' in self.path:
	    spIP = self.path.split('/')[2]
            spMAC = self.path.split('/')[3]
            spState = self.path.split('/')[4]
	    result = sendSPCommand(spIP, spMAC, spState)
            if result == False:
                self.wfile.write("Failed: Unknonwn command")
            else:
                self.wfile.write("Sent: %s" % spState)

        elif 'sendCommand' in self.path:
            commandName = self.path.split('/')[2]
            if 'on' in commandName or 'off' in commandName:
                status = commandName.rsplit('o', 1)[1]
                realcommandName = commandName.rsplit('o', 1)[0]
                print(status,realcommandName)
                if 'n' in status:
                    setStatus(realcommandName, '1', True)
                elif 'ff' in status:
                    setStatus(realcommandName, '0', True)
            result = sendCommand(commandName)
            if result == False:
                self.wfile.write("Failed: Unknonwn command")
            else:
                self.wfile.write("Sent: %s" % commandName)
                

        elif 'getStatus' in self.path:
            commandName = self.path.split('/')[2]
            if 'temp' in commandName:
                result = getTempRM()
                if result == False:
                    self.wfile.write("Failed: Cannot get temperature")
                else:
                    self.wfile.write('''{ "temperature": %s } ''' % result)
            else:
                status = getStatus(commandName)
                if (status):
                    self.wfile.write(status)
                else:
                    self.wfile.write("Failed: Unknown command")
        
        elif 'setStatus' in self.path:
            commandName = self.path.split('/')[2]
            status = self.path.split('/')[3]
            result = setStatus(commandName, status)
            print('Setting status %s of %s' % (commandName,status))
            if (result):
                self.wfile.write("Set status of %s to %s" % (commandName, status))
            else:
                self.wfile.write("Failed: Unknown command")

        elif 'a1'  in self.path:
            sensor = self.path.split('/')[2]
            result = getA1Sensor(sensor)
            if result == False:
                self.wfile.write("Failed getting A1 data")
            else:
                if sensor == 'temperature' or sensor == 'humidity':
                    self.wfile.write('''{ "%s": %s }''' % (sensor, result))
                else:
                    self.wfile.write('''{ "%s": "%s" }''' % (sensor, result))
        else:
            self.wfile.write("Failed")

serverPort = ''

def sendSPCommand(spIP, spMAC, spState):

        try:
                device = broadlink.sp2(host=(spIP,80), mac=bytearray.fromhex(spMAC))
                device.auth()
                time.sleep(3)
                device.host

                if spState == "1":
                        device.set_power(True)
			print "on"
                else:
                        device.set_power(False)
			print "off"
        except:
                        print "error"
                        pass


        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(4)   # Ten seconds
        try:
            device.send_data(finalCommand)
        except Exception, msg:
            print "Probably timed out.."
            return True



def sendCommand(commandName):
    device = broadlink.rm((RMIPAddress, RMPort), RMMACAddress)
    device.auth()

    if settingsFile.has_option('Commands', commandName):
        commandFromSettings = settingsFile.get('Commands', commandName)
    else:
        return False

    print('sending command %s' % commandName)
    if commandFromSettings.strip() != '':
        decodedCommand = binascii.unhexlify(commandFromSettings)
        
        finalCommand = decodedCommand
	device.send_data(finalCommand)   
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(4)   # Ten seconds
        try:
            device.send_data(finalCommand)
        except Exception, msg:
            print "Probably timed out.."
            return True

def learnCommand(commandName):
    device = broadlink.rm((RMIPAddress, RMPort), RMMACAddress)
    device.auth()

    device.enter_learning()
    time.sleep(RealTimeout)
    LearnedCommand = device.check_data()

    if LearnedCommand is None:
        print('Command not received')
        return False

    finalCommand = LearnedCommand

    decodedCommand = binascii.hexlify(str(finalCommand))

    broadlinkControlIniFile = open(path.join(settings.applicationDir, 'settings.ini'), 'w')    
    settingsFile.set('Commands', commandName, decodedCommand)
    settingsFile.write(broadlinkControlIniFile)
    broadlinkControlIniFile.close()
    return True

def setStatus(commandName, status, exist = False):
    if exist:
        broadlinkControlIniFile = open(path.join(settings.applicationDir, 'settings.ini'), 'w')    
        settingsFile.set('Status', commandName, status)
        settingsFile.write(broadlinkControlIniFile)
        broadlinkControlIniFile.close()
        return True

    if settingsFile.has_option('Status', commandName):
        commandFromSettings = settingsFile.get('Status', commandName)
    else:
        return False
    if commandFromSettings.strip() != '':
        broadlinkControlIniFile = open(path.join(settings.applicationDir, 'settings.ini'), 'w')    
        settingsFile.set('Status', commandName, status)
        settingsFile.write(broadlinkControlIniFile)
        broadlinkControlIniFile.close()
        return True
    else:
        return False

def getStatus(commandName):
    if settingsFile.has_option('Status', commandName):
        status = settingsFile.get('Status', commandName)
        return status
    else:
        return False

def getTempRM():
    device = broadlink.rm((RMIPAddress, RMPort), RMMACAddress)
    device.auth()
    temperature = device.check_temperature()
    if temperature:
        return temperature
    return False 

def getA1Sensor(sensor):
    device = broadlink.a1((A1IPAddress, A1Port), A1MACAddress)
    device.auth()
    result = device.check_sensors()
    if result:
        return result[sensor]
    return False 

def signal_handler(signum, frame):
    print ("HTTP timeout, but the command should be already sent.")
        
def start(server_class=HTTPServer, handler_class=Server, port=serverPort):


    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting broadlink-rest server on port %s ...' % port
    httpd.serve_forever()

if __name__ == "__main__":

    settingsFile = configparser.ConfigParser()
    settingsFile.optionxform = str
    settingsFile.read(settings.settingsINI)

    RMIPAddress = settings.RMIPAddress
    if RMIPAddress.strip() == '':
        print('IP address must exist in settings.ini or it should be entered as a command line parameter')
        sys.exit(2)

    RMPort = settings.RMPort
    if RMPort.strip() == '':
        print('Port must exist in settings.ini or it should be entered as a command line parameter')
        sys.exit(2)
    else:
        RMPort = int(RMPort.strip())

    RMMACAddress = settings.RMMACAddress
    if RMMACAddress.strip() == '':
        print('MAC address must exist in settings.ini or it should be entered as a command line parameter')
        sys.exit(2)
    else:
        RMMACAddress = netaddr.EUI(RMMACAddress)

    A1IPAddress = settings.A1IPAddress
    if A1IPAddress.strip() == '':
        print('IP address must exist in settings.ini or it should be entered as a command line parameter')
        sys.exit(2)

    A1Port = settings.A1Port
    if A1Port.strip() == '':
        print('Port must exist in settings.ini or it should be entered as a command line parameter')
        sys.exit(2)
    else:
        A1Port = int(A1Port.strip())

    A1MACAddress = settings.A1MACAddress
    if A1MACAddress.strip() == '':
        print('MAC address must exist in settings.ini or it should be entered as a command line parameter')
        sys.exit(2)
    else:
        A1MACAddress = netaddr.EUI(A1MACAddress)

    RealTimeout = settings.Timeout
    if RealTimeout.strip() == '':
        print('Timeout must exist in settings.ini or it should be entered as a command line parameter')
        sys.exit(2)
    else:
        RealTimeout = int(RealTimeout.strip())    


    if settingsFile.has_option('General', 'serverPort'):
        serverPort = int(settingsFile.get('General', 'serverPort'))
    else:
        serverPort = 8080


    start(port=serverPort)
