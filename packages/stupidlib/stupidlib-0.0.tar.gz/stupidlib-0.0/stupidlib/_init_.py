import pygame
import requests
def Boom():
    url = "https://www.myinstants.com/media/sounds/vine-boom.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Fart():
    url = "https://www.myinstants.com/media/sounds/dry-fart.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Wow():
    url = "https://www.myinstants.com/media/sounds/anime-wow-sound-effect.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Xaxaxa():
    url = "https://www.myinstants.com/media/sounds/baby-laughing-meme.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Meow():
    url = "https://www.myinstants.com/media/sounds/sad-meow-song.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Metal():
    url = "https://www.myinstants.com/media/sounds/metal-pipe-clang.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Sad():
    url = "https://www.myinstants.com/media/sounds/tf_nemesis.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Beep():
    url = "https://www.myinstants.com/media/sounds/wrong-answer-sound-effect.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def DunDunDun():
    url = "https://www.myinstants.com/media/sounds/dun-dun-dun-sound-effect-brass_8nFBccR.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def CatXaxaxa():
    url = "https://www.myinstants.com/media/sounds/cat-laugh-meme-1.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Galaxy():
    url = "https://www.myinstants.com/media/sounds/galaxy-meme.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def BrainFart():
    url = "https://www.myinstants.com/media/sounds/long-brain-fart.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Bell():
    url = "https://www.myinstants.com/media/sounds/taco-bell-bong-sfx.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Sexy():
    url = "https://www.myinstants.com/media/sounds/george-micael-wham-careless-whisper-1.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Rrrr():
    url = "https://www.myinstants.com/media/sounds/zhiostkaia-otryzhka.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Ph():
    url = "https://www.myinstants.com/media/sounds/hub-intro-sound.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def SocialCredit():
    url = "https://www.myinstants.com/media/sounds/999-social-credit-siren.mp3"
    response = requests.get(url)
    with open("sound.mp3", "wb") as f:
        f.write(response.content)
    pygame.mixer.init()
    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
def Stop():
    pygame.mixer.music.stop()
def Info():
    print("*The library needs pygame to work!*")
    print("                              ")
    print("------------Sounds------------")
    print("Boom()")
    print("Fart()")
    print("Wow()")
    print("Xaxaxa()")
    print("Meow()")
    print("Metal()")
    print("Sad()")
    print("Beep()")
    print("DunDunDun()")
    print("CatXaxaxa()")
    print("Galaxy()")
    print("BrainFart()")
    print("Bell()")
    print("Sexy()")
    print("Rrrr()")
    print("Ph()")
    print("SocialCredit()")
    print("------------Sounds------------")
    print("                              ")
    print("------------Functions------------")
    print("Stop()")
    print("Info()")
    print("------------Functions------------")
    print("                                 ")
