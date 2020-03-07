
"""
This program was written for an introductory course in Python programming, hence the elaborate comments for each and every function
"""



"""
Make sure to first download the following modules and some of its components by running the 
following commands in the command line:
    
    pip install google-api-python-client                            This installs the API client necessary to analyze YouTube data
    pip install -U nltk                                             This installs the "Natural Language Toolkit" which is necessary to classify words by their function in a sentence
    python -m nltk.downloader universal_tagset                      This extension for the nltk module installs the tagset necessary to run our analysis of words in a comment
    python -m nltk.downloader averaged_perceptron_tagger            This extension for the nltk module installs the tool necessary to run our analysis of words in a comment
    python -m nltk.downloader punkt                                 Downloading this extension prevents a certain type of error occurring randomly
    
    
This program opens a tkinter window in which you can specify the URL of a random YouTube video of which
you would like to analyze the comment section. It then opens another window with a graph showing
the frequency in which the 20 most used words appears in the comment section. 
Warning: for videos with above 50.000 comments it can take about 5 minutes to analyze.
"""
# The following modules are used throughout this script. 
# Their purpose will be explained in the context of where they are used.
from apiclient.discovery import build
import re 
import tkinter as tk
from tkinter import messagebox
from urllib.parse import urlparse
import nltk
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def save_output():
# This function saves the output of the program when the user presses a certain button (which is defined later on).
    plt.savefig("Output comment section.pdf") # Saves the plot as a .pdf file in the current working directory.
    messagebox.showinfo("Output saved", "Output was saved as .pdf file in the current working directory." )
    # When the function is done, a message is displayed to let the user know the output was saved.
    
