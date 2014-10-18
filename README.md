pybkick
=======

Push software to a pyboard quickly, without using USB Mass Storage mode.

Rationale
---------

Pyboards are small microcomputers which can execute code written in Micropython, which is a Python3
compatible language which includes a small subset of the Python3 standard library. 

The suggest way to deploy code to a PyBoard is to mount it as a USB Mass Storage device, and then edit
files directly on the device, or simply copy over the relevant files from a PC. This approach can
be problematic because if the device is reset, it can cause the Mass Storage drive to be suddenly
unmounted. At best this will cause confusion in the operating system.

Further problems can occur if the device needs to be factory reset - this will wipe the code on the device
and will require everything to be re-copied, or possibly loosing work.

In short, using USB Mass Storage mode is a real pain. It would be much simpler to have something that was able
to use the Serial mode connection to quickly copy code across without any kind of stateful connection. That
is the goal of this project.  

Installation
------------

Install using pip:

    pip install pybkick

Basic usage
-----------

In this example, all my micropython code is in a single, flat directory called 'mpy' which is in the same directory
as the script containing the following code:

	from pybkick import kick
	
	kick(
		# How do we connect to the pyboard?
	    port='/dev/ttyACM0',
	    
	    # Which files should we copy to the pyboard?
	    src=os.path.join(dirname(__file__), 'mpy'), 
	)

Advanced usage
--------------

In your setup.py file, add 'pybkick' to install_requires. You can also add a script which calls the kick function as an entry point. This will
create a command-line utility that can automatically deploy your project to the pyboard.

Limitations
-----------

The kick function can only copy flat directories of files into the root directory of the pyboard. It cannot
currently handle heirarchical directories or 