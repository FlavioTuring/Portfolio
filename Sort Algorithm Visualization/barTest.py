from OpenGL.GL import*
import pyglet as pyg
import random
import copy


class BarCoreVariables:
    runningSimulation = False
    barN = 20
    minHeight = 20
    maxHeight = 300
    ms = 0.1
    sortMethod = 1


class BarCoreFunctions:
    @staticmethod
    def run():
        BarCoreVariables.runningSimulation = True

    @staticmethod
    def setBarN(userBarN):
        BarCoreVariables.barN = userBarN

    @staticmethod
    def setSort(userSort):
        BarCoreVariables.sortMethod = userSort

    @staticmethod
    def setMS(userMS):
        BarCoreVariables.ms = userMS

    @staticmethod
    def setMinHeight(userMinHeight):
        BarCoreVariables.minHeight = userMinHeight

    @staticmethod
    def setMaxHeight(userMaxHeight):
        BarCoreVariables.maxHeight = userMaxHeight


class BarCmdLog:
    cmdList = []

    def initStdLogBar(self):
        self.cmdList.append("run")
        self.cmdList.append("set_bar_n")
        self.cmdList.append("set_sort")
        self.cmdList.append("set_ms")
        self.cmdList.append("set_min_height")
        self.cmdList.append("set_max_height")

    def addCmd(self, newCmd):
        if isinstance(newCmd, str):
            self.cmdList.append(newCmd)


class ConsoleReader(BarCmdLog):
    def __init__(self):
        self.userInput = None
        self.function = None
        self.parameter = None
        self.gotError = False
        self.initStdLogBar()

    def error(self, errorType):
        self.gotError = True
        if errorType == "syntax":
            print("ERROR: Incorrect syntax")
        if errorType == "cmd":
            print("ERROR: Unknown command")

    def readCmd(self):
        self.function = None
        self.parameter = None
        self.gotError = False
        self.userInput = input()

    def checkCmd(self):
        openIndex = self.userInput.find("(")
        closeIndex = self.userInput.find(")")

        if (openIndex == -1) or (closeIndex == -1) or (closeIndex != len(self.userInput)-1):
            self.error("syntax")

        if not self.gotError:
            self.function = self.userInput[:openIndex]
            self.parameter = self.userInput[openIndex+1:closeIndex]

    def interpretCmd(self):
        if not self.gotError:
            cmdIndex = -1
            for i in range(len(self.cmdList)):
                if self.cmdList[i] == self.function:
                    cmdIndex = i

            if cmdIndex == -1:
                self.error("cmd")
            else:
                if cmdIndex == 0:
                    if self.parameter == "":
                        print("A")
                        BarCoreFunctions.run()
                    else:
                        self.error("syntax")

                elif cmdIndex == 1:
                    BarCoreFunctions.setBarN(int(self.parameter))
                    print(BarCoreVariables.barN)
                elif cmdIndex == 2:
                    BarCoreFunctions.setSort(int(self.parameter))
                elif cmdIndex == 3:
                    BarCoreFunctions.setMS(float(self.parameter))
                elif cmdIndex == 4:
                    BarCoreFunctions.setMinHeight(int(self.parameter))
                elif cmdIndex == 5:
                    BarCoreFunctions.setMaxHeight(int(self.parameter))


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Drawer:
    @staticmethod
    def comparisionBarDraw(barVectorRaw, barIndex):
        glClear(GL_COLOR_BUFFER_BIT)
        for i in range(len(barVectorRaw)):
            if i == barIndex:
                barVectorRaw[i].draw(drawMode="red")
            else:
                barVectorRaw[i].draw(drawMode="std")

    @staticmethod
    def swapBarDraw(barVectorRaw, barIndex1, barIndex2):
        glClear(GL_COLOR_BUFFER_BIT)
        for i in range(len(barVectorRaw)):
            if i == barIndex1:
                barVectorRaw[i].draw(drawMode="green")
            if i == barIndex2:
                barVectorRaw[i].draw(drawMode="green")
            if i != barIndex1 and i != barIndex2:
                barVectorRaw[i].draw(drawMode="std")

    @staticmethod
    def barVectorDraw(AnyBarVector):
        glClear(GL_COLOR_BUFFER_BIT)
        for i in range(len(AnyBarVector)):
            AnyBarVector[i].draw(drawMode="std")


