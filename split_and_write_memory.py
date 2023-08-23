import os
import sys
import time
import subprocess
import shlex

#This script will accept a STM32 binary firmware file as input
#and split it up into specified CHUNK_SIZE files writing each
#chunk to the STM32 using the ST-LINK CLI tool.
#If the write fails it will keep trying every two seconds

#STM32 is little endian
#3|3|2|2|2|2|2|2|2|2|2|2|1|1|1|1|1|1|1|1|1|1|
#1|0|9|8|7|6|5|4|3|2|1|0|9|8|7|6|5|4|3|2|1|0|9|8|7|6|5|4|3|2|1|0
#0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
#Debug Exception and Monitor Control Register (CoreDebug->DEMCR,
#0xE000EDFC), set to 0x1000000 (bit 24) hex to enable Trace system 
#enable; to use DWT, ETM, ITM and TPIU 


#This tool is handy if you have some oddly behaving devices that
#have spurious failures when using the GUI ST LINK tools to write
#new firmware images

def run_command(command):
    tryAgain=False
    p = subprocess.Popen(command, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                   universal_newlines=True)
    (output, err) = p.communicate()  
    #This makes the wait possible
    p_status = p.wait()
    #This will give you the output of the command being executed
    #print('Error: ' , err.split('\n'))
    #print('Output: ' , output.split('\n'))
    thisoutput = output.split('\n')
    lineno=0;
    for line in thisoutput:
        #print('Line: ' + str(lineno) + ' ' + line)
        lineno += 1
        if "Error" in line:
            tryAgain=True
            print('ERROR, TRYING AGAIN')
        else:
            print('SUCCESS')
    return tryAgain



#CHUNK_SIZE=2048

if(len(sys.argv)<3):
    print("Not enough arguments")
    print("file name is arg1")
    print("optional chunk size is arg 2")
    exit(0)


CHUNK_SIZE = int(sys.argv[2])
FILE_NAME = sys.argv[1]
print(CHUNK_SIZE)
CWD = os.getcwd()

file_number = 1
f=open(sys.argv[1], "rb")
chunk = f.read(CHUNK_SIZE)
print("Chunk size is " + hex(CHUNK_SIZE))
ADDRESS = 0x08000000
ST_LINK_SN = '32FF6D064247363310341857'
#ST_LINK_SN = '52FF6E064852854852521167'
while chunk:
    tempfile = sys.argv[1] + '_' + str(file_number) + '.bin'
    with open(tempfile,"wb") as chunk_file:
        chunk_file.write(chunk)
    
    ARGS = ['.\ST-LINK_CLI.exe', '-c', 'SN=32FF6D064247363310341857', 'SWD',  'Hrst', 'LPM', '-P ', tempfile, ' ',hex(ADDRESS)]
    
    while (run_command(['.\ST-LINK_CLI.exe', '-c', 'SWD',  'HOTPLUG', 'Srst', '-P', tempfile, hex(ADDRESS)])==True):
        time.sleep(2)
    file_number += 1
    ADDRESS=ADDRESS+CHUNK_SIZE
    chunk = f.read(CHUNK_SIZE)
