import turtle
import random
import time
import math

class Player:
    x = 0
    y = -75
    reachedGoal = False
    dead = False
    coefficient = []
    movesTaken = 1

    def __init__(self, goal, playerTurtle, colour):
        self.colour = colour
        self.vel = 50
        self.goal = goal
        self.playerTurtle = playerTurtle
        if playerTurtle:
            self.playerTurtle.speed(0)
            self.playerTurtle.penup()
            if colour == "black":
                self.playerTurtle.color("black")
            self.playerTurtle.shape("square")
            self.playerTurtle.shapesize(0.5,0.5)
            self.playerTurtle.hideturtle()
            self.playerTurtle.goto(0, -75)
            self.playerTurtle.showturtle()
        self.generateRandom()

    def move(self, moveX, moveY):
        #if not reached goal and not dead allow movement
        if not self.reachedGoal and not self.dead:
            self.playerTurtle.showturtle()
            #self.playerTurtle.setheading(self.coefficient[step])
            #self.playerTurtle.forward(self.vel)
            self.playerTurtle.goto((self.x + moveX), (self.y + moveY))
            self.x = self.playerTurtle.xcor()
            self.y = self.playerTurtle.ycor()
            self.movesTaken += 1

    def checkCollision(self):
        if self.y > 295 or self.y < -290 or self.x < -395 or self.x > 390:
            self.dead = True
            self.x = self.playerTurtle.xcor()
            self.y = self.playerTurtle.ycor()
            return True
        if self.goal.checkCollision(self):
            self.reachedGoal = True
            self.x = self.playerTurtle.xcor()
            self.y = self.playerTurtle.ycor()
            return True

    def won(self):
        return self.reachedGoal

    def lost(self):
        return self.dead
  
    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def reset(self):
        self.dead = False
        self.reachedGoal = False
        self.x = 0
        self.y = -75

    def generateRandom(self):
        # gradientX, gradientY, distanceX, distanceY
        coefficient = []
        for i in range(4):
            randomCoefficient = random.random()
            pon = random.random()
            if pon > 0.5:
                coefficient.append(randomCoefficient)
            else:
                coefficient.append(-randomCoefficient)
        self.coefficient = coefficient

    def mutate(self):
        chance = 0.05
        mutating = random.random()
        if mutating < chance:
            self.generateRandom()

    def calculateOutput(self):
        changeInY = (self.goal.y - self.y)
        changeInX = (self.goal.x - self.x)
        distanceToGoal = (abs(self.goal.y - self.y)**2 + abs((self.goal.x - self.x)) ** 2)**(1/2)
        hiddenLayer = self.coefficient
        moveX = (changeInX * hiddenLayer[0]) + (50 + distanceToGoal)* hiddenLayer[2]
        moveY = (changeInY * hiddenLayer[1]) + (50 + distanceToGoal)* hiddenLayer[3]
        self.move(moveX, moveY)

    def fitness(self):
        distanceFromGoal = (abs(self.goal.y - self.y)**2 + abs((self.goal.x - self.x)) ** 2)**(1/2)
        finish = 2 if self.reachedGoal else 0
        return (1/(distanceFromGoal**3) if distanceFromGoal != 0 else 1) + finish + (1/self.movesTaken**2)

class Goal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def checkCollision(self, player: Player):
        xCollision = player.getX() >= self.x - 11 and player.getX() <= self.x + 11
        yCollision = player.getY() <= self.y + 11 and player.getY() >= self.y - 11
        if xCollision and yCollision:
            return True
        return False
    
    def getX(self):
        return self.x

    def getY(self):
        return self.y
        
bias = 1

