import pygame,sys, math, random
from pygame.locals import QUIT

screen_x=1000
screen_y=800

tick=0
pygame.init()
screen=pygame.display.set_mode((screen_x,screen_y))
pygame.display.set_caption('C_o_c testing')


transparent_p1_cooldown_bg=pygame.Surface((200,screen_y))
transparent_p1_cooldown_bg.set_alpha(96)
transparent_p1_cooldown_bg.fill((255,192,129))

transparent_p2_cooldown_bg=pygame.Surface((200,screen_y))
transparent_p2_cooldown_bg.set_alpha(96)
transparent_p2_cooldown_bg.fill((192,255,192))

p1_points_bar=0.0
p2_points_bar=0.0
p1_regen_speed=1.0
p2_regen_speed=1.0

p1_deck_options=[1,2,3,4,5,6,7,8] #legend has it that two of the same card cannot be found on the same options table
p2_deck_options=[1,2,3,4,5,6,7,8] #Hugo is a reasonably reliable source 

#ids are as follows
bg_img=pygame.image.load("background_area_piskel.png").convert_alpha()

red_victory_png=pygame.image.load("red_victory_piskel.png").convert_alpha()
green_victory_png=pygame.image.load("green_victory_piskel.png").convert_alpha()

tile_images=[0, #the tower has no icon because it can't be deployed
             pygame.image.load("generic_fellow_piskel.png").convert_alpha(),
             pygame.image.load("giant_piskel.png").convert_alpha(),
             pygame.image.load("speedy_boi_piskel.png").convert_alpha(),
             pygame.image.load("wizard_icon_piskel.png").convert_alpha(),
             pygame.image.load("angry_tree_fellow_piskel.png").convert_alpha(),
             pygame.image.load("distraction_bot_piskel.png").convert_alpha(),
             pygame.image.load("archer_piskel.png").convert_alpha(),
             pygame.image.load("regen_piskel.png").convert_alpha(),]

#2d list, [hp,speed,atk_speed,range,behaviour_id,attack_id,size,cost]
unit_data=[[1000,0,120,300,0,0,64,-1], #0:tower
           [100,1,60,32,1,0,24,2],#1:generic fellow
           [300,0.4,120,100,2,3,36,4], #2:big boi
           [100,2,6,128,1,2,20,3], #3: speedy fellow
           [200,0.8,15,150,1,4,40,5], #4: wizard
           [500,0.1,360,300,1,5,48,5], #5: ent
           [400,2,1200,100,1,6,16,1], #6: distractor
           [400,1.5,20,250,1,7,24,2], #7: archer
           [1,1,1,1,1,1,1,7], #8: regen upgrade
           []
           ] 

#2d list: [dmg,abs_speed,size]
projectile_data=[[10,40,16], #0:fire or smthn idk
                 [20,10,18], #1:strong proj idk 
                 [15,20,8], #2:bullet ig
                 [50,5,40], #3: big boi attack (very technical vocabulary)
                 [40,10,16], #4: magic thing ig
                 [200,5,60], #5: tree?
                 [20,20,32], #6: laser
                 [16,10,20], #7: arrow
                 []]

class projectile:
    def __init__(self,x,y,x_vel,y_vel,id,force):
        self.x=x
        self.y=y
        self.x_vel=x_vel
        self.y_vel=y_vel
        self.id=id
        self.force=force

        self.dmg=projectile_data[self.id][0]
        self.abs_speed=projectile_data[self.id][1]
        self.size=projectile_data[self.id][2]

        self.rect=pygame.Rect(self.x,self.y,self.size,self.size)



    def move(self): #collisions handled elsewhere
        self.x+=self.x_vel
        self.y+=self.y_vel

    def draw(self):
        pygame.draw.rect(screen,((255,96,255),(255,255,96))[int(self.force)],self.rect)

    def update(self):
        self.move()
        self.rect=pygame.Rect(self.x,self.y,self.size,self.size)


