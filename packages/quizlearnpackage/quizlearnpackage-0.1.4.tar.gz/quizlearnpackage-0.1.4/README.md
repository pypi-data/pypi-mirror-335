![Quizlearn CI/CD](https://github.com/software-students-spring2025/3-python-package-usps-525-3-violation/actions/workflows/build.yaml/badge.svg)


# Python Package Exercise
## Team members
- [Tim Xu](https://github.com/timxu23)
- [Anna Ye](https://github.com/AnnaTheYe)
- [Jack Wang](https://github.com/JackInTheBox314)
- [Joylyn Gong](https://github.com/joylyngong)

## Description

This is an educational quiz game package. Choose between playing a math game, vocab game, geography game, or science game to test your skills and knowledge!

## [PyPI Link](https://pypi.org/project/quizlearnpackage/)

## Steps necessary to run program

### Package installation steps
1. Create `pipenv` virtual environment:

```
pip install pipenv
```
2. Activate virtual environment:

```
pipenv shell
```
3. Install package:
```
pipenv install quizlearnpackage
```
4. Import package into Python
```
from quizlearnpackage import quizlearn
```
5. Choose quiz type and enjoy!

```
# sample usage
quizlearn.play_vocab('hard', 'both', 12)
```

### Running example usages

1. First, clone the respository:

```
git clone https://github.com/software-students-spring2025/3-python-package-usps-525-3-violation.git
```
2. Then change directories into the repository:

```
cd 3-python-package-usps-525-3-violation
```

3. Create `pipenv` virtual environment:

```
pip install pipenv
```
4. Activate virtual environment:

```
pipenv shell
```

5. Run example script:

```
PYTHONPATH=src python3 -m quizlearnpackage
```

6. Follow instructions and enjoy!

### How to contribute to quizlearnpackage

1. First, clone the respository:

```
git clone https://github.com/software-students-spring2025/3-python-package-usps-525-3-violation.git
```
2. Then change directories into the repository:

```
cd 3-python-package-usps-525-3-violation
```

3. Create `pipenv` virtual environment:

```
pip install pipenv
```
4. Activate virtual environment:

```
pipenv shell
```

5. After making contributions, verify that they pass tests:

```
PYTHONPATH=src pipenv run pytest --cov=quizlearnpackage --cov-report=term-missing
```

6. Upload to PyPI
Remove any `dist` or `src/*.egg-info`, and increment version in `pyproject.toml`. Then,

```
pip install build twine
python -m build
twine upload dist/*
```

## Function usages and examples:

### play_math
This function starts a math quiz game. Users can choose the number of questions, and the difficulty of the questions to be easy, medium, or hard. Users interact with the function via `input()`.

| Argument    | Type | Description |
|------------|------|-------------|
| `level`  | `string`  | Must be either `'easy'`, `'medium'`, or `'hard'`. Indicates difficulty level of arithmetic problems. |
| `num_ questions` | `int`  | Indicates how many questions will be asked |

```
>>> play_math('easy', 3)

8 * 5 = 
Input your answer: 40
Correct!

30 / 3 = 
Input your answer: 10
Correct!

4 * 1 = 
Input your answer: 4
Correct!

Well done! 3/3 Correct
Elapsed time: 5.4 seconds
```

### play_geo(numOfQuestions, difficulty)
This function will prompt users to begin a geography quiz game that will challenge their knowledge on a diverse set of world geography questions. At each difficulty level of easy, medium, and hard, there will be 15 questions to be answered. The questions will range from topics about countries, states, rivers, to capitals. Once the user is finished with answering a question, they will be informed on whether the answer they provided was correct or not. At the end, they will be given a final score of how many questions they were able to answer correctly 

| Argument    | Type | Description |
|------------|------|-------------|
| `difficulty`  | `string`  | Revolves around three levels of difficulty from `'easy'`, `'medium'`, to `'hard'`. |
| `numOfQuestions` | `int`  | Number of questions prompted for users to answer at each difficulty level. |

Exceptions Raised:
- `ValueError("Invalid number of questions")`: `numOfQuestions` less than 1 or greater than 15 questions
- `ValueError("Invalid difficulty")`: `level` outside of `['easy', 'medium', 'hard']`
- `TypeError("Invalid type for numOfQuestions")`: `numOfQuestions` is not an integer value (e.g. in cases where the user is passing a float value or string when only an integer is suitable)

```
>>> play_geo(numOfQuestions=8, difficulty='easy')

What is the capital of Germany?
Your answer: Berlin
Correct!

Which continent is home to the Sahara Desert?
Your answer: Africa
Correct!

Which country has the largest population in the world?
Your answer: China
Correct!

Which U.S. state is known for having the Grand Canyon?
Your answer: Nevada
Incorrect! The correct answer was Arizona.

What is the name of the mountain range that separates Europe and Asia?
Your answer: Ural Mountains
Correct!

Which ocean borders the eastern coast of the United States?
Your answer: Pacific
Incorrect! The correct answer was Atlantic.

What is the capital of Argentina?
Your answer: Buenos Aires
Correct!

Which country is known for the ancient ruins of Machu Picchu?
Your answer: Bolivia
Incorrect! The correct answer was Peru.

Your final score: 6/8 (75%)
```

### play_vocab(level, mode, num_questions)
This function starts a vocab quiz game. Users can choose between three difficulties -- easy, medium, and hard -- and between three gamemodes -- synonyms only, antonyms only, or both. Users can also choose a number of questions to be asked between 1 through 15. There are 20 synonym/antonym tuples for each difficulty, and for each question, users can choose between 4 multiple choice answers. At the end, the score is printed. Users interact with the function via `input()`. Questions are capped at 15 to prevent the same words from appearing too many times in one game session.

Exceptions raised:
- `ValueError("Invalid difficulty")`: `level` outside of `['easy', 'medium', 'hard']`
- `ValueError("Invalid gamemode")`: `mode` outside of `['synonyms', 'antonyms', 'both']`
- `ValueError("Invalid number of questions)`: `num_questions` less than 1 or greater than 15

| Argument    | Type | Description |
|------------|------|-------------|
| `level`  | `string`  | Must be either `'easy'`, `'medium'`, or `'hard'`. Indictes which difficulty level of the wordbank questions will be drawn from. |
| `mode` | `string`  | Must be either `'synonyms'`, `'antonyms'`, or `'both'`. Indicates which types of questions will be asked.|
| `num_questions` | `int`  | Must be between `1` and `15`. Indicates how many questions will be asked.|

```
>>> play_vocab('hard', 'both', 3)

Which word is an antonym for Exultant?
A: Melancholic
B: Perspicacious
C: Indolent
D: Intrepid
Choose A, B, C, or D: 
>>> a
Correct!

Which word is an antonym for Diligent?
A: Pusillanimous
B: Frugal
C: Indolent
D: Thrifty
Choose A, B, C, or D: 
>>> d
Incorrect. The correct answer was Indolent

Which word is a synonym for Ephemeral?
A: Dauntless
B: Imperious
C: Transient
D: Ostentatious
Choose A, B, C, or D: 
>>> c
Correct!

Your total score this game was 2/3: 66%
```

### play_science
This function starts a science quiz game. Users can choose number of questions, ranging from 1 to 10, and choose the difficulty of the questions to be easy, hard, or a mix of both. Users interact with the function via `input()`.

| Argument    | Type | Description |
|------------|------|-------------|
| `num_questions`  | `int`  | Number of questions you will be given, has to be between 1 and 10. |
| `difficulty` | `string`  | Difficulty of the questions, must be `easy`, `hard`, or `mix` for a mix of questions of both difficulties. |

```
>>> package.play_science(num_questions=10, difficulty='easy')

What do you call the study of weather, climate and the atmosphere?
A: Climatology
B: Aerology
C: Atmospheric Science
D: Meteorology
Please enter A, B, C, or D: a
Incorrect! The correct answer was Meteorology.
Press ENTER to continue

Who is credited with coming up with the theory of evolution?
A: Robert Oppenheimer
B: Galileo Galilei
C: Charles Darwin
D: Gregor Mendel
Please enter A, B, C, or D: a
Incorrect! The correct answer was Charles Darwin.
Press ENTER to continue

What are the three layers of the Earth
A: Outer shell, inner shell, and center
B: Land, water, and atmosphere
C: Rock layer, magma layer, and deep core
D: Crust, mantle and core
Please enter A, B, C, or D: d
Correct!
Press ENTER to continue

You need to study more! Your score was 1/3.
```
