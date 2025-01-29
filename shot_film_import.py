from notion_client import Client
from bilibili_api import getBiliInfor
from youtube_api import  getYoutubeInfor



# initialize
notion = Client(auth="secret_e5VwPByosWlI1dwF6i7WFabyAKodNUrOW5k1HDp6PKk")
database_id = "80ca70f22ccb41d6b2d9ed81d10c6f9d"
pages = []



#get video information from its link
def getVideoInfor(video_url : str):
    if "bilibili" in video_url:
        return getBiliInfor(video_url)
    elif "youtube" in video_url:
        return getYoutubeInfor(video_url)



#get all pages from the diary database
def getPages():
    results = []
    query = notion.databases.query(database_id=database_id)
    results.extend(query["results"])

    #if has more pages
    while query["has_more"]:
        query = notion.databases.query(database_id=database_id, start_cursor=query["next_cursor"])
        results.extend(query["results"])

    return results




class ShortFilm():
    # initinal properties
    def __init__(self, infor : dict):
        self.title = infor["title"]
        self.des = infor["description"]
        self.release_date = infor["release_date"]
        self.uploader = infor["uploader"]
        self.image_url = infor["image_url"]
        self.url = infor["url"]
        self.duration = infor["duration"]



    def makeAttributes(self, cate1 : str = "", cate2 : str = ""):
        self.properties = {
            "Name": {"title": [{"text": {"content": self.title}}]},
            "Uploader": {"rich_text": [{"type": "text", "text": {"content": self.uploader}}]},
            "Cover": {"files": [{"type": "external", "name": "Wallpaper", "external": {"url": self.image_url}}]},
            "Release Date": {"date": {"start": self.release_date, "end": None}},
            "Duration (Min)": {"number": self.duration},
         }


        #input categories like "2D" "3D" "Animated Film" "Motion Design & Commercial"
        if cate1 and cate2:
            self.properties["Categories"] = {"multi_select": [
                {"name": cate1},
                {"name": cate2}
            ]}


        self.children = [
            #video cover
            {"type": "image",
                "image": {"type": "external", "external": {"url" : self.image_url}}},

            #video title
            {"object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {
                    "content": self.title,
                    "link": {"url": self.url}}}]}
             },

            #empty line
            {"object": "block", "type": "paragraph",
                "paragraph": {"rich_text": []}}
        ]


        #a block cannot be too long
        for paragraph in self.des.split("\n"):
            self.children.append(
                {"object": "block", "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": paragraph}}]}}
            )


        #override by different sites
        if "bilibili" in self.url:
            self.properties["URL"] = {"url": self.url}
        elif "youtube" in self.url:
            self.properties["URL2"] = {"url": self.url}



    def updatePage(self, page_id):
        self.properties.pop("Name")

        # update page
        print("Update existing page.")
        notion.pages.update(
            page_id=page_id,
            properties=self.properties
        )

        # delete existing blocks
        blocks = notion.blocks.children.list(block_id=page_id)
        for block in blocks["results"]:
            block_id = block["id"]
            notion.blocks.delete(block_id=block_id)

        # append new blocks
        notion.blocks.children.append(
            block_id=page_id,
            children=self.children
        )




    # check if the same URL attribute exists in current pages, and update or make a new page
    def checkExistence(self):
        # for page in pages:
        #     page_ret = notion.pages.retrieve(page_id=page["id"])
        #     properties = page_ret["properties"]
        #
        #     if "URL" in properties and properties["URL"]["url"] == self.url:
        #         self.updatePage(page["id"])
        #         return page_ret
        #
        #     else:
                # create new page
                print("Making new page.")
                new_page = notion.pages.create(
                    parent={"database_id": database_id},
                    properties=self.properties,
                    children=self.children
                )

                return new_page



    def makePage(self, cate1 : str, cate2 : str):
        self.makeAttributes(cate1, cate2)
        #self.properties["Name"] = {"title": [{"text": {"content": self.title}}]}
        self.checkExistence()
        print("Successfully made page.")


    def updateSpeciPage(self, page_id):
        self.makeAttributes()
        self.updatePage(page_id)
        print("Successfully updated page.")




def createNewPage(cate1 : str, cate2 : str):
    #input video link
    video_url = input("Input video links: ")

    urls = video_url.split()
    for url in urls:
        infor = getVideoInfor(url)
        if infor:
            sf = ShortFilm(infor)
            sf.makePage(cate1, cate2)



# find pages with certain keywords in URL2 property, and return the pages list found
def findPages(keywords : str):
    # Query the database for today's page
    response = notion.databases.query(
        **{"database_id": database_id,
           "filter": {"property": "URL2", "url": {"contains": keywords}}}
    )
    if len(response["results"]) > 0:
        return response["results"]



# update information for youtube pages
def updatePages():
    pages = findPages("youtube")
    for page in pages:
        properties = notion.pages.retrieve(page_id=page["id"])["properties"]

        youtube_url = properties["URL2"]["url"]
        # if youtube_url and "youtube" in youtube_url:
            # if properties["Name"]["title"][0]["text"]["content"] == "TEAR OFF (2022)":
        infor = getYoutubeInfor(youtube_url)
        if infor:
            sf = ShortFilm(infor)
            sf.updateSpeciPage(page["id"])



createNewPage("2D", "Animated Film")
# createNewPage("3D", "Motion Design & Commercial")
# updatePages()