class unit:
    def __init__(self,x,y,id,force):
        self.x=x
        self.y=y
        self.id=id
        self.force=force #bool, True is player, False is bot
        self.cooldown=0 #starts at 0, but is reset later
        self.target_pos=[self.x,self.y]
        self.init_draw_tick_offset=random.randint(0,10) #used so things arent in sync (if i can be asked to draw pngs for them all)
        

        self.hp=unit_data[self.id][0] #just done for convenience
        self.speed=unit_data[self.id][1]
        self.atk_speed=unit_data[self.id][2] #tick cooldown for attacking
        self.range=unit_data[self.id][3]
        self.behaviour_id=unit_data[self.id][4]
        self.attack_id=unit_data[self.id][5]
        self.size=unit_data[self.id][6]

        self.rect=pygame.Rect(self.x,self.y,self.size,self.size)
        self.start_hp=self.hp

    def target(self,container_name):
        init_target=[self.x,self.y]
        if self.behaviour_id==-1: #"erm ackshually use a switch statement" SHUT UP
            init_target=[self.x,self.y]#-1 is for towers, as they get first priority

        if self.behaviour_id==0:
            init_target=[self.x,self.y]
        if self.behaviour_id==1:

            self.closest_unit_dist=99999 #high number for debug purposes
            self.closest_unit_index=-1
            if (not self.force) in [i.force for i in container_name.units]: #only does this when enemies exist (enemy.force = opposite of self.force)
                for e in range(0,len(container_name.units)):
                    if container_name.units[e].force!=self.force:
                        if math.dist((self.x,self.y),(container_name.units[e].x,container_name.units[e].y))<self.closest_unit_dist:
                            self.closest_unit_dist=math.dist((self.x,self.y),(container_name.units[e].x,container_name.units[e].y))
                            self.closest_unit_index=e

            if self.closest_unit_index!=-1 and ((self.y>=400 and container_name.units[self.closest_unit_index].y>=400) or (self.y<400 and container_name.units[self.closest_unit_index].y<400)): #straight path towards enemy if on same side
                    init_target=[container_name.units[self.closest_unit_index].x,container_name.units[self.closest_unit_index].y] #enemy pos
            elif (self.force and self.y>360) or (not self.force and self.y<440): #bridge in between iirc (360<->440 y), so goes to bridge
                if self.x<=screen_x//2:
                    
                    if self.force:
                        init_target=[330,400] #goes to closest bridge
                    else:
                        init_target=[330,400]
                else:
                    if self.force:
                        init_target=[630,400]
                    else:
                        init_target=[630,400]

        if self.behaviour_id==2: #beelines to towers
            # if (not self.force) in [i.force for i in container_name.units]:
            #     for e in range(0,len(container_name.units)):
            #         if self.force!=container_name.units[e].force and container_name.units[e].behaviour_id==0:
            #             init_target=[container_name.units[e].x,container_name.units[e].y]
            #             break

            self.closest_unit_dist=99999 #high number for debug purposes
            self.closest_unit_index=-1
            if (not self.force) in [i.force for i in container_name.units]: #only does this when enemies exist (enemy.force = opposite of self.force)
                for e in range(0,len(container_name.units)):
                    if container_name.units[e].force!=self.force and container_name.units[e].behaviour_id==0:
                        if math.dist((self.x,self.y),(container_name.units[e].x,container_name.units[e].y))<self.closest_unit_dist:
                            self.closest_unit_dist=math.dist((self.x,self.y),(container_name.units[e].x,container_name.units[e].y))
                            self.closest_unit_index=e

            if self.closest_unit_index!=-1 and ((self.y>=400 and container_name.units[self.closest_unit_index].y>=400) or (self.y<400 and container_name.units[self.closest_unit_index].y<400)): #straight path towards enemy if on same side
                    init_target=[container_name.units[self.closest_unit_index].x,container_name.units[self.closest_unit_index].y] #enemy pos
            elif (self.force and self.y>360) or (not self.force and self.y<440): #bridge in between iirc (360<->440 y), so goes to bridge
                if self.x<=screen_x//2:
                    
                    if self.force:
                        init_target=[330,400] #goes to closest bridge
                    else:
                        init_target=[330,400]
                else:
                    if self.force:
                        init_target=[630,400]
                    else:
                        init_target=[630,400]
            

        # # init_target=[400,400] #DEBUG
        # pygame.draw.rect(screen,(0,0,255),pygame.Rect(init_target[0],init_target[1],64,64)) #DEBUG
        return init_target
    
    def move(self):
        total_vector=[self.target_pos[0]-self.x,self.target_pos[1]-self.y]
        total_magnitude=math.sqrt(((total_vector[0])**2)+((total_vector[1])**2))
        if total_magnitude!=0: #stops div by 0
            relative_magitude=self.speed/total_magnitude
            if pygame.Rect.colliderect(self.rect,pygame.Rect(200,360,screen_x-400,80)):
                relative_magitude/=1.5
                if not (pygame.Rect.colliderect(self.rect,pygame.Rect(200+150-20,360,40,80)) or pygame.Rect.colliderect(self.rect,pygame.Rect(200+450-20,360,40,80))): 
                    relative_magitude/=6 #moves (1.5*6)x slower on water
            # print([total_vector[0]*relative_magitude,total_vector[1]*relative_magitude])
            self.x+=total_vector[0]*relative_magitude#ig this sort of counts as linear interpolation in a sense?
            self.y+=total_vector[1]*relative_magitude#idk this will probably be a nuisance (should have just used math.atan2(theta) like before)

    def attack(self,container_name):
        attack_action=0
        if (not self.cooldown) and ((not self.force) in [i.force for i in container_name.units]): #coldown over and enemies exist
            for e in range(0,len(container_name.units)):
                if (self.force!=container_name.units[e].force) and math.dist((self.x,self.y),(container_name.units[e].x,container_name.units[e].y))<self.range: #if is enemy and in range
                    atk_target_index=e #just makes it look bit nicer
                    abs_proj_speed=projectile_data[self.attack_id][1]
                    dist_factor=abs_proj_speed/max(math.dist((self.x,self.y),(container_name.units[atk_target_index].x,container_name.units[atk_target_index].y)),0.0001)
                    temp_x_vel=dist_factor*(container_name.units[atk_target_index].x-self.x) #no math.atan2() needed
                    temp_y_vel=dist_factor*(container_name.units[atk_target_index].y-self.y) #just vector multiplied by the proportion of speed to distance
                    attack_action=projectile(self.x,self.y,temp_x_vel,temp_y_vel,self.attack_id,self.force)
                    self.cooldown=self.atk_speed #resets attack cooldown
                    break

        return attack_action #just sanitize proj container by removing all Falses, done bacause of variable locailty or smthn

    def draw(self): #done by container
        pygame.draw.rect(screen,((255,0,0),(0,255,0))[int(self.force)],self.rect)

        pygame.draw.rect(screen,(0,0,0),pygame.Rect(self.x-1,self.rect.bottom+4-1,self.rect.width*(self.hp/self.start_hp),8))
        pygame.draw.rect(screen,[(255,0,96),(0,255,96)][self.force],pygame.Rect(self.x,self.rect.bottom+4,self.rect.width*(self.hp/self.start_hp),8))



    def update(self):
        self.target_pos=self.target(units_container)
        self.move()
        self.cooldown=max(self.cooldown-1,0)
        self.rect=pygame.Rect(self.x,self.y,self.size,self.size)


