import random
import time
    
def math_ans(op, num1, num2):
   if op == 1:
      return num1 + num2
   elif op == 2:
      return num1 - num2
   elif op == 3:
      return num1 * num2
   else:
      return num1
    
def play_math(level, num_questions):
   low_num = 1
   level = level.lower()
   num_correct = 0
   if level == "easy":
      high_num = 10
   elif level == "medium":
      high_num = 20
   elif level == "hard":
      high_num = 50
   else:
      print("Please enter a valid difficulty")
      return
   
   start_time = time.time()
   for i in range(num_questions):
      #1: +, 2: -, 3: *, 4: /
      num1 = random.randint(low_num, high_num)
      num2 = random.randint(low_num, high_num)

      if num1 < num2:
         #make sure num1 is not smaller than num2
         temp = num1
         num1 = num2
         num2 = temp
      
      op_num = random.randint(1,4)
      ops = "+-*/"
      correct = math_ans(op_num, num1, num2)
      if op_num == 4:
         num1 = num1 * num2

      print(f"{num1} {ops[op_num-1]} {num2} = ")
      ans = int(input("Input your answer: "))
      if ans == correct:
         num_correct += 1
         print("Correct!")
      else:
         print(f"Incorrect. The correct answer was {correct}")
   end_time = time.time()
   elapsed_time = end_time - start_time
   print(f"Well done! {num_correct}/{num_questions} Correct")
   print(f"Elapsed time: {elapsed_time:.1f} seconds")
   return num_correct

def play_geo(numOfQuestions=15, difficulty="easy"):
    if difficulty not in ["easy", "medium", "hard"]:
        print("Please choose either easy, medium, or hard in difficulty.")
        return

    questions = {
        "easy": {
            1: "What is the capital of Germany?",
            2: "Which continent is home to the Sahara Desert?",
            3: "Which country has the largest population in the world?",
            4: "Which U.S. state is known for having the Grand Canyon?",
            5: "What is the name of the mountain range that separates Europe and Asia?",
            6: "Which ocean borders the eastern coast of the United States?",
            7: "What is the capital of Argentina?",
            8: "Which country is known for the ancient ruins of Machu Picchu?",
            9: "Which major river flows through the city of London?",
            10: "What is the name of the coldest continent on Earth?",
            11: "Which African country is famous for its pyramids?",
            12: "What is the capital of Japan?",
            13: "Which U.S. state is famous for its large potato production?",
            14: "Which country is home to the Taj Mahal?",
            15: "What is the name of the sea located between Europe and Africa?"
        },

        "medium": {
            16: "What country has the longest coastline in the world?",
            17: "Which river is the longest in Africa?",
            18: "Which U.S. state shares the longest border with Canada?",
            19: "What is the largest island in the world?",
            20: "Which desert is the largest hot desert in the world?",
            21: "Which country is home to the most lakes?",
            22: "Which city is known as the 'City of Canals'?",
            23: "What is the longest river in the United States?",
            24: "Which ocean is the smallest by surface area?",
            25: "Which sea separates the Arabian Peninsula from Africa?",
            26: "Which U.S. state has the highest peak?",
            27: "Which country has the highest population density?",
            28: "Which African country has the most people?",
            29: "Which city in China has the largest population?",
            30: "Which island is the largest in the Mediterranean Sea?"
        },

        "hard": {
            31: "What country has the longest uninterrupted coastline?",
            32: "What city has the most bridges in the world?",
            33: "What is the oldest active volcano on Earth?",
            34: "What African country has the longest coastline?",
            35: "What U.S. state has the most islands?",
            36: "What island nation has the most languages spoken?",
            37: "What is the capital of the country that has the highest capital city by elevation?",
            38: "What country has the lowest average elevation?",
            39: "What river is the only one to flow north in the United States?",
            40: "What desert is the largest cold desert in the world?",
            41: "What country has the most mountains by total land area?",
            42: "What country is home to the world's highest waterfall?",
            43: "What country spans the most degrees of longitude?",
            44: "What body of water has the highest evaporation rate on Earth?",
            45: "What city is known for being the highest permanently inhabited place on Earth?"
        }
    }

    answers = {
        "easy": {
            1: "Berlin",
            2: "Africa",
            3: "China",
            4: "Arizona",
            5: "Ural Mountains",
            6: "Atlantic",
            7: "Buenos Aires",
            8: "Peru",
            9: "Thames",
            10: "Antarctica",
            11: "Egypt",
            12: "Tokyo",
            13: "Idaho",
            14: "India",
            15: "Mediterranean Sea"
        },

        "medium": {
            16: "Canada",
            17: "Nile River",
            18: "Alaska",
            19: "Greenland",
            20: "Sahara Desert",
            21: "Canada",
            22: "Venice",
            23: "Missouri",
            24: "Arctic Ocean",
            25: "Red Sea",
            26: "Denali",
            27: "Monaco",
            28: "Nigeria",
            29: "Shanghai",
            30: "Sicily"
        },

        "hard": {
            31: "Canada",
            32: "Hamburg",
            33: "Mount Etna",
            34: "Madagascar",
            35: "Alaska",
            36: "Papua New Guinea",
            37: "La Paz",
            38: "Maldives",
            39: "New River",
            40: "Antarctic Desert",
            41: "Nepal",
            42: "Venezuela",
            43: "France",
            44: "Lake Assal",
            45: "La Rinconada"
        }
    }

    selectedAnswers = random.sample(list(questions[difficulty].keys()), numOfQuestions)
    correct = 0
    total = 0

    for i in selectedAnswers:
        print(questions[difficulty][i])
        ans = input("Your answer: ").strip().title()

        if ans == answers[difficulty][i]:
            print("Correct!")
            correct += 1
            
        else:
            print(f"Incorrect! The correct answer was {answers[difficulty][i]}.")

        print()
        total += 1

    print(f"Your final score: {correct}/{total} ({int(correct * 100 / total)}%)")
    return correct
  
