# Sandbot
A discord bot that I built to do random things for fun

## Live Commands:
```
$inspire - Receive a inspiring message
    
$new <quote>  - Send the users qoute to a mongo database
    
$list - View all quotes in the database 
    
$del <quoteID> - Delete a qoute from the database 

$news - Gets Recent news

$decide choice1?choice2?choicex - Makes a difficult decision for a user

$clean amount - Deletes amount number of messages in the current channel after confirmation  

$search <engine> <query> - Search for a given word on the specified engine. Default google
Current Engines: Google,Wikipedia,Urban Dictionary

```

  
  ## Planned Commands: 
  
- [X] Jokes on command
- [ ] A Command to create a poll
- [X] A search for a word or sentence on google
  - [X] Add ability to search using different engines (wiki,google,urban dictionary)
    - [X] Add additional searches as needed {Image Search}
  - [ ] Return first three results from urban dictionary 
  - [X] Auto post Urban Dictionary word of the day
    -[ ] command to retreive urban dictionary trending words
  - [ ] Add wiki image to embed
  - [ ] Modify current google results to better format
- [X] Add ability to get current news headlines and links 
  - [ ] Allow news search by category 
  - [ ] Post only to news text channel
- [X] Delete message history
  - [ ] Only specific role can delete chat history
- [X] very advanced decision making
- [ ] to do lists
- [ ] post memes every hour
- [ ] Post live updates on videogame sales 

Known issues

- No responses are sent if the del command receives an incorrect argument