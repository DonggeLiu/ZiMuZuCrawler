#**ZiMuZuCrawler**

A web crawler for you to automatically check-in and download latest TV series from [zimuzu.tv](http://www.zimuzu.tv/)


##Before start:


1. [x] Check if you have [Python 3](https://docs.python.org/3/) installed. 
    
    If not, you can download latest version of Python 3 from [here](https://www.python.org/downloads/) 
    or via [homebrew](http://brew.sh/): `brew intall Python3`


2. [x] Check if you have [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) installed. 
    
    If not, you can use [pip](https://pip.pypa.io/en/latest/reference/pip_install/) (or pip3 if you have both Pyhton2 and Python3) to install it:
    `pip3 install beautifulsoup4`

3. [x] Check if you have [requests](http://docs.python-requests.org/en/master/) installed. 
    
    If not, again you can use `pip` to install it:
    `pip3 install requests`

4. [x] Change the 'account' and 'password' in the ZiMuZuCrawler.py to your own.

    If you don't have one, you can apply from [here](http://www.zimuzu.tv/user/reg)


##Usage:

1. Run `Python3 update.py` in terminal to store all the latest TV shows into `updatedResources.txt`
2. Run `Python3 download.py` in terminal to download shows stored in previous step and keep record of the latest ones with `downloadedResources.txt`


##Recommandations: 

    
1. Use [Crontab](http://www.adminschoice.com/crontab-quick-reference) to update shows automatically, for example:

	  `*/30 * * * * /usr/local/bin/python3 /Users/donggeliu/kit/ZiMuZu/update.py >> /Users/donggeliu/kit/ZiMuZu/dialog.log`

	
Remember using absolute path in Crontab.


## TODO list:
1. SMS notification
2. aria2 integration

##Donation:

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/DonggeLiu)