class container:
    def __init__(self):
        self.units=[]
        self.projectiles=[]
        # self.towers=[] towers are generalised into units with behaviour_id 0 and stand still

    def attack_handling(self): #best done here for ease of management
        for e in range(0,len(self.units)):
            self.projectiles.append(self.units[e].attack(self))
            if not self.projectiles[-1]:
                self.projectiles.pop() #if false(0) then remove
    
    def validate(self):#gets rid of invalid projectiless and (dead) units
        for e in range(0,len(self.projectiles)): 
            if self.projectiles[e].x<-1000:
                self.projectiles[e]="remove"
        while "remove" in self.projectiles:
            self.projectiles.remove("remove")

        for e in range(0,len(self.units)):
            if self.units[e].x<-1000:
                self.units[e]="remove"
        while "remove" in self.units:
            self.units.remove("remove")

    def collision_handling(self):
        for e in range(0,len(self.projectiles)):
            if (not self.projectiles[e].force) not in ([i.force for i in self.units]): #skips projectile if no enemies exist
                continue
            for f in range(0,len(self.units)):
                if self.projectiles[e].force==self.units[f].force:
                    continue
                if pygame.Rect.colliderect(self.projectiles[e].rect,self.units[f].rect):
                    self.units[f].hp-=self.projectiles[e].dmg
                    if self.units[f].hp<=0:
                        self.units[f].x-=10000000 #same as with proj, its just safer to do it this way
                    self.projectiles[e].x-=10000000 #casts the projectile into the void, because removing items during iteration is severely dangerous
                    break
        self.validate()


    def items_draw(self):
        for e in range(0,len(self.units)):
            self.units[e].draw()
        for e in range(0,len(self.projectiles)):
            self.projectiles[e].draw()


    def update(self):
        self.attack_handling()
        self.collision_handling()
        for e in range(0,len(self.units)):
            self.units[e].update()
        for e in range(0,len(self.projectiles)):
            self.projectiles[e].update()





units_container=container()

