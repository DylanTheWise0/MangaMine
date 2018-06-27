#Ver. 0.1.0
#Authors: Dylan Wise & Zach Almon

import urllib.request
import re
import os
import platform
import sys
import string
import html

platformType = platform.system()

#Check All .re Expressions      DONE

#Fix Chapter Names              DONE
#Make Sure Titles are Good.     DONE

#BUG: Manga doesnt have Chapters but is listed by volume only instead:
#       (http://bato.to/comic/_/comics/tenshi-no-kiss-r3789) As Example

#BUG: Because some chapter names are Weird (IE. 15.5 or 15v3 or 20 (v2) or Non-Numbers)
#       You wont be able to START or END at those chapters. Entered chapters HAVE To be ints
#       This is to check that Start < End and also to size the lists according to the Start and/or End

#BUG: Because there can be chapters that arnt numbers There ARE Bugs with poping off the chapters with custom starts and ends because
#       each item is converted to floats. This is similar yet different then the above bug and WILL Cause some breaking in the program



def main():

    success = False

    currentDirectory = os.getcwd()
    if platformType == 'Windows':
        MASTERdirectoryName = currentDirectory + "\\Batoto"
    else:
        MASTERdirectoryName = currentDirectory + "/Batoto"

    try: 
        os.makedirs(MASTERdirectoryName)
    except OSError:                    
        if not os.path.isdir(MASTERdirectoryName):
            raise

    #MASTERdirectoryName is the Variable that will keep the program downloading
    #Different Manga to the same Batoto Folder
    os.chdir(MASTERdirectoryName)

    #NO SEARCH FEATURE SORRY!
    print('Currently MangaMine2 only supports Bato.to.')
    print()
    print('The URL you are to input below should be the top level page of the')
    print('manga you wish to download')
    print('Ex: http://bato.to/comic/_/comics/seto-no-hanayome-r385 ')

    while success == False:
        downloadManga = True
        type_one_manga = False
        type_two_manga = False

        print()
        print('Please enter the url of the manga you wish to download (or q to quit): ')
        urlRequest = input('')
        print('\n')

        if urlRequest == 'q':
            return

        try:
            urllibHTML = urllib.request.urlopen(urlRequest).read()

        except:
            print()
            print('Invalid URL!')
            downloadManga = False

        if downloadManga == True:

            Manga_Title = re.findall(r'<title>+(.*?)- Scanlations', str(urllibHTML))

            if len(Manga_Title) == 0:
                print("Title not found. URL or HTML Error.")
                return
            
            Manga_Title_string = Manga_Title[0]
            Manga_Title_string = Manga_Title_string[:-1]

            Manga_Title_string = re.sub(r'\\x\w{2}', r' ', Manga_Title_string)

            
            #Python 3.4 Converts '&amp;' Type things to their string equivalent. 
            Manga_Title_string = html.unescape(Manga_Title_string)

            #Get rid of Non-Functioning characters for Filenames
            directorySafeName = Manga_Title_string
            directorySafeName = directorySafeName.replace("/", " over ")
            directorySafeName = directorySafeName.replace(":", "")
            directorySafeName = directorySafeName.replace("?", "")
            directorySafeName = directorySafeName.replace("+", " plus ")
            directorySafeName = directorySafeName.replace("\"","'")
            directorySafeName = directorySafeName.replace("%", " Percent ")
            directorySafeName = directorySafeName.replace("<", "")   
            directorySafeName = directorySafeName.replace(">", "")

            Manga_Title_string = directorySafeName

            #For any other language on Bato.to change lang_English to whatever matches the language you desire. 
            #Then this file *SHOULD* work with your language
            allENGLISHChaps = re.findall(r'lang_English+(.*?)\ title="+', str(urllibHTML))
            
            if len(allENGLISHChaps) == 0:
                print("Manga has no English Chapters or there was an error reading the HTML!")
            else:
                First_chapter_string = allENGLISHChaps[-1]
                First_chapter_address = re.findall(r'href=\"+(.*?)\"', First_chapter_string)
                First_chapter_address_string = First_chapter_address[0]
                
                try:
                    First_chapter_html = urllib.request.urlopen(First_chapter_address_string).read()
                except:
                    print()
                    print('Trouble Opening Webpage!')
                    downloadManga = False

                if downloadManga == True:
                    #Find which type of manga this manga is. Whether all pages of the chapter are on one page or multiple pages.
                    type_one_padding_right = re.search("<div style=\"text-align:center;\">", str(First_chapter_html))
                    type_two_comic_page = re.search("comic_page", str(First_chapter_html))
                    #THERE IS A THIRD TYPE!?!?! http://bato.to/comic/_/comics/gaussian-blur-r8172


                    #Type one is All images on One Page
                    if type_one_padding_right != None:
                        type_one_manga = True
                    #Type two is All images on seperate pages
                    elif type_two_comic_page != None:
                        type_two_manga = True
                    else:
                        print("There was an error with the Manga Type!")
                        return

                    
                    #This will get the chapter links from the Select options on the chapters first page
                    #There are 2 select options (one at top and one at bottom
                    #They are same so its arbutrary which you pick. I Will be selecting [0]
                    get_Chapters = re.findall(r'250px;">+(.*?)</select>', str(First_chapter_html))

                    chapter_master_string = get_Chapters[0]

                    #Get all chapter links. Last thing in list is an unneeded "selected" string. Pop that off.
                    list_of_Chapter_Links = re.findall(r'\"+(.*?)\"', chapter_master_string)

                    #In this list there may be a "selected". It may or may not be at the end. The loop solves it.
                    #I am 95% sure there will only ever be 1 "selected" per list.
                    #list_of_Chapter_Links.pop(-1)
                    for i in range(len(list_of_Chapter_Links)):
                        if list_of_Chapter_Links[i] == "selected":
                            list_of_Chapter_Links.pop(i)
                            break

                    #Get Numbers of the chapters. Will be "Matched" up to the list_of_Chapter_Links.
                    list_of_Chapter_Numbers_raw = re.findall(r'Ch\.+(.*?)<', chapter_master_string)
                    list_of_chapter_names_refined = []

                    #   EXCEPTION HERE (http://bato.to/comic/_/comics/tenshi-no-kiss-r3789)
                    # GOES BY VOLUME NOT CHAPTER. BY THIS METHOD IT WONT WORK

                    #Some chapters may be like "230: Title of Chapter" Some may be "145"
                    for i in range(len(list_of_Chapter_Numbers_raw)):
                        temp_list = re.findall('^(.*?):', list_of_Chapter_Numbers_raw[i])

                        if len(temp_list) == 0:
                            list_of_chapter_names_refined.append(list_of_Chapter_Numbers_raw[i])
                        elif len(temp_list) == 1:
                            list_of_chapter_names_refined.append(temp_list[0])
                        else:
                            print("Manga Chapter Name Error!")
                            return
                    
                    # list_of_Chapter_Links             Has Links    -Has Duplicates at this point
                    # list_of_chapter_names_refined     Has Names    -Has Duplicates at this point


                    list_of_Chapter_Links_Final = []
                    list_of_Chapter_Numbers_Final = []

                    for i in range(len(list_of_chapter_names_refined)):

                        if list_of_chapter_names_refined[i] in list_of_Chapter_Numbers_Final:
                            pass
                        else:
                            list_of_Chapter_Numbers_Final.append(list_of_chapter_names_refined[i])
                            list_of_Chapter_Links_Final.append(list_of_Chapter_Links[i])

                    
                    list_of_Chapter_Links_Final.reverse()
                    list_of_Chapter_Numbers_Final.reverse()


                    fullDownload = False
                    chapter_found = False
                    custom_start = False
                    custom_end = False
                    chapter_to_start_from = 0
                    chapter_to_end_at = 0
                
                    while 1:
                        print('Do you wish to download the entire manga?[y/n], or [q] to quit.')
                        continueChoiceFullDownload = input('')
                        print('\n')

                        if continueChoiceFullDownload == 'y':
                            fullDownload = True
                            break

                        elif continueChoiceFullDownload == 'n':
                            while 1:
                                print('Do you wish to start download from a certain chapter?[y/n], or [q] to quit.')
                                print('By Choosing no the entire manga will download')
                                continueChoiceCustomChap = input('')
                                print('\n')

                                try:
                                    if continueChoiceCustomChap == 'y':
                                        print('Please enter the chapter you wish to start from')
                                        chapNum = input('')
                                        print('\n')
                                    
                                        for i in range(len(list_of_Chapter_Numbers_Final)):
                                            if chapNum == list_of_Chapter_Numbers_Final[i]:
                                                chapter_found = True
                                                custom_start = True
                                                chapter_to_start_from = int(list_of_Chapter_Numbers_Final[i])
                                                break
                            
                                        if chapter_found == False:
                                            print('Invalid chapter number! Maybe the chapter is missing?')
                                            print()

                                        else:
                                            print('Chapter Found!')
                                            print('\n')
                                            #May use chapter_found again for the end point
                                            chapter_found = False
                                            break

                                    elif continueChoiceCustomChap == 'n':
                                        fullDownload = True
                                        break
                                
                                    elif continueChoiceCustomChap == 'q':
                                        return

                                    else:
                                        print('Invalid Option!')
                                        print()

                                except ValueError:
                                    print('Invalid chapter number!')
                                    print('Numbers must be whole numbers. You cannot start at a half chapter')
                                    print('\t Or at a non-numerical chapter.')
                                    print('Please enter a Real Number!')
                                    print('\n')
                        
                            if fullDownload == False:
                                while 1:
                                    print('Do you wish to end the download at a certain chapter?[y/n], or [q] to quit.')
                                    print('By Choosing no the entire manga will download from the start location')
                                    continueChoiceCustomChap = input('')
                                    print('\n')
                                
                                    if continueChoiceCustomChap == 'y':
                                        print('Please enter the chapter you wish to end at')
                                        chapNum = input('')
                                        print('\n')

                                        #Check if number entered is actually a number or not.
                                        try:
                                            temporary_int = int(chapNum)

                                            #END CHAPTER MUST BE BIGGER OR EQUAL TO THAN START CHAPTER
                                            if temporary_int < chapter_to_start_from:
                                                print('Sorry, Number must be greater than the Start chapter, which is:', chapter_to_start_from)
                                                print('Invalid Option!')
                                                print()

                                            else:
                                                for i in range(len(list_of_Chapter_Numbers_Final)):
                                                    if chapNum == list_of_Chapter_Numbers_Final[i]:
                                                        chapter_found = True
                                                        custom_end = True
                                                        chapter_to_end_at = chapNum
                                                        break
                            
                                                if chapter_found == False:
                                                    print('Invalid chapter number! Maybe the chapter is missing?')
                                                    print()

                                                else:
                                                    print('Chapter Found!')
                                                    print('\n')
                                                    break
                                        except ValueError:
                                            print('Invalid chapter number!')
                                            print('Numbers must be whole numbers. You cannot end at a half chapter')
                                            print('\t or a non-numerical chapter.')
                                            print('Please enter a Real Number!')
                                            print('\n')
                                            

                                    elif continueChoiceCustomChap == 'n':
                                        break
    
                                    elif continueChoiceCustomChap == 'q':
                                        return

                                    else:
                                        print('Invalid Option!')
                                        print()
                            #At the end of the elif choice == no
                            break
    
                        elif continueChoiceFullDownload == 'q':
                            return

                        else:
                            print('Invalid Option!')
                
                    #For Reference:
                    #If fullDownload = True  
                            #The user wants to download From chapter 1 to the end (Whatever is available)
                    #If custom_start = True Than fullDownload == False  
                            #The user wants to download from The start chapter which was Found and stored in chapter_to_start_from
                            #Does not Need custom_end to be True. If it isnt then it will download until the end of manga
                    #If custom_end = True Than custom_start == True AND fullDownload == False                          
                            #The user wants to download from The start chapter which was Found and stored in chapter_to_start_from
                            #The user also wants to download until an end chapter which was Found and stored in chapter_to_end_at

                    currentDirectory = MASTERdirectoryName

                    if platformType == 'Windows':
                        manga_directory_name = currentDirectory + "\\" + Manga_Title_string
                    else:
                        manga_directory_name = currentDirectory + "/" + Manga_Title_string

                    try: 
                        os.makedirs(manga_directory_name)    
                    except OSError:                    
                        if not os.path.isdir(manga_directory_name):
                            raise

                    os.chdir(manga_directory_name)

                    first_page_of_first_chapter = False

                    #This if, elif, and elif are to set which chapters are to be downloaded.
                    if fullDownload == True:
                        first_page_of_first_chapter = True                      
                    #If you only have a start location, pop off chapter numbers/links until you hit that chapter
                    elif custom_start == True and custom_end == False:
                        for i in range(len(list_of_Chapter_Numbers_Final)):

                            try:
                                float_value = float(list_of_Chapter_Numbers_Final[0])
                                float_value_start = float(chapter_to_start_from)

                                if float_value < float_value_start:
                                    list_of_Chapter_Links_Final.pop(0)
                                    list_of_Chapter_Numbers_Final.pop(0)
                                else:
                                    break

                            except ValueError:
                                list_of_Chapter_Links_Final.pop(0)
                                list_of_Chapter_Numbers_Final.pop(0)

                    #Do same As before But will need to pop off end as well
                    #I found it easier to reverse then do down the list in decending order
                    #And pop off from begining until the end chapter is reached.
                    #Then reverse again.           
                    elif custom_start == True and custom_end == True:
                        for i in range(len(list_of_Chapter_Numbers_Final)):
                            try:
                                float_value = float(list_of_Chapter_Numbers_Final[0])
                                float_value_start = float(chapter_to_start_from)

                                if float_value < float_value_start:
                                    list_of_Chapter_Links_Final.pop(0)
                                    list_of_Chapter_Numbers_Final.pop(0)
                                else:
                                    break

                            except ValueError:
                                list_of_Chapter_Links_Final.pop(0)
                                list_of_Chapter_Numbers_Final.pop(0)
                        
                        list_of_Chapter_Numbers_Final.reverse()
                        list_of_Chapter_Links_Final.reverse()

                        for i in range(len(list_of_Chapter_Numbers_Final)):
        
                            try:
                                float_value = float(list_of_Chapter_Numbers_Final[0])
                                float_value_end = float(chapter_to_end_at)

                                if float_value > float_value_end:
                                    list_of_Chapter_Links_Final.pop(0)
                                    list_of_Chapter_Numbers_Final.pop(0)
                                else:
                                    break

                            except ValueError:
                                list_of_Chapter_Links_Final.pop(0)
                                list_of_Chapter_Numbers_Final.pop(0)

                        list_of_Chapter_Numbers_Final.reverse()
                        list_of_Chapter_Links_Final.reverse()
                    
                    #Main Loop for Downloading Images.         
                    if fullDownload == True or custom_start == True:
                        for i in range(len(list_of_Chapter_Numbers_Final)):
                        
                            first_page_of_each_chapter = True
                            chapter_number = list_of_Chapter_Numbers_Final[i]
                            chapter_link = list_of_Chapter_Links_Final[i]

                            
                            if platformType == 'Windows':
                                chapDirectoryName = manga_directory_name + "\\Chapter " + chapter_number
                            else:
                                chapDirectoryName = manga_directory_name + "/Chapter " + chapter_number

                            try: 
                                os.makedirs(chapDirectoryName)    
                            except OSError:                    
                                if not os.path.isdir(chapDirectoryName):
                                    raise

                            os.chdir(chapDirectoryName)

                            print("Downloading Chapter", chapter_number)

                            #I ALREADY HAVE THE FIRST PAGE OF FIRST CHAPTER
                            #Check Then move on makes it a bit quicker but not by much.
                            if first_page_of_first_chapter == True:
                                #This variable is set to False then ONLY set to true during Full Downloads 
                                #when the first chapter is Gurenteed to be downloaded
                                first_page_of_first_chapter = False
                                urllibHTML = First_chapter_html
                            else:
                                urllibHTML = urllib.request.urlopen(list_of_Chapter_Links_Final[i]).read()
                            
                            if type_one_manga == True:
                                get_images = re.findall(r'text-align:center;">+(.*?)</div><div', str(urllibHTML))
                                get_images_master_string = get_images[0]
                                image_file_name_list = re.findall(r"<img src=\\'(.*?)\\'", str(get_images_master_string))

                                Amount_of_pages = len(image_file_name_list)

                                for j in range(len(image_file_name_list)):

                                    if first_page_of_each_chapter == True:
                                        first_page_of_each_chapter = False
                                        numOfFileInCWD = len([name for name in os.listdir('.') if os.path.isfile(name)])
                                        if numOfFileInCWD == Amount_of_pages:
                                            break

                                    image_file_name = image_file_name_list[j]
                                    image_file_extension_list = re.findall(r'(\.\D[^\.]+)', image_file_name)
                                    image_file_extension = image_file_extension_list[-1]

                                    imageName = "Page " + str(j+1) + image_file_extension

                                    print("Downloading Page %d" % (j+1), end="", flush=True)
                                    print("\r", end="", flush=True)

                                    fileExists = os.path.isfile(imageName)
                                    #If file does not already exist, opens a file, writes image binary data to it and closes
                                    if fileExists == False:
                                        rawImage = urllib.request.urlopen(image_file_name).read()
                                        fout = open(imageName, 'wb')       
                                        fout.write(rawImage)                          
                                        fout.close()
                            
                            elif type_two_manga == True:
                                #Get the pages between "<id..." and "</se..."
                                get_Pages = re.findall(r'id="page_select" onchange="window.location=this.value;">+(.*?)</select></li>', str(urllibHTML))
                                #There will be Two found
                                Pages_master_string = get_Pages[0]

                                #Get all page links. Second thing in list is an unneeded "selected" string. Loop to get rid
                                list_of_page_Links = re.findall(r'\"+(.*?)\"', Pages_master_string)

                                list_of_page_links_final = []
                                #Loop to rid of the "Selected" part of list
                                for j in range(len(list_of_page_Links)):
                                    if list_of_page_Links[j] != "selected":
                                        list_of_page_links_final.append(list_of_page_Links[j])
    
                                Amount_of_pages = len(list_of_page_links_final)
                                
                                for j in range(len(list_of_page_links_final)):
                                    try:
                                        print("Downloading Page %d" % (j+1), end="", flush=True)
                                        print("\r", end="", flush=True)

                                        #Check for First page. Checks to see if anything is already downloaded
                                        if first_page_of_each_chapter == True:
                                            first_page_of_each_chapter = False
                                            numOfFileInCWD = len([name for name in os.listdir('.') if os.path.isfile(name)])
                                            if numOfFileInCWD == Amount_of_pages:
                                                break
                                            #At this point There will be something you need to download.
                                            #Since we already have the HTML for the first page of EACH Chapter
                                            #We dont need to waste time to read that again, set it here.
                                            page_urllibHTML = urllibHTML
                                        else:
                                            page_urllibHTML = urllib.request.urlopen(list_of_page_links_final[j]).read()

                                        #Get Image URL
                                        image_file_name_list = re.findall(r'comic_page" style="max-width: 100%;" src="(.*?)"', str(page_urllibHTML))
                                        image_file_name = image_file_name_list[0]
                                        #CHECK EXTENSION. Bato.to Could use .png or .jpg or .jpeg
                                        image_file_extension_list = re.findall(r'(\.\D[^\.]+)', image_file_name)
                                        image_file_extension = image_file_extension_list[-1]

                                        imageName = "Page " + str(j+1) + image_file_extension
                                        fileExists = os.path.isfile(imageName)

                                        #If file does not already exist, opens a file, writes image binary data to it and closes
                                        if fileExists == False:
                                            rawImage = urllib.request.urlopen(image_file_name).read()
                                            fout = open(imageName, 'wb')       
                                            fout.write(rawImage)                          
                                            fout.close()

                                    except:
                                        print("Invalid URL Error, or Connection Timeout!")
                                        return
                            else:
                                print("Manga Type Error!")
                                return


                    while 1:
                        print('\n')
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