class Population:
    winners = 0
    playerPopulation = []
    def __init__(self, size, goal):
        startX = random.randint(-375, 375)
        startY = random.randint(-275, 275)
        self.size = size
        self.winners = 0
        self.goal = goal
        for i in range(size):
            newplayer = Player(goal, turtle.Turtle(), "black")
            newplayer.x = startX
            newplayer.y = startY
            self.playerPopulation.append(newplayer)
        print("Population Initialized")
    
    def update(self):
        finished = False
        moves = 0
        while not finished:
            moves += 1
            hasFinished = 0
            turtle.tracer(0,0)
            for player in self.playerPopulation:
                player.calculateOutput()
                if player.checkCollision():
                    hasFinished += 1
            turtle.update()
            if hasFinished == len(self.playerPopulation) or moves > 50:
                finished = True

    def finished(self):
        for player in self.playerPopulation:
            dead = player.lost()
            won = player.won()
            if not (dead or won):
                return False
        return True

    def mutate(self):
        startX = random.randint(-375, 375)
        startY = random.randint(-275, 275)
        global bias
        self.winners = 0
        fitnessTotal = int(sum([player.fitness() for player in self.playerPopulation]))
        newPopulation = []
        for player in self.playerPopulation:
            player.playerTurtle.clear()
            player.playerTurtle.hideturtle()
        for i in range(len(self.playerPopulation)):
            parent1 = self.getParent(fitnessTotal)
            parent2 = self.getParent(fitnessTotal)
            babycoefficients = []
            for j in range(4):
                rand = random.randint(0, 1)
                if rand == 0:
                    babycoefficients.append(parent1.coefficient[j])
                elif rand == 1:
                    babycoefficients.append(parent2.coefficient[j])
                else:
                    print("You stupid")
            newPlayer = Player(self.goal, None, "green" if (parent1.won() or parent2.won()) else "black")
            newPlayer.coefficient = babycoefficients
            newPlayer.vel = parent1.vel if random.random() > 0.5 else parent2.vel
            newPlayer.mutate()
            newPlayer.x = startX
            newPlayer.y = startY
            newPopulation.append(newPlayer)
        self.playerPopulation = newPopulation
        self.goal.x = random.randint(-375, 375)
        self.goal.y = random.randint(-275, 275)

    def getParent(self, fitnessTotal):
        randomFitness = random.randint(0, fitnessTotal)
        runningSum = 0
        for i in self.playerPopulation:
            fit = i.fitness()
            if runningSum <= randomFitness and runningSum + fit > randomFitness:
                #print(randomFitness, runningSum)
                return i
            runningSum += fit
        print("Broken")
        return Player(goal, turtle.Turtle(), "black")

window = turtle.Screen()
windowWidth = 800
windowHeight = 600
window.setup(windowWidth, windowHeight)
window.bgcolor("grey")

turtle.tracer(0, 0)

popSize = int(input("Population Size: "))
goalTurtle = turtle.Turtle()
goal = Goal(random.randint(-375, 375), random.randint(-275, 275))
goalTurtle.penup()
goalTurtle.hideturtle()
goalTurtle.color("red")
goalTurtle.shape("square")
goalTurtle.shapesize(1,1)
goalTurtle.goto(goal.getX(), goal.getY())
generation = Population(popSize, goal)

generationCount = 0
winners = 0

try:
    while True:
        window.bgcolor("grey")
        goalTurtle = turtle.Turtle()
        goalTurtle.penup()
        goalTurtle.hideturtle()
        goalTurtle.color("red")
        goalTurtle.shape("square")
        goalTurtle.shapesize(1,1)
        goalTurtle.goto(goal.getX(), goal.getY())
        goalTurtle.showturtle()
        turtle.tracer(0,0)
        genTurtle = turtle.Turtle()
        genTurtle.hideturtle()
        genTurtle.penup()
        genTurtle.goto(-375, 275)
        genTurtle.pendown()
        genTurtle.write("Generation "+str(generationCount))
        genTurtle.penup()
        genTurtle.goto(275, 275)
        genTurtle.pendown()
        genTurtle.write("Last gen winners:" + str(round(100*winners/popSize)) + "%")
        if generationCount > 0:
            for i in generation.playerPopulation:
                i.playerTurtle = turtle.Turtle()
                i.playerTurtle.speed(0)
                i.playerTurtle.penup()
                if i.colour == "green":
                    i.playerTurtle.color("green")
                else:
                    i.playerTurtle.color("black")
                i.playerTurtle.shape("square")
                i.playerTurtle.shapesize(0.5,0.5)
                i.playerTurtle.hideturtle()
                i.playerTurtle.goto(0, -75)
                i.playerTurtle.showturtle()
            turtle.update()

        turtle.tracer(0,0)
        generation.update()
        winners = 0
        for i in generation.playerPopulation:
            if i.won():
                winners += 1

        generationCount += 1
        with open("BestPath.txt", "w") as f:
            fittest = []
            fitness = 0
            for i in generation.playerPopulation:
                if i.fitness() > fitness:
                    fittest = i.coefficient
                    fitness = i.fitness()
            f.write(str(fittest[0]) + ", " + str(fittest[1]) + ", " + str(fittest[2]) + ", " + str(fittest[3]))
        generation.mutate()
        window.clear()
except Exception:
    with open("BestPath.txt", "w") as f:
        fittest = []
        fitness = 0
        for i in generation.playerPopulation:
            if i.fitness() > fitness:
                fittest = i.coefficient
                fitness = i.fitness()
        f.write(str(fittest[0]) + ", " + str(fittest[1]) + ", " + str(fittest[2]) + ", " + str(fittest[3]))
    
        
