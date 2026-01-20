import turtle

screen = turtle.Screen()
screen.title("My Game")
screen.bgcolor("#030227")

player = turtle.Turtle()
player.shape("turtle")
player.color("white")
player.speed(0)

def move_up():
    player.setheading(90)
    player.forward(10)

screen.listen()
screen.onkey(move_up, "w")

turtle.done()