def play_vocab(level, mode, num_questions):
   wordbank = wordbank = {
   "easy": [
      ("Love", "Like", "Hate"),
      ("Happy", "Joyful", "Sad"),
      ("Fast", "Quick", "Slow"),
      ("Big", "Large", "Small"),
      ("Easy", "Simple", "Difficult"),
      ("Loud", "Noisy", "Quiet"),
      ("Hot", "Warm", "Cold"),
      ("Dark", "Dim", "Bright"),
      ("Strong", "Powerful", "Weak"),
      ("Clean", "Tidy", "Messy"),
      ("Friendly", "Kind", "Mean"),
      ("Soft", "Gentle", "Rough"),
      ("Smart", "Clever", "Dumb"),
      ("Fun", "Enjoyable", "Boring"),
      ("Shout", "Yell", "Whisper"),
      ("Wet", "Damp", "Dry"),
      ("Brave", "Courageous", "Fearful"),
      ("Thin", "Slim", "Thick"),
      ("New", "Fresh", "Old"),
      ("Safe", "Secure", "Dangerous")
   ],
   "medium": [
      ("Muted", "Faint", "Blaring"),
      ("Sturdy", "Robust", "Frail"),
      ("Vivid", "Radiant", "Subdued"),
      ("Lazy", "Idle", "Energetic"),
      ("Sharp", "Pointed", "Dull"),
      ("Brisk", "Lively", "Sluggish"),
      ("Famous", "Renowned", "Obscure"),
      ("Shy", "Timid", "Bold"),
      ("Smooth", "Even", "Bumpy"),
      ("Lucky", "Fortunate", "Hapless"),
      ("Heavy", "Weighty", "Light"),
      ("Precise", "Exact", "Vague"),
      ("Curious", "Inquisitive", "Indifferent"),
      ("Deep", "Profound", "Shallow"),
      ("Proud", "Confident", "Ashamed"),
      ("Polite", "Courteous", "Rude"),
      ("Elusive", "Evasive", "Obvious"),
      ("Precise", "Exact", "Vague"),
      ("Tough", "Sturdy", "Fragile"),
      ("Eager", "Keen", "Reluctant")
   ],
   "hard": [
      ("Ephemeral", "Transient", "Perpetual"),
      ("Maelstrom", "Turmoil", "Tranquil"),
      ("Obsequious", "Sycophantic", "Contemptuous"),
      ("Eloquent", "Articulate", "Incoherent"),
      ("Diligent", "Industrious", "Indolent"),
      ("Frugal", "Thrifty", "Wasteful"),
      ("Conceited", "Imperious", "Humble"),
      ("Elucidate", "Clarify", "Obfuscate"),
      ("Intrepid", "Dauntless", "Pusillanimous"),
      ("Exultant", "Jubilant", "Melancholic"),
      ("Antediluvian", "Obsolete", "Voguish"),
      ("Ostentatious", "Flamboyant", "Austere"),
      ("Meticulous", "Punctilious", "Negligent"),
      ("Gregarious", "Convivial", "Reticent"),
      ("Impartial", "Nonpartisan", "Prejudiced"),
      ("Perspicacious", "Astute", "Barmy"),
      ("Clandestine", "Surreptitious", "Overt"),
      ("Phlegmatic", "Placid", "Mercurial"),
      ("Lethargic", "Torpid", "Zestful"),
      ("Amicable", "Cordial", "Hostile")
   ]
   }
   if level not in ['easy', 'medium', 'hard']:
      raise ValueError("Invalid difficulty. Please choose from easy, medium, or difficult")
   if mode not in ['synonyms', 'antonyms', 'both']:
      raise ValueError("Invalid gamemode. Please choose from synonyms, antonyms, or both")
   if not isinstance(num_questions, int) or num_questions != max(min(int(num_questions), 15), 1):
      raise ValueError("Invalid number of questions. Please enter an integer between 1 and 15")

   score = 0

   for i in range(num_questions):
      word = random.choice(wordbank[level])
      wordbank[level].remove(word)
      mode_names = [" synonym", "n antonym"]
      if mode == "synonyms":
         correct = word[1]
         mode_name = mode_names[0]
      elif mode == "antonyms":
         correct = word[2]
         mode_name = mode_names[1]
      elif mode == "both":
         mode_num = random.randint(0, 1)
         correct = word[mode_num + 1]
         mode_name = mode_names[mode_num]


      options = {correct}
      while len(options) < 4:
         options.add(random.choice(wordbank[level])[random.randint(0, 2)])
      options = list(options)
      random.shuffle(options)


      key = {
         "A": options[0],
         "B": options[1],
         "C": options[2],
         "D": options[3]
      }


      print(f"Which word is a{mode_name} for {word[0]}?")
      print(f"A: {options[0]}")
      print(f"B: {options[1]}")
      print(f"C: {options[2]}")
      print(f"D: {options[3]}")
      ans = input("Choose A, B, C, or D: ").upper()
      while ans not in key:
         print("Invalid option.")
         ans = input("Invalid option. Choose A, B, C, or D: ").upper()


      if key[ans] == correct:
         print("Correct!")
         score += 1
      else:
         print(f"Incorrect. The correct answer was {correct}")
      print()
   
   print(f"Your total score this game was {score}/{num_questions}: {int(score*100/num_questions)}%")



