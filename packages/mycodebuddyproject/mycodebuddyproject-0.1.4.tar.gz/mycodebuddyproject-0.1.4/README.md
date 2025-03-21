# MyCodeBuddyProject

![Python build & test](https://github.com/software-students-spring2025/3-python-package-float/actions/workflows/build.yaml/badge.svg)

A Python package designed to assist you throughout your coding projects. This package allows users to receive debugging tips, fun facts, resources for language help, and has a study timer to help users stay focused.

## Teammates

- [Angel Serrano](https://github.com/a-ngels)
- [Aria Nguyen](https://github.com/ariangn)
- [Melissa Kelly](https://github.com/melissalkelly)
- [Siyu Lei](https://github.com/em815)

## Link to package on PyPI
[MyCodeBuddyProject](https://pypi.org/project/mycodebuddyproject/0.1.4/)

## Developer Instructions

### Step 1: Install the Package
To use MyCodeBuddyProject in your project, first install it from PyPI. In your terminal or command prompt, type:
```
pip install mycodebuddyproject
```

### Step 2: Import Package
After installing the package, import mycodebuddyproject functions so they can be used directly in your code.

A sample program can be found [here](https://github.com/software-students-spring2025/3-python-package-float/blob/main/example.py).

```python
import mycodebuddyproject.get_debug_tips as debug
import mycodebuddyproject.get_help as get_help
import mycodebuddyproject.fun_facts as fun_facts
from mycodebuddyproject.study_timer import StudyTimer

print("Get a debugging tip for runtime errors")
print(debug.debug_tip("runtime"))

print("# Get a documentation link for Python")
print(get_help.language_help("python"))

print("Get a fun fact about Python features")
print(fun_facts.get("features"))

print("Start a study timer for 2 minutes")
timer = StudyTimer()  # Create an instance of StudyTimer
timer.start(25)       # Start a 25-minute study session
timer.pause()         # Pause the session
timer.resume()        # Resume the session
timer.cancel()        # Cancel the session
```

## Functions

#### `debug_tip(error_type)`
Returns a random debugging tip for the specified error type.
- **Parameters**:
   - `error_type` (str): The type of error ("syntax, "runtime", "logic").
- **Returns**: random debugging tip

##### Example
```python
debug_tip("runtime")
# Output: "Are you trying to divide by 0? This will cause an error."
```

#### `language_help(language)`
Returns a link to documentation for a specified programming language.
- **Parameters**:
   - `language` (str): The programming language name.
- **Returns**: a link to documentation.

##### Example
```python
language_help("python")
# Output: "https://docs.python.org/3/"
```

#### `get(fact_type)`
Returns a random fun fact for the specified fact type.
- **Parameters**:
   - `fact_type` (str): The type of fact ("features", "libraries", "trivia", "performance").
- **Returns**: random fun fact

##### Example 
```python
get("features")
# Output: "Python uses indentation (whitespace) to define code blocks instead of braces {}."
```
### Study Timer
#### `start(timer_length)`
Starts timer with length specified in minutes.
- **Parameters**:
   - `timer_length` (str): The desired length of the timer in minutes.
- **Returns**:
   - No return value

#### `pause()`
Pauses current timer.
- **Parameters**:
   - no parameters
- **Returns**:
   - No return value

#### `resume()`
Resumes paused timer.
- **Parameters**:
   - no parameters
- **Returns**:
   - No return value

#### `cancel()`
Ends current session.
- **Parameters**:
   - no parameters
- **Returns**:
   - No return value

##### Example
```python
timer = StudyTimer() # Instantiate study timer class
timer.start(25) 
# Output: 
# Study session started! Good luck, you got it!!
#Enter 'pause' to pause the session at any time.
timer.pause()         # Pause the session
# Output:
# Study session paused, please enter 'resume' when you want to resume.
timer.resume()        # Resume the session
# Output:
# Resuming now.
timer.cancel()        # Cancel the session
#Output:
# Study session canceled.
```

## Developer Contributions

If you’d like to contribute:

1. Clone the repository using:
   ```bash
   git clone https://github.com/software-students-spring2025/3-python-package-float.git
   cd 3-python-package-float
   ```
2. Create and run virtual environment
   ```bash
   # Install or update pipenv if needed
   pip install --upgrade pipenv

   # Create virtual environment and install dependencies
   pipenv install --dev

   # Activate virtual environment
   pipenv shell
   ```
3. Create a new branch and make your changes.
   ```bash
   git checkout -b branch-name
   ```

4. Run all pytests with the following command:
   ```bash
   pytest
   ```

5. Build the package with the following command:
   ```bash
   python -m build
   ```

6. Commit and push changes
   ```bash
   git add .
   git commit -m "description of changes"
   git push origin branch-name
   ```

7. Make a pull request on this project's repository on Github.
