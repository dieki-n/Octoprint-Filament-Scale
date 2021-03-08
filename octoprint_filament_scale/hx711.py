import RPi.GPIO as GPIO
import time


def bitsToBytes(a):
    a = [0] * (8 - len(a) % 8) + a # adding in extra 0 values to make a multiple of 8 bits
    s = ''.join(str(x) for x in a)[::1] # reverses and joins all bits
    returnInts = []
    for i in range(0,len(s),8):
        returnInts.append(int(s[i:i+8],2)) # goes 8 bits at a time to save as ints
    return returnInts
	
class HX711:
	def __init__(self, dout, pd_sck, gain=128):
		self.PD_SCK = pd_sck
		self.DOUT = dout

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.PD_SCK, GPIO.OUT)
		GPIO.setup(self.DOUT, GPIO.IN)

		self.GAIN = 0
		self.REFERENCE_UNIT = 1	 # The value returned by the hx711 that corresponds to your reference unit AFTER dividing by the SCALE.
		
		self.OFFSET = 1
		self.lastVal = int(0)

		self.LSByte = [2, -1, -1]
		self.MSByte = [0, 3, 1]
		
		self.MSBit = [0, 8, 1]
		self.LSBit = [7, -1, -1]

		self.byte_format = 'LSB'
		self.bit_format = 'MSB'

		self.byte_range_values = self.LSByte
		self.bit_range_values = self.MSBit

		self.set_gain(gain)

		time.sleep(1)

	def is_ready(self):
		return GPIO.input(self.DOUT) == 0

	def set_gain(self, gain):
		if gain is 128:
			self.GAIN = 1
		elif gain is 64:
			self.GAIN = 3
		elif gain is 32:
			self.GAIN = 2

		GPIO.output(self.PD_SCK, False)
		self.read()
	
	def createBoolList(self, size=8):
		ret = []
		for i in range(size):
			ret.append(False)
		return ret
	def read(self):
		x = time.time()
		while x+5 > time.time() and not self.is_ready():
			GPIO.wait_for_edge(self.DOUT, GPIO.FALLING, timeout=1000)
			time.sleep(0.01)
		
		dataBits = [self.createBoolList(), self.createBoolList(), self.createBoolList()]
		dataBytes = [0x0] * 4

		for j in range(self.byte_range_values[0], self.byte_range_values[1], self.byte_range_values[2]):
			for i in range(self.bit_range_values[0], self.bit_range_values[1], self.bit_range_values[2]):
				GPIO.output(self.PD_SCK, True)
				
				dataBits[j][i] = GPIO.input(self.DOUT)
				GPIO.output(self.PD_SCK, False)
				time.sleep(0.000001)
				
			dataBytes[j] = bitsToBytes(dataBits[j])[1] 

			
		#set channel and gain factor for next reading
		for i in range(self.GAIN):
			GPIO.output(self.PD_SCK, True)
			GPIO.output(self.PD_SCK, False)

		#check for all 1
		#if all(item is True for item in dataBits[0]):
		#	 return int(self.lastVal)

		dataBytes[2] ^= 0x80

		np_arr32 = (dataBytes[3] << 24) + (dataBytes[2] << 16) + (dataBytes[1] << 8) + dataBytes[0]
		
		self.lastVal = np_arr32

		return int(self.lastVal)
		

	def read_average(self, times=3):
		

		values = int(0)
		for i in range(times):
			values += self.read()

		return values / times

	def get_raw_value(self, times=3):
		return self.read_average(times)

	def get_weight(self, times=3):
		value = self.read_average(times) - self.OFFSET
		value = value / self.REFERENCE_UNIT
		return value

	def tare(self, times=15):
	   
		# Backup REFERENCE_UNIT value
		reference_unit = self.REFERENCE_UNIT
		self.set_reference_unit(1)

		value = self.read_average(times)
		print(value)
		self.set_offset(value)

		self.set_reference_unit(reference_unit)
		return value;

	def set_reading_format(self, byte_format="LSB", bit_format="MSB"):

		self.byte_format = byte_format
		self.bit_format = bit_format

		if byte_format == "LSB":
			self.byte_range_values = self.LSByte
		elif byte_format == "MSB":
			self.byte_range_values = self.MSByte

		if bit_format == "LSB":
			self.bit_range_values = self.LSBit
		elif bit_format == "MSB":
			self.bit_range_values = self.MSBit

	def set_offset(self, offset):
		self.OFFSET = offset

	def set_reference_unit(self, reference_unit):
		self.REFERENCE_UNIT = reference_unit

	# HX711 datasheet states that setting the PDA_CLOCK pin on high for >60 microseconds would power off the chip.
	# I used 100 microseconds, just in case.
	# I've found it is good practice to reset the hx711 if it wasn't used for more than a few seconds.
	def power_down(self):
		GPIO.output(self.PD_SCK, False)
		GPIO.output(self.PD_SCK, True)
		time.sleep(0.0001)

	def power_up(self):
		GPIO.output(self.PD_SCK, False)
		time.sleep(0.0001)

	def reset(self):
		self.power_down()
		self.power_up()