def play_science(num_questions=10, difficulty="mix"):
   
   if num_questions > 10:
      print("Maximum of 10 questions")
      return
   
   questions = {
      'easy': {
         1: "What is the largest planet in our solar system?",
         2: "What is the fastest animal on land?",
         3: "What are the three layers of the Earth",
         4: "How many elements are on the periodic table?",
         5: "What do you call an animal that eats a variety of other organisms, including plants, animals and fungi?",
         6: "What do you call the study of weather, climate and the atmosphere?",
         7: "What is the study of fungi called?",
         8: "Which is the most abundant element in the universe?",
         9: "What element is the most commonly used to create nuclear energy?",
         10: "Who is credited with coming up with the theory of evolution?",
      },
      'hard': {
         11: "How many bones does a sharks have?",
         12: "What does a Geiger counter measure?",
         13: "Which is the only rock that floats?",
         14: "What scale is used to measure the hardness of minerals?",
         15: "What is it called when a solid changes directly into a gas?",
         16: "What is the most abundant element in the Earth’s crust?",
         17: "What is the newest element on the periodic table?",
         18: "What color is the sunset on Mars?",
         19: "What is the hottest planet in our solar system?",
         20: "What is the heaviest internal organ in the human body?"
      }
   }
   
   options = {
      'easy': {
         1: ["Mars", "Saturn", "Jupiter", "Ceres"],
         2: ["A Cheetah", "A Falcon", "An Antelope", "Usain Bolt"],
         3: ["Outer shell, inner shell, and center", "Land, water, and atmosphere", "Rock layer, magma layer, and deep core", "Crust, mantle and core"],
         4: ['100', '118', '80', '79'],
         5: ['An omnivore', 'A herbivore', 'A carnivore', 'An organivore'],
         6: ['Climatology', 'Aerology', 'Atmospheric Science', 'Meteorology'],
         7: ['Phycology', 'Botany', 'Mycology', 'Lichenology'],
         8: ['Oxygen', 'Carbon', 'Water', 'Hydrogen'],
         9: ['Plutonium', 'Uranium', 'Thorium', 'Radon'],
         10: ['Robert Oppenheimer', 'Galileo Galilei', 'Charles Darwin', 'Gregor Mendel'],
      },
      'hard': {
         11: ['206', '0', '35', '50'],
         12: ['Radiation', 'Sound', 'Pressure', 'Magnitude'],
         13: ['Limestone', 'Pumice', 'Basalt', 'Granite'],
         14: ['Richter Scale', "Mohs' Scale", "Kelvin Scale", "Beaufort Scale"],
         15: ['Condensation', 'Evaporation', 'Sublimation', 'Deposition'],
         16: ['Silicon', 'Oxygen', 'Iron', 'Calcium'],
         17: ['Nihonium (Nh)', 'Tennessine (Ts)', 'Moscovium (Mc)', 'Oganesson (Og)'],
         18: ['Blue', 'Red', 'Orange', 'Pink'],
         19: ['Mercury', 'Mars', 'Venus', 'Jupiter'],
         20: ['Heart', 'Liver', 'Brain', 'Stomach']
      }
   }
   
   answers = {
      'easy': {
         1: "Jupiter",
         2: "A Cheetah",
         3: "Crust, mantle and core",
         4: "118",
         5: "An omnivore",
         6: "Meteorology",
         7: "Mycology",
         8: "Hydrogen",
         9: 'Uranium',
         10: 'Charles Darwin',
      },
      'hard': {
         11: '0',
         12: 'Radiation',
         13: 'Pumice',
         14: "Mohs' Scale",
         15: 'Sublimation',
         16: 'Oxygen',
         17: 'Oganesson (Og)',
         18: 'Blue',
         19: 'Venus',
         20: 'Liver'
      }
   }
   
   if difficulty == 'easy':
      questions = questions[difficulty]
      options = options[difficulty]
      answers = answers[difficulty]
      selected_keys = random.sample(list(questions.keys()), num_questions)
   elif difficulty == 'hard':
      questions = questions[difficulty]
      options = options[difficulty]
      answers = answers[difficulty]
      selected_keys = random.sample(list(questions.keys()), num_questions)
   elif difficulty == 'mix':
      questions = questions['easy'] | questions['hard']
      options = options['easy'] | options['hard']
      answers = answers['easy'] | answers['hard']
      selected_keys = random.sample(list(questions.keys()), num_questions)
   else:
      print('Invalid Difficulty')
      return
      
   selected_questions = {key: questions[key] for key in selected_keys}
   selected_options = {key: options[key] for key in selected_keys}
   selected_answers = {key: answers[key] for key in selected_keys}
   
   correct = 0
   total = 0
   
   for i in selected_keys:
      
      option_map = {
         'A': selected_options[i][0],
         'B': selected_options[i][1],
         'C': selected_options[i][2],
         'D': selected_options[i][3]
      }
      
      print(selected_questions[i])
      print(f"A: {option_map['A']}")
      print(f"B: {option_map['B']}")
      print(f"C: {option_map['C']}")
      print(f"D: {option_map['D']}")
      
      ans = input("Please enter A, B, C, or D: ").upper()
      
      while ans not in option_map:
         ans = input("Invalid input. Please enter A, B, C, or D: ").upper()
      
      if option_map[ans] == selected_answers[i]:
         print("Correct!")
         correct += 1
      else:
         print(f"Incorrect! The correct answer was {selected_answers[i]}.")
      input("Press ENTER to continue")
      print()
      total += 1
      
   if correct / total == 1:
      result = "Perfect!"
   elif correct / total >= 0.8:
      result = "Great!"
   elif correct / total >= 0.6:
      result = "Not bad!"
   elif correct / total >= 0.4:
      result = "Good effort."
   elif correct / total >= 0:
      result = "You need to study more!"
      
   print(f"{result} Your score was {correct}/{total}.")
   return correct
