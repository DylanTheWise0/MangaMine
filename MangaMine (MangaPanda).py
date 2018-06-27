#Ver. 0.3.0
#Authors: Dylan Wise & Zach Almon

import urllib.request
import re
import os
import platform
import sys

platformType = platform.system()

def main():
    success = False
    currentDirectory = os.getcwd()
    downloadMangaListOnce = False
    searchAgain = False

    print('Currently MangaMine only supports MangaPanda.')
    print()
    print('The URL you are to input below should be the top level page of the')
    print('manga you wish to download')
    print('Ex: http://www.mangapanda.com/372/seto-no-hanayome.html ')

    while success == False:
        downloadManga = True
        mangaFound = False

        while 1:
            if searchAgain == False:
                print()
                print('Do you wish to search for a manga or provide a link like the one above?')
                print('[s]earch, [l]ink and [q]uit')
                searchRequest = input('')

            if searchRequest == 's' or searchAgain == True:
                mangaFound = False
                tryLink = False
                searchAgain = False

                #to ensure we aren't repeatedly loading the same page of HTML this bool will trigger once per time the script is run
                if downloadMangaListOnce == False:
                    listOfLinks = []
                    listOfNames = []
                    downloadMangaListOnce = True

                    allManga = urllib.request.urlopen('http://www.mangapanda.com/alphabetical').read()

                    #grabs all manga starting with a particular letter, number or symbol
                    mangasInAlphaBeta = re.findall(r'ul class=+(.*?)</ul>', str(allManga))

                    #using regular patters from the text grabbed above seperates statments into links and names
                    for i in range(len(mangasInAlphaBeta)):

                        #the first item is the list is manga that start with a space which need to be handled differently from the rest
                        if i == 0:
                            linksInAlphaNumeric = re.findall(r'href="(.*?)"', mangasInAlphaBeta[i])
                            for k in range(len(linksInAlphaNumeric)):
                                listOfLinks.append(linksInAlphaNumeric[k])

                            namesInAlphaNumeric = re.findall(r'> (.*?)</a>', mangasInAlphaBeta[i])
                            for k in range(len(namesInAlphaNumeric)):
                                listOfNames.append(namesInAlphaNumeric[k])

                        else:
                            linksInAlphaNumeric = re.findall(r'href="(.*?)"', mangasInAlphaBeta[i])
                            for k in range(len(linksInAlphaNumeric)):
                                listOfLinks.append(linksInAlphaNumeric[k])

                            namesInAlphaNumeric = re.findall(r'<li>(.*?)</li>', mangasInAlphaBeta[i])
                            for k in range(len(namesInAlphaNumeric)):
                                tempNameList = re.findall(r'>(.*?)</a>', namesInAlphaNumeric[k])
                                listOfNames.append(tempNameList[0])
                          

                #checks list created above for the particular manga stated below
                print('What is the name of the Manga you wish to download? (Case sensitive!)')
                potentialMangaName = input('')
                for i in range(len(listOfNames)):
                    if potentialMangaName == listOfNames[i]:
                        mangaFound = True
                        searchedMangaLink = listOfLinks[i]
                        break

                if mangaFound == True:
                    print('Success! That manga exists on MangaPanda.')
                    break

                else:
                    print('Error! That manga does not exist on MangaPanda!')
                    while 1:
                        print()
                        print('Do you wish to [s]earch again or provide a [l]ink? (or [q]uit)')
                        failSearchQuery = input('')

                        if failSearchQuery == 's':
                            searchAgain = True
                            break

                        elif failSearchQuery == 'l':
                            tryLink = True
                            break

                        elif failSearchQuery == 'q':
                            return

                        else:
                            print('Invalid Input!')

            elif searchRequest == 'l':
                break

            else:
                print('Invalid input!')

            if tryLink == True:
                break

        if mangaFound == False:
            print()
            print('Please enter the url of the manga you wish to download or [q]uit: ')
            urlRequest = input('')

            if urlRequest == 'q':
                return
            
        else:
            urlRequest = 'http://www.mangapanda.com' + searchedMangaLink 

        #take the URL the user gave and cut off last five characters (.html)
        try:
            urllibHTML = urllib.request.urlopen(urlRequest).read()
            urlRequest = urlRequest[:-5]

        except:
            print()
            print('Invalid URL!')
            downloadManga = False

            #links to chapters on mangapanda are identified by the class 'chico_manga'
        if downloadManga == True:
            allChaps = re.findall(r'<div class="chico_manga"></div>\\n<a href="+(.*?)\">+', str(urllibHTML))

            numOfChapLinks = len(allChaps)
            
            #However the 6 most recent chapters are also under the 'chico_manga' class
            #so it is necessary to pop those chapters off and if there are not a total
            #of 6 chapters in the manga we have special cases
            if numOfChapLinks < 12:

                if numOfChapLinks == 10:
                    for i in range(5):
                        allChaps.pop(0)
                    
                elif numOfChapLinks == 8:
                    for i in range(4):
                        allChaps.pop(0)

                elif numOfChapLinks == 6:
                    for i in range(3):
                        allChaps.pop(0)

                elif numOfChapLinks == 4:
                    for i in range(2):
                        allChaps.pop(0)

                elif numOfChapLinks == 2:
                    allChaps.pop(0)

                else:
                    print('There was an error parsing the HTML!')

            else:
                for i in range(6):
                    allChaps.pop(0)

            #Rather conveniently, there is a class called 'aname' which contains the name of the manga
            grabName = re.findall(r'<h2 class="aname">+(.*?)\</h2>+', str(urllibHTML))

            #some mangas contained characters in aname which cannot be used in windows directories
            #these statements attempt to make said strings directory friendly
            directorySafeName = grabName[0]
            directorySafeName = directorySafeName.replace("/", " over ")
            directorySafeName = directorySafeName.replace(":", "")
            directorySafeName = directorySafeName.replace("?", "")
            directorySafeName = directorySafeName.replace("+", "")
            directorySafeName = directorySafeName.replace("\"","'")
            directorySafeName = directorySafeName.replace("%", " Percent")
            directorySafeName = directorySafeName.replace("<", "")   
            directorySafeName = directorySafeName.replace(">", "")

            if platformType == 'Windows':
                directoryName = currentDirectory + "\\MangaPanda\\" + str(directorySafeName)

            else:
                directoryName = currentDirectory + "/MangaPanda/" + str(directorySafeName)

            try: 
                os.makedirs(directoryName)    

            except OSError:                    
                if not os.path.isdir(directoryName):
                    raise

            os.chdir(directoryName)

            #loops chapter URLs to determine chapter number for both types of URLs
            chapterNames = []
            for i in range(len(allChaps)):
                chapterNum = re.findall('((?:\d)+)', allChaps[i])
                chapterNames.append(chapterNum[-1])
            
            fullDownload = False
            while 1:
                print('Do you wish to download the entire manga?[y/n]')
                continueChoiceFullDownload = input('')

                if continueChoiceFullDownload == 'y':
                    fullDownload = True
                    break

                elif continueChoiceFullDownload == 'n':
                    break

                else:
                    print('Invalid Option!')

            #Inquires the user if they wish to start from a specific chapter instead of downloading them all
            customStart = False
            chapterFound = False
            startLocation = 0

            if fullDownload == False:
                while 1:
                    print('Do you wish to start download from a certain chapter?[y/n]')
                    continueChoiceCustomChap = input('')

                    if continueChoiceCustomChap == 'y':
                        print('Please enter the chapter you wish to start from.')
                        chapNum = input('')

                        for i in range(len(chapterNames)):
                            if chapNum == chapterNames[i]:
                                chapterFound = True
                                customStart = True
                                startLocation = i

                        if chapterFound == False:
                            print('Invalid chapter number! Maybe the chapter is missing?')
                            print()

                        else:
                            break

                    elif continueChoiceCustomChap == 'n':
                        break

                    else:
                        print('Invalid Option!')
                        print()

            singleChapter = False
            validRange = False
            firstChap = 0
            lastChap = 0
            onlyChap = 0
            if customStart == False and fullDownload == False:
                while 1:
                    print('Do you wish to download a specific range of chapters? (or a single chapter?)')
                    print('[y/n]')
                    continueChoiceRangeChap = input('')

                    if continueChoiceRangeChap == 'y':
                        print('Please enter the range (in format 34-65) with no spaces or a single number for') 
                        print('one chapter.')
                        chapterRange = input('')

                        #looks for the pattern 23-32, the numbers can be of any size
                        rangeString = re.findall('((?:\d+)[-/.](?:\d+))', chapterRange)
                        if len(rangeString) == 0:
                            #if that pattern is not detected it looks for a single number of any size
                            singleString = re.findall('((?:\d)+)', chapterRange)

                            if len(singleString) == 0:
                                print('That is an invalid range!')
                                print()

                            elif len(singleString) == 1:
                                for i in range(len(chapterNames)):
                                    if singleString[0] == chapterNames[i]:
                                        singleChapter = True
                                        onlyChap = i

                            else:
                                print('That is an invalid range!')
                                print()

                        elif len(rangeString) == 1:
                            #if pattern is valid look for the individual numbers
                            startAndEnd = re.findall('((?:\d)+)', rangeString[0])

                            if int(startAndEnd[1]) - int(startAndEnd[0]) > 0:
                                firstChapFound = False
                                lastChapFound = False

                                #we can always assume that the length of startAndEnd is 2
                                for i in range(len(startAndEnd)):
                                    for k in range(len(chapterNames)):

                                        if startAndEnd[i] == chapterNames[k]:

                                            if i == 0:
                                                firstChap = k
                                                firstChapFound = True

                                            if i == 1:
                                                lastChap = k
                                                lastChapFound = True

                                if firstChapFound == True and lastChapFound == True:
                                    validRange = True

                            #if the range is just one number (ex. 61-61) we only download that chapter
                            elif int(startAndEnd[1]) - int(startAndEnd[0]) == 0:

                                for i in range(len(chapterNames)):
                                    if startAndEnd[0] == chapterNames[i]:
                                        singleChapter = True
                                        onlyChap = i

                            else:
                                print('That is an invalid range!')
                                print()

                        else:
                            print('That is an invalid range!')
                            print()

                        if singleChapter == True or validRange == True:
                            break

                        else:
                            print('That is an invalid range!')
                            print('')

                    elif continueChoiceRangeChap == 'n':
                        break

                    else:
                        print('Invalid Option!')
                        print()

            #If the user chose a custom start location pop all chapters before off
            if customStart == True:
                for i in range(startLocation):
                    allChaps.pop(0)
                    chapterNames.pop(0)

            if singleChapter == True:
                for i in range(onlyChap):
                    allChaps.pop(0)
                    chapterNames.pop(0)

                for i in range(len(allChaps)-1):
                    allChaps.pop(-1)
                    chapterNames.pop(-1)

            if validRange == True:
                for i in range(firstChap):
                    allChaps.pop(0)
                    chapterNames.pop(0)

                for i in range(len(allChaps)-(lastChap-firstChap)-1):
                    allChaps.pop(-1)
                    chapterNames.pop(-1)


            if fullDownload == True or customStart == True or singleChapter == True or validRange == True:

                for i in range(len(allChaps)):

                    if platformType == 'Windows':
                        chapDirectoryName = directoryName + "\\Chapter " + str(chapterNames[i])

                    else:
                        chapDirectoryName = directoryName + "/Chapter " + str(chapterNames[i])

                    try: 
                        os.makedirs(chapDirectoryName)    

                    except OSError:                    
                        if not os.path.isdir(chapDirectoryName):
                            raise

                    os.chdir(chapDirectoryName)

                    #There are some special cases associated with the first loop through the chapter
                    isFirstLoopPage = True

                    chapURL = "http://www.mangapanda.com" + allChaps[i]
                    print("Downloading Chapter", str(chapterNames[i]))

                    imageLocation = 0

                    while 1:
                        try:
                            imageLocation += 1

                            #Looks at page URLs for any and all sequences of numbers
                            nextChapDetermine = re.findall('((?:\d)+)', chapURL)

                            urllibHTML = urllib.request.urlopen(chapURL).read()

                            if isFirstLoopPage == True:
                                determineAmountOfPages = re.findall('<option value="+(.*?)\</option>', str(urllibHTML))

                            if len(determineAmountOfPages) == imageLocation - 1:
                                break

                            #Checks the number of files in directory in comparison to the number of images in the chapter
                            #If the number is the same the assumption is made that all images have been downloaded
                            if isFirstLoopPage == True:
                                isFirstLoopPage = False
                                numOfFileInCWD = len([name for name in os.listdir('.') if os.path.isfile(name)])
                                if numOfFileInCWD == len(determineAmountOfPages):
                                    break
                        
                            #grabs both the next page URL and the URL for the image on the current page
                            URLandIMG = re.findall(r'<div id="imgholder">+(.*?)\" alt=+', str(urllibHTML))
                            nextPageURL = re.findall(r'<a href="+(.*?)\">', URLandIMG[0])
                            imageURL = re.findall(r'src="+(.*?)\.jpg', URLandIMG[0])
                        
                            imageName = "Page " + str(imageLocation) + ".jpg"
                            fileExists = os.path.isfile(imageName)

                            #Old code that would put each page thats currently downloading on a new line
                            #print("Downloading Page", imageLocation) 
                            
                            #New code that will overwrite each "Downloading Page #" with the next page 
                            #and will eventually be overwrote by the "Downloading Chapter #"
                            print("Downloading Page %d" % imageLocation, end="", flush=True)
                            print("\r", end="", flush=True)

                            #If file does not already exist, opens a file, writes image binary data to it and closes
                            if fileExists == False:
                                rawImage = urllib.request.urlopen(imageURL[0] + ".jpg").read()
                                fout = open(imageName, 'wb')       
                                fout.write(rawImage)                          
                                fout.close()
                        
                            chapURL = "http://www.mangapanda.com" + nextPageURL[0]

                        #Probably need to do more with this error
                        except:
                            print("Invalid URL Error!")
                            return
            
                while 1:
                    print('Do you wish to download another manga?[y/n]')
                    continueChoice = input('')

                    if continueChoice == 'y':
                        break

                    elif continueChoice == 'n':
                        success = True
                        break

                    else:
                        print('Invalid Option!')

main()
