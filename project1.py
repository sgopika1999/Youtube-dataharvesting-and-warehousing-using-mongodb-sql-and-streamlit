import googleapiclient.discovery
import pymongo
import mysql.connector
import pandas as pd
import streamlit as st

def api_key():
    API_key= "AIzaSyAQ36-xaey3Gj4-WT3IEhfVBCrhHIQqtg4"

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=API_key)

    return youtube

youtube=api_key()

#channel details
def get_data(ch_id):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=ch_id
    )
    response = request.execute()
    z=dict(channel_name=response["items"][0]["snippet"]["localized"]["title"],
       channel_id=response["items"][0]["id"],
       subscription_count=response["items"][0]["statistics"]["subscriberCount"],
       channel_views=response["items"][0]["statistics"]["viewCount"],
       channel_videos=response["items"][0]["statistics"]["videoCount"],
       channel_description=response["items"][0]["snippet"]["description"],
       playlist_id=response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"])
    
    return z

#video id
def get_videoid(ch_id):
     video_id=[]
     response=youtube.channels().list(id=ch_id,
                                             part="contentDetails").execute()
     playlist_id=response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
     page_token=None
     while True:
          request = youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    maxResults=50,
                    playlistId=playlist_id,
                    pageToken=page_token)
          response1 = request.execute()  


          for i in range(len(response1["items"])):
               video_id.append(response1["items"][i]["contentDetails"]["videoId"])
               page_token=response1.get("nextPageToken")

          if page_token is None:
               break
     
     return video_id

##video details
def video_info(vi_ids):
    video=[]
    for video_id in vi_ids: 
        request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
        response = request.execute()

        for i in range(len(response["items"])):
        
            
            info=dict(channel_name=response["items"][i]["snippet"]["localized"]["title"],
                 channel_id=response["items"][i]["id"],
                video_id=response["items"][i]["id"],
                video_name=response["items"][i]["snippet"]["title"],
                video_description=response["items"][i]["snippet"].get("description"),
                tags=response["items"][i]["snippet"].get("tags"),
                published_at=response["items"][i]["snippet"]["publishedAt"],
                view_count=response["items"][i]["statistics"].get("viewCount"),
                like_count=response["items"][i]["statistics"].get("likeCount", 0),
                favorite_count=response["items"][i]["statistics"]["favoriteCount"],
                comment_count=response["items"][i]["statistics"].get("commentCount"),
                duration=response["items"][i]["contentDetails"]["duration"],
                Thumbnail=response["items"][i]["snippet"]["thumbnails"]["default"]["url"],
                caption_status=response["items"][i]["contentDetails"]["caption"])
            video.append(info)
             
    return video

##comment details
def comment_details(vi_ids):
    out=[]
    try:
        for videoinfo in vi_ids: 
            request = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=videoinfo,
                    maxResults=10
                )
            response = request.execute()

            for i in range(len(response["items"])):
                comment=dict(comment_id=response["items"][i]["snippet"]["topLevelComment"]["id"],
                             video_id=response["items"][i]["snippet"]["topLevelComment"]["snippet"]["videoId"],                        
                            comment_text=response["items"][i]["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                            comment_author=response["items"][i]["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                            published_at=response["items"][i]["snippet"]["topLevelComment"]["snippet"]["publishedAt"])
                out.append(comment)
    except:
        pass 

    return out     

#mongodb connection
import certifi
ca = certifi.where()
client=pymongo.MongoClient("mongodb+srv://sgopika:1234@cluster0.cjfpbe5.mongodb.net/?retryWrites=true&w=majority",tlsCAFile=ca)
db=client["youtube"] 


#upload to mongodb
def channelinfo(ch_id):
    ch_details=get_data(ch_id)
    video_ids=get_videoid(ch_id)
    video_details=video_info(video_ids)
    comment_info=comment_details(video_ids)

    collection=db["channelinfo"]

    collection.insert_one({"channel_information":ch_details,"video_information":video_details,
                           "comment_information":comment_info})
    return "upload successfully completed"

#table creation of channels
def channels_table():
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="youtubedata"
    )

    print(mydb)
    mycursor = mydb.cursor(buffered=True)



    mycursor.execute("DROP table if exists channels")


    mycursor.execute('''CREATE TABLE if not exists youtubedata.channels(channel_name VARCHAR(50),
                                                                            channel_id VARCHAR(25) primary key,
                                                                            subscription_count int,
                                                                            channel_views int,
                                                                            channel_videos int,
                                                                            channel_description VARCHAR(100),
                                                                            playlist_id VARCHAR(20))''')

    channels=[]
    db=client["youtube"]
    collection=db["channelinfo"]
    for channel in collection.find({},{"_id":False,"channel_information":True}):
        channels.append(channel["channel_information"])

    df=pd.DataFrame(channels)

    for index,row in df.iterrows():
        X='''insert into youtubedata.channels
                                
                                values(%s,%s,%s,%s,%s,%s,%s)'''
        
        values=(row['channel_name'],
                row['channel_id'],
                row['subscription_count'],
                row['channel_views'],
                row['channel_videos'],
                row['channel_description'],
                row['playlist_id'])
        try:
            mycursor.execute(X,values)
            mydb.commit()
        except:
            print("channels already created")


