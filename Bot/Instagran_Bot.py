from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import os
import time
from Bot.links import scrollBar1, scrollBar2
from Bot import userinfo, links
import urllib


class Bot:
    driverPath = "chromedriver.exe"

    def __init__(self):
        self.username = userinfo.username
        self.password = userinfo.password

        self.my_followers = []
        self.my_following = []

        self.browser = webdriver.Chrome(Bot.driverPath)

    def sign_in(self):
        self.browser.get(links.website)
        time.sleep(3)

        sernameInput = self.browser.find_element("name", "username")
        passwordInput = self.browser.find_element("name", "password")

        sernameInput.send_keys(self.username)
        passwordInput.send_keys(self.password)

        passwordInput.send_keys(Keys.ENTER)
        print("INFO :: Logged In")
        time.sleep(10)

        if self.browser.find_element(By.CLASS_NAME, links.box1):
            print("INFO :: Box-1")
            val = self.browser.find_element(By.CLASS_NAME, links.box1)
            val.find_element(By.TAG_NAME, "button").click()

        time.sleep(3)
        #
        if self.browser.find_element(By.XPATH, links.box2):
            print("INFO :: Box-2")
            self.browser.find_element(By.XPATH, links.box2).click()
            time.sleep(1)

    def get_followers(self, username):
        self.browser.get("https://www.instagram.com/{}/followers/".format(username))
        time.sleep(10)

        scrollBar = self.browser.find_element(By.XPATH, scrollBar1)

        last_ht, ht = 0, 1
        while last_ht != ht:
            last_ht = ht
            time.sleep(2)
            ht = self.browser.execute_script("""
                            arguments[0].scrollTo(0, arguments[0].scrollHeight);
                            return arguments[0].scrollHeight; 
                                             """, scrollBar)

        links = scrollBar.find_elements(By.TAG_NAME, 'a')
        time.sleep(3)
        names = [name.text for name in links if name.text != '']
        return names

    def get_following(self, username, mode=0):
        self.browser.get("https://www.instagram.com/{}/following/".format(username))
        time.sleep(5)

        scrollBar = self.browser.find_element(By.XPATH, scrollBar2)

        last_ht, ht = 0, 1
        verified = []
        while last_ht != ht:
            last_ht = ht
            time.sleep(2)
            # scroll down and retrun the height of scroll (JS script)
            ht = self.browser.execute_script(""" 
                                arguments[0].scrollTo(0, arguments[0].scrollHeight);
                                return arguments[0].scrollHeight; 
                                       """, scrollBar)


        links = scrollBar.find_elements(By.TAG_NAME, 'a')
        time.sleep(3)
        names = [name.text for name in links if name.text != '']

        if mode == 1:
            for name in names:
                val = name.split("\n")
                if len(val) > 1:
                    index = names.index(name)
                    names[index] = val[0]
                    verified.append(val[0])

            return names, verified

        else:
            return names

    def get_my_followers(self):
        return self.get_followers((userinfo.username))

    def get_my_following(self):
        return self.get_following(userinfo.username)

    def compare_lists(self):
        self.my_following = self.get_my_followers()
        self.my_followers = self.get_my_following()


        mutual = []
        followers = []
        following = []

        l = [self.my_followers, self.my_following]

        for i in range(2):
            for n in l[i]:
                cnt = 0
                for m in l[1-i]:
                    if n == m:
                        cnt += 1
                        if mutual != []:
                            mutual.append(n)

                if cnt == 0:
                    if i == 0:
                        following.append(n)
                    elif i == 1:
                        followers.append(n)

        return following, mutual, followers

    def unfollow_user(self, username):
        self.browser.get("https://www.instagram.com/{}/".format(username))
        time.sleep(3)
        btn = self.browser.find_element(By.TAG_NAME, 'button')
        if btn.text == "Mesaj Gönder":
            self.browser.find_elements(By.TAG_NAME, 'button')[1].click()
            time.sleep(1)
            self.browser.find_element(By.CSS_SELECTOR, 'div[role=dialog] button').click()
            print("INFO :: Account succsefully unfollowed")
        else:
            print("INFO :: You don't follow the account")

    def send_message(self, username, message):
        self.browser.get("https://www.instagram.com/{}/".format(username))
        time.sleep(3)
        btn = self.browser.find_element(By.TAG_NAME, 'button')
        if btn.text == "Mesaj Gönder":
            btn.click()
            time.sleep(5)
            textbox = self.browser.find_element(By.XPATH, links.textbox)
            textbox.send_keys(message)
            textbox.send_keys(Keys.ENTER)
            print("INFO :: Mesage has been sent to {}".format(username))
        else:
            print("INFO :: This account is private and you don't follow it")

    def send_to_all(self, accounts, message):
        for account in accounts:
            self.message(account, message)

    def get_profile_info(self, username):
        self.browser.get("https://www.instagram.com/{}/".format(username))
        time.sleep(3)

        try:
            image = self.browser.find_element(By.XPATH, '//img[@class="_aa8j"]')
            private = False
        except:
            image = self.browser.find_element(By.XPATH, '//img[@class="_aadp"]')
            private = True

        img_link = image.get_attribute('src')
        urllib.request.urlretrieve(img_link, "profile_picture.jpg")

        post = self.browser.find_element(By.CLASS_NAME, "_ac2a").text

        followers = self.browser.find_elements(By.TAG_NAME, "a")[0].text
        following = self.browser.find_elements(By.TAG_NAME, "a")[1].text

        verified = self.get_following(username, 1)[1]

        return  private, post, following, followers, verified

    def download_all_posts(self, username):
        self.browser.get("https://www.instagram.com/{}/".format(username))
        time.sleep(3)
        posts = self.browser.find_elements(By.CLASS_NAME, "_aagu")
        posts[0].click()
        time.sleep(3)
        cnt = 1
        os.mkdir("{}posts".format(username))

        while True:
            print("\t--> Downloading Post", cnt)
            time.sleep(1)

            images = posts[cnt - 1].find_elements(By.TAG_NAME, "img")
            for num, img in enumerate(images):
                img_link = img.get_attribute('src')
                urllib.request.urlretrieve(img_link, "{}posts/{}_{}_{}.jpg".format(username, username, cnt, num))

            for num, post in enumerate(posts):
                if post.find_element(By.TAG_NAME, "video"):
                    vid = post.find_element(By.TAG_NAME, "video")
                    vid_link = vid.get_attribute('src')
                    urllib.request.urlretrieve(vid_link, "{}posts/{}_{}_{}.mp4".format(username, username, cnt, num))
                elif post.find_element(By.TAG_NAME, "img"):
                    img = post.find_element(By.TAG_NAME, "img")
                    img_link = img.get_attribute('src')
                    urllib.request.urlretrieve(img_link, "{}posts/{}_{}_{}.mp4".format(username, username, cnt, num))

            if self.browser.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div[1]/div/div/div/button"):
                self.browser.find_elements(By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div[1]/div/div/div/button")[-1].click()
                cnt+=1
                time.sleep(.5)

            if cnt > len(posts):
                break

bot = Bot()
