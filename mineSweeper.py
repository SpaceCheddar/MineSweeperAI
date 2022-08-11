import tkinter
import random
from keras.models import load_model
import numpy as np

toClear = 0
field = []
seenField = []
gameOver = False
window = tkinter.Tk()
model = None
model_file = None

def playMineField(_model_file = None):
    global model
    global model_file
    model_file = _model_file
    if model_file != None:
        model = load_model(model_file)
        print("Loaded model.")
    layMines()
    window.configure(bg = "lightgrey")
    startField(window)
    print(seenField)
    window.mainloop()

def layMines():
	global toClear
	bombs = 0
	for row in range(0, 10):
		rowList = []
		seenRowList = []
		for column in range(0, 10):
			seenRowList.append(-2)
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
				seenField[row][column] = 0
	print("Bombs: "+str(bombs))
	print("To clear: "+str(toClear))
	toClear -= 1

def startField(window):
    global toClear
    startEmpty = 0
    for rowNum, rowList in enumerate(field):
        for columnNum, columnValue in enumerate(field):
            if findNeighborMines(rowNum, columnNum) == 0:
                square = tkinter.Label(window, text = "    ", bg = "saddlebrown")
                seenField[rowNum][columnNum] = 0
                startEmpty += 1
                for y in range(-1, 2):
                    for x in range(-1, 2):
                        if rowNum+y > -1 and rowNum+y < 10 and columnNum+x > -1 and columnNum+x < 10:
                            seenField[rowNum+y][columnNum+x] = findNeighborMines(rowNum+y, columnNum+x)
                            startEmpty += 1
                            toClear -= 1
            elif random.randint(1,100) < 25:
                square = tkinter.Label(window, text = "    ", bg = "darkgreen")
            elif random.randint(1, 100) > 75:
                square = tkinter.Label(window, text = "    ", bg = "seagreen")
            else:
                square = tkinter.Label(window, text = "    ", bg = "green")
            square.grid(row = rowNum, column = columnNum)
            square.bind("<Button-1>", onClick)
            square.bind("<Button-3>", flagSquare)
    
    children = window.winfo_children()
    for row in range(0, 10):
        for column in range(0, 10):
            if seenField[row][column] != 0 and seenField[row][column] != -2:
                for i in range(len(children)):
                    if int(children[i].grid_info()["row"]) == row and int(children[i].grid_info()["column"]) == column:
                        children[i].config(bg = "saddlebrown")
                        textColors = ["lime","greenyellow","yellow","gold","orange","orangered","red","red"]
                        children[i].config(text = " "+str(seenField[row][column])+" ")
                        children[i].config(fg = textColors[seenField[row][column]])

    indeterminate = tkinter.Label(window, text = "indeterminate", bg = "grey")
    indeterminate.grid(row = 0, column = 11)
    indeterminate.bind("<Button-1>", giveIndeterminate)
    print("Started empty: "+str(startEmpty))

def findNeighborMines(row, column):
	mines = 0
	for y in range(-1,2):
		for x in range(-1,2):
			if row+y >= 0 and row+y <= 9 and column+x >= 0 and column+x <= 9:
				if field[row+y][column+x] == 1:
					mines += 1
	return mines

def onClick(event):
    global toClear
    global window
    global gameOver
    if gameOver:
        window.quit()
    if toClear == 0:
        print("All mines cleared.")
        window.quit()
    square = event.widget
    row = int(square.grid_info()["row"])
    column = int(square.grid_info()["column"])
    currentText = square.cget("text")
    if field[row][column] == 1:
        square.config(bg = "red")
        print("Hit a mine.")
        gameOver = True
    elif currentText == "    ":
        square.config(bg = "saddlebrown")
        textColors = ["lime","greenyellow","yellow","gold","orange","orangered","red","red"]
        minesBack = findNeighborMines(row, column)
        if minesBack > 0:
            square.config(text = " "+str(minesBack)+" ")
            square.config(fg = textColors[minesBack])
        if field[row][column] == 0 and seenField[row][column] == -2:
            seenField[row][column] = minesBack
            print(str(toClear)+" left")
            toClear -= 1
            #notify the network this is correct
            if model != None:
                inputData = []
                inputData.append(seenField)
                inputData[0][row][column] = -2

                oneHotClick = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
                oneHotClick[0][row] = 1
                oneHotClick[0][column+10] = 1
                model.fit(inputData, oneHotClick, epochs = 2)
                model.save(model_file)

                inputData[0][row][column] = findNeighborMines(row, column)
                output = model.predict(inputData)
                output = output.tolist()
                if output[0][20] > 0.8:
                    #suggestSquare(0, 11) #would create an out of index error probably
                    pass
                else:
                    suggestSquare(output[0].index(max(output[0][0:9])), output[0].index(max(output[0][10:19]))-10)
            else:
                suggestSquare(random.randint(0, 9), random.randint(0, 9))

def flagSquare(event):
    square = event.widget
    row = int(square.grid_info()["row"])
    column = int(square.grid_info()["column"])
    currentText = square.cget("text")
    square.config(bg = "steelblue")

def giveIndeterminate(event):
    print("Identified as indeterminate, process terminated.")
    global gameOver
    gameOver = True #notify the network there is no absolute solution

def suggestSquare(row, column):
    global window
    print("Suggested "+str(column)+", "+str(row))
    children = window.winfo_children()
    for i in range(len(window.children)):
        if children[i].cget("bg") == "hotpink":
            if seenField[int(children[i].grid_info()["row"])][int(children[i].grid_info()["column"])] == -2:
                children[i].config(bg = "green")
            else:
                children[i].config(bg = "saddlebrown")
        if int(children[i].grid_info()["row"]) == row and int(children[i].grid_info()["column"]) == column:
            children[i].config(bg = "hotpink")
            if seenField[row][column] == 0:
                children[i].config(text = " 0 ")
                children[i].config(fg = "saddlebrown")

#Clicking a valid suggested square is good for learning
#playMineField()