import io
import os
import argparse
import platform
import requests
import progressbar
from bs4 import BeautifulSoup


def help():
    return """
        to set [Link] send with "" :>
        app.py "Link" [quality] [directory]
        python app.py "https://www.aparat.com/v/xxxxxx"
        python app.py "https://www.aparat.com/v/xxxxxx" -q 720
        python app.py "https://www.aparat.com/v/xxxxxx" -q 720 -d /path/to/save/file
        The default quality is 720 or get best quality video exist in quality list.
        The default directory is data in current directory.
    """


def main():
    print("Please wait...")
    mainPage = requests.get(link).content
    main_soup = BeautifulSoup(mainPage, 'html.parser')
    playlist = main_soup.find('div', attrs={'class': 'playlist-list dd'})
    playListLinks = playlist.find_all('a', attrs={'class': 'light-80 dark-10'})
    video_pages = [f"https://www.aparat.com{video.get('href')}" for video in playListLinks]
    count = len(video_pages)
    print(f"This playlist contains {count} videos")
    bar = progressbar.ProgressBar(maxval=count, widgets=[progressbar.Bar('*', '[', ']'), progressbar.Percentage()])
    bar.start()
    links = {}
    print("writing download list ...")
    # Create Output File....
    with io.open('output.sh', "a", encoding="utf-8") as file:
        file.write(f"#!/bin/bash\n")
        if dir != "/data/":
            file.write("cd " + dir + "\n")
        for index, page in enumerate(video_pages):
            bar.update(index + 1)
            html = requests.get(page).content
            soup = BeautifulSoup(html, 'html.parser')
            name = soup.find("h1", attrs={"id": "videoTitle", "class": "title"}).text.encode()
            qualitys = soup.find('div', attrs={'class': 'dropdown-content'}).find_all('a')
            for qual in qualitys:
                if quality in qual.get('aria-label'):
                    links[name] = qual.get('href')
                else:
                    links[name] = qualitys[len(qualitys) - 1].get('href')
            try:
                print(links[name])
                file.write('aria2c -x16 -s16 -k1M {} -o \"{:03d}.mp4\"\n'.format(links[name], (index + 1)))
            except KeyError as err:
                print(err)
    bar.finish()

    # Run Output File To Downloading....
    remove = True
    if platform.system() == "Linux":
        os.system('sh output.sh')
    elif platform.system() == "Windows":
        os.system('bash output.sh')
    else:
        print("Run ouput.sh")
        remove = False

    # Remove File When Download Ended...
    if remove:
        os.remove("output.sh")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Aparat Playlist Downloader", usage=help())
    parser.add_argument("link", help="Insert PlayList Address")
    parser.add_argument("-q", "--quality", help="eg: [480, 720, 1080, ...]", default='720')
    parser.add_argument("-d", "--directory", help="eg: /path/to/save/file", default='/data/')
    '''parser.add_argument("--debug", action="store_true")'''

    args = parser.parse_args()
    link = args.link
    quality = args.quality
    dir = args.directory

    if quality:
        main()
    else:
        help()
