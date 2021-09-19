import pygame
import sys       #sys模組:內含很多函式方法和變數，用來處理Python執行時配置以及資源，從而可以與當前程式之外的系統環境互動
import numpy as np
import os



#定義鳥類    (類別裡面的成員都要用self來存取，可以把self想成是java的this)
class Bird:
    #定義初始化方法 => 裡面有此類別的成員  (  記得是__init(self)__ 而不是 _init(self)_  )
    def __init__(self):    
        self.status = 1                               #預設飛行狀態為中立
        self.birdX = 120                              #鳥所在的x座標
        self.birdY = 350                              #鳥所在的y座標
        self.jumpHeight = 10                          #跳躍高度 
        self.flapped = False                          #預設小鳥無揮動翅膀
        self.survive = True                           #預設小鳥生命狀態為活著
        self.birdRect = pygame.Rect(self.birdX, self.birdY, 30, 25)   #鳥的矩形，參數(left，top，width，height) => 用矩形的目的是要來判定碰撞
        #鳥的三種狀態(往上飛，中立位置，下落)           
        self.birdStatus = [pygame.image.load(os.path.join("image", "upflap.png")).convert_alpha(),\
                           pygame.image.load(os.path.join("image", "midflap.png")).convert_alpha(), pygame.image.load(os.path.join("image", "downflap.png")).convert_alpha()]
    #鳥的飛行控制
    def birdUp(self):  
        if self.flapped:             #拍打翅膀
            self.jumpHeight -= 1
            self.birdY -= self.jumpHeight
            self.flapped = False

        else:                        #沒拍打翅膀=>下降
            self.jumpHeight -= 1
            self.birdY -= self.jumpHeight
        self.birdRect[1] = self.birdY                   #更新Y軸位置

#定義管道類        
class Pipeline:                                         
    #定義初始化方法
    def __init__(self, pipeX = 700):  
        self.pipeX = pipeX        #一開始管道所在位置(即畫面最右方)
        self.y_gap = 130        #上下管道高度差距為120

        #利用mouse.get_pos()得到位置並計算管道的長.寬 => 長:320  寬:50；注意blit()最後兩個參數是左上角座標，所以可以依據這個做管道配置的計算  
        self.pipeY_bottom = np.random.randint(330, 450)                  #下方管道的左上角，數值要調整使得下方管道底下不會為中空以及上方管道上方不會中空
        self.pipeY_top = self.pipeY_bottom - self.y_gap - 320           #上方管道的左上角
        self.bottomRect = pygame.Rect(self.pipeX, self.pipeY_bottom, 50, 320)
        self.topRect = pygame.Rect(self.pipeX, self.pipeY_top, 50, 320)
        self.bottom = pygame.image.load(os.path.join("image", "pipe.png")).convert_alpha()
        self.top = pygame.transform.rotate(pygame.image.load(os.path.join("image", "pipe.png")).convert_alpha(), 180)    #將管道翻轉
        
    def move(self):             #讓管道一直向左側移動，就好像小鳥在向前飛行
        global score
        
        self.pipeX -= 5         #管道向左移動
        self.bottomRect = pygame.Rect(self.pipeX, self.pipeY_bottom, 50, 320)   #更新位置
        self.topRect = pygame.Rect(self.pipeX, self.pipeY_top, 50, 320)
        
        if self.pipeX < 70:     #管道向左移動到一個邊界，就像鳥飛過了管道一樣 => 得分並重製管道
            if bird_object.survive:
                score += 1
                score_effect.play()
        #管道到達邊界，需要再重新回到右側並設立新高度
            self.pipeX = window[0]
            self.pipeY_bottom = np.random.randint(330, 450)        
            self.pipeY_top = self.pipeY_bottom - self.y_gap - 320