class Log(Drawer):
    def __init__(self, barVector, barVectorRaw):
        self.barVector = barVector
        self.barVectorRaw = barVectorRaw
        self.actionList = []
        self.callIndex = 0

    def register(self, actionType, index1, index2=None):
        if actionType == "comparision":
            self.actionList.append(["comparision", index1])
        if actionType == "swap":
            self.actionList.append(["swap", index1, index2])

    def actionCall(self):
        if self.callIndex == len(self.actionList):
            endOfList = True
            self.barVectorDraw(self.barVectorRaw)
        else:
            endOfList = False

        if not endOfList:
            if self.actionList[self.callIndex][0] == "comparision":
                i = self.actionList[self.callIndex][1]
                self.comparisionBarDraw(self.barVectorRaw, i)

            if self.actionList[self.callIndex][0] == "swap":
                i = self.actionList[self.callIndex][1]
                j = self.actionList[self.callIndex][2]
                heightAux = self.barVectorRaw[i].height
                self.barVectorRaw[i].height = self.barVectorRaw[j].height
                self.barVectorRaw[j].height = heightAux
                self.swapBarDraw(self.barVectorRaw, i, j)

            self.callIndex += 1


class Bar:
    def __init__(self, leftBottomVertexX, leftBottomVertexY, length, height):
        self.height = height
        self.length = length

        self.leftBottomVertex = Point(leftBottomVertexX, leftBottomVertexY)
        self.rightBottomVertex = Point(self.leftBottomVertex.x + self.length, self.leftBottomVertex.y)

        self.leftTopVertex = Point(self.leftBottomVertex.x, self.leftBottomVertex.y + self.height)
        self.rightTopVertex = Point(self.rightBottomVertex.x, self.rightBottomVertex.y + self.height)

    def resetHeight(self):
        self.leftTopVertex = Point(self.leftBottomVertex.x, self.leftBottomVertex.y + self.height)
        self.rightTopVertex = Point(self.rightBottomVertex.x, self.rightBottomVertex.y + self.height)

    def draw(self, drawMode="std"):
        if drawMode == "std":
            self.resetHeight()
            glColor3f(1, 1, 1)

            glBegin(GL_QUADS)
            glVertex2f(self.rightTopVertex.x, self.rightTopVertex.y)
            glVertex2f(self.leftTopVertex.x, self.leftTopVertex.y)
            glVertex2f(self.leftBottomVertex.x, self.leftBottomVertex.y)
            glVertex2f(self.rightBottomVertex.x, self.rightBottomVertex.y)
            glEnd()

        if drawMode == "red":
            self.resetHeight()
            glColor3f(1, 0, 0)

            glBegin(GL_QUADS)
            glVertex2f(self.rightTopVertex.x, self.rightTopVertex.y)
            glVertex2f(self.leftTopVertex.x, self.leftTopVertex.y)
            glVertex2f(self.leftBottomVertex.x, self.leftBottomVertex.y)
            glVertex2f(self.rightBottomVertex.x, self.rightBottomVertex.y)
            glEnd()

        if drawMode == "green":
            self.resetHeight()
            glColor3f(0, 1, 0)

            glBegin(GL_QUADS)
            glVertex2f(self.rightTopVertex.x, self.rightTopVertex.y)
            glVertex2f(self.leftTopVertex.x, self.leftTopVertex.y)
            glVertex2f(self.leftBottomVertex.x, self.leftBottomVertex.y)
            glVertex2f(self.rightBottomVertex.x, self.rightBottomVertex.y)
            glEnd()


