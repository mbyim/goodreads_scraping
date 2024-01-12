import os
import json
import time
import argparse
from datetime import datetime
import requests
#import beautifulsoup4 as bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

def get_bookdata(driver, id):
    #how to pull out the table of data as a dataframe?
    #read html it seems like
    print(id)
    #get author id & statistics
    driver.get(f"https://www.goodreads.com/book/show/{id}")
    time.sleep(5)
    #why does author link using xpath not get found in particular hmm? 
    try:
        author_link = driver.find_element(By.CLASS_NAME, "ContributorLink").get_attribute('href')
    except: 
        time.sleep(10)
        driver.refresh() 
        author_link = driver.find_element(By.CLASS_NAME, "ContributorLink").get_attribute('href')
    driver.get(f"https://www.goodreads.com/book/stats?id={id}")
    try:
        book_stats = pd.read_html(driver.page_source)[0] 
    except:
        try:
            print("trying again")
            time.sleep(15) #try again, sometimes goodreads jsut times out
            driver.refresh()
            book_stats = pd.read_html(driver.page_source)[0] 
        except:
            print("trying again x2")
            time.sleep(30) #try again, sometimes goodreads jsut times out
            driver.refresh()
            book_stats = pd.read_html(driver.page_source)[0] 
    #print(book_stats)
    return author_link, book_stats  

def get_booksdata_of_author(driver, authorlink):
    driver.get(authorlink)
    #tablerows = driver.find_elements(By.XPATH, """//*[@id="bodycontainer"]/div[3]/div[1]/div[2]/div[3]/div[2]/div[4]/div/div[2]/div/table/tbody/tr""") #hmm
    tablerows = driver.find_element(By.XPATH, """//*[@class="stacked tableList"]""") 
    authbooks = tablerows.find_elements(By.CSS_SELECTOR, 'tr')
    print(type(authbooks))
    print(len(authbooks))
    abooks = [row.find_element(By.CLASS_NAME, "bookTitle").get_attribute('href') for row in authbooks]    
    print(abooks)
    books = [x.split('/')[-1].split('.')[0].split('-')[0] for x in abooks]
    return books, abooks #book title, book link

def login():
    #LOGIN
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.goodreads.com/user/sign_in")
    driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div/div/div[1]/div/a[4]/button").click()
    driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div[2]/div/form/div/div/div/div[1]/input").send_keys(os.getenv("GR_EMAIL"))
    time.sleep(2)
    driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div[2]/div/form/div/div/div/div[2]/input").send_keys(os.getenv("GR_PASS"))
    time.sleep(1) 
    driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div[2]/div/form/div/div/div/div[3]/span/span/input").click()
    time.sleep(90)
    return driver
   
def main(books):
    print(books)
    driver = login()
    authors = []
    book_data = [] #how should i massage this hmm
    for book in books:
        authorlink, book_stats = get_bookdata(driver, book)
        authors.append([book, authorlink]) #attach book id so we can map to it's treatment period
        book_data.append([book, book, book_stats])

        #break #TODO: remove
    print("------- ABOUT TO START DOING BY AUTHOR ------------")
    #now for each author get data on all their other books
    for origin_book_id, author in authors:
        idbooks, abooks = get_booksdata_of_author(driver, author)
        print(author)
        print(f"num books: {len(abooks)}")
        #should be ok with empty lists, i checked
        for idbook, abook in [(x,y) for (x,y) in zip(idbooks, abooks) if y not in books]:
            authorlink, book_stats = get_bookdata(driver, idbook)
            book_data.append([idbook, origin_book_id, book_stats]) #we dont need author link, can throw that out now
            #break #TODO REMOVE
 
    #massage data into one big df & store it to disk
    clean_booklist = []
    for id, origin_book_id, df in book_data:
        df['book_id'] = id
        df['origin_book_id'] = origin_book_id
        clean_booklist.append(df)
    
    books_df = pd.concat(clean_booklist, ignore_index=True)
    print(books_df)
    books_df.to_csv('enhanced_book_data.csv', index=False) #books_data.csv 
    #books_data_new_try
    print("done")


#Notes:
#https://www.ft.com/content/d5f38896-34e3-419e-bb09-42f537b69e0a
#synthetic control, is it do-able in this case, we will see?
#130758645 62217087 62192405 193907194 61282598 62847908 61884887 62121704 75657079 61898069 61089447

if __name__ == "__main__":
    print("here")
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--names-list', action='store', dest='books_treated', default=[], nargs='+') #books treated 
    #parser.add_argument()
    args = parser.parse_args()
    main(args.books_treated)