#顯示地圖上所有物件        
def show():        
    #背景
    screen.fill((255, 255, 255))            #填充顏色(白色)
    screen.blit(background,(0, 0))          #填入圖片
    #鳥
    if not bird_object.survive:
        bird_object.status = 2
    elif bird_object.flapped:
        bird_object.status = 0
    else:
        bird_object.status = 1
    screen.blit(bird_object.birdStatus[bird_object.status], (bird_object.birdX, bird_object.birdY))
    if not stop:         #在遊玩狀態才讓鳥移動
        bird_object.birdUp()
    #管道  
    global pipe_reset

    for element in pipeline_list: #印出在管道陣列的元素(即管道類別的物件)
        #分別印出上下管道
        screen.blit(element.top ,(element.pipeX, element.pipeY_top)) 
        screen.blit(element.bottom ,(element.pipeX, element.pipeY_bottom))        
        if not stop:        #在遊玩狀態才讓管道移動
            element.move()     
  
#碰撞偵測  回傳True代表碰撞到管道或地圖邊界=＞鳥死亡
def touching():                                                   
    for element in pipeline_list:
        if element.bottomRect.colliderect(bird_object.birdRect) or element.topRect.colliderect(bird_object.birdRect):   #碰撞到管道
            return True    
    if not 0 < bird_object.birdRect[1] < window[1]:    #碰撞到地圖上下邊界
        return True
    return False