units_container.units.extend([unit(500-32,64,0,False),unit(300-32,96,0,False),unit(700-32,96,0,False),
                              unit(500-32,screen_y-64,0,True),unit(300-32,screen_y-96,0,True),unit(700-32,screen_y-96,0,True)])

# units_container.units.extend([unit(400,200,1,False),unit(500,100,1,True),unit(400,500,1,False)]) #debug testing

# for e in range(0,10):
#     units_container.units.append(unit(400+random.randint(-100,100),[700,300][e%2],[1,1,1,2][e%4],[True,False][e%2])) #debug testing

p1_options=[]
p1_cooldown=0
p2_options=[]
p2_cooldown=0

def draw_options(options_list,x):
    for e in range(0,len(options_list)):
        screen.blit(tile_images[options_list[e]],(x,(16*math.sin((tick/160)+20*e))+100+(180*e)))
        #pygame.draw.rect(screen,[(0,0,0),(255,128,32),(128,255,32),(32,128,255)][options_list[e]],pygame.Rect(x,(16*math.sin((tick/160)+20*e))+100+(180*e),100,128))


def refill_p1_options(removal_index):
        global p1_options,p1_deck_options
        while len(p1_options)<4:
            if len(p1_deck_options)>=5:
                random.shuffle(p1_deck_options)
                if p1_deck_options[0] not in p1_options:
                    p1_options.insert(removal_index,p1_deck_options[0])
                    p1_deck_options.pop(0)
            else:
                p1_deck_options=[1,2,3,4,5,6,7,8]

def refill_p2_options(removal_index):
        global p2_options,p2_deck_options
        while len(p2_options)<4:
            if len(p2_deck_options)>=5:
                random.shuffle(p2_deck_options)
                if p2_deck_options[0] not in p2_options:
                    p2_options.insert(removal_index,p2_deck_options[0])
                    p2_deck_options.pop(0)
            else:
                p2_deck_options=[1,2,3,4,5,6,7,8]

refill_p1_options(0)
refill_p2_options(0)

def choose_options():
    global p1_regen_speed,p2_regen_speed
    global p1_cooldown,p1_points_bar
    if p1_cooldown==0 and (board[pygame.K_1] or board[pygame.K_2] or board[pygame.K_3] or board[pygame.K_4]):
        temp_p1_choices=[board[pygame.K_1],board[pygame.K_2],board[pygame.K_3],board[pygame.K_4]]
        for e in range(0,len(temp_p1_choices)):
            if temp_p1_choices[e]:
                if p1_points_bar>=unit_data[p1_options[e]][7]:
                    p1_points_bar-=unit_data[p1_options[e]][7]
                    # print(unit_data[p1_options[e]],unit_data[p1_options[e]][7])
                    p1_cooldown=60
                    if p1_options[e]==8:
                        p1_regen_speed+=1
                    else:
                        units_container.units.append(unit(random.randint(-40,40)+(screen_x/2),200,p1_options[e],False))
                    p1_options.pop(e)
                    refill_p1_options(e)
                    break

    global p2_cooldown,p2_points_bar
    if p2_cooldown==0 and (board[pygame.K_7] or board[pygame.K_8] or board[pygame.K_9] or board[pygame.K_0]):
        temp_p2_choices=[board[pygame.K_7],board[pygame.K_8],board[pygame.K_9],board[pygame.K_0]]
        for e in range(0,len(temp_p2_choices)):
            if temp_p2_choices[e]:
                if p2_points_bar>=unit_data[p2_options[e]][7]:
                    p2_points_bar-=unit_data[p2_options[e]][7]
                    p2_cooldown=60
                    if p2_options[e]==8:
                        p2_regen_speed+=1
                    else:
                        units_container.units.append(unit(random.randint(-40,40)+(screen_x/2),screen_y-200,p2_options[e],True))
                    p2_options.pop(e)
                    refill_p2_options(e)
                    break

def player_presence():
    p1_alive=False
    p2_alive=False
    for e in range(0,len(units_container.units)):
        if units_container.units[e].id==0:
            if units_container.units[e].force:
                p2_alive=True
            else:
                p1_alive=True
    return [p1_alive,p2_alive] #red,green

