![Quizlearn CI/CD](https://github.com/software-students-spring2025/3-python-package-usps-525-3-violation/actions/workflows/build.yaml/badge.svg)


# Python Package Exercise

An exercise to create a Python package, build it, test it, distribute it, and use it. See [instructions](./instructions.md) for details.

## Team members
- [Tim Xu](https://github.com/timxu23)
- [Anna Ye](https://github.com/AnnaTheYe)
- [Jack Wang](https://github.com/JackInTheBox314)
- [Joylyn Gong](https://github.com/joylyngong)

## Description

This is an educational quiz game package. Users can choose between playing a math game, vocab game, geography game, or science game to test their skills and knowledge.

## PyPI Link

## Steps necessary to run program

### Importing into your project
# TODO

### Running example usages

1. First, clone the respository:

```
git clone https://github.com/software-students-spring2025/3-python-package-usps-525-3-violation.git
```
2. Then change directories into the repository:

```
cd 3-python-package-usps-525-3-violation
```

3. Create `pipenv` virtual environment and install package:

```
something to do with PyPI will go here, refer to example
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

### Running Pytest

1. First, clone the respository:

```
git clone https://github.com/software-students-spring2025/3-python-package-usps-525-3-violation.git
```
2. Then change directories into the repository:

```
cd 3-python-package-usps-525-3-violation
```

3. Create `pipenv` virtual environment and install package:

```
something to do with PyPI will go here, refer to example
```
4. Activate virtual environment:

```
pipenv shell
```

5. Run pytest with coverage reports:

```
PYTHONPATH=src pipenv run pytest --cov=quizlearnpackage --cov-report=term-missing
```


- how a developer who wants to import your project into their own code can do so - include documentation and code examples for all functions in your package and a link to an example Python program that uses each of them.
- how a developer who wants to contribute to your project can set up the virtual environment, install dependencies, and build and test your package for themselves.
- the names of all teammates as links to their GitHub profiles in the `README.md` file.
- instructions for how to configure and run all parts of your project for any developer on any platform - these instructions must work!
- instructions for how to set up any environment variables and import any starter data into the database, as necessary, for the system to operate correctly when run.
- if there are any "secret" configuration files, such as `.env` or similar files, that are not included in the version control repository, examples of these files, such as `env.example`, with dummy data must be included in the repository and exact instructions for how to create the proper configuration files and what their contents should be must be supplied to the course admins by the due date.

## Function usages and examples:

### play_math
This function starts a math quiz game. Users can choose the number of questions, and the difficulty of the questions to be easy, medium, or hard. Users interact with the function via `input()`.

| Argument    | Type | Description |
|------------|------|-------------|
| `level`  | `string`  | Must be either `'easy'`, `'medium'`, or `'hard'`. Indictes difficulty level of arithmetic problems. |
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

### play_geo
what does the code do
exceptions thrown:

| Argument    | Type | Description |
|------------|------|-------------|
| `arg1`  | `datatype`  | wordwords. |
| `arg2` | `datatype`  | yadayada |

```
example input output
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
| `num_questions`  | `Integer`  | Number of questions you will be given, has to be between 1 and 10. |
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