def analyze_comments(video_id):
# This function gets the data from a YouTube video id that is obtained from the URL
# that is obtained from the tkinter box specified later on. The function is called when 
# the user submits its input in the tkinter window specified below.
    api_key = "xxx" 
    # This API key must be obtained from Google. Every project that analyzes Google data 
    # must first register their project. Then, an API key can be requested for that project.
    # The key is needed to access YouTube data through certain functions.
    # Also, for usage of one API key there a daily quota of 100 units. Analyzing one comment section costs
    # 1 unit, so the program may break down in case of overusage. 
    
    youtube = build('youtube', 'v3', developerKey = api_key)
    # This variable gives access to all data from YouTube. The build command is imported 
    # from Google's API client library module. 
    results = youtube.commentThreads().list(part='snippet', 
                                            videoId=video_id, 
                                            textFormat='plainText',
                                            maxResults=100).execute()
    # Now, with the access to all YouTube data, we obtain some results. 
    # Specifically, with the .commentThreads().list() command, we store all data (in dictionary format) from the comment
    # section in the variable results. It downloads all data of the "snippet", which contains
    # the comments, commenter IDs, etc. The videoId argument takes the video id of the video
    # which comment section we want to analyze (it is equal to the part of a YouTube URL after "v=") The video id is obtained in a later function. 
    # The textformat is specified as plaintext, because it is easier than HTML format, and the max results
    # are set to 100, because that is the maximum amount you can retrieve in one go from a certain page.
    # Source: https://developers.google.com/youtube/v3/docs/commentThreads/list
    comments = [] 
    # This empty list will be filled with the text of every comment.
    
    while True: # Infinite while loop which only breaks when every page of the results is scraped for comments.
        # Source: based on https://stackoverflow.com/questions/34606055/how-to-get-comments-from-videos-using-youtube-api-v3-and-python
        # This loop is needed to collect info from every possible page of results, instead of just the first page.
        nextPageToken = results['nextPageToken'] 
        # This variable is equal to the "nextPageToken" of the current page of results. 
        # A nextPageToken is the pageToken (a kind of id for a certain page of results) of the next page
        results = youtube.commentThreads().list(
          part="snippet",
          videoId=video_id,
          pageToken= nextPageToken,
          textFormat="plainText",
          maxResults=100).execute()
        # This is largely the same command as was used to get the first page of results. 
        # Now, the argument pageToken= is added, which takes the nextPageToken as its current pageToken.
        # This makes sure the results of the next page are added to the variable results.
        for item in results["items"]:
              comment = item["snippet"]["topLevelComment"]
              text = comment["snippet"]["textDisplay"]
              comments.append(text)
        # This loop goes over every item of the results. For every item in the results page,
        # the loop finds a certain comment (denoted by "topLevelComment", whose information is
        # included in the snippet) and then finds the text (denoted by "textDisplay") of that specific comment.
        # Then, it adds the text of that comment to the list containing all comments.
        try:
            nextPageToken = results["nextPageToken"]
        # When all comments of a page of results are added to the list of comments, the nextPageToken variable
        # is set to the nextPageToken of the current page. So, when this command is performed, 
        # the loop starts again and takes the nextPageToken as its current pageToken, which
        # ensures that the program scrolls through every page of results.
        except KeyError:
            break
        # When there is no nextPageToken included on the current page of results, which is the case on 
        # every last page of results, the try command above will give a KeyError. When this happens,
        # the while loop will break because every comment has been scraped. 
    
    
    comments_all_together = ' '.join(comments) 
    # In order to analyze the content of the comments, we have to turn the list of comments into one large string.
    words_to_analyze = [] 
    # This empty list will contain the words we want to count. Not all words will be counted,
    # because otherwise every analysis of comments will look the same (i.e. with "is", 
    # "or", "and" being the most frequently used words)
    type_of_words_allowed = ["NOUN","ADJ"] 
    # In this list, we specify the words that our comment scraper should include in its count. 
    # In our case, we want to analyze nouns and adjectives, denoted by their ntlk specific tagnames.
    # If we also want to include verbs (which often come down to "are", "is", "have"), we just
    # add "VERB" to the list type_of_words_allowed.
    
    comments_separated = nltk.word_tokenize(comments_all_together)
    # Here, all words are separated from each other by making use of the ntlk module.
    # This command returns a list with every separate word, also separated from their special characters.
    # Source: https://www.nltk.org/book/ch05.html
    tags = nltk.pos_tag(comments_separated, tagset = 'universal')
    # This ntlk function returns a list with 2-tuples containing the word and its type,
    # following the "universal" tagset (i.e. verb = "VERB", adjective = "ADJ")
    # Sources:   https://www.nltk.org/book/ch05.html
    #           https://www.nltk.org/api/nltk.tag.html?highlight=.pos_tag#nltk.tag.pos_tag
    for word in tags:
        for word_type in type_of_words_allowed:
            if word[1] == word_type:
                words_to_analyze.append(word[0])
    # This for loop goes through every tuple in the "tags" list and checks if the type of the word
    # (which is at index 1) is equal to any of the types that we want to analyze (from the list type_of_words_allowed)
    # If the type of word is the type we want to analyze, it is added to the words_to_analyze list.
        
    most_common = dict(Counter(words_to_analyze).most_common(20))
    # Now, we want to count the amount of times a certain word appears in all comments. 
    # This statement (which makes use of the counter module) creates a dictionary called most_common
    # which includes the 20 most common words as the key and the amount of times they appear in the comments
    # as the respective value.
    # Source: https://docs.python.org/2/library/collections.html
    
    figure, canvas, window2 = ".", ".", "."
    # Clears the variables "figure", "canvas" and "window2" to make sure no data is stored in these windows
    # when the rest of the function tries to draw these. This makes sure that 
    # the window can analyze multiple videos in one session.
    
    window2 = tk.Tk() # Creates a window using tkinter
    window2.title("Results: Word use in comment section") # Sets the title of the tkinter window
    window2.geometry("%dx%d+%d+%d" % (w, h, w, h))
    # The .geometry command sets the dimensions of the window, and the location
    # of where the window should appear. In this case, the window is w x h (which is equal
    # to the dimensions of the screen, the w and h variables are defined later on in the code)
    # and the window appears starts in the top left corner, so that the window fills the 
    # entire screen. 
    # Source: based on https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
    
    figure = plt.figure(1, figsize = [w/100,h/100])
    # Creates a figure using matplotlib.pyplot (imported as plt). The size of the figure 
    # is equal to the size of the screen (the unit of measurement of dimensions in matplotlib is 
    # equal to 1/100 of the measurement unit used by tkinter above).
    plt.bar(range(len(most_common)), list(most_common.values()), align='center')
    plt.xticks(range(len(most_common)), list(most_common.keys()), fontsize = 8)
    # This section creates a bar chart out of the dictionary of words and their respective counts. 
    # First, creates 20 bars representing the counts of the words, and then it creates
    # the lables that need to appear on the x-axis, namely the words to which the count belong. 
    # Source on how to make a bar chart out of a dictionary:
    # https://stackoverflow.com/questions/16010869/plot-a-bar-using-matplotlib-using-a-dictionary
    
    plt.title("Frequency of words in comment section") # Creates a title for the bar chart
    
    canvas = FigureCanvasTkAgg(figure, master=window2) 
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
    # This section creates a tkinter canvas figure containing the bar chart that is created above. 
    # The FigureCanvasTkAgg command is imported from the matplotlib.backends.backend_tkagg module. 
    # It makes use of matplotlib's backend to be able to plot the data in a tkinter window. 
    # Source: https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html
   
    tk.Button(window2, text = "Save", width = 6, command=save_output).place(x = w/2, y = 5*h/6, anchor = "center")
    # Creates a button in the graph window called "Save" which saves the output as a .png file
    # in the current working directory.
    
    # This concludes the operations that need to be done to receive a frequency chart of a given
    # YouTube comment section. 
