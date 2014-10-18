pybkick
=======

Push software to a pyboard automatically

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