functions = [
  {
    "type": "function",
    "function": {
      "name": "task_question",
      "description": "checking movie query from the user",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "The query must be around the movie industry, e.g. what horror movie do you recommend, who plays in this movie,what year was this movie released, how much does the movie make",
          },
        },
        "required": ['query'],
      },
    }
  },
  {
    "type": "function",
    "function": {
      "name": "reference_question",
      "description": "checking the query from the user",
      "parameters": {
        "type": "object",
        "properties": {
          "ref_query": {
            "type": "string",
            "description": "a question with the word movie/film, e.g. how good is the movie, who act in the movie, when the film shoot",
          },
        },
        "required": ['ref_query'],
      },
    }
  },
]

univ_functions = [
  {
    "type": "function",
    "function": {
      "name": "task_question",
      "description": "question for the assistant about university",
      "parameters": {
        "type": "object",
        "properties": {
          "main_idea": {
            "type": "string",
            "description": "The main idea of the question, e.g. attendance, scholarship, course",
          },
          "univ_name": {
            "type": "string",
            "description": "The name of the univ, e.g. SP Jain, University of Wroclaw, MIT, Oxford",
          },
        },
        "required": ['main_idea'],
      },
    }
  },
]
