class levelEditor(object):

    def __init__(self, window, display, margin, filename):
        """Initalizes instance of object"""
        self.margin = margin
        self.display = display
        self.window = window
        self.fpsClock = pygame.time.Clock()
        self.FPS = 30
        self.filename = filename
        self.init()
        self.levelEditorLoop()

    def init(self):
        """Initalizes essential variables"""
        self.initColors()
        self.initDisplay()
        self.initObjects()
        self.initModes()
        self.initLevelData()
        self.initEditorData()
        self.initOther()
        self.initBoard()
        self.initEnemies()
        self.initCoins()

    def initOther(self):
        self.levelEditor = True
        self.messageStarted = False
        self.oldMessage = None
        self.delay = 250
        self.x, self.y = None, None

    def initColors(self):
        self.black, self.white = (0, 0, 0), (255, 255, 255)
        self.grey = (150, 150, 150)
        self.green = (142, 239, 131)
        self.red = (255, 0, 0)
        self.blue = (0, 0, 255)

    def initDisplay(self):
        self.boardCellSize = 30
        self.objectCellSize = 15
        self.width = self.display.get_width()
        self.height = self.display.get_height()
        self.windowWidth = self.window.get_width()
        self.windowHeight = self.window.get_height()
        self.rows = self.height / self.boardCellSize
        self.cols = self.width / self.boardCellSize
        self.objectRows = self.height / self.objectCellSize
        self.objectCols = self.width / self.objectCellSize
        self.board = [[[False, False] for i in range(int(self.cols))]
                      for i in range(int(self.rows))]
        self.message = "Welcome to the World's Hardest Game Level Editor"
        self.myfont = pygame.font.SysFont("Arial", 30)
        self.player = None
        self.linEnemyGroup = []
        self.cEnemyGroup = []
        self.coinGroup = []

    def initObjects(self):
        coin((0, 0))
        player((0, 0))
        enemy((0, 0))

    def initModes(self):
        self.fillMode = False
        self.boardMode = False
        self.greenZoneMode = False
        self.playerMode = False
        self.linEnemyMode = False
        self.linEnemyComplete = False
        self.cEnemyMode = False
        self.cEnemyComplete = 0
        self.coinMode = False

    def initLevelData(self):
        self.data = {}
        readFileData(self.data).readFile(self.filename)
        self.playerLocation = copy.deepcopy(self.data["playerLocation"])
        self.player = (player(self.playerLocation)
                       if self.playerLocation != [] else None)
        self.playerSpeed = copy.deepcopy(self.data["playerSpeed"])
        self.linEnemyLocation = copy.deepcopy(self.data["linEnemyLocation"])
        self.linEnemyBounds = copy.deepcopy(self.data["linEnemyBounds"])
        self.linEnemySpeed = copy.deepcopy(self.data["linEnemySpeed"])
        self.cEnemyCenter = copy.deepcopy(self.data["cEnemyCenter"])
        self.cEnemyRadius = copy.deepcopy(self.data["cEnemyRadius"])
        self.cEnemyAngle = copy.deepcopy(self.data["cEnemyAngle"])
        self.cEnemySpeed = copy.deepcopy(self.data["cEnemySpeed"])
        self.greenZoneCoords = copy.deepcopy(self.data["greenZoneCoords"])
        self.greenZoneBools = []
        self.boardCoords = copy.deepcopy(self.data["boardCoords"])
        self.coinLocs = copy.deepcopy(self.data["coinLocs"])
        self.leftBorder = []
        self.rightBorder = []
        self.topBorder = []
        self.bottomBorder = []

    def initEditorData(self):
        self.linEnemyBoundsDraw = copy.deepcopy(self.data["linEnemyBoundsDraw"])
        self.cEnemyCount = int(copy.deepcopy(self.data["cEnemyCount"])[0])
        self.enemyCircles = copy.deepcopy(self.data["enemyCircles"])
        self.tempLinear = []
        self.tempLinearData = []

    def initBoard(self):
        for row in range(int(self.rows)):
            for col in range(int(self.cols)):
                xCoord = col * self.boardCellSize
                yCoord = row * self.boardCellSize
                if [xCoord, yCoord] in self.boardCoords:
                    self.board[row][col][0] = True
        for row in range(int(self.rows)):
            for col in range(int(self.cols)):
                xCoord = col * self.boardCellSize
                yCoord = row * self.boardCellSize
                if [xCoord, yCoord] in self.greenZoneCoords:
                    self.board[row][col][1] = True

    def initEnemies(self):
        length = enemy.image.get_rect()[3]
        for location in self.linEnemyLocation:
            enemySprite = pygame.sprite.GroupSingle(enemy(location))
            self.linEnemyGroup.append(enemySprite)
        for i in range(len(self.enemyCircles)):
            x0, y0 = self.enemyCircles[i][0]
            radius = self.enemyCircles[i][1][0]
            angle = self.cEnemyAngle[i]
            location = (x0, y0)
            enemySprite = pygame.sprite.GroupSingle(enemy(location))
            xPoint = x0 + math.cos(angle - math.pi / 2) * radius
            yPoint = y0 + math.sin(angle - math.pi / 2) * radius
            enemySprite = pygame.sprite.GroupSingle(enemy
                                                    ((xPoint - length / 2, yPoint - length / 2)))
            self.cEnemyGroup.append(enemySprite)

    def initCoins(self):
        for location in self.coinLocs:
            coinSprite = pygame.sprite.GroupSingle(coin(location))
            self.coinGroup.append(coinSprite)

    def levelEditorLoop(self):
        """Create Mode Game Loop"""
        self.run = True
        while self.run:
            self.clearCanvas()
            self.createBoard()
            if (self.coinMode or self.linEnemyMode or self.cEnemyMode or
                    self.playerMode): self.createObjectBoard()
            self.drawButtons()
            self.mousePress()
            for event in pygame.event.get():
                self.checkEvents(event)
            self.drawToolBar()
            self.drawLinearMotion()
            self.drawCircularMotion()
            self.drawMessage()
            self.drawObjects()
            pygame.display.flip()
            self.fpsClock.tick(self.FPS)

    def drawButtons(self):
        self.instButton = pygame.image.load("Images/instructionButton.png")
        self.backButton = pygame.image.load("Images/backButton.png")
        yCoord = self.margin / 2 - self.instButton.get_height() / 2
        self.shift = 15
        xCoord = self.shift
        self.window.blit(self.backButton, (xCoord, yCoord))
        xCoord = self.windowWidth - self.shift - self.instButton.get_width()
        self.window.blit(self.instButton, (xCoord, yCoord))

    def checkButtonPress(self, x, y):
        # determines if a button has been pressed
        if (y > self.margin / 2 - self.backButton.get_height() / 2 and
                y < self.margin / 2 + self.backButton.get_height() / 2):
            if (x > self.shift and x < self.backButton.get_width()
                    + self.shift):
                self.run = False
            elif (x > self.windowWidth - self.shift -
                  self.instButton.get_width() and
                  x < self.windowWidth - self.shift):
                instructions(self.window, self.display, self.margin)

    def checkEvents(self, event):
        # checks all events
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                self.fillMode = True
            elif event.key == pygame.K_u:
                self.objectUndo()
            elif event.key == pygame.K_c:
                self.clear()
            elif event.key == pygame.K_e:
                self.enemyMode = True
            elif event.key == pygame.K_d:
                self.debug()
            elif event.key == pygame.K_s:
                self.makeBoardData()
                if self.legalWrite():
                    self.findBorder()
                    self.createContent()
                    self.message = "Level Saved Successfully!"
            elif event.key == pygame.K_ESCAPE:
                self.deselect()
            elif event.key == pygame.K_BACKSPACE:
                self.run = False
            self.enemySpeed(event)

    def legalWrite(self):
        if self.checkBoard() and self.validModeChange():
            return True
        else:
            return False

    def checkBoard(self):
        # determines if the board is valid to be saved
        self.foundBoardCoords = []
        self.boardIsAllOneCount = 0
        if len(self.boardCoords) == 0:
            self.message = "There is no board to save!"
            return False
        elif (self.checkBoardIsAllOne(self.boardCoords[0][0],
                                      self.boardCoords[0][1]) == False):
            self.message = "The board must be completely connected!"
            return False
        elif self.checkGreenZone() == False:
            return False
        elif self.playerLocation == []:
            self.message = "There is no player!"
            return False
        return True

    def checkBoardIsAllOne(self, xCoord, yCoord):
        # determines if the board is all one
        # an altered version of floodfill from 15-112 notes
        if ((xCoord >= 0) and (xCoord < self.width) and (yCoord >= 0) and
                (yCoord < self.height) and ([xCoord, yCoord] in self.boardCoords)
                and [xCoord, yCoord] not in self.foundBoardCoords):
            self.foundBoardCoords.append([xCoord, yCoord])
            self.boardIsAllOneCount += 1
            self.checkBoardIsAllOne(xCoord, yCoord - self.boardCellSize)
            self.checkBoardIsAllOne(xCoord, yCoord + self.boardCellSize)
            self.checkBoardIsAllOne(xCoord - self.boardCellSize, yCoord)
            self.checkBoardIsAllOne(xCoord + self.boardCellSize, yCoord)
        return (self.boardIsAllOneCount == len(self.boardCoords))

    def checkGreenZone(self):
        # determines if the green zone is valid
        greenZoneCount = 0
        self.foundGreenZoneCoords = []
        while len(self.foundGreenZoneCoords) != len(self.greenZoneCoords):
            greenZoneCount += 1
            for location in self.greenZoneCoords:
                if location not in self.foundGreenZoneCoords:
                    x, y = location
                    self.countGreenZones(x, y)
                    break
        if (greenZoneCount == 0):
            self.message = "There is no green zone!"
            return False
        elif (greenZoneCount > 2):
            self.message = "There cannot be more than 2 green zones!"
            return False
        else:
            return True

    def countGreenZones(self, xCoord, yCoord):
        # altered version of floodfill from 15-112 notes
        # counts how many green zones there are
        if ((xCoord >= 0) and (xCoord < self.width) and (yCoord >= 0) and
                (yCoord < self.height) and ([xCoord, yCoord] in
                                            self.greenZoneCoords) and [xCoord, yCoord] not in
                self.foundGreenZoneCoords):
            self.foundGreenZoneCoords.append([xCoord, yCoord])
            self.countGreenZones(xCoord, yCoord - self.boardCellSize)
            self.countGreenZones(xCoord, yCoord + self.boardCellSize)
            self.countGreenZones(xCoord - self.boardCellSize, yCoord)
            self.countGreenZones(xCoord + self.boardCellSize, yCoord)

    def clearCanvas(self):
        # clears the canvas
        self.window.fill(self.white)
        self.window.blit(self.display, (self.margin, self.margin))
        self.display.fill(self.white)
        pygame.draw.rect(self.display, self.black, (0, 0,
                                                    self.width, self.height), 1)

    def enemySpeed(self, event):
        # adds enemySpeeds
        if self.linEnemyComplete:
            if event.key == pygame.K_1:
                self.refreshTempLinearData()
                self.addLinearEnemySpeed(1)
            elif event.key == pygame.K_2:
                self.refreshTempLinearData()
                self.addLinearEnemySpeed(2)
            elif event.key == pygame.K_3:
                self.refreshTempLinearData()
                self.addLinearEnemySpeed(3)
        elif self.cEnemyComplete == 2:
            if event.key == pygame.K_1:
                self.addCircularEnemySpeed(1)
            elif event.key == pygame.K_2:
                self.addCircularEnemySpeed(2)
            elif event.key == pygame.K_3:
                self.addCircularEnemySpeed(3)

    def refreshTempLinearData(self):
        # refreshes the temp data and stores it to the perm data
        self.linEnemyBounds.append(self.tempLinearData)
        self.linEnemyBoundsDraw.append(self.tempLinear)
        self.linEnemyComplete = False
        self.tempLinear = []
        self.tempLinearData = []

    def objectUndo(self):
        # for right click undo of objects
        if self.linEnemyMode:
            self.linearMotionUndo()
        elif self.cEnemyMode:
            self.circularMotionUndo()
        elif self.coinMode:
            self.coinUndo()

    def circularMotionUndo(self):
        # undoing circular motion
        if len(self.cEnemyCenter) > 0 and self.cEnemyComplete == 0:
            self.cEnemyCenter.pop()
            self.cEnemyRadius.pop()
            self.cEnemyAngle.pop()
            self.cEnemySpeed.pop()
            self.enemyCircles.pop()
            self.cEnemyGroup.pop()
            self.cEnemyCount -= 1
        elif len(self.cEnemyCenter) > 0 and self.cEnemyComplete == 1:
            if len(self.cEnemyRadius) == len(self.cEnemySpeed):
                self.cEnemyCenter.pop()
            self.cEnemyComplete -= 1
        elif self.cEnemyComplete == 2:
            self.cEnemyGroup.pop()
            self.cEnemyRadius.pop()
            self.cEnemyAngle.pop()
            self.enemyCircles.pop()
            self.cEnemyCount -= 1
            self.cEnemyComplete -= 1

    def linearMotionUndo(self):
        # undoin linear motion
        if len(self.linEnemyBounds) > 0 and self.linEnemyComplete == False:
            self.linEnemyLocation.pop()
            self.linEnemyBounds.pop()
            self.linEnemyBoundsDraw.pop()
            self.linEnemyGroup.pop()
            self.linEnemySpeed.pop()
        elif (len(self.tempLinear) > 1 and self.linEnemyComplete):
            self.tempLinear.pop()
            self.tempLinearData.pop()
        elif self.linEnemyComplete:
            self.linEnemyLocation.pop()
            self.linEnemyGroup.pop()
            self.tempLinear.pop()
            self.tempLinearData.pop()
            self.linEnemyComplete = False

    def coinUndo(self):
        if len(self.coinGroup) > 0:
            self.coinGroup.pop()
        if len(self.coinLocs) > 0:
            self.coinLocs.pop()

    def drawObjects(self):
        if self.player != None:
            self.display.blit(self.player.image, self.player.rect)
        for sprite in self.linEnemyGroup:
            sprite.draw(self.display)
        for sprite in self.cEnemyGroup:
            sprite.draw(self.display)
        for sprite in self.coinGroup:
            sprite.draw(self.display)

    def drawLinearMotion(self):
        thickness = 5
        radius = 7
        if len(self.tempLinear) > 1:
            pygame.draw.lines(self.display, self.red, False,
                              self.tempLinear, thickness)
            pygame.draw.line(self.display, self.blue,
                             self.tempLinear[0], self.tempLinear[1], thickness)
            for i in range(1, len(self.tempLinear)):
                pygame.draw.circle(self.display, self.black,
                                   self.tempLinear[i], radius)
        if len(self.linEnemyBoundsDraw) > 0:
            for i in range(len(self.linEnemyBoundsDraw)):
                if len(self.linEnemyBoundsDraw[i]) > 1:
                    pygame.draw.lines(self.display, self.red, True,
                                      self.linEnemyBoundsDraw[i], thickness)
            for i in range(len(self.linEnemyBoundsDraw)):
                if len(self.linEnemyBoundsDraw[i]) > 1:
                    pygame.draw.line(self.display, self.blue,
                                     self.linEnemyBoundsDraw[i][0],
                                     self.linEnemyBoundsDraw[i][1], thickness)
                for j in range(1, len(self.linEnemyBounds[i])):
                    centerX, centerY = self.linEnemyBoundsDraw[i][j]
                    center = (int(centerX), int(centerY))
                    pygame.draw.circle(self.display, self.black,
                                       center, radius)

    def drawCircularMotion(self):
        thickness = 5
        if len(self.enemyCircles) > 0:
            for i in range(len(self.enemyCircles)):
                radius = int(round(self.enemyCircles[i][1][0]))
                centerX, centerY = self.enemyCircles[i][0]
                center = (int(centerX), int(centerY))
                pygame.draw.circle(self.display, self.red,
                                   center, radius, thickness)
        if len(self.cEnemyCenter) > 0:
            for i in range(len(self.cEnemyCenter)):
                pygame.draw.circle(self.display, self.black,
                                   self.cEnemyCenter[i], thickness)

    def deselect(self):
        self.boardMode = False
        self.greenZoneMode = False
        self.playerMode = False
        self.linEnemyMode = False
        self.cEnemyMode = False
        self.coinMode = False

    def addLinearEnemySpeed(self, key):
        points = self.linEnemyBounds[-1]
        distance = self.findDistance(points)
        speedConstant = 100
        speed = distance / speedConstant * key * 2
        self.linEnemySpeed.append(speed)
        self.linEnemyComplete = False

    def addCircularEnemySpeed(self, key):
        radius = self.cEnemyRadius[-1]
        speedConstant = 100
        speed = radius / speedConstant * key * 2
        self.cEnemySpeed.append(speed)
        self.cEnemyComplete = 0

    def findDistance(self, points):
        # finds the smallest distance
        smallestDistance = 10000  # arbitrary large value
        length = len(points)
        for i in range(len(points)):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % length]
            distance = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            if distance < smallestDistance:
                smallestDistance = distance
        return smallestDistance

    def drawToolBar(self):
        # draws the tool bar
        boardFig = (board((self.windowWidth / 7
                           , self.windowHeight - self.margin / 2 - self.boardCellSize / 2),
                          (self.boardCellSize, self.boardCellSize), self.grey))
        greenZoneFig = (greenZone((self.windowWidth * 2 / 7
                                   , self.windowHeight - self.margin / 2 - self.boardCellSize / 2),
                                  (self.boardCellSize, self.boardCellSize)))
        playerFig = player((self.windowWidth * 3 / 7
                            , self.windowHeight - self.margin / 2 - player.image.get_rect()[3] / 2))
        self.window.blit(boardFig.image, boardFig.rect)
        enemyLinearFig = enemy((self.windowWidth * 4 / 7
                                , self.windowHeight - self.margin / 2 - enemy.image.get_rect()[3] / 2))
        enemycFig = enemy((self.windowWidth * 5 / 7
                           , self.windowHeight - self.margin / 2 - enemy.image.get_rect()[3] / 2))
        coinFig = coin((self.windowWidth * 6 / 7
                        , self.windowHeight - self.margin / 2 - coin.image.get_rect()[3] / 2))
        self.window.blit(boardFig.image, boardFig.rect)
        self.window.blit(greenZoneFig.image, greenZoneFig.rect)
        self.window.blit(playerFig.image, playerFig.rect)
        self.window.blit(enemyLinearFig.image, enemyLinearFig.rect)
        self.window.blit(enemycFig.image, enemycFig.rect)
        self.window.blit(coinFig.image, coinFig.rect)
        self.drawLabels()

    def drawLabels(self):
        # draws the enemy labels
        linearMessage = "Linear"
        circularMessage = "Circular"
        font = pygame.font.SysFont("Arial", 14)
        linearText = font.render(linearMessage, 0, self.black)
        circularText = font.render(circularMessage, 0, self.black)
        linearX, linearY = (linearText.get_width() / 2,
                            linearText.get_height() / 2)
        circularX, circularY = (circularText.get_width() / 2,
                                circularText.get_height() / 2)
        linearCoord = (self.width * 4.43 / 7, self.windowHeight - self.margin * 7 / 8)
        circularCoord = (self.width * 5.52 / 7,
                         self.windowHeight - self.margin * 7 / 8)
        self.window.blit(circularText, circularCoord)
        self.window.blit(linearText, linearCoord)

    def drawMessage(self):
        # draws a message if
        maxTime = 4
        if (self.messageStarted == False and self.message != None or
                self.message != self.oldMessage):
            self.oldMessage = self.message
            self.messageTimer = time.time()
            self.messageStarted = True
        elif time.time() - self.messageTimer > maxTime:
            self.messageStarted = False
            self.message = None
        if self.message != None:
            message = self.myfont.render(self.message, 1, (0, 0, 0))
            adjustX = message.get_width() / 2
            adjustY = message.get_height() / 2
            coord = (self.windowWidth / 2 - adjustX, self.margin / 2 - adjustY)
            self.window.blit(message, coord)

    def clear(self):
        # clears all the data
        self.board = [[[False, False] for i in range(int(self.cols))]
                      for i in range(int(self.rows))]
        self.playerLocation = []
        self.playerSpeed = []
        self.linEnemyLocation = []
        self.linEnemyBounds = []
        self.linEnemySpeed = []
        self.cEnemyCenter = []
        self.cEnemyRadius = []
        self.cEnemyAngle = []
        self.cEnemySpeed = []
        self.greenZoneCoords = []
        self.boardCoords = []
        self.clear2()

    def clear2(self):
        # clears all the data
        self.coinLocs = []
        self.boardCoords = []
        self.leftBorder = []
        self.rightBorder = []
        self.topBorder = []
        self.bottomBorder = []
        self.tempLinear = []
        self.tempLinearData = []
        self.player = None
        self.linEnemyBoundsDraw = []
        self.cEnemyCount = 0
        self.enemyCircles = []
        self.cEnemyGroup = []
        self.coinGroup = []
        self.linEnemyGroup = []

    def mousePress(self):
        # if left, make cell True, if right, make cell False
        if pygame.mouse.get_pressed() == (1, 0, 0):
            self.x, self.y = pygame.mouse.get_pos()
            if self.cEnemyComplete == 2:
                self.message = "Press 1,2, or 3 to indicate speed"
            self.checkButtonPress(self.x, self.y)
            if not (self.checkToolBarClick()):
                if self.legalClick():
                    if self.boardMode:
                        self.createBoardPiece("LEFT")
                    elif self.greenZoneMode:
                        self.createGreenZone("LEFT")
                    elif self.playerMode:
                        self.createPlayer()
                    elif self.linEnemyMode:
                        self.createLinearEnemy()
                    elif self.cEnemyMode:
                        self.createCircularEnemy()
                    elif self.coinMode:
                        self.createCoin()
        elif pygame.mouse.get_pressed() == (0, 0, 1):
            self.x, self.y = pygame.mouse.get_pos()
            if self.boardMode:
                self.createBoardPiece("RIGHT")
            elif self.greenZoneMode:
                self.createGreenZone("RIGHT")
            else:
                self.objectUndo()
                pygame.time.delay(self.delay)

    def checkToolBarClick(self):
        # determines if the toolbar has been clicked
        if (self.y > self.windowHeight - self.margin / 2 -
                self.boardCellSize / 2 and self.y < self.windowHeight -
                self.margin / 2 + self.boardCellSize / 2):
            self.checkToolBarClick1()
            self.checkToolBarClick2()
        return False

    def checkToolBarClick1(self):
        # determines if the toolbar has been clicked
        if (self.x > self.windowWidth / 7 and
                self.x < self.windowWidth / 7 + self.boardCellSize):
            if self.validModeChange():
                self.message = "Click a cell to place a board piece!"
                self.initModes()
                self.boardMode = True
                pygame.time.delay(self.delay)
                return True
        elif (self.x > self.windowWidth * 2 / 7 and
              self.x < self.windowWidth * 2 / 7 + self.boardCellSize):
            if self.validModeChange():
                self.message = "Click a cell to place a green zone!"
                self.initModes()
                self.greenZoneMode = True
                pygame.time.delay(self.delay)
                return True
        elif (self.x > self.windowWidth * 3 / 7 and
              self.x < self.windowWidth * 3 / 7 + self.boardCellSize):
            if self.validModeChange():
                self.message = "Click a node to place the player"
                self.message += " starting location!"
                self.initModes()
                self.playerMode = True
                pygame.time.delay(self.delay)
                return True

    def checkToolBarClick2(self):
        # determines if the tool bar has been clicked
        if (self.x > self.windowWidth * 4 / 7 and
                self.x < self.windowWidth * 4 / 7 + self.boardCellSize):
            if self.validModeChange():
                self.message = "Click a node to begin placing linear motion!"
                self.initModes()
                self.linEnemyMode = True
                pygame.time.delay(self.delay)
            return True
        elif (self.x > self.windowWidth * 5 / 7 and
              self.x < self.windowWidth * 5 / 7 + self.boardCellSize):
            if self.validModeChange():
                self.message = "Click a node to begin placing circular motion!"
                self.initModes()
                self.cEnemyMode = True
                pygame.time.delay(self.delay)
                return True
        elif (self.x > self.windowWidth * 6 / 7 and
              self.x < self.windowWidth * 6 / 7 + self.boardCellSize):
            if self.validModeChange():
                self.message = "Click a node to place a coin!"
                self.initModes()
                self.coinMode = True
                pygame.time.delay(self.delay)
                return True

    def validModeChange(self):
        # determines if the enemies have finished being created
        if self.cEnemyComplete != 0:
            self.message = "Finish creating circular Enemy!"
            return False
        elif self.linEnemyComplete:
            self.message = "Finish creating linear Enemy!"
            return False
        return True

    def legalClick(self):
        # ensures click is in bounds
        if ((self.x < self.margin) or (self.x > self.width + self.margin)
                or (self.y < self.margin) or (self.y > self.height + self.margin)):
            return False
        return True

    def createBoardPiece(self, click):
        # Finds the cell and sets it True if left click, false if right click
        row = int((self.y - self.margin) / self.boardCellSize)
        col = int((self.x - self.margin) / self.boardCellSize)
        if row >= self.rows or col >= self.cols: return
        if self.fillMode:
            self.fillBoard(row, col, 0)
            self.fillMode = False
            pygame.time.delay(self.delay)
        elif click == "LEFT":
            self.board[row][col][0] = True
        else:
            self.board[row][col][0] = False

    def createGreenZone(self, click):
        # Finds the cell and sets it True if left click, false if right click
        row = int((self.y - self.margin) / self.boardCellSize)
        col = int((self.x - self.margin) / self.boardCellSize)
        if row >= self.rows or col >= self.cols: return
        if self.fillMode:
            self.fillBoard(row, col, 1)
            self.fillMode = False
            pygame.time.delay(self.delay)
        elif click == "LEFT":
            self.board[row][col][1] = True
            self.board[row][col][0] = True
        else:
            self.board[row][col][1] = False

    def findNode(self):
        # determines the nearest node
        x, y = self.x, self.y
        row = int(round((x - self.margin) / float(self.objectCellSize)))
        col = int(round((y - self.margin) / float(self.objectCellSize)))
        x = row * self.objectCellSize + self.margin
        y = col * self.objectCellSize + self.margin
        self.x = x
        self.y = y

    def createPlayer(self):
        # creates the player
        self.findNode()
        length = player.image.get_rect()[3]
        # top right
        row = int((self.y - self.margin - length / 2) / self.boardCellSize)
        col = int((self.x - self.margin - length / 2) / self.boardCellSize)
        # bottom left
        row1 = int((self.y - self.margin + length / 2) / self.boardCellSize)
        col1 = int((self.x - self.margin + length / 2) / self.boardCellSize)
        # player is centered at mouse click
        if (self.board[row][col][0] and self.board[row1][col1][0] and
                self.board[row][col][1] and self.board[row1][col1][1]):
            self.playerLocation = [int(self.x - self.margin - length / 2)
                , int(self.y - self.margin - length / 2)]
            self.player = player(self.playerLocation)
        pygame.time.delay(self.delay)

    def createLinearEnemy(self):
        # creates a linear enemy. When self.linEnemyComplete is False, that
        # means nothing has yet been created. When it becomes True, it means
        # the initial point has been placed, and the path can be continued to
        # be drawn. Entering a speed ends the path at any time.
        self.findNode()
        length = enemy.image.get_rect()[3]
        if self.linEnemyComplete:
            enemyLocation = [self.x - self.margin - length / 2,
                             self.y - self.margin - length / 2]
            if enemyLocation not in self.tempLinearData:
                self.tempLinearData.append(enemyLocation)
            enemyLocation = [self.x - self.margin, self.y - self.margin]
            if enemyLocation not in self.tempLinear:
                self.tempLinear.append(enemyLocation)
        else:
            enemyLocation = [self.x - self.margin - length / 2,
                             self.y - self.margin - length / 2]
            enemySprite = pygame.sprite.GroupSingle(enemy(enemyLocation))
            self.linEnemyGroup.append(enemySprite)
            enemyLocation = [self.x - self.margin - length / 2,
                             self.y - self.margin - length / 2]
            self.linEnemyLocation.append(enemyLocation)
            self.tempLinearData.append(enemyLocation)
            enemyLocation = [self.x - self.margin, self.y - self.margin]
            self.tempLinear.append(enemyLocation)
            self.message = "When finished creating a path"
            self.message += " press 1,2, or 3 to indicate speed"
            self.linEnemyComplete = True
        pygame.time.delay(self.delay)

    def createCircularEnemy(self):
        # creates a circular enemy through the use of three different phases
        # of self.cEnemyComplete. 0 indicates that nothing has been created
        # yet, 1 indicates that a center has been created, 2 indicates that
        # the full path has been created and just the speed input is needed
        length = enemy.image.get_rect()[3]
        self.findNode()
        if self.cEnemyComplete == 1:
            # appends all the data to various different lists
            x1, y1 = self.x - self.margin, self.y - self.margin
            x0, y0 = self.cEnemyCenter[self.cEnemyCount]
            radius = (((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
            angle = (math.atan2(y1 - y0 + radius, x1 - x0) * 2)
            xPoint = x0 + math.cos(angle - math.pi / 2) * radius
            yPoint = y0 + math.sin(angle - math.pi / 2) * radius
            enemySprite = pygame.sprite.GroupSingle(enemy
                                                    ((xPoint - length / 2, yPoint - length / 2)))
            if radius > 0:
                self.cEnemyGroup.append(enemySprite)
                self.cEnemyRadius.append(radius)
                self.cEnemyAngle.append(angle)
                self.enemyCircles.append([[x0, y0], [radius]])
                self.cEnemyCount += 1
                self.cEnemyComplete = 2
        elif self.cEnemyComplete == 0:
            enemyLocation = [self.x - self.margin,
                             self.y - self.margin]
            self.cEnemyCenter.append(enemyLocation)
            self.cEnemyComplete = 1
        pygame.time.delay(self.delay)

    def createCoin(self):
        # creates the coins
        self.findNode()
        length = coin.image.get_rect()[3]
        # top right
        row = int((self.y - self.margin - length / 2) / self.boardCellSize)
        col = int((self.x - self.margin - length / 2) / self.boardCellSize)
        # bottom left
        row1 = int((self.y - self.margin + length / 2) / self.boardCellSize)
        col1 = int((self.x - self.margin + length / 2) / self.boardCellSize)
        # coin is centered at mouse click
        coinLoc = ([self.x - self.margin - length / 2
            , self.y - self.margin - length / 2])
        if (coinLoc not in self.coinLocs and
                self.board[row][col][0] and self.board[row1][col1][0]):
            self.coinLocs.append(coinLoc)
            coinSprite = pygame.sprite.GroupSingle(coin(coinLoc))
            self.coinGroup.append(coinSprite)

    def fillBoard(self, row, col, boardType):
        # fills the board using a modified version of floodFill which was
        # taken from the 15-112 recursion course notes
        if ((row >= 0) and (row < self.rows) and (col >= 0) and
                (col < self.cols) and (self.board[row][col][boardType] == False)):
            self.board[row][col][boardType] = True
            self.fillBoard(row, col - 1, boardType)
            self.fillBoard(row, col + 1, boardType)
            self.fillBoard(row - 1, col, boardType)
            self.fillBoard(row + 1, col, boardType)

    def createBoard(self):
        # creates the grid
        for row in range(int(self.rows)):
            for col in range(int(self.cols)):
                self.createCell(row, col)

    def createCell(self, row, col):
        # creates the cell, if it it is True, color it in
        self.xPos = col * self.boardCellSize
        self.yPos = row * self.boardCellSize
        rect = (self.xPos, self.yPos, self.boardCellSize, self.boardCellSize)
        if self.boardMode or self.greenZoneMode:
            pygame.draw.rect(self.display, self.black, rect, 2)
        if self.board[row][col][0]:
            pygame.draw.rect(self.display, self.grey, rect)
        if self.board[row][col][1]:
            pygame.draw.rect(self.display, self.green, rect)

    def createObjectBoard(self):
        # creates the board for objects
        for row in range(int(self.objectRows)):
            for col in range(int(self.objectCols)):
                self.createObjectCell(row, col)

    def createObjectCell(self, row, col):
        # creates the cell, if it is True, color it in grey
        self.xPos = col * self.objectCellSize
        self.yPos = row * self.objectCellSize
        rect = (self.xPos, self.yPos, self.objectCellSize, self.boardCellSize)
        pygame.draw.rect(self.display, self.black, rect, 1)

    def makeBoardData(self):
        # adds all board coordinate data to self.boardCoords
        self.boardCoords = []
        self.greenZoneCoords = []
        for row in range(int(self.rows)):
            for col in range(int(self.cols)):
                xPos = col * self.boardCellSize
                yPos = row * self.boardCellSize
                if self.board[row][col][0] == True:
                    self.boardCoords.append([xPos, yPos])
                if self.board[row][col][1] == True:
                    self.greenZoneCoords.append([xPos, yPos])

    def findBorder(self):
        # finds the border of the board
        for row in range(int(self.rows)):
            for col in range(int(self.cols)):
                if self.board[row][col][0] == True:
                    self.findBorderInDirection(row, col)

    def findBorderInDirection(self, row, col):
        # finds all the border points of the board
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for direction in directions:
            drow, dcol = direction
            bordRow = drow + row
            bordCol = dcol + col
            xPos = bordCol * self.boardCellSize
            yPos = bordRow * self.boardCellSize
            newXPos = xPos
            newYPos = yPos
            # creates different lists of the different sides of the border
            if self.board[bordRow][bordCol][0] == False:
                if direction == (-1, 0):
                    self.topBorder.append((newXPos, newYPos))
                    newXPos += self.boardCellSize
                    newYPos += self.boardCellSize
                elif direction == (0, 1):
                    self.rightBorder.append((newXPos, newYPos))
                    newYPos += self.boardCellSize
                elif direction == (0, -1):
                    self.leftBorder.append((newXPos, newYPos))
                    newXPos += self.boardCellSize
                else:
                    self.bottomBorder.append((newXPos, newYPos))

    def createContent(self):
        # writes all the necessary data to a textfile
        a = self.playerLocation
        b = self.playerSpeed
        c = self.linEnemyLocation
        d = self.linEnemyBounds
        e = self.linEnemySpeed
        f = self.cEnemyCenter
        g = self.cEnemyRadius
        h = self.cEnemyAngle
        i = self.cEnemySpeed
        j = self.greenZoneCoords
        k = self.boardCoords
        l = self.coinLocs
        m = self.leftBorder
        n = self.rightBorder
        o = self.topBorder
        p = self.bottomBorder
        q = self.linEnemyBoundsDraw
        r = self.cEnemyCount
        s = self.enemyCircles
        allData = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s]
        contents = ""
        for data in allData:
            contents += str(data)
            contents += "\n"
        self.writeFile(self.filename, contents)

        # taken from 15-112 class notes on IO

    def writeFile(self, filename, contents, mode="wt"):
        # wt stands for "write text"
        fout = None
        fout = open(filename, mode)
        fout.write(contents)
        fout.close()