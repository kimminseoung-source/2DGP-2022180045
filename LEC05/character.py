from pico2d import *


open_canvas(800, 600)

character = load_image('character.png')
grass = load_image('grass.png')



x=0
y=0
while x<100:
    
    x+=2
    
    clear_canvas()
    grass.draw(400, 30)
    character.draw(400+x, 300+y)
   
    update_canvas()
    delay(0.01)

while y<100:
    y+=2

    clear_canvas()
    grass.draw(400, 30)
    character.draw(400+x, 300+y)
       
    update_canvas()
    delay(0.01)


while x>-100:
     x-=3

     clear_canvas()
     grass.draw(400,30)
     character.draw(400+x, 300+y)

     update_canvas()
     delay(0.01)

while y>-100:
    y-=3

    clear_canvas()
    grass.draw(400, 30)
    character.draw(400+x, 300+y)
       
    update_canvas()
    delay(0.01)

delay(2)

close_canvas()

