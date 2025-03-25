'''
     ___  ____   ____ ____ 
    / _ \/ ___| / ___|  _ \ 
   | | | \___ \| |   | |_) |
   | |_| |___) | |___|  _ < 
    \___/|____/ \____|_| \_\
'''
# BTW let me tell me tell you that whenever a new OSCR version is made 
#,it is made from scratch (the older versions aren't used)
#importing important modules (make sure you have it)
import time
import sys
import pygame
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import os
import random

#initial declerations
console = Console()

#reading the txt file
file_name = str(input("Please enter the file name: "))
with open(file_name,'r') as file:
	raw_program = file.readlines()

#removing the useless parts
program = []
program = [line.strip() for line in raw_program if line.strip()]

def display_state():
	table = Table(title="+---------------------< CPU State >------------------+", style ="bold bright_green",show_lines=True)
	
	table.add_column("DATA NAME", style="grey70", justify="left")
	table.add_column("DATA", style="khaki1", justify="right")
	
	table.add_row("Program" , str(file_name))
	table.add_row("Counter Count", str(cpu.count))
	table.add_row("Current Command", str(cpu.command))
	table.add_row("Registers", str(cpu.register))
	list1 = []
	list1.append(str(cpu.changed_ram))
	list1.append(str(cpu.ram[int(cpu.changed_ram)]))
	table.add_row("Last changed ram" , str(list1))
	table.add_row("Stack", str(cpu.stack))
	table.add_row("Flag" , str(cpu.flag_register))
	
	console.print(table)

def draw_line(x1, y1, x2, y2):
    """Draws a line using Bresenham's algorithm."""
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx, sy = (1 if x1 < x2 else -1), (1 if y1 < y2 else -1)
    err = dx - dy
    
    while True:
        if 0 <= x1 < 256 and 0 <= y1 < 256:
            cpu.pixels[y1][x1] = 1
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

class main():
	
	'''helper functions'''
	
	@staticmethod
	#creating a new memory made easy!
	def create_memory(size):
		memory = [0] * size
		return memory
	
	@staticmethod
	def counter(count):
		count += 1
		return count
	
	@staticmethod
	def delete_last_line():
		x = 100
		while x != 0:
			sys.stdout.write("\x1b[1A")  # cursor up one line
			sys.stdout.write("\x1b[2K")  # delete the last line
			x -= 1