#針對不同狀態顯示文字(分數.結果)
def show_result():
    global stop
    
    #初始狀態 => 一開始需要等使用者先按下空白鍵，鳥才能開始動作，並且管道才開始向左移動
    if stop and not space_pressed:
        screen.blit(font2.render("SPACE : jump ", -1, (255, 255, 255)), (30, window[1] // 2 - 200 ))
        screen.blit(font2.render("R     : restart ", -1, (255, 255, 255)), (30, window[1] // 2 - 100 ))
        screen.blit(font2.render("ESC   : quit ", -1, (255, 255, 255)), (30, window[1] // 2))
    #死亡狀態 => 有碰撞 
    elif touching():                              
        pygame.mixer.music.stop()
        bird_object.survive = False
        screen.blit(font2.render("GAME OVER", -1, (255, 255, 255)), (window[0] // 2 - 100, window[1] // 2 -100))
        screen.blit(font1.render("Score : " + str(score), -1, (255, 255, 255)), (window[0] // 2 - 100, window[1] // 2))
        screen.blit(font1.render("press R to restart", -1, (255, 255, 255)), (window[0] // 2 - 100, window[1] // 2 + 50))
    #沒碰撞且鳥存活
    elif not touching() and bird_object.survive:   

        #正常游玩狀態
        screen.blit(font1.render("Score : " + str(score), -1, (255, 255, 255)), (550, 50))    #顯示分數

        #過關狀態 => 分數達到門檻，成功過關，跳出迴圈並撥放影片
        if score >= 20:         #過關所需的分數
            screen.blit(font2.render("congratulations!", -1, (255, 255, 255)), (window[0] // 2 - 200, window[1] // 2 - 100))
            #screen.blit(font1.render("請按Enter鍵進入下一階段", -1, (255, 255, 255)), (window[0] // 2 - 100, window[1] // 2))
            game_passed = True
            stop = True
            
    pygame.display.update()           #更新顯示(刷屏)，也可以用pygame.display.flip()
        
def main():
    global window, screen, clock, background , font1, font2, score, gameover_effect, hit_effect, score_effect
    global bird_object, pipeline_list   #物件相關變數
    global game_passed    #使用者是否通關
    global space_pressed  #使用者按過跳躍鍵
    global stop           #一開始.死亡.過關的情況下，鳥和管道不可以移動

    game_passed = False
    space_pressed = False
    stop = True
    lock = False          #過關或死亡後不能再操控鳥
    hit_sound = False     #控制音效播放
    over_sound = False    #控制音效播放

    #初始化pygame
    pygame.init()        
    pygame.mixer.init()
    #介面設定
    window = [700, 600]       
    screen = pygame.display.set_mode(window)  
    clock = pygame.time.Clock()           #設定時鐘
    #文字設定
    font1 = pygame.font.SysFont("simsunnsimsun", 30)
    font2 = pygame.font.SysFont("simsunnsimsun", 50)
    #載入音樂
    pygame.mixer.music.load(os.path.join("music", "flappy_bgm.mp3"))
    #設定音樂的音量
    pygame.mixer.music.set_volume(0.5)
    #載入音效
    flap_effect = pygame.mixer.Sound(os.path.join("music", "flap.wav"))
    hit_effect = pygame.mixer.Sound(os.path.join("music", "touch_pipe.wav"))
    hit_effect.set_volume(0.3)
    gameover_effect = pygame.mixer.Sound(os.path.join("music", "game_over.wav"))
    gameover_effect.set_volume(0.3)
    score_effect = pygame.mixer.Sound(os.path.join("music", "score.wav"))
    #載入圖片
    background = pygame.image.load(os.path.join("image", "flappy_bg.jpg")).convert_alpha()    #os.path.join() => 獲取當前目錄，並組合成新目錄
    background = pygame.transform.scale(background, window)                   #將圖片縮放至螢幕大小
    #創立物件
    bird_object = Bird()                #鳥類只需要一個物件(即玩家操控的鳥)
    pipeline_object1 = Pipeline()     
    pipeline_object2 = Pipeline(400)   #初始化pipeX值預設為700，這裡做了更動是因為要讓兩根管道初始位置不一樣，才可以顯示兩個出來而不會重疊  
    pipeline_list = [pipeline_object1, pipeline_object2]
    #分數
    score = 0
    #音樂播放
    pygame.mixer.music.play(-1)
    
    while True:            #遊戲迴圈

        key = pygame.key.get_pressed()        #新增鍵盤輸入
             
        #檢測碰撞(為了播音效才加，本來應該沒必要加)    
        if touching():
            if not hit_sound:
                hit_effect.play()  #播放碰撞音效
                hit_sound = True
##############################################################################################                
                
        #成功通關        
        if game_passed:
            lock = True
            stop = True
            #win.preview()
        #鳥死亡  遊戲結束
        elif not bird_object.survive:
            lock = True
            stop = True
            bird_object.birdY = 800
            if not over_sound:
                gameover_effect.play()  #播放遊戲結束音效
                over_sound = True
        #正常遊玩情況
        else:
            if not lock:
                if key[pygame.K_SPACE] :                #空白鍵操控鳥拍打翅膀
                    space_pressed = True
                    stop = False
                    if space_pressed:
                        bird_object.flapped = True           
                        bird_object.jumpHeight = 10
                        flap_effect.play()              #播放拍翅膀音效
                        
##################################################################################################
        show()             #顯示地圖上物件
        show_result()      #顯示分數.結果  此函數已經包含碰撞偵測函數( touching() ) 

        clock.tick(50)
         
        for event in pygame.event.get():
            if event.type == pygame.QUIT or key[pygame.K_ESCAPE]:  #ecs鍵離開遊戲
                pygame.quit()
                sys.exit()
        #按g鍵作弊，直接通關
        if key[pygame.K_g] and space_pressed and bird_object.survive:
            score = 20
            stop = True
            lock = True
            bird_object.survive = True
            #win.preview()
        #按r鍵重新開始遊戲
        if key[pygame.K_r]:               
            pygame.mixer.stop()            #重新開始遊戲前先停止所有音樂.音效
            stop = True
            lock = False
            main()
            
#主程式
if __name__ == '__main__':             
#python 直譯器執行程式碼時，有一些內建、隱含的變數，__name__就是其中之一
#其意義是「模組名稱」。如果該檔案是被引用，其值會是模組名稱
#但若該檔案是(透過命令列)直接執行，其值會是 __main__ 
    main()
   









