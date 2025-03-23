
import copy
import os
import numpy as np
import itertools
from PIL import Image
A = 0  # A ... integer (Row ID)                    Example: 1
B = 1  # B ... IP address (Source IP)              Example: 192.168.248.159
C = 2  # C ... MAC address (Source MAC)            Example: 52:54:00:34:65:b2
D = 3  # D ... IP address (Destination IP)         Example: 192.168.248.10
E = 4  # E ... integer (Source Port)               Example: 443
F = 5  # F ... integer (Destination Port)          Example: 61374
G = 6  # G ... integer (Protocol Type)             Example: 17
H = 7  # H ... integer (Packet Size)               Example: 90
I = 8  # I ... integer (Payload Size)              Example: 40
J = 9  # J ... float (Auxiliary Data 1)            Example: 1.0
K = 10 # K ... float (Auxiliary Data 2)            Example: 1.0
L = 11 # L ... float (Auxiliary Data 3)            Example: 1.0
M = 12 # M ... float (Auxiliary Data 4)            Example: 700
N = 13 # N ... float (Auxiliary Data 5)            Example: 800
O = 14 # O ... float (Auxiliary Data 6)            Example: 900
P = 15 # P ... float (Auxiliary Data 7)            Example: 2400
Q = 16 # Q ... integer (Flag 1)                    Example: 1
R = 17 # R ... integer (Flag 2)                    Example: 5200


#==================================================================================================
def csv_to_2Dlist(input_file):
	result = []
	with open(input_file, "r") as file_obj:
			for line in file_obj:
					line = line.strip().split(",")
					result.append(line)
	return result
#==================================================================================================

#==================================================================================================
def convert_to_integer(content):
		result = []
		for line_list in content:
				try:
						temp = list_to_int(line_list)  # Process each line
						result.append(temp)         # Append the processed line
				except Exception as e:
						# Print the line and error details for debugging
						print(f"Error processing line: {line_list}")
						print(f"Error details: {e}")
		return result
#==================================================================================================

#==================================================================================================
def list_to_int(line_to_cypher):
		result = []
		temp = 0

		col_A = int(float(line_to_cypher[A]))
		col_B = line_to_cypher[B]
		col_C = line_to_cypher[C]
		col_D = line_to_cypher[D]
		col_E = int(float(line_to_cypher[E]))
		col_F = int(float(line_to_cypher[F]))
		col_G = int(float(line_to_cypher[G]))
		col_H = int(float(line_to_cypher[H]))
		col_I = int(float(line_to_cypher[I]))
		col_J = int(float(line_to_cypher[J]))
		col_K = int(float(line_to_cypher[K]))
		col_L = int(float(line_to_cypher[L]))
		col_M = int(float(line_to_cypher[M]))
		col_N = int(float(line_to_cypher[N]))
		col_O = int(float(line_to_cypher[O]))
		col_P = int(float(line_to_cypher[P]))
		col_Q = int(float(line_to_cypher[Q]))
		col_R = int(float(line_to_cypher[R]))
		return [col_A, col_B, col_C, col_D, col_E, col_F, col_G, col_H, col_I, col_J, col_K, col_L, col_M, col_N, col_O, col_P, col_Q, col_R]
#==================================================================================================

#==================================================================================================
def splitMac(source_out):
	for line in source_out:
		mac = copy.copy(line[2])
		mac = mac.replace(':', '')
		mac = [mac[i:i+6] for i in range(0, len(mac), 6)]
		line.remove(line[2])
		line.insert(2,mac[1])
		line.insert(2,mac[0])
	return source_out
#==================================================================================================

#==================================================================================================
def macaddres_to_int(source_out):
	source_out = copy.deepcopy(source_out)
	for line in source_out:
		line[2] = int(line[2], 16)
		line[3] = int(line[3], 16)
	return source_out
#==================================================================================================

#==================================================================================================
def splitIP(source_out):
	result = []
	for x in source_out:
		ip = x[1]
		ip = ip.split('.')
		
		fiq = ip[0]
		seq = ip[1]
		thq = ip[2]
		frq = ip[3]

		x.remove(x[1])

		x.insert(1, frq)
		x.insert(1, thq)
		x.insert(1, seq)
		x.insert(1, fiq)

		ip = x[7]
		ip = ip.split('.')


		fiq = ip[0]
		seq = ip[1]
		thq = ip[2]
		frq = ip[3]

		x.remove(x[7])

		x.insert(7, frq)
		x.insert(7, thq)
		x.insert(7, seq)
		x.insert(7, fiq)

		
		x = [int(y) for y in x]
		result.append(x)

	return result
#==================================================================================================

#==================================================================================================
def writeCSV(output_file, content):
	with open(output_file, "w") as file_obj:
		for line in content:
			for item in range(len(line)):
				val = str(line[item])
				file_obj.write(val)
				if item != len(line) - 1:
					file_obj.write(",")
			file_obj.write("\n")
#==================================================================================================

#==================================================================================================
def convertContentToRGB(source_out):
	def getRGBfromI(RGBint):
		blue =  RGBint & 255
		green = (RGBint >> 8) & 255
		red =   (RGBint >> 16) & 255
		return red, green, blue

	def convertLineToRGB(line):
		result = []
		for value in line:
			value = getRGBfromI(int(value))
			result.append(value)
		return result

	result = []
	temp = []
	temp_list = []
	for line_list in source_out:
		temp = convertLineToRGB(line_list)
		result.append(temp)
	return result
#==================================================================================================


#==================================================================================================
def imageCreatorByLine(line, image_id):
	array = np.zeros([150, 1, 3], dtype=np.uint8)
	new_line = tuple(itertools.chain.from_iterable(itertools.repeat(x, 6) for x in line)) # repeating lines 6 times since 25*6 = 150 pix

	for x in range(0, len(array)):
		for n in array[x]:
			l = list(new_line[x])			
			n[0] = l[0]
			n[1] = l[1]
			n[2] = l[2]

	xx = np.tile(array,(150,1))

	img = Image.fromarray(xx)
	img.save('data/'+str(image_id)+'.png')
#==================================================================================================


#==================================================================================================
def imagesCreatorForMultiLines(all_lines):
	
	for line in range(0,len(all_lines)):
		imageCreatorByLine(all_lines[line],line)	
#==================================================================================================



CSV_INPUT = "source_in.csv"
if not os.path.isdir("data"):
	os.mkdir("data")

user_data  = csv_to_2Dlist(CSV_INPUT)
user_data2 = convert_to_integer(user_data) 
user_data3 = splitMac(user_data2)
user_data4 = macaddres_to_int(user_data3)
user_data5 = splitIP(user_data4)
ready_to_plot = (convertContentToRGB(user_data5)) # convert to RGB
imagesCreatorForMultiLines(ready_to_plot)
