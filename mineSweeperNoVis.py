import random

toClear = 0
field = []
seenField = []
gameOver = False

def playMineField():
	layMines()
	startField()

def layMines():
	global toClear
	bombs = 0
	for row in range(0, 10):
		rowList = []
		seenRowList = []
		for column in range(0, 10):
			seenRowList.append(-1)
			if random.randint(1, 100) < 15:
				rowList.append(1)
				bombs += 1
			else:
				rowList.append(0)
				toClear += 1
		field.append(rowList)
		seenField.append(seenRowList)
	for row in range(0, 10):
		for column in range(0, 10):
			if findNeighborMines(row, column) == 0:
				toClear -= 1
				seenField[row][column] = 1
	print("Bombs: "+str(bombs))
	print("To clear: "+str(toClear))
	toClear -= 1

def startField():
	startEmpty = 0
	for rowNum, _ in enumerate(field):
		for columnNum, _ in enumerate(field):
			if findNeighborMines(rowNum, columnNum) == 0:
				seenField[rowNum][columnNum] = 0
				startEmpty += 1
	print("Started empty: "+str(startEmpty))

def findNeighborMines(row, column):
	mines = 0
	for y in range(-1,2):
		for x in range(-1,2):
			if row+y >= 0 and row+y <= 9 and column+x >= 0 and column+x <= 9:
				if field[row+y][column+x] == 1:
					mines += 1
	return mines

def uncover(x, y):
	global toClear
	row = x
	column = y
	print(toClear)
	if field[row][column] == 1:
		gameOver = True
	elif field[row][column] == 0 and seenField[row][column] == 0:
		minesBack = findNeighborMines(row, column)
		seenField[row][column] = minesBack
		toClear -= 1

playMineField()