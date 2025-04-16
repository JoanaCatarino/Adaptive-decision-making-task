# Adaptive decision-making task

This Github repository describes the hardware and software code we are currently developing in the DMC lab to train mice in adaptive decision-making task. Our work is inspired by previously published work such as the [International Brain Laboratory task](https://github.com/int-brain-lab/iblrig) and the [DMC-Behavior Platform](https://github.com/hejDMC/dmc-behavior).

## Behavior setup

### Hardware required:

 
\- Raspberry Pi 5  
\- Hifiberry Amp2  
\- Arduino UNO REV3

Start by assembling all the structural setup components (breadboard, mouse holder, head bar holder, spout holders, and LED holder).

![](https://github.com/JoanaCatarino/Adaptive-decision-making-task/Images/1.png?raw=true)


### Liquid Feed Pump

- Pump model: Campden Instruments Model 80204A Precision \- Liquid Feed Pump

Each power cord can supply power to 4 pumps, therefore we will have one power cord for each two behavior setups (1 behavior setup \= 2 pumps) and another one for the ephys rig.  
The pump comes with cable formed by 3 wires: red, green and blue. Red \= 24/28V, Green \= 0V and Blue is the operate (5V to 28V signal, switch to 0V to operate). The blue cable is the one we are going to connect  to the Rbpi to control the opening and closing of the pump. Important to keep in mind that when we code the pump, gpio\_off means that the pump is actually delivering water and gpio\_on means that the pump is not delivering anything.

Pump will be connected to GPIO 22 (left pump) and to GPIO 27 (right pump) in the Rbpi.

Steps to connect the pump:

- Solder a female dupont wire to the blue wire in the pump cable \- this is the wire we will later connect to the Rbpi. 

- Connect the red and green wires to the adaptors that will then connect to the power supply. We should have a adaptor only for the red wires and another one only for the green wires. \+ from the cable will connect to the red wire and the \- from the cable will connect to the green wire.

### Piezo sensor

- Piezo model: TE connectivity \- 1-1002908-0-M

Assemble piezo case:

- add protocol to assemble a pezo sensor with the foam and the case \+ put reference for the tubing in the spout we use inside the piezo case

Assemble piezo cables/connections:

The piezos will be directly connected to the Arduino, which will then read the signal and send information to the Rbpi. To assemble the piezos we will start by soldering a resistor in between the red and black wire. Then, similar to what we did in the pumps, we will solder a male dupont wire that will be used to establish the connection to the Arduino.

The resistor we will be using is the 1M ohm \- color order: golden, green, black, brown

When connecting the piezos to the Arduino, the red wire should be connected to the Analog slot, and the black wire should be connected to the ground slot (GND).

Left piezo is connected to Arduino in A0(red) and the second GND slot (before 5V \- black). Right piezo is connected to Arduino in A1(red) and first GND slot (after Vin black). Both black wires are connected on the power side of the arduino and the red wires in the Analog in.

**Tubing for water delivery \- buy more tubing**

- Tubing model:  Campden Instruments \- CI.80204A-M/R-T15  
  - Specifications:  Santoprene Tubing TPE 64; Bore: 0.50mm; O.D.: 2.6mm

Start by cutting two pieces of tubing with 170cm each \- this amount should be enough to connect the spout to the pump and the pump to the water container. Important to note that the pumps and water container are outside the box (on top of it), therefore, the tubing needs to be long enough to reach them.

After that, get two small pipette tips (orange box: 0.1-20uL) and cut them after the bigger part at the end (see dasehd black line in the picture). To help cut the plastic, start by warming it up with the soldering iron and then use a blade.

Next, attach the pipette tips to the tubing at the end of the piezo case (licking spout) and to the tubing that was just cut. The smaller opening of the tip should face the piezo and the bigger one the tubing.

The rest of the tubing should then be placed inside the pump and into the water container. Flush some water to check that everything is working properly.

**Speakers**

- Speaker model: Visaton K 28 WP

Start by gluing the speaker to the 3D printed case that we will then use to attach to the animal holder structure.  
Next, cut two pieces of 50cm of speaker cable (C1362.21.01 \- Digikey). This cable is composed of two different wire \- a silver wire and a copper wire. The wires are the same, but we can use the colors to identify which one is connected to the \+ or \- terminal in the Hifiberry. For this behavior setup we are using the copper wire for plus and the silver wire for minus. Therefore, the wires should be soldered to the speaker according to this.

After that, the connection between the speaker and the Hifiberry can be made. For this, we will once again attach the copper cable to the \+ terminal in the Hifiberry and the silver one to the minus terminal.

When everything is in place in the setup, we can glue the speakers to each side of the animal holder in a diagonal position using the glue gun. 

To add:  
**Blue LED**  
brown cable is \+ (positive) and white cable is \- (negative)

we are gonna make a new bnc cable \- inner layer is signal \- correspond to the \+ . outside layer is ground.

- Remove outer coat \- ground is the silver part  
- pull the silver mesh apart and put is together on the side  
- remove the inner coat to get to the signal part  
- repeat this on the other side of

Connect the LED to its power supply \- 15V. If you turn the LED to the ‘CW’ to check if the light is working.

**White LEDs**

**Hardware Connection**

Once all the different devices are assembled, we can connect the Rbpi, Hifiberry, and Arduino.  
The Hifiberry is assembled on top of the Rbpi. The Hifiberry and the Rbpi will be powered by the same power supply, which should be connected to the Hifiberry. The Arduino will be connected to the Rbpi and powered by it.

The overall configuration should look similar to this:

Start connecting all the different components to the pins in the Raspberry Pi. The schematic below represents everything that we will need to connect.

Schematic of the GPIO pins we will be using to assemble the different components of the setup. In green we have the pins that can be used for different devices, and in orange we have the pins that should be avoided because are already occupied by the Hifiberry or have other functions that do not serve our purpose.

This the map for the pins used to connect the different devices to the Raspberry Pi: (Re-check this part)

| Device | Ground | \+ |
| :---: | :---: | :---: |
| Blue LED | \#9 | 17 |
| White LED Left | \#9 | 6 |
| White LED right | \#9 | 26 |
| Pump Left | \- | 22 |
| Pumo right | \- | 27 |

Currently, the ground is connected to a breadboard, and all the LEDs use the same one.

**Raspberry Pi installation:**

To start the installation of all the packages we need in the Raspberry PI we will start by turning it into a physical computer station. For this, we will start by inserting the microSD card for storage and then connecting a mouse, keyboard, and screen/monitor.

Connect the ethernet cable. We will only be able to access ethernet when the Raspberry Pi is whitelisted. to whitelist the Rbpi we need to get the number. To get it, type this command in the terminal:

ifconfig 

Next, connect the power supply to the Hifiberry, which will power the Raspberry Pi simultaneously.

Boot the Raspberry Pi:

Raspberry Pi models lack onboard storage, so you have to supply it. You can boot your Raspberry Pi from an operating system image installed on any supported media, e.g., microSD card.  
To use your Raspberry Pi, you’ll need an operating system. By default, Raspberry Pis check for an operating system on any SD card inserted in the SD card slot.

To install an operating system on a storage device for your Raspberry Pi, you’ll need:

- a computer you can use to image the storage device into a boot device  
- a way to plug your storage device into that computer

We recommend installing an operating system using [Raspberry Pi Imager](https://www.raspberrypi.com/documentation/computers/getting-started.html#raspberry-pi-imager).

**Set up the Raspberry Pi**

- Choose a user and password: The user should be Rbpi, followed by the box number to identify to which training rig that device belongs (e.g., rbpi-box1). For all the Rbpis, we will use the same password: 1234dmc. To facilitate the access to the rbpi, we will, for now, remove the password from the booting step:

Rbpi icon  \> Preferences \> Raspberry pi configuration \> System \> Auto Login (Activate)

- Activate different interfaces that might be useful to access the Rbpi in the future:

Rbpi icon \> Preferences \> Raspberry Pi configuration \> Interfaces: SSH, VNC, SPI, I2C, Serial Console (Activate all)

- Change Timezone and Locale:

Rbpi icon \> Preferences \> Raspberry Pi configuration \> Localization \> Locale: en (language), US (country), ISO-8859-1 (character set); Timezone: Europe (area), Stockholm (location); Keyboard: Swedish (both layout and variant)

If, by any chance, the date and time are not updating, try running this line in the terminal:

sudo date \-s "10 JAN 2016 20:37:00"

- Install the programming editor via terminal:

sudo apt-get update  
sudo apt-get dist-upgrade  
sudo apt-get install mu-editor

Create a shortcut for the editor in the desktop by clicking the Rbpi icon \> Programming and dragging the icon of the mu editor

- Setup environment by running the following line in the main directory:

python3 \-m venv \--system-site-packages Task

Activate the environment using this command:

source Task/bin/activate

- Create a new folder in the main directory called ‘git\_repo’ and clone the code for the task and arduino into that folder.

cd git\_repo  
git clone [https://github.com/JoanaCatarino/Adaptive-decision-making-task.git](https://github.com/JoanaCatarino/Adaptive-decision-making-task.git) 

- With the environment activated, install the requeriments.txt to install in one go all the packages required to run the gui and the task. Follow the steps below:

source Task/bin/activate  
cd git\_repo/  
cd Adaptive\_decision\_making\_task/    (directory with the requirements.txt file)  
pip3 install \-r requirements.txt

- Try to run the Gui and check if there is any package missing. To run the gui follow the steps bellow:

source Task/bin/activate  
cd git\_repo/  
cd Adaptive\_decision\_making\_task/  
cd Task\_GUI\_Joana/  
python3 taskController.py

I found the cv2, qasync, pyaudio and pyqtgraph packages to be missing (maybe the were installed outside the environment) and they are installed using the following code, respectively: add them to requirements.txt

pip3 install opencv-python  
pip3 install qasync  
sudo apt install portaudio19-dev python3-pyaudio  
pip3 install pyqtgraph

After this installations the task seems to launch fine\!

- Make shortcuts to activate the environment and launch the task. Type the following commands in the terminal:

nano .bash\_aliases

Inside the bash aliases page write the paths for the env and the Gui:

alias env='source /home/rasppi-ephys/Task/bin/activate'  
alias gui=’python3 /home/rasppi-ephys/git\_repo/Adaptive-decision-making-task/Task\_Gui\_Joana/taskController.py’

If you want to remove the ALSA and Jack warnings in the terminal, then the alias for the gui should look like this:

alias gui='python3 /home/rasppi-ephys/git\_repo/Adaptive-decision-making-task/Task\_Gui\_Joana/taskController.py 2\>/dev/null'

Take into consideration that when you do this you will also silence all the error messages, which makes it harder to troubleshoot possible problem in the code.

**Set up Hifiberry Amp2**

It was assembled on top of the Raspberry Pi and the pyaudio module was installed but we still need to change the system configurations so that the sound is outputed through the speaker connected to the Hifiberry instead of through the Raspberry Pi. To do this follow the commands belows:

- Start by checking if the Hifiberry dac is recognized by the Hifiberry and if so, in which card:

	aplay \-l

- Change the config file to set the Hifiberry as the output system for the audio:

	sudo nano /boot/firmware/config.txt

sudo nano /etc/asound.conf

After doing this alterations, reboot the system by typing in the terminal: sudo reboot  
After rebooting check if the sounds are working by playing the test rig task and pressing both sound types. If it is not working, try to unplug and re-plug the power supply.

Before following to next step is also good to update the system. Try the following commands:  
	  
	sudo apt update  
	sudo apt upgrade

**Set up Arduino UNO Rev3**

Start by connecting the Arduino to the Raspberry Pi. When doing this step, check that the camera is already connected, if not, connect it first. Camera shoul be the first to be connect in order to be assigned as device 0 and the Arduino as device 1\.

- Install the arduino via terminal:


  sudo apt-get install arduino

If the installation was successful you should see the **arduino icon** under Rbpi icon \> Programming

- Open the Arduino app and open the arduino file that was cloned from the Github repository for the task. The path for the file should be something similar to this:

home \> kmb-box1-raspi \> git\_repo \> Adaptive-decision-making-task \> Arduino \> 2piezo\_serial.ino

When opening the file, a message will pop up with the following information:

‘The file “2piezo\_serial.ino” needs to be inside a sketch folder named “2piezo\_serial”. Create this folder, move the file and continue?’

press “OK”

A new window with the code should pop up. If this happen start by confirming that the code is ok by pressing the verify button (✓).  If the system says “Done complaining” and does not show any errors, go ahead and flush the code into the Arduino by pressing the arrow (→).

If the serial port was not previously selected we will receive a pop up message saying: 

‘ Serial port not selected. retry the upload with another serial port \-\> drop down menu with serial port options’ \- select the option with “Arduino Uno” and press “OK”

If the system says ‘ Done uploading’ withow showing any error messages than the upload of the code into the Arduino was successful.

The Arduino is ready to use\!

To test if everything is ok, run the test rig task and check if the piezo are being detected. If they are not, it could be because we are trying to read the signal from the wrong device (it should be device 1 instead of 0). To check/change this follow this steps:

	open mu and import the piezo\_reader.py file:

/home/kmb-box1-rasppi/git\_repo/Adaptive-decision-making-task/Task\_GUI\_Joana/piezo\_reader.py

Under the class PiezoReader, check wich device is set in self.port. It should be: ‘/dev/ttyACM1’

Save the new file. The piezo signal should now be detectable during the task\!

**To run the task**

env  
gui

Still need to check if any other folders need to be created according to the code \+ the tone-spout map need to be uploaded to every Raspberry pi in the beginning of  a new cohort of animals → super important\!\!\!

Give unique identity to each raspberry pi to be able to identify  it when connecting via VNC

to check:

- is the tubing enough for all the rigs? do we have more for eventual replacements?  
- should I do the calibration of the pumps with sucrose water? viscosity might change the flush rate  
- 