def valid_url(url): 
# This function is created to analyze the input that the user types in the tkinter window. 
# It is called everytime the player presses the submit button in the tkinter window. 
    youtube_url = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    # Creates a regular expression to which the URL that is entered in the function can be compared to 
    # check whether it is an actual YouTube URL.
    youtube_match = re.match(youtube_url, url)
    # Uses the regular expression module (re) to check whether the entered URL is an actual YouTube URL,
    # as defined above. Output is a boolean.
    if youtube_match:
        return youtube_match.group(6)
    # If the entered URL is an actual URL, it returns a boolean to outside of the function.
    # Source: https://stackoverflow.com/questions/4705996/python-regex-convert-youtube-url-to-youtube-video

def click():
# This function is used to define what the program needs to do when the "start" button of the tkinter
# window is pressed. 
    entered_text=textentry.get() # entered_text is defined as the string that is put in the text entry window
    if valid_url(entered_text): 
    # Checks whether the entered text is an actual YouTube URL by calling the valid_url function.
        messagebox.showinfo("Processing", "We will start analyzing the comment section. This may take a while depending on the size of the comment thread. Please press OK to proceed.")
        # Displays a message box when the URL is valid.
        parsed_url = urlparse(entered_text)
        # Here, the input URL is parsed by making use of the urlparse command from the
        # urllib.parse module. parsed_url is a list containing all components of a URL.
        # The URL needs to be parsed because the YouTube api client needs only the video id
        # as input to get results, not the entire URL.
        video_id = parsed_url[4][2:]
        # The video id is contained within the query part of a URL. The query is located in
        # the 4th index of parsed_url. The query starts with "v=", which is not part of the video id,
        # but the rest is. So, from the 4th index of parsed_url, we need everything from the 2nd index onward.
        #Source: https://docs.python.org/3.2/library/urllib.parse.html
        try:
            analyze_comments(video_id) # Calls the analyze_comments function defined above and takes the video id as input.
        except:
            messagebox.showinfo("Error", "Please try again, something went wrong while interpreting the results. Check the console whether there are any additional modules you might have to install.")
            # When something goes wrong in the analyze_comments function, an error message is displayed.
    else:
        messagebox.showinfo("Error", "Please fill in a valid Youtube URL" )
        # If the input URL is not a valid YouTube URL, the program displays an error window and the 
        # user can try again.

window = tk.Tk() # Creates the main window in which the user will have to give his/her input.

w , h = window.winfo_screenwidth(), window.winfo_screenheight()
# Creates variables w(idth) and h(eight) which are equal to the width and height of the screen respectively.
# Source: based on https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
window.geometry("%dx%d+%d+%d" % (w, h, w, h))
# The main tkinter window's dimensions are set to the dimensions of the screen, and the window
# starts in the top left corner of the screen (as done before for the graph window). 
window.title("YouTube Comment Analyzer") # Sets the title of the main window.
window.configure(background = "brown") # Sets the background color of the main window.

tk.Label (window, text = "YouTube Comment Analyzer", 
       bg = "brown", fg="white", 
       font="none 26 bold underline").place(x = w/2, y = h/5, anchor="center")
tk.Label (window, text = "By: Axel van 't Westeinde, Hessel Tabor and Daan van den Bremen", 
       bg = "brown", fg="black", font="none 12 italic") .place(x = w/2, y = h/4, anchor="center")
tk.Label (window, text = "Please enter the URL of the YouTube video comment section you want to analyze:", 
       bg = "brown", fg="white", font="none 16 bold") .place(x = w/2, y = h/3, anchor = "center")
# This section creates some text to be displayed in the main window. Our color scheme is equal to red, white and black
# in line with the original YouTube theme. The locations of the text are set with respect to the height and width
# of the screen it is displayed on. Every line of text is centered, and the vertical positions of the lines 
# are at 1/5th, 1/4th and 1/3rd the height of the screen.

textentry = tk.Entry(window, width = 40, bg = "white")
textentry.place(x = w/2, y = h/2, anchor = "center")
# This section creates a text entry window in which the user will input the URL. 
# The text entry window is located in the center of the screen, at half the width and half the height
# of the screen. 

tk.Button(window, text = "Start", width = 6, command=click).place(x = w/2, y = 2*h/3, anchor = "center")
# Creates a start button which calls the "click" function defined above (which in turn calls the other functions)
# The button is located at half the width of the screen and at 2/3rd of the height of the screen. 

tk.mainloop()
# Makes sure that tkinter goes to work.

#Source: https://www.youtube.com/watch?v=_lSNIrR1nZU - Learn Tkinter in 20 minutes - Teacher of Computing - 16/01/17

