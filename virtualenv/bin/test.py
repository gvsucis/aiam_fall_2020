from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument( "--headless" )

print( "Spawnning webdriver isntance" )

d = webdriver.Chrome( executable_path="./linux_chromedriver", chrome_options=options )

print( "Launching..." )

d.get( "https://google.com" )

print( d.title )
print( "Done!" )
