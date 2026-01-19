import turtle 
screen = turtle.Screen()
w = turtle.color()
i = turtle.Turtle()
i.speed(100)
def move_up():
    i.forward(10)
    i.setheading(90)
screen.onkey(move_up, "w")
screen.listen() # This makes the "w" key work
screen.bgcolor("#030227")
turtle.done()