class BarsGenerator:
    def __init__(self, startPointX, startPointY, endPointX, endPointY, barsN):
        self.startPoint = Point(startPointX, startPointY)
        self.endPoint = Point(endPointX, endPointY)

        self.lineLength = self.endPoint.x - self.startPoint.x
        self.barLength = self.lineLength / barsN

        self.barVector = []
        for i in range(barsN):
            barX = self.startPoint.x + i*self.barLength
            barY = self.startPoint.y
            barHeight = random.randint(20, 300)
            bar = Bar(barX, barY, self.barLength, barHeight)
            self.barVector.append(bar)
        self.barVectorRaw = copy.deepcopy(self.barVector)

    def draw(self):
        for i in range(len(self.barVector)):
            self.barVector[i].draw()

    def drawRaw(self):
        for i in range(len(self.barVectorRaw)):
            self.barVectorRaw[i].draw()


class Sorter:

    def __init__(self, barVector):
        self.barVector = barVector
        self.searchIndexRange = len(barVector)
        self.callIndex = 0
        self.maxHeight = 0
        self.maxHeightIndex = 0
        self.sortingDone = False

    @staticmethod
    def mySort(barVector, log):
        searchIndexRange = len(barVector)
        sortingDone = False

        while not sortingDone:
            maxHeight = 0
            maxHeightIndex = 0

            for i in range(searchIndexRange):
                if barVector[i].height > maxHeight:
                    maxHeight = barVector[i].height
                    maxHeightIndex = i
                log.register("comparision", i)

            barVector[maxHeightIndex].height = barVector[searchIndexRange-1].height
            barVector[searchIndexRange-1].height = maxHeight
            log.register("swap", maxHeightIndex, searchIndexRange-1)
            searchIndexRange -= 1
            if searchIndexRange == 0:
                sortingDone = True

    def UpdateSort(self):

        if not self.sortingDone:
            print(self.callIndex)
            if self.barVector[self.callIndex].height > self.maxHeight:
                self.maxHeight = self.barVector[self.callIndex].height
                self.maxHeightIndex = self.callIndex
            self.barVector[self.callIndex].draw(drawMode="red")

            if self.callIndex == self.searchIndexRange:
                self.callIndex = 0
                self.barVector[self.maxHeightIndex].height = self.barVector[self.searchIndexRange-1].height
                self.barVector[self.searchIndexRange-1].height = self.maxHeight
                self.barVector[self.maxHeightIndex].draw(drawMode="green")
                self.barVector[self.searchIndexRange-1].draw(drawMode="green")

                self.searchIndexRange -= 1
                if self.searchIndexRange == 1:
                    self.sortingDone = True

            self.callIndex += 1

consoleReader = ConsoleReader()
while True:
    consoleReader.readCmd()
    consoleReader.checkCmd()
    consoleReader.interpretCmd()

    if BarCoreVariables.runningSimulation:
        window = pyg.window.Window(500, 500)

        bars = BarsGenerator(25, 100, 475, 100, BarCoreVariables.barN)
        barLog = Log(bars.barVector, bars.barVectorRaw)
        startSorting = False
        Sorter.mySort(bars.barVector, barLog)
        test = False

        @window.event
        def on_key_press(symbol, modifier):
            global startSorting
            if symbol == pyg.window.key.SPACE:
                startSorting = True
            global test
            if symbol == pyg.window.key.T:
                test = True


        def update(dt):
            global startSorting
            if startSorting:
                barLog.actionCall()
            else:
                bars.drawRaw()

            global test
            if test:
                testInput = input()
                test = False

        pyg.clock.schedule_interval(update, 0.1)

        # @window.event
        # def on_key_press(symbol, modifier):
        #     global startSorting
        #     if symbol == pyg.window.key.SPACE:
        #         startSorting = True
        #
        # @window.event
        # def on_draw():
        #     global startSorting
        #
        #     if startSorting:
        #         bars.draw()
        #     else:
        #         bars.drawRaw()
        pyg.app.run()