#this class is made for main cpu variables & functions
class cpu():
	
	'''CPU FUNCTIONS'''
	raw_mode = input("What mode do you want?\n>>>")
	mode = raw_mode.lower()
	tick = 0
	count = 0
	SCREEN_SIZE = 128
	PIXEL_SIZE = 3     # Scale factor for visibility
	WINDOW_SIZE = SCREEN_SIZE * PIXEL_SIZE
	# Pixel buffer (2D array)
	pixels = [[0] * 256 for _ in range(256)]
	
	changed_ram = 0
	register = main.create_memory(16)
	ram = main.create_memory(65536)
	program = []
	command = ' '
	flag_register = ' '
	stack = []
	
	#COMPILING THE FILE BEFORE RUNNING THE PROGRAM
	@staticmethod
	def command_assigner(program):
		cpu.program = [line.strip().split(',') for line in program if line.strip()]
	
	@staticmethod
	def update_variable():
		real_command = []
		
		for x in range(len(cpu.command)):
			if cpu.command[x].startswith('$'):
				add = int(cpu.command[x].strip("$"))
				cmd = cpu.ram[add]
				real_command.append(cmd)
			else:
				real_command.append(cpu.command[x])
		
		cpu.command = real_command

	
	#Instructions dictionary
	instructions = {
	"JMP"   : lambda: cpu.jmp(),				#JMP
	"STR"   : lambda: cpu.mov(),				#STR
	"OUT"   : lambda: cpu.out(), 				#OUT
	"ADD"   : lambda: cpu.add(),	 			#ADD
	"SUB"   : lambda: cpu.sub(),	 			#SUB
	'DEL'   : lambda: cpu.delay(),	 		#DEL
	"MOV"   : lambda: cpu.change(),  			#MOV
	"NOP"   : lambda: cpu.nop(),	 			#NOP
	"MUL"   : lambda: cpu.mul(),	 			#MUL
	"DIV"   : lambda: cpu.div(),				#DIV
	"AND"   : lambda: cpu.and1(),	 		#ADD
	"OR"    : lambda: cpu.or1(),			#OR
	"XOR"   : lambda: cpu.xor(), 			#XOR
	"JMPZ"  : lambda: cpu.jmpz(),				#JMPZ
	"JMPN"  : lambda: cpu.jmpn(),				#JMPN
	"JMPO"  : lambda: cpu.jmpo(),				#JMPO
	"JMPZ-N": lambda: cpu.jmpzn(),				#JMPZ-N
	"PUSH"  : lambda: cpu.push(),				#PUSH
	"POP"   : lambda: cpu.pop(),				#POP
	"INC"   : lambda: cpu.inc(),				#INC
	"DEC"   : lambda: cpu.dec(),				#DEC
	"LSH"   : lambda: cpu.lsh(),				#LSH
	"RSH"   : lambda: cpu.rsh(),				#RSH
	"INP"   : lambda: cpu.get_input(),   	#INP
	"CALL"  : lambda: cpu.call_function(),	#CALL
	"RET"   : lambda: cpu.return1(),			#RET
	"DRAW"  : lambda: cpu.draw_pixel(),		#DRAW
	"CLS"   : lambda: cpu.cls(),				#CLS
	"UPD"   : lambda: cpu.refresh(),			#UPD
	"SCR"   : lambda: cpu.initial(),			#SCR
	"CHN"   : lambda: cpu.change_program(),  #CHN
	"CLR"   : lambda: cpu.clear(),			#CLR
	"RAND"  : lambda: cpu.rand(),				#RAND
	"KEY"   : lambda: cpu.check_keypress(),
	"HALT   ": None 								#HALT
	}
	
	#DIFFERENT FUNCTIONS FOR THE CPU Dictionary
	
	#----JMP Functions----
	
	#JMP FUNCTION
	def jmp():
		cpu.count = int(cpu.command[1]) - 1
	
	#JMPZ FUNCTION (CONDITIONAL JUMP)
	def jmpz():
		if cpu.flag_register == 'Z':
			cpu.count = int(cpu.command[1]) - 1
	
	#JMPN FUNCTION (CONDITIONAL JUMP)
	def jmpn():
		if cpu.flag_register == 'N':
			cpu.count = int(cpu.command[1]) - 1
	
	#JMPZ-N FUNCTION (CONDITIONAL JUMP)
	def jmpzn():
		if cpu.flag_register != 'Z' or cpu.flag_register != 'N':
			cpu.count = int(cpu.command[1]) - 1
		
	
	#JMPO FUNCTION (CONDITIONAL JUMP)
	def jmpo():
		if cpu.flag_register == 'O':
			cpu.count = int(cpu.command[1]) - 1

	#ADDING ELEMENTS TO REGISTER/RAM
	def mov():
		if cpu.command[1] == 'REG':
			cpu.register[int(cpu.command[2])] = cpu.command[3]
		
		elif cpu.command[1] == 'RAM':
			cpu.ram[int(cpu.command[2])] = cpu.command[3]
			cpu.changed_ram = int(cpu.command[2])
	
	#OUTPUTING THE DATA IN THE MEMORY
	def out():
		if cpu.command[1] == 'REG':
			print( cpu.register[int(cpu.command[2])])
		
		elif cpu.command[1] == 'RAM':
			print("[" , cpu.command[2] , "]" , ">>>" , cpu.ram[int(cpu.command[2])])
	
	
	#Acceptig data from the user
	def get_input():
		inp = input(">>>")
		if inp == '':
			inp = 0
		else:
			if cpu.command[1] == 'REG':
				cpu.register[int(cpu.command[2])] = inp
			elif cpu.command[1] == 'RAM':
				cpu.ram[int(cpu.command[2])] = inp
	
	#ADD function
	def add():
		if cpu.command[1] == 'REG':
			cpu.register[int(cpu.command[4])] = int(cpu.register[int(cpu.command[2])]) + int(cpu.register[int(cpu.command[3])])
			answer = cpu.register[int(cpu.command[4])]
			cpu.flag_check(answer)
		elif cpu.command[1] == 'RAM':
			cpu.ram[int(cpu.command[4])] = int(cpu.ram[int(cpu.command[2])]) + int(cpu.ram[int(cpu.command[3])])
			answer = cpu.ram[int(cpu.command[4])]
			cpu.flag_check(answer)
	
	#SUB function
	def sub():
		if cpu.command[1] == 'REG':
			cpu.register[int(cpu.command[4])] = int(cpu.register[int(cpu.command[2])]) - int(cpu.register[int(cpu.command[3])])
			answer = cpu.register[int(cpu.command[4])]
			cpu.flag_check(answer)
		elif cpu.command[1] == 'RAM':
			cpu.ram[int(cpu.command[4])] = int(cpu.ram[int(cpu.command[2])]) - int(cpu.ram[int(cpu.command[3])])
			answer = cpu.ram[int(cpu.command[4])]
			cpu.flag_check(answer)
	
	#MUL function
	def mul():
		if cpu.command[1] == 'REG':
			cpu.register[int(cpu.command[4])] = float(cpu.register[int(cpu.command[2])]) * float(cpu.register[int(cpu.command[3])])
			answer = cpu.register[int(cpu.command[4])]
			cpu.flag_check(answer)
		elif cpu.command[1] == 'RAM':
			cpu.ram[int(cpu.command[4])] = float(cpu.ram[int(cpu.command[2])]) * float(cpu.ram[int(cpu.command[3])])
			answer = cpu.ram[int(cpu.command[4])]
			cpu.flag_check(answer)
	
	#DIV function
	def div():
		if cpu.command[1] == 'REG':
			cpu.register[int(cpu.command[4])] = float(cpu.register[int(cpu.command[2])]) // float(cpu.register[int(cpu.command[3])])
			answer = cpu.register[int(cpu.command[4])]
			cpu.flag_check(answer)
		elif cpu.command[1] == 'RAM':
			cpu.ram[int(cpu.command[4])] = float(cpu.ram[int(cpu.command[2])]) // float(cpu.ram[int(cpu.command[3])])
			answer = cpu.ram[int(cpu.command[4])]
			cpu.flag_check(answer)
	
	def inc():
		if cpu.command[1] == 'REG':
			cpu.register[int(cpu.command[2])] = int(cpu.register[int(cpu.command[2])]) + 1
			cpu.flag_check(cpu.register[int(cpu.command[2])])
		elif cpu.command[1] == 'RAM':
			cpu.ram[int(cpu.command[2])] = 1 + int(cpu.ram[int(cpu.command[2])])
			cpu.flag_check(cpu.ram[int(cpu.command[2])])
	
	def dec():
		if cpu.command[1] == 'REG':
			cpu.register[int(cpu.command[2])] = int(cpu.register[int(cpu.command[2])]) - 1
			cpu.flag_check(cpu.register[int(cpu.command[2])])
		elif cpu.command[1] == 'RAM':
			cpu.ram[int(cpu.command[2])] = int(cpu.ram[int(cpu.command[2])]) - 1
			cpu.flag_check(cpu.ram[int(cpu.command[2])])
	
	def lsh():
		if cpu.command[1] == 'REG':
			cpu.register[int(cpu.command[2])] = int(cpu.register[int(cpu.command[2])]) << int(cpu.command[3])
			cpu.flag_check(cpu.register[int(cpu.command[2])])
		elif cpu.command[1] == 'RAM':
			cpu.ram[int(cpu.command[2])] = int(cpu.ram[int(cpu.command[2])]) << int(cpu.command[3])
			cpu.flag_check(cpu.ram[int(cpu.command[2])])
	
	def rsh():
		if cpu.command[1] == 'REG':
			cpu.register[int(cpu.command[2])] = int(cpu.register[int(cpu.command[2])]) >> int(cpu.command[3])
			cpu.flag_check(cpu.register[int(cpu.command[2])])
		elif cpu.command[1] == 'RAM':
			cpu.ram[int(cpu.command[2])] = int(cpu.ram[int(cpu.command[2])]) >> int(cpu.command[3])
			cpu.flag_check(cpu.ram[int(cpu.command[2])])
	
	def and1():
		cpu.register[int(cpu.command[3])] = int(cpu.register[int(cpu.command[1])]) & int(cpu.register[int(cpu.command[2])])
	
	def or1():
		cpu.register[int(cpu.command[3])] = int(cpu.register[int(cpu.command[1])]) | int(cpu.register[int(cpu.command[2])])
	
	def xor():
		cpu.register[int(cpu.command[3])] = int(cpu.register[int(cpu.command[1])]) ^ int(cpu.register[int(cpu.command[2])])
	
	#Flags for ALU Functions
	def flag_check(answer):
		if answer == 0:
			cpu.flag_register = 'Z'
		
		elif answer < 0:
			cpu.flag_register = 'N'
		
		elif answer >= 65535:
			cpu.flag_register = 'O'
		
		else:
			cpu.flag_register = 'N/A'
	
	#Delay function
	def delay():
		time.sleep(float(cpu.command[1]))
	
	#MEMROY interchange
	def change():
		if cpu.command[1] == 'REG':
			cpu.register[int(cpu.command[2])] = cpu.ram[int(cpu.command[3])]
			
		if cpu.command[1] == 'RAM':
			cpu.ram[int(cpu.command[2])] = cpu.register[int(cpu.command[3])]
	
	#NO OPERATION Function
	def nop():
		pass
	
	#stack functions
	#Push
	def push():
		if cpu.command[1] == 'REG':
			cpu.stack.append(cpu.register[int(cpu.command[2])])
		elif cpu.command[1] == 'RAM':
			cpu.stack.append(cpu.ram[int(cpu.command[2])])
	
	#POP function
	def pop():
		if cpu.command[1] == 'REG':
			cpu.register[int(cpu.command[2])] = cpu.stack.pop()
		elif cpu.command[1] == 'RAM':
			cpu.ram[int(cpu.command[2])] = cpu.stack.pop()
	
	#Calling a function
	def call_function():
		cpu.stack.append(cpu.count)
		cpu.count = int(cpu.command[1]) - 1
	
	#returning to the last saved count
	def return1():
		cpu.count = cpu.stack.pop()
	
	#DRAWING ON SCREEN
	def draw_pixel():
		cmd_len = len(cpu.command)
		
		if cmd_len == 4:
			x = int(cpu.command[1])
			y = int(cpu.command[2])
			s = int(cpu.command[3])
			if 0 <= x < cpu.SCREEN_SIZE and 0 <= y < cpu.SCREEN_SIZE:
				cpu.pixels[y][x] = s
		
		elif cmd_len == 5:  # DRAW X1 Y1 X2 Y2 (line)
			x1, y1, x2, y2 = map(int, cpu.command[1:])
			draw_line(x1, y1, x2, y2)
	
	#CLEARING THE SCREEN
	def cls():
		cpu.pixels = [[0] * cpu.SCREEN_SIZE for _ in range(cpu.SCREEN_SIZE)]  # Clear pixel data
		cpu.refresh()  # Ensure screen updates
	
	#REFRESH THE SCREEN FOR BEST PERFORMANCE
	def refresh():
		screen.fill((0, 0, 0))  # Clear with black
		
		for y in range(cpu.SCREEN_SIZE):
			for x in range(cpu.SCREEN_SIZE):
				if cpu.pixels[y][x] == 1:
					pygame.draw.rect(screen, (255, 255, 255), 
										(x * cpu.PIXEL_SIZE, y * cpu.PIXEL_SIZE, cpu.PIXEL_SIZE, cpu.PIXEL_SIZE))
		
		pygame.display.flip()
	
	def initial():
		#pygame initialization
		pygame.init()
		global screen
		screen = pygame.display.set_mode((cpu.WINDOW_SIZE, cpu.WINDOW_SIZE))
		pygame.display.set_caption("OSCR-16 Display")
		clock = pygame.time.Clock()
	
	def change_program():
		#reading the txt file
		file_name = cpu.register[int(cpu.command[1])]
		with open(file_name,'r') as file:
			raw_program = file.readlines()
		
		#removing the useless parts
		program = []
		program = [line.strip() for line in raw_program if line.strip()]
		cpu.command_assigner(raw_program)
		cpu.count = 0
		cpu.tick = 0
		cpu.command = ''
	
	def clear():
		os.system("clear")
	
	def rand():
		cpu.register[int(cpu.command[1])] = random.randint(int(cpu.command[2]),int(cpu.command[3]))
	
	def check_keypress():
		pygame.init()
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				cpu.register[int(cpu.command[1])] = event.key
				print(f"Key Pressed: {pygame.key.name(event.key)} (Code: {event.key})")

	

#+--------< MAIN LOOP >-----------+

cpu.command_assigner(raw_program)

while True:
	
	memory = [["Counter count" , cpu.count],["Current command" , cpu.command],["Register" , cpu.register],["Stack" , cpu.stack]]
	headers = ['DATA NAME' , 'DATA']
	
	#Ui
	if cpu.mode == 'i' or cpu.mode == 'interactive' or cpu.mode == 'c' or cpu.mode == 'custom':
		display_state()
		main.delete_last_line()
	
	cpu.count = main.counter(cpu.count)
	cpu.command = cpu.program[cpu.count]
	cpu.update_variable()
	
	if cpu.command[0] == "HLT":
		break
	else:
		if cpu.command[0] in cpu.instructions:
			cpu.instructions[cpu.command[0]]()
		else:
			print(f"Unknown instruction: {cpu.command}")

print("====The program Ended!====")
