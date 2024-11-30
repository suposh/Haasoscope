Commands are received in serialprocessor.v and handled in the SOLVING case. 
Each command has a `starting id` number. 

Some commands take additional arguments. 
> Commands are passed along a multiboard chain so they are seen by all boards.

### Command 0 - 9
Tells the board its ID.
The first board will get usually be sent a 0, and then it sends a 1 to the next board,
which then sends a 2 to the next, and so on.
**Board 0 is special since it creates the clock for all boards.**

### Command 10-19
Tells the board with ID 10 less to send its event data.

**For instance**, 10 will tell board 0 to send its data. 
The data is 4 channels of 
- fast ADC data, and 
- additional info, if other options are enabled.

Each channel's data is sent in order, starting with channel 0.
- N samples are sent for each channel, from earliest to latest in time.
- Each sample is one byte (8 bits), where 0 is the highest voltage for the input (e.g. 3.75V), and 255 is the lowest (e.g. -3.75V).
	> Its an inverting op-amp configuration.

### Command 20-29
Tells the board with ID 20 less that it's the last one (the highest ID). For instance, sending 21 tells board with ID 1 that it's the last board. It needs to know this in order to ignore signals on its unconnected trigger inputs on its left-side male connector.

### Command 30-39
Tells the board with ID 30 less to be the "active" board. For instance, 31 would tell the board with ID 1 to be active, and all other boards to the right of it to be in "passthrough".
Then sending another request for some data with come from the active board,
and be passed through the boards to its right. If one wanted to get the board unique max10 string from board 2, they would send 32 followed by the command to send the unique string (142).

- 100 tells all boards **to arm** their triggers, and then record a new event.
	> There is also an auto-rearm mode which will always get a new event after sending the last one. Read about **Rolling**.
	> 
If the board does not record a new event, it will continue to send the same event each time it is asked to send an event.


### Rolling Command
Rolling the trigger means automatically generating a trigger every 0.2 seconds (like auto mode on a scope).

- 101 - Enable Rolling
- 102 - Disable Rolling

### Command 110-119
Tells boards to send the `slow ADC` data from a given pin.
For instance
- 110 sends the data from all boards from slow ADC input 1 (pin 6)
- 118 would send slow ADC data from input 8 (pin 14), etc.

The data is sent as N samples (set below), where each sample is 2 bytes.
- The first byte is the lowest 8 bits (0-255), and the second holds the higher 4 bits (0-15). 
- It's a 12-bit ADC. 
- So the 12-bit value is 256 times the second byte plus the first byte.

### Command 120

(+ 2 more bytes) is how many slow ADC samples to send. It is 256*a+b samples, where a is the first byte and b is the second byte. For instance, 120 1 10 would send 256*1+10=266 samples.

### Command 121
(+ 2 more bytes) is the trigger point in time (how many samples to record before the trigger).

- It is 256*a+b samples, where a is the first byte and b is the second byte.
- Add pow(2,12) to the number (i.e. 16 to a) in order to use the current timebase in the calculation (recommended!).

### Command 122
(+ 2 more bytes) is how many fast ADC samples to send.
- It is 256*a+b samples, where a is the first byte and b is the second byte.
> Example - 122 1 100 would send 256*1+100=356 samples.

### Command 123
(+ 1 more byte) is how many fast ADC samples to skip sending after each sample sent. The byte is 2^n. 
> Example - If the byte is 3, then 2^3=8 samples are skipped.

### Command 124
(+ 1 more byte) is the "timebase", i.e. what fraction of fast ADC samples to actually record.
It is 1/2^n, so if the byte is 3, then 1/2^3=1/8 fast ADC samples are recorded.

### Command 125
(+ 1 more byte) is the number of clock ticks (20ns) to wait between sending serial bytes. It is 2^n.
> Example - If the byte is 4, then 2^4=16 ticks are waited.

### Command 126
(+ 1 more byte) is the channel to draw on the miniscreen.
> Example - 126 3 would draw channel 3 on each board's mini-screen.

### Command 127
(+ 1 more byte) sets the trigger threshold for the fast ADC channels.

### Command 128
(+ 1 more byte) is the Edge type. (Probably for threshold)
- 1 for rising edge
- 0 for falling edge


### Command 129
(+ 2 more bytes) is how long a channel must be above/below the trigger threshold to fire it.
It is 256*a+b samples, where a is the first byte and b is the second byte.

### Command  130
(+ 1 more byte) toggles whether the trigger is active for a given channel.
> Example - 130 6 would toggle the trigger activity for channel 6.

### Command 131
(+ 2 more bytes) is for talking to the SPI interface on the fast ADCs on all boards.
The first byte is the 7 bit address to send to on the ADC, and the second is the byte sent to that address. See the max19506 datasheet for info, and/or see example commands in the python programs.

### Command  132/133
This will send the delaycounter / carrycounter extra data (1 byte) from the active board.


### Command  134
(+ 1 more byte) toggles the x10 gain for a given channel.
> Example - 134 6 would toggle the x10 gain for channel 6.

### Command 135
(+ 2 more bytes) says how many 2us ticks to wait after sending each 32 bytes of serial data (serialdelaytimerwait). It is 256*a+b ticks, where a is the first byte and b is the second byte.

### Command 136
(+ 6 more bytes!) talks over i2c to the IO expanders and DAC on the boards.
- `Byte 1` -   How many bytes of info to send, excluding addresses.
- `Byte 2` -   The i2c address to send to.
- `Byte 3` -   Data byte 1
- `Byte 4` -   Data byte 2
- `Byte 5` -   Data byte 3
- `Byte 6` -   Board ID to talk to (or 200 to talk to all boards)

### Command 137
Toggles whether data is sent back over the serial interface or the USB2 hat.

### Command 138
Is how many ADC samples to shift the reference wave by in order to be 90deg out of phase, for lockin calculations in the FPGA.

### Command 139
Toggles auto-ReArming of the trigger. Without it, you need to send 100 to record a new event each time.

### Command 140
(+ 1 more byte) sets the "runt" trigger threshold for the fast ADC channels.

### Command 141
(+ 1 more byte) toggles the oversampling for a given channel.
> Example - 130 4 would toggle oversampling for channel 4.

### Command 142
Tells the active board to send its unique 8-byte ID back over serial.

### Command 143
Toggles "high-res" mode for all channels.

### Command 144
Toggles whether the external trigger pin is active, for all boards.

-- Following commands require the new firmware!

145 (+ 1 more byte) is how many channels to send data for, from each board. For instance, 145 4 would send all 4 channels from all boards. Note that the logic analyzer data is the "5th channel" on each board, so 145 5 sends all 4 channels plus the logic analyzer data. The logic analyzer data is the same number of samples as and synchronous with the fast ADC data. It is 1 byte per sample, and each bit is 0/1 for each of the 8 logic analyzer pins being low/high.

146 (+ 3 more bytes) requests a byte to be read from i2c (e.g. ioexpander inputs) from a given i2c address, chip address, and board.

147 requests the firmware version byte to be sent back over serial from the currently active board.