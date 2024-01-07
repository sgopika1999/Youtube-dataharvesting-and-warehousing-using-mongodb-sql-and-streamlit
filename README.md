This project aims to provide a comprehensive solution for efficiently collecting, storing, and analyzing YouTube data using a combination of SQL, MongoDB, and Streamlit.

INTRODUCTION

YouTube Data Harvesting and Warehousing is a project aimed at developing a user-friendly Streamlit application that leverages the power of the Google API to extract valuable information from YouTube channels. The extracted data is then stored in a MongoDB database, subsequently migrated to a SQL data warehouse, and made accessible for analysis and exploration within the Streamlit app.

TABLE OF CONTENTS
  -  Key Technologies and Skills
  -  Installation
  -  Features
  -  Retrieving data from the YouTube API
  -  Storing data in MongoDB
  -  Migrating data to a SQL data warehouse
  -  Data Analysis
  -  Conclusion 

KEY TECHNOLOFIES AND SKILLS
  -  Python scripting
  -  Data Collection
  -  API integration
  -  streamlit
  -  Data Management using MongoDB and SQL(MySQL)

INSTALLATION

To run this project, you need to install the following packages:

          import googleapiclient.discovery
          import pymongo
          import mysql.connector
          import pandas as pd
          import streamlit as st

FEATURES
  -  Retrieve data from the YouTube API, including channel information, videos and comments.
  -  Store the retrieved data in a MongoDB database.
  -  Migrate the data to a SQL data warehouse.
  -  Analyze and visualize data using Streamlit.
  -  Perform queries on the SQL data warehouse.
  -  Gain insights into channel performance, video metrics, and more.

RETRIEVING DATA FROM THE YOUTUBE API

The project utilizes the Google API to retrieve comprehensive data from YouTube channels. The data includes information on channels,videos and comments. By interacting with the Google API, we collect the data and merge it into a JSON file.

STORING DATA IN MONGODB

The retrieved data is stored in a MongoDB database based on user authorization. If the data already exists in the database, it can be overwritten with user consent. This storage process ensures efficient data management and preservation, allowing for seamless handling of the collected data.

MIGRATING DATA TO A SQL DATA WAREHOUSE

The application allows users to migrate data from MongoDB to a SQL data warehouse. Users can choose which channel's data to migrate. To ensure compatibility with a structured format, the data is cleansed using the powerful pandas library. Following data cleaning, the information is segregated into separate tables, including channels, playlists, videos, and comments, utilizing SQL queries.

DATA ANALYSIS

The data can be analyzed using a variety of tools. In this project, we will use Streamlit. Streamlit is a Python library that can be used to create interactive web applications. We will use Streamlit to create a dashboard that allows users to visualize and analyze the data.

CONCLUSION

This project has demonstrated how to harvest and warehouse YouTube data using SQL, MongoDB, and Streamlit. This approach can be used to collect, store, and analyze data from a variety of sources.









