import numpy as np
import cv2
import os
import time
import win32gui
from PIL import ImageGrab
import math

from directkeys import PressKey, ReleaseKey, W, A, S, D, LCTRL, F2

# Movement = WASD
# Fire = LCTRL
# Reset = F2

class Node:
	def __init__(self, parent=None, position=None):
		self.parent = parent
		self.position = position

		self.g = 0
		self.h = 0
		self.f = 0

	def __eq__(self, other):
		return self.position == other.position

def main():
	#Get Maze Craze window
	print("Focusing Stella Window...")
	hwnd = getWindow()

	#make window active
	win32gui.SetForegroundWindow(hwnd)
	time.sleep(.5)
	print("Window found\n")

	#get maze
	print("Constructing Maze...")
	maze,printableMaze,start,end = getMaze(hwnd)
	print("Maze Constructed")
	print('\n'.join(map(''.join, printableMaze)))
	print("Start position found at: (%d,%d)"%(start[0],start[1]))
	print("End position found at: (%d,%d)\n"%(end[0],end[1]))

	#find path
	print("Finding path...")
	path = astar(maze, start, end)
	print("Path found")
	#print(path)
	print("")

	print("Applying path...")
	applyPath(path)
	print("Complete!")

	time.sleep(1.5)
	print("\n===========================================\n")
	PressKey(LCTRL)
	time.sleep(0.167)
	ReleaseKey(LCTRL)
	

	return


def getWindow():
	toplist, winlist = [], []
	def enum_cb(hwnd, results):
	    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
	win32gui.EnumWindows(enum_cb, toplist)

	mc = [(hwnd, title) for hwnd, title in winlist if 'maze craze (1980)' in title.lower()]
	# just grab the hwnd for first window matching maze craze
	mc = mc[0]
	hwnd = mc[0]

	return hwnd


def getMaze(hwnd):
	bbox = win32gui.GetWindowRect(hwnd)

	frame = np.array(ImageGrab.grab(bbox).crop((3,143,861,593)))
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	#print (frame.shape)
	cv2.imwrite("test.png",frame)
	
	#maze is 858x450
	#each section is roughly 22x18
	#thus, the resulting maze should be 39x25

	maze = [[0] * 39 for i in range(25)]
	printableMaze = [["0"] * 39 for i in range(25)]
	#print (np.array(maze).shape)

	x = 0
	y = 0

	start = (0,0)
	end = (0,0)

	while (y * 18 < 450):
		while (x * 22 < 858):
			section = frame[y*18:((y+1)*18), x*22:((x+1)*22)]
			avgInt = np.average(section)
			#print ("(%d,%d)\t%s\t%s"%(x+1,y+1,section.shape,avgInt))

			#if average is < 100, it is a wall
			#else it is an open space

			#start position is always in the 2nd column (x = 1)
			#if y = 1 and 80 < avgInt < 90, it is the start

			#if it is the last col (x = 38) and an open space is found
			#that is the goal

			if (avgInt < 100):
				if (x == 1 and (80 < avgInt and avgInt < 90)):
					start = (x,y)
					maze[y][x] = 0
					printableMaze[y][x] = "0"
				else:
					maze[y][x] = 1
					printableMaze[y][x] = "1"
			else:
				maze[y][x] = 0
				printableMaze[y][x] = "0"
				if (x == 38):
					end = (x,y)

			x += 1
		y += 1
		x = 0

	return maze,printableMaze,start,end

def astar(maze,start,end):

	openList = []
	closedList = []

	startNode = Node(None, start)
	startNode.g = 0
	startNode.h = 0
	startNode.f = 0

	endNode = Node(None, end)
	endNode.g = 0
	endNode.h = 0
	endNode.f = 0

	openList.append(startNode)

	while (len(openList) > 0):

		#simulate priority queue; find lowest f in openList:
		cur = openList[0]
		curInd = 0
		for ind, item in enumerate(openList):
			if (item.f < cur.f):
				cur = item
				curInd = ind
		openList.pop(curInd)
		closedList.append(cur)
		#print("cur position: (%d,%d)"%(cur.position[0],cur.position[1]))

		#check if goal, and if it is the goal then return the path
		if (cur == endNode):
			path = []
			pathNode = cur
			while (pathNode is not None):
				path.append(pathNode.position)
				pathNode = pathNode.parent
			return path[::-1]

		#generate current node's children
		#remember that you cannot move diagonal
		children = []
		directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
		for newPos in directions:
			#get child position:
			check = (cur.position[0] + newPos[0], cur.position[1] + newPos[1])

			#see if child is within maze's boundaries
			if ((check[0] > len(maze[0]) - 1) or (check[0] < 0) or (check[1] > len(maze) - 1) or (check[1] < 0)):
				continue

			#see if child is within a wall
			if (maze[check[1]][check[0]] == 1):
				continue

			#else, child is valid
			newNode = Node(cur, check)
			children.append(newNode)

		#check each new child for various parameters:
		for child in children:
			#if child in closed list, dont include it
			if (child in closedList):
				continue

			#create child's f, g, and h values
			child.g = cur.g + 1
			child.h = (((child.position[0] - endNode.position[0]) ** 2) + (child.position[1] - endNode.position[1]) ** 2)
			child.f = child.g + child.h

			#if child is in open list and it is farther from start, dont add it
			if (child in openList):
				continue

			openList.append(child)

	return None



def applyPath(path):
	i = 0

	frame = 0.0167
	t = 8
	wait = frame * t

	while (i < len(path) - 2):
		cur = path[i]
		step = path[i+2]
		#print("%d. step = (%d,%d)"%(i,step[0],step[1]))

		#up
		if (cur[1] > step[1] and cur[0] == step[0]):
			#print("U")
			PressKey(W)
			time.sleep(wait)
			ReleaseKey(W)

		#down
		if (cur[1] < step[1] and cur[0] == step[0]):
			#print("D")
			PressKey(S)
			time.sleep(wait)
			ReleaseKey(S)

		#left
		if (cur[0] > step[0] and cur[1] == step[1]):
			#print("L")
			PressKey(A)
			time.sleep(wait)
			ReleaseKey(A)

		#right
		if (cur[0] < step[0] and cur[1] == step[1]):
			#print("R")
			PressKey(D)
			time.sleep(wait)
			ReleaseKey(D)

		i += 2

	#one last R to leave the maze
	#print("R")
	PressKey(D)
	time.sleep(wait)
	ReleaseKey(D)

if __name__ == "__main__":
	main()