#table creation for videos
def video_table():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="youtubedata"
    )

    print(mydb)
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("DROP TABLE if exists videos")

    mycursor.execute('''CREATE TABLE if not exists youtubedata.videos(channel_name VARCHAR(50),
                                                                    channel_id VARCHAR(25),
                                                                    video_id VARCHAR(20),
                                                                    video_name VARCHAR(255),
                                                                    video_description TEXT,
                                                                    tags VARCHAR(255),
                                                                    published_at DATETIME,
                                                                    view_count INT,
                                                                    like_count INT,
                                                                    favorite_count INT,
                                                                    comment_count INT,
                                                                    duration TIME,
                                                                    Thumbnail VARCHAR(255),
                                                                    caption_status VARCHAR(10))''')
    videoinfo=[]
    db=client["youtube"]
    collection=db["channelinfo"]
    for video in collection.find({},{"_id":False,"video_information":True}):
        for i in range (len(video["video_information"])):
            videoinfo.append(video["video_information"][i])
    
    df1=pd.DataFrame(videoinfo)

    for index,row in df1.iterrows():
            
            SQL_query = '''INSERT INTO youtubedata.videos 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)'''
            
            tags_str = ','.join([str(tag) for tag in row['tags']]) if isinstance(row['tags'], list) else None

            values = (row['channel_name'],
                    row['channel_id'],
                    row['video_id'],
                    row['video_name'],
                    row['video_description'],
                    tags_str,
                    row['published_at'],
                    row['view_count'],
                    row['like_count'],
                    row['favorite_count'],
                    row['comment_count'],
                    row['duration'],
                    row['Thumbnail'],
                    row['caption_status']
            )

            mycursor.execute(SQL_query, values)

    mydb.commit()


#table creation for comments
def comments_table():
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="youtubedata"
        )

        print(mydb)
        mycursor = mydb.cursor(buffered=True)



        mycursor.execute("DROP table if exists comments")

        mycursor.execute('''CREATE TABLE youtubedata.comments(comment_id VARCHAR(30) PRIMARY KEY,
                                                               video_id VARCHAR(20),
                                                                comment_text TEXT,
                                                                comment_author VARCHAR(50),
                                                                published_at TIMESTAMP)''')

        comments_list=[]
        db=client["youtube"]
        collection=db["channelinfo"]
        for comments_data in collection.find({},{"_id":False, "comment_information":True}):
                for i in range (len(comments_data["comment_information"])):
                        comments_list.append(comments_data["comment_information"][i])
        df4=pd.DataFrame(comments_list)

        for index,row in df4.iterrows():
                X = '''INSERT INTO youtubedata.comments 
                        VALUES (%s, %s, %s, %s,%s)'''
                values = (row['comment_id'],
                          row['video_id'],
                        row['comment_text'],
                        row['comment_author'],
                        row['published_at'])
        mycursor.execute(X,values)
        mydb.commit()

#To create tables
def tables():
    channels_table()
    video_table()
    comments_table()

    return "tables created"

#channel dataframe
def ch_table():
    channels=[]
    db=client["youtube"]
    collection=db["channelinfo"]
    for channel in collection.find({},{"_id":False,"channel_information":True}):
        channels.append(channel["channel_information"])

    df=st.dataframe(channels)

    return df

#video datafrme
def vi_id():
    videoinfo=[]
    db=client["youtube"]
    collection=db["channelinfo"]
    for video in collection.find({},{"_id":False,"video_information":True}):
        for i in range (len(video["video_information"])):
            videoinfo.append(video["video_information"][i])

    df1=st.dataframe(videoinfo)

    return df1

#comments dataframe
def cmt_id():
    comments_list=[]
    db=client["youtube"]
    collection=db["channelinfo"]
    for comments_data in collection.find({},{"_id":False, "comment_information":True}):
            for i in range (len(comments_data["comment_information"])):
                    comments_list.append(comments_data["comment_information"][i])
    df4=st.dataframe(comments_list)

    return df4


##streamlit 
with st.sidebar:
    st.title(":black[YOUTUBE DATA HARVESTING AND WAREHOUSING]")

channel_id=st.text_input("Enter the channel id")

if st.button ("collect and store data"):
    ch_ids=[]
    db=client["youtube"]
    collection=db["channelinfo"]
    for ch_id in collection .find({},{"_id":False,"channel_information":True}):
        ch_ids.append(ch_id["channel_information"]["channel_id"])
        
    if channel_id in ch_ids:
        st.success("channel id is already existed")

    else:
        insert=channelinfo(channel_id)
        st.success(insert)

if st.button("Migrate to sql"):
    Table=tables()
    st.success(Table)

show_tables=st.radio("select the table for view",("channels","videos","comments"))  

if show_tables=="channels":
    ch_table()

elif show_tables=="videos":
   vi_id() 

elif show_tables=="comments":
    cmt_id()
 

 ##SQL connection

mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="youtubedata"
        )

print(mydb)
mycursor = mydb.cursor(buffered=True)

question=st.selectbox("select your question",("1. What are the names of all the videos and their corresponding channels?",
                                             "2. Which channels have the most number of videos, and how many videos do they have?",
                                             "3. What are the top 10 most viewed videos and their respective channels?",
                                             "4. How many comments were made on each video, and what are their corresponding video names?",
                                             "5. Which videos have the highest number of likes, and what are their corresponding channel names?",
                                             "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
                                             "7. What is the total number of views for each channel, and what are their corresponding channel names?",
                                             "8. What are the names of all the channels that have published videos in the year 2022?",
                                             "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?",
                                             "10. Which videos have the highest number of comments, and what are their corresponding channel names?"))

if question=="1. What are the names of all the videos and their corresponding channels?":
        question1='''SELECT video_name as videonames,channel_name as channelnames from videos'''
        mycursor.execute(question1)
        t1=mycursor.fetchall()
        df1=pd.DataFrame(t1,columns=["videoname","channelname"])
        st.write(df1)

elif question=="2. Which channels have the most number of videos, and how many videos do they have?":
        question2='''SELECT channel_videos as videos_count,channel_name as channelnames from channels 
                order by videos_count desc'''
        mycursor.execute(question2)
        t2=mycursor.fetchall()
        df2=pd.DataFrame(t2,columns=["videos_count","channelnames"])
        st.write(df2)


elif question=="3. What are the top 10 most viewed videos and their respective channels?":
        question3='''SELECT videos.view_count as views,channels.channel_name as channelnames from videos inner join 
             channels on channels.channel_name=videos.channel_name where view_count is not null order by views desc 
             limit 10'''
        mycursor.execute(question3)
        t3=mycursor.fetchall()
        df3=pd.DataFrame(t3,columns=["views","channelnames"])
        st.write(df3)


elif question=="4. How many comments were made on each video, and what are their corresponding video names?":
        question4="SELECT comment_count as commentscount,video_name as videoname from videos where comment_count is not null"
        mycursor.execute(question4)
        t4=mycursor.fetchall()
        df4=pd.DataFrame(t4,columns=["commentscount","videoname"])
        st.write(df4)

elif question=="5. Which videos have the highest number of likes, and what are their corresponding channel names?":
        question5='''SELECT videos.like_count as likes,channels.channel_name as channelnames,videos.video_name as videoname 
                    from videos inner join channels on videos.channel_name=channels.channel_name
                    where like_count is not null order by likes desc'''
        mycursor.execute(question5)
        t5=mycursor.fetchall()
        df5=pd.DataFrame(t5,columns=["likes","channelnames","videoname"])
        st.write(df5)

elif question=="6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?":
        question6="SELECT like_count as likes,video_name as videoname from videos"
        mycursor.execute(question6)
        t6=mycursor.fetchall()
        df6=pd.DataFrame(t6,columns=["likes","videoname"])
        st.write(df6)   

elif question=="7. What is the total number of views for each channel, and what are their corresponding channel names?":
        question7="SELECT channel_views as views,channel_name as channelnames from channels"
        mycursor.execute(question7)
        t7=mycursor.fetchall()
        df7=pd.DataFrame(t7,columns=["views","channelnames"])
        st.write(df7)

elif question=="8. What are the names of all the channels that have published videos in the year 2022?":
        question8='''SELECT channels.channel_name as channelnames,videos.published_at as publisheddate,videos.video_name as videoname 
           from videos inner join channels on videos.channel_name=channels.channel_name where 
           extract(year from published_at)=2022'''
        mycursor.execute(question8)
        t8=mycursor.fetchall()
        df8=pd.DataFrame(t8,columns=["channelnames","publisheddate","videoname"])
        st.write(df8)

elif question=="9. What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        question9='''SELECT channels.channel_name as channelnames, AVG(videos.duration) as average_duration from videos inner join
           channels on channels.channel_name=videos.channel_name group by channels.channel_name'''
        mycursor.execute(question9)
        t9=mycursor.fetchall()
        df9=pd.DataFrame(t9,columns=["channelnames","average_duration"])

        t9=[]
        for index,row in df9.iterrows():
                channelname=row["channelnames"]
                duration_str=str(row["average_duration"])
                t9.append(dict(channel_name=channelname,duration=duration_str))
        df91=pd.DataFrame(t9) 
        st.write(df91)
        
elif question=="10. Which videos have the highest number of comments, and what are their corresponding channel names?":
        question10='''SELECT videos.video_name as videoname,videos.comment_count as comments,channels.channel_name as 
              channelnames from videos inner join channels on videos.channel_name=channels.channel_name 
              where comment_count is not null order by comments desc''' 
        mycursor.execute(question10)
        t10=mycursor.fetchall()
        df10=pd.DataFrame(t10,columns=["videoname","comments","channelnames"])
        st.write(df10)