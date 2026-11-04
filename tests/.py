import test_new_module as hp
hp.Manager.load_env() 

gig = hp.GigaChat()
hp.Auto.screenshot("image.png")

res = gig.chat(
    "Что на этой картинке?", 
    temperature=0.0, 
    images=r'image.png',
    max_tokens=2000
)

print(res)