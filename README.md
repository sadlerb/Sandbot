# Sandbot



A discord bot that I built to do random things for fun

## Live Commands:
```
$poll 'question' *options - Create a poll using the given parameters
$inspire - Receive a inspiring message

$joke - Sandbot will tell a joke    

$meme - Sandbot will send a random meme

$new <quote>  - Send the users qoute to a mongo database
    
$list - View all quotes in the database 
    
$del <quoteID> - Delete a qoute from the database 

$news - Gets Recent news

$decide choice1?choice2?choicex - Makes a difficult decision for a user

$clean amount - Deletes amount number of messages in the current channel after confirmation  

$search <engine> <query> - Search for a given word on the specified engine. Default google
Current Engines: Google,Wikipedia,Urban Dictionary,Images

$reddit <subreddit> - Get a random post from the specified subreddit>

```

  
  ## Planned Commands: 
  
- [X] Jokes on command
- [X] A Command to create a poll
- [X] A search for a word or sentence on google
  - [X] Add ability to search using different engines (wiki,google,urban dictionary)
    - [X] Add additional searches as needed {Image Search}
  - [X] Auto post Urban Dictionary word of the day
- [X] Add ability to get current news headlines and links 
- [X] Delete message history
  - [X] Only specific role can delete chat history
- [X] very advanced decision making
- [X] ~post memes every hour~ Command to post a random meme from reddit
- [X] Post live updates on videogame sales 

Known issues

- No responses are sent if the del command receives an incorrect argument
