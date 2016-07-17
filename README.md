#**ZiMuZuCrawler**

A web crawler for you to automatically check-in and download latest TV series from [zimuzu.tv](http://www.zimuzu.tv/)


##Before start:


1. [x] Check if you have `Python 3` installed. 
    
    If not, you can download latest version of Python 3 from [here](https://www.python.org/downloads/) 
    or via [homebrew](http://brew.sh/): `brew intall Python3`


2. [x] Check if you have `BeautifulSoup4` installed. 
    
    If not, you can use [pip](https://pip.pypa.io/en/latest/reference/pip_install/) (or pip3 if you have both Pyhton2 and Python3) to install it:
    `pip3 install beautifulsoup4`

3. [x] Check if you have `requests` installed. 
    
    If not, again you can use `pip` to install it:
    `pip3 install requests`

4. [x] Change the 'account' and 'password' in the ZiMuZuCrawler.py to your own.

    If you don't have one, you can apply from [here](http://www.zimuzu.tv/user/reg)


##Usage:

1. You can run it directly in terminal with: 
    `Python3 ZiMuZuCrawler.py`
    
    OR
    
2. Use [Crontab](http://www.adminschoice.com/crontab-quick-reference) to run it automatically, for example:

	  `45 7-8,19-21 * * * /usr/local/bin/Python3 /Users/.../ZimuZu/zimuzu.py >> /Users/.../ZiMuZu/dialog.log`
	
Remember using absolute path in Crontab.

##Recommendations:

[Homebrew](http://brew.sh/) is a good way to install Python3



##Donation:

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/DonggeLiu)




