import boto3
from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import creds 


TABLE_NAME = "Users"

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

def add_user():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']


    '''name = input("Enter the name of the board game: ")
    brand = input("Enter the brand that makes the board game: ")
    min_num_players = int(input("Enter the minimum number of players: "))

    rating_list = []
    num_ratings = int(input("Enter the number of ratings you would like to input: "))
    current = 0
    while current < num_ratings:
        rating = int(input("Enter the rating: "))
        rating_list.append(rating)
        current += 1'''

    table.put_item (
        Item={
        "FirstName": first_name,
        "LastName": last_name,
        "Email": email,
        "Password": password,
        }
    )

def delete_user():
    email = request.form['email of the user you want to delete']
    password = request.form['password of the user you want to delete']

    table.delete_item(
    Key={
        "Email": email,
        "Password": password,
        }
    )

def update_user():
    try:
        email = request.form['current email of the user you want to update']
        password = request.form['current password of the user you want to update']
        
        '''name = input("Enter the name of the board game: ")
        rating = int(input("What is the rating: "))

        table.update_item(
            Key = {"Email": email}, 
            UpdateExpression = "SET Ratings = list_append(Ratings, :r)", 
            ExpressionAttributeValues = {':r': [rating],}
        )'''
        

    except:
        print("error in updating user")





def print_game(game_dict):
    print("Name: ", game_dict["Name"])
    print("Brand: ", game_dict["Brand"])
    print("Minimum Number of Players", game_dict["MinNumPlayers"])
    print(" Ratings: ", end="")

    for rating in game_dict["Ratings"]:
        print(rating, end=" ")

def print_all_games():
    response = table.scan()
    for game in response["Items"]:
        print_game(game)
        print(" \n")

def update_rating():
    try:
        name = input("Enter the name of the board game: ")
        rating = int(input("What is the rating: "))

        table.update_item(
            Key = {"Name": name}, 
            UpdateExpression = "SET Ratings = list_append(Ratings, :r)", 
            ExpressionAttributeValues = {':r': [rating],}
        )

    except:
        print("error in updating game rating")



def query_games():
    name = input("Enter the title of the board game: ")
    try:
        ratings_sum = 0
        response = table.get_item(
        Key={
            "Name": name,
            }
        )
        game = response.get("Item")
        ratings_list = game["Ratings"]
        for rating in ratings_list:
            ratings_sum += rating
        avg_rating = ratings_sum / len(ratings_list)
        print("The average rating of", name,  "is", avg_rating)
    except TypeError:
        print("game not found")
              
    except ZeroDivisionError:
        print("game has no ratings")
    