game_over=False
#NOTE: P1 IS FALSE, P2 IS TRUE
while True:
    clock=pygame.time.Clock()
    tick+=1
    board=pygame.key.get_pressed()

    if game_over:
        pass
        if player_presence()[1]:
            screen.blit(green_victory_png,((screen_x/2)-128,(screen_y/2)-128))
        else:
            screen.blit(red_victory_png,((screen_x/2)-128,(screen_y/2)-128))

        if board[pygame.K_r]:
            game_over=False
            tick=0
            units_container=container()
            units_container.units.extend([unit(500-32,64,0,False),unit(300-32,96,0,False),unit(700-32,96,0,False),
                                        unit(500-32,screen_y-64,0,True),unit(300-32,screen_y-96,0,True),unit(700-32,screen_y-96,0,True)])
            p1_cooldown=0
            p1_options=[]
            p1_points_bar=0.0
            p1_regen_speed=1
            p1_deck_options=[1,2,3,4,5,6,7,8]
            refill_p1_options(0)


            p2_cooldown=0
            p2_options=[]
            p2_points_bar=0.0
            p2_regen_speed=1   
            p2_deck_options=[1,2,3,4,5,6,7,8] 
            refill_p2_options(0)

    else:
        p1_points_bar+=0.01*p1_regen_speed
        p2_points_bar+=0.01*p2_regen_speed
        p1_points_bar=min(p1_points_bar,10) #why not, let spaghetti code take the wheel
        p2_points_bar=min(p2_points_bar,10)
        p1_cooldown=max(p1_cooldown-1,0)
        p2_cooldown=max(p2_cooldown-1,0)

        choose_options()
        # while len(p1_options)<4:
        #     if len(p1_deck_options)>=1:
        #         random.shuffle(p1_deck_options)
        #         if p1_deck_options[0] not in p1_options:
        #             p1_options.append(p1_deck_options[0])
        #             p1_deck_options.pop(0)
        #     else:
        #         p1_deck_options=[1,2,3,4,5,6,7,8]
        # while len(p2_options)<4:
        #     if len(p2_deck_options)>=1:
        #         random.shuffle(p2_deck_options)
        #         if p2_deck_options[0] not in p2_options:
        #             p2_options.append(p2_deck_options[0])
        #             p2_deck_options.pop(0)
        #     else:
        #         p2_deck_options=[1,2,3,4,5,6,7,8]
            
        

        #<DRAW ZONE>
        # pygame.draw.rect(screen,(20,200,20),pygame.Rect(200,0,screen_x-400,screen_y)) #grass and water
        # pygame.draw.rect(screen,(20,20,200),pygame.Rect(200,360,screen_x-400,80))
        screen.blit(bg_img,(200,0)) #done with piskel image

        # pygame.draw.rect(screen,(150,75,0),pygame.Rect(200+150-20,360,40,80)) #-20 down to centre it due to width of 40
        # pygame.draw.rect(screen,(150,75,0),pygame.Rect(200+450-20,360,40,80)) bridge

        pygame.draw.rect(screen,(128,0,0),pygame.Rect(0,0,200,screen_y)) #select screen bg
        pygame.draw.rect(screen,(0,128,0),pygame.Rect(800,0,200,screen_y))

        pygame.draw.rect(screen,(48,0,0),pygame.Rect(200-10,0,20,screen_y)) #borders
        pygame.draw.rect(screen,(0,48,0),pygame.Rect(800-10,0,20,screen_y))

        pygame.draw.rect(screen,(255,0,255),pygame.Rect(0,0,190*(p1_points_bar/10),32))
        pygame.draw.rect(screen,(255,0,255),pygame.Rect(screen_x-190,0,190*(p2_points_bar/10),32))
        for e in range(0,10):
            pygame.draw.rect(screen,(0,0,0),pygame.Rect(19*e,0,4,32))
            pygame.draw.rect(screen,(0,0,0),pygame.Rect(screen_x-(19*e),0,4,32))
        pygame.draw.rect(screen,(0,0,0),pygame.Rect(0,32,190,4))
        pygame.draw.rect(screen,(0,0,0),pygame.Rect(screen_x-190,32,190,4))
        draw_options(p1_options,50)
        draw_options(p2_options,850)
        if p1_cooldown:
            screen.blit(transparent_p1_cooldown_bg,(0,36)) 
        if p2_cooldown:
            screen.blit(transparent_p2_cooldown_bg,(800,36)) 

        #print(player_presence())
        units_container.update()
        units_container.items_draw()
        if sum(player_presence())!=2:
            game_over=True
        #</DRAW ZONE>

    clock.tick(60)
    for event in pygame.event.get():
       if event.type == QUIT:
           pygame.quit()
           sys.exit()
    pygame.display.update()









