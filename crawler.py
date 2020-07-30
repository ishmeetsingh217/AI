import re
from html.parser import HTMLParser
from urllib.request import urlopen
from googlesearch import search
import os
import sys
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Get path of topic and doc files
basepath = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(basepath, "dataset")
# Check dataset folder exist and make
if not os.path.exists(dataset_path):
    os.mkdir(dataset_path)

# Get data from HTML page
class LinkParser(HTMLParser):

    def get_links(self, url):
        self.links = []
        self.base_url = url
        # Get web page content as response
        response = urlopen(url)
        # Read response
        html_bytes = response.read()
        # Get content as string with utf-8
        html_string = html_bytes.decode("utf-8")
        self.feed(html_string)
        return html_string, self.links

# Remove substring between from start to end
def remove_between(document, start_str, end_str):

    while start_str in document and end_str in document:
        # Get start and end index
        start_str_index = document.find(start_str)
        end_str_index = document.find(end_str, start_str_index) + len(end_str) - 1
        # get new content without from start to end
        document = document[0: start_str_index] + document[end_str_index + 1: len(document)]
    return document

# Get substring between from first to last
def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

# Function that get content of web page
def parsePage(website_url):

    parser = LinkParser()
    # Get web page content
    name = ""
    data = ""
    # Get document from url
    loop_data = True
    while loop_data:
        try:
            data, links = parser.get_links(website_url)
            loop_data = False
        except:
            return [],"",False
    # Get name of files
    if "title" in str(data):
        name = str(find_between_r(str(data),"<title>","</title>")) + ".txt"
        if "|" in name:
            name = name.replace("|","")
        elif ":" in name:
            name = name.replace(":","")
        elif ";" in name:
            name = name.replace(";","")
        elif "&" in name:
            name = name.replace("&","")
        else:
            pass
    else:
        name = str(website_url).split("/")[-2] + "_" + str(website_url).split("/")[-1]
        if "_" == name[-1]:
            name = name[:-1] + ".txt"
        else:
            name = name + ".txt"
    if "\n" in name:
        name = name.replace("\n", "")
    if "\r" in name:
        name = name.replace("\r", "")
    if "\t" in name:
        name = name.replace("\t", "")
    # Remove several parts that dont need
    data = remove_between(data, "<script>", "</script>")
    data = remove_between(data, "<script", "</script>")
    data = remove_between(data, "<footer", "</footer>")
    data = remove_between(data, "<style>", "</style>")
    data = remove_between(data, "<head>", "</head>")
    data = remove_between(data, "<!--", "-->")
    data = re.sub(">", "> ", data)
    data = remove_between(data, "<", ">")
    data = re.sub("[\r]", " ", data)
    data = re.sub("[\n]", " ", data)
    # Remove first and end spaces
    reallines = []
    lines = str(data).split(" ")
    for line in lines:
        if str(line) == "" or "" ==  str(line).strip(" "):
            continue
        else:
            reallines.append(line)
    factlines = []
    flag = True
    # Remove lines that dont need
    for line in reallines:
        if "&" in line:
            continue
        elif "\t" in line:
            line = line.replace("\t","")
        elif "," == line or '"' == line or ":" == line or "," == line or ")" == line or "(" == line or "^" == line or "|" == line:
            continue
        elif len(factlines) > 500:
            break
        factlines.append(line)
    if len(factlines) < 200:
        flag = False
    return factlines,name,flag

# function that out docs
def putfile(topic_word,urls):

    # Get topic path and make topic folder
    topic_path = os.path.join(dataset_path, topic_word)
    if not os.path.exists(topic_path):
        os.mkdir(topic_path)
    # Get words and make each doc files in topic folder
    k = 0
    file_index = 0
    for url in urls:
        if "(" in str(url):
            url = remove_between(str(url),"(",")")
        print(url)
        # Get data from HTML page
        lines,name,flag = parsePage(url)
        if not flag:
            continue
        elif k > 11:
            break
        # Get txt file path
        content_path = os.path.join(topic_path,name)
        if os.path.isfile(content_path):
            file_index = file_index + 1
            content_path = os.path.join(topic_path, str(file_index) + name)
            print(str(file_index) + name)
        else:
            print(name)
        array_index = 0
        line_index = 1
        # write the content and make the txt file
        with open(content_path, "w",encoding="utf-8") as file:
            for line in lines:
                while True:
                    try:
                        file.write("[" + str(line_index) + "]")
                        file.write(line)
                        file.write(" ")
                        line_index = line_index + 1
                        break
                    except Exception as error:
                        break
            file.close()
        k = k + 1

def main():

    loop_command = True
    while loop_command:
        try:
            topic = input("Please input topic : ")
            if topic == "quit":
                loop_command = False
                break
            my_results_list = []
            # Search and Get urls for topic
            for i in search(topic,  # The query you want to run
                            # tld='com',  # The top level domain
                            lang='en',  # The language
                            num=10,  # Number of results per page
                            start=0,  # First result to retrieve
                            stop=20,  # Last result to retrieve
                            pause=2.0,  # Lapse between HTTP requests
                            ):
                if "youtube" in str(i):
                    continue
                my_results_list.append(i)
            putfile(topic,my_results_list)
        except Exception as error:
            print("First step :",error)

main()


