import turtle
import random
import time
import math

class Player:
    x = 0
    y = -75
    reachedGoal = False
    dead = False
    path = []
    movesTaken = 0

    def __init__(self, goal, playerTurtle, colour):
        self.colour = colour
        self.vel = random.randint(75, 125)
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

    def move(self, step):
        #if not reached goal and not dead allow movement
        if not self.reachedGoal and not self.dead:
            self.playerTurtle.showturtle()
            self.playerTurtle.setheading(self.path[step])
            self.playerTurtle.forward(self.vel)
            self.x = self.playerTurtle.xcor()
            self.y = self.playerTurtle.ycor()
            self.movesTaken += 1

    def checkCollision(self):
        if self.y > 295 or self.y < -290 or self.x < -395 or self.x > 390:
            self.dead = True
            self.movesTaken = 50
        if self.goal.checkCollision(self):
            self.reachedGoal = True

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
        path = []
        for i in range(50):
            randomAngle = random.randint(0, 360)
            path.append(randomAngle)
        self.path = path

    def mutate(self):
        chance = 0.1
        for i in range(len(self.path)):
            self.path[i] += random.randint(-5, 5)

    def fitness(self):
        distanceFromGoal = (abs(275 - self.y)**2 + abs((0 - self.x)) ** 2)**(1/2)
        finish = 1 if self.reachedGoal else 0
        return (1/(distanceFromGoal**2) if distanceFromGoal != 0 else 1) + finish + (1/self.movesTaken)

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
        self.size = size
        self.winners = 0
        self.goal = goal
        for i in range(size):
            newplayer = Player(goal, turtle.Turtle(), "black")
            self.playerPopulation.append(newplayer)
        print("Population Initialized")
    
    def update(self):
        for step in range(50):
            turtle.tracer(0,0)
            for player in self.playerPopulation:
                player.move(step)
                player.checkCollision()
            turtle.update()

    def finished(self):
        for player in self.playerPopulation:
            dead = player.lost()
            won = player.won()
            if not (dead or won):
                return False
        return True

    def mutate(self):
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
            babyPaths = []
            for j in range(50):
                rand = random.randint(0, 1)
                if rand == 0:
                    babyPaths.append(parent1.path[j])
                elif rand == 1:
                    babyPaths.append(parent2.path[j])
                else:
                    print("You stupid")
            newPlayer = Player(self.goal, None, "green" if (parent1.won() or parent2.won()) else "black")
            newPlayer.path = babyPaths
            newPlayer.vel = parent1.vel if random.random() > 0.5 else parent2.vel
            newPlayer.mutate()
            newPopulation.append(newPlayer)
        self.playerPopulation = newPopulation

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
goal = Goal(0, 275)
goalTurtle.penup()
goalTurtle.hideturtle()
goalTurtle.color("red")
goalTurtle.shape("square")
goalTurtle.shapesize(1,1)
goalTurtle.goto(goal.getX(), goal.getY())
generation = Population(popSize, goal)

generationCount = 0
winners = 0

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
    genTurtle.write("Last gen winners:" + str(winners))
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
    generation.mutate()
    window.clearscreen()
    
        