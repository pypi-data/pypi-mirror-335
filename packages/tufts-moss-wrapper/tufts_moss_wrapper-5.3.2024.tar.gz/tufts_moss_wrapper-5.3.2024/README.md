# MOSS Wrapper

## Description
This repository is for `moss` a wrapper of `moss.pl`. `moss.pl` is the [Measure of Software Similarity (MOSS)](http://theory.stanford.edu/~aiken/moss/) submission script. MOSS can be used to detect plagiarism in students' code. [This somewhat humorous article](https://github.com/genchang1234/How-to-cheat-in-computer-science-101) describes some types of plagiarism that can be detected. MOSS has influenced other plagiarism detection software such as the [software used by Gradescope](https://www.cs.washington.edu/lab/course-resources/gradescope). However, one benefit using MOSS outside of Gradescope is that you can incorporate previous semesters as well as scraped GitHub repositories into the job. 

`moss` was designed for Tufts University computer science courses and offers the following features: 

* It enables use of MOSS with the Tufts Computer Science Department `provide` submission and `grade` frameworks.
* It provides a more user friendly interface than `moss.pl` in terms of specifying base files and even the files to upload.
* It enables organized downloading of MOSS results in the interest of maintaining a record of plagiarism cases (and not relying on the MOSS servers being stable).
* It offers protection against someone uploading files that could break MOSS (e.g. a non source file named like a source file, e.g. a zip named `x.cpp`). `moss.pl` does not have this protection, and neither do the MOSS wrappers I've used in the past (e.g. the [C# GUI one](https://github.com/shanemay/MossApp)).

**Fall 2022 - Present**

## Prerequisites

1. This has been tested on Python 3.9.2 and Python 3.10.6.
2. Get the Python modules that are needed with `pip3 install -r requirements.txt`.
3. Download `moss.pl` from [here](http://moss.stanford.edu/general/scripts/mossnet).
4. Ensure that `moss.pl` is on your `PATH` and is executable.
5. Substitute your MOSS UUID in the `$userid` variable in `moss.pl` with a UUID requested from MOSS (see the Registering for MOSS section [here](http://theory.stanford.edu/~aiken/moss/) for instructions).

## Installation

1. Download `moss` from this repository. 
2. Optional: Set it to be executable (if you're on a Unix-based system this will allow you to just do `./moss`). Note, it can also just be run with `python moss` if you're working on Windows. 

## Usage

This script requires the user to pass in a [TOML](https://toml.io/en/) configuration file. The options that are required are different for [Non-Job Mode](#non-job-mode) and [Job Mode](#job-mode). These are both discussed in detail below.

### Non-Job Mode

This is the regular mode that you are more likely to use. This mode submits a job to Stanford's servers to run MOSS and identify plagiarism. For this mode, you must specify the `curr_sem` setting to be a string that has the path to the directory holding submissions for an assignment that will be considered the current semester. See [here](#what-should-curr_sem-and-assn_dirs-directories-look-like) for how this directory should be set up. 

This is the full list of configuration options you can specify in the TOML listed here. The default values have been specified in the context of [CS 15](https://www.cs.tufts.edu/comp/15/).

| Option | Type | Default Value | Description |
|---|---|---|---|
| `name` | `str` | `None` | Name of the assignment. This will be displayed in MOSS results and in downloaded folder name. It is recommended you set this so you can keep track of MOSS results if you're running jobs for various assignments and are storing them all together. |
| `base` | `str` | `None` | MOSS allows you to provide base files that are provided to students that are similar among all student submissions. This helps reduce false positives for instances of plagiarism. This is the directory where these base files are stored. See [here](#what-should-base-directory-look-like) for how this directory should be set up. |
| `output` | `str` | `"."` | This is the directory where all output from this script will go consolidated in a job folder. `moss` creates a job folder named with `name` if it was provided as well as the date and time to make it unique within `output`. This job folder includes at least a file with the MOSS returned URL and the script's log. However, if `download` is set to `true`, then the matches will also be downloaded into there as well. |
| `curr_sem` | `str` | Required | This is the assignment directory corresponding to the submissions in the current semester. This is used to determine which results to save from MOSS. See [here](#what-should-curr_sem-and-assn_dirs-directories-look-like) for how these directories should be set up. |
| `assn_dirs` | `List[str]` | `[]` | List of additional assignment directories to include in the job in addition to the current semester. This should be a list of strings of paths to these directories. These directories could be previous semesters or GitHub repositories for example. See [here](#what-should-curr_sem-and-assn_dirs-directories-look-like) for how these directories should be set up. |
| `download` | `bool` | `false` | This specifies whether MOSS results should be downloaded from the provided MOSS URL. **While this is `false` by default, it is recommended you set this to `true` to avoid having to run in job mode.** The way `moss` downloads results is more easily usable than the results shown online and means you don't have to resubmit jobs once the two week time window MOSS provide expires if you are conducting a longer term investigation. |
| `match_formatter` | `str` | `None` | This is a string specifying a Python function in `custom_file` that will be used to format directory names in matches. See [here](#what-should-match_formatter-look-like) for how this should be written. |
| `submission_filter` | `str` | `None` | This is a string specifying a Python function in `custom_file` that will be used to filter out certain files from submission directories when running MOSS. See [here](#what-should-submission_filter-look-like) for how this should be written. |
| `custom_file` | `str` | `None` | This is a string specifying a path to a Python source file that contains `match_formatter` and `submission_filter`. *This must be provided if either `match_formatter` or `submission_filter` is provided.* |
| `submissions_to_collect` | `int` | 250 | This corresponds to the `-n` value in `moss.pl` which determines the number of matching files to show in the results. The default value is the `moss.pl` default which I've never touched. |
| `threshold_for_repeated_code` | `int` | 10 | This corresponds to the `-m` value in `moss.pl` which sets the maximum number of times a given passage may appear before it is ignored.  A passage of code that appears in many programs is probably legitimate sharing and not the result of plagiarism.  With `-m N`, any passage appearing in more than `N` programs is treated as if it appeared in a base file (i.e., it is never reported). Note, `moss.pl` gives a second explanation of `-m` after this which from experience is incorrect and most likely an old comment. The default value is the `moss.pl` default which I've never touched. |
| `language` | `str` | `"cc"` | This corresponds to the `-l` value in `moss.pl` which sets the language of the submissions. The current list in `moss.pl` is `"c", "cc", "java", "ml", "pascal", "ada", "lisp", "scheme", "haskell", "fortran", "ascii", "vhdl", "perl", "matlab", "python", "mips", "prolog", "spice", "vb", "csharp", "modula2", "a8086", "javascript", "plsql"`. However, it is unclear whether `moss.pl` enforces it. |
| `source_extensions` | `List[str]` | `[".h", ".cpp"]` | Provides a list of file extensions to specify which files should be input to `moss.pl` to submit to the MOSS servers. Note files with any of these extensions are checked to be text files. This is done to protect against a student accidentally renaming something that isn't a source file to have one of the expected extensions. There is no protection in MOSS against this, and the job will fail (this is learned from personal experience). *Note, if this is empty, then no files will be match on extension.* This is used in addition to `source_file_types` to collect files. |
| `source_file_types` | `List[str]` | `["C source", "C++ source"]` | Provides a list of strings that will be searched in the file types of a file. Any file whose type contains at least one of these strings is collected into the job. By file types, we mean the types reported by the Linux `file` command. For example `file x.cpp` could report things like `C++ source, ASCII text`, `C++ source, ASCII text, with CRLF line terminators`, `C source, ASCII text`, or others. You should set this to be a relatively conservative list. Don't put things like `text` as non source files (e.g. a README) will be included. If some source files don't have types who contain any string in `source_file_types`, they could be handled based on the extension specified in `source_extensions`. So, tune these parameters jointly. |
| `required_groups` | `List[str]` | `["grade15", "ta15"]` | This allows one to specify which groups the user running `moss` must belong to in order to run the script appropriately. For example, if submission directories are in protected folders, this is provides a nice check to make sure the person running this script can access them. |


#### **What should `base` directory look like?**

The base directory should have the files provided to the students inside. For example, it could look something like this: 

```
|--- ~/courses/cs50/assn1/starter/
|   |--- Utilities.h
|   |--- Utilities.cpp
|   |--- input.txt
|   |--- data_files/
```

We would specify this in the TOML with `base = "~/courses/cs50/spring2023/assn1/starter"`.

Only the `.h` and `.cpp` files will be taken from this folder (`Utilities.h` and `Utilities.cpp`), all other files, directories, and symlinks will be ignored so you do not have to worry about having them there.

#### **What should `curr_sem` and `assn_dirs` directories look like?**

`curr_sem` and `assn_dirs` all form assignment directories. They should have the students' submissions collected into folders inside. It is assumed these folders are uniquely identifiable in some way (e.g. with a student ID or GitHub username, repository combination). Students submission directories should take on one of two forms. 

1. The Tufts provide form. Here, students are allowed to submit multiple times and the submissions are numbered based on their name followed by `.` and a number. 

2. The normal form. Here, each directory is assumed to be a separate student's submission. 

Suppose we have the following submissions directory. 

```
|--- ~/courses/cs50/spring2023/assn1/submissions
|   |--- student1.1/
|   |--- student1.2/
|   |--- student1.3/
|   |--- student2.1/
|   |--- student3.1/
|   |--- student3.2/
|   |--- student4/
|   |--- gituser1_repo1/
```

The first six folders follow the Tufts provide form. `moss` will only select the most recent submissions of these. In this case, `student1.3`, `student2.1`, and `student3.2`. The other folders are identified to be in normal form as they do not have `.` followed by a number, so they are also identified as submissions.

Within each of these folders, `moss` will: 

1. Reject any files that fail the `submission_filter` if it was provided.
2. Use the `source_file_types` first to look for files whose types contain those strings. Any that match are collected.
3. Use the `source_extensions` to collect other files. These candidates are then checked to be non-empty text files. Those that match are collected as well.  

Any directories or symlinks or other files inside will be ignored, so you can leave in other things students may submit (READMEs, input testing files, etc.). 

Note this is one Tufts-specific automation that `moss` makes, the other has to do with adjusting for the `grade` utility used in the past. Please read [this section](#what-is-special-about-studentd041) in the demo for more information. If you have some submission framework where students have code in nested directories, you will have to flatten those directories. We actually do this with GitHubs we scrape before piping them into this script.

#### **What should `match_formatter` look like?**

The function named by `match_formatter` in `custom_file` should take a single string parameter and return a single string. You should use this function to simplify paths to student submissions. For example, suppose you have collected the submissions for an assignment in a folder named `~/courses/cs50/spring2023/assn1/submissions`. By default, results will be displayed on the MOSS website with the full path to these submissions something like: 

```
/home/yourname/courses/cs50/spring2023/assn1/submissions/student1 ... /home/yourname/courses/cs50/spring2023/assn1/submissions/student2 ...
```

And similarly, `moss` will download these matches into folders named: 

```
_home_yourname_courses_cs50_spring2023_assn1_submissions_student1_and__home_yourname_courses_cs50_spring2023_assn1_submissions_student1
```

As you can see, this is somewhat unreadable and unwiedly. Unfortunately, there is no way via `moss.pl` to change how MOSS chooses to display the results on their HTML page online. However, `match_formatter` provides you with a way to simplify these paths to shorter, but still unique names in the downloaded match folders. For example, you could reduce the match folders to just have the student name and semester (as you may be interested in seeing people copy from previous semesters). This assumes the student name and semester pair will be unique, so using some sort of ID in place of the student's actual name may be more useful.

Here's one way you could do this. Note that the `match_formatter` function will receive a string submission path like `"/home/yourname/courses/cs50/spring2023/assn1/submissions/student1"`. 

```python
def simplify_folder(submission_path):
  comps = submission_path.split("/")
  return comps[5] + "_" + comps[-1]
```

This would take `"/home/yourname/courses/cs50/spring2023/assn1/submissions/student1"` and return `"spring2023_student1"`. Suppose this function lived in `~/courses/cs50/utilities/moss_customization.py`. You would point this information to `moss` with these TOML settings:

```
custom_file = "~/courses/cs50/utilities/moss_customization.py"
match_formatter = "simplify_folder"
```

Note, by setting `name` as well in the TOML, these results will go into a `moss`-produced folder that will identify the assignment.

#### **What should `submission_filter` look like?** 

The function named by `submission_filter` in `custom_file` should take a single string parameter and return a boolean. You should use this function to filter out any submissions you may want to skip. For example, if you have a special student you use for testing every semester, you may want to filter them out so you don't get meaningless results of this student "cheating" off of themselves every semester. Suppose this student is identified by `course50fakestudent`. 

We could write a function to filter these out: 

```python
def filter_fake_student(submission_filepath):
  return "course50fakestudent" not in submission_filepath
```

`moss` will pass this function individual files paths like `"/home/yourname/courses/cs50/spring2023/assn1/submissions/student1/file1.h"`, `"/home/yourname/courses/cs50/spring2023/assn1/submissions/student1/file1.cpp"`, etc. *Note, `moss` will only pass in `.h` and `.cpp` files to this filter*. Suppose this function lived in `~/courses/cs50/utilities/moss_customization.py`. You would point this information to `moss` with these TOML settings:

```
custom_file = "~/courses/cs50/utilities/moss_customization.py"
submission_filter = "filter_fake_student"
```

### Job Mode

Job mode is designed in the event you have already run `moss` but did not specify `download = true` and you want go back and download results. This assumes you have already run `moss` successfully. In this mode you can specify either two or four TOML configuration options. The two options you must supply are `curr_sem` as defined in [Non-Job Mode](#non-job-mode) and `job`. `job` is a string that is a path to a previously created job folder that will hold the URL file. Recall from the description of `output` in [Non-Job Mode](#non-job-mode) that a job folder will always hold a URL file. 

You can additionally supply `custom_file` and `match_formatter` as described in [Non-Job Mode](#non-job-mode). However you *other TOML options will be ignored if `job` is specified*. 

## Demonstrations

### Non-Job Mode Example

#### **Setup**

For the Non-Job Mode example, I have provided a `demo` folder. Inside it there is a collection of folders for an assignment in `assignment`. `assignment` has the following directory structure: 

```
|--- githubs/                   [Directory with scraped git repositories]
|   |--- githubuser1/           [Git repository of solution to homework 1]
|--- sem1/                      [Directory with a "semester" of assignments]
|   |--- fakestudent/           [Fake student used for testing]
|   |--- studenta01.1/          [A solution to homework 1]
|   |--- studenta01.2/          
|   |--- studentb02.1/          [Another solution to homework 1]
|   |--- studentb02.2/
|   |--- exceptions.conf        [some configuration files]
|   |--- grace.conf             
|   |--- studenta01.1.log       [some submission record files]
|   |--- studenta01.1.time
|   |--- studenta01.2.log
|   |--- studenta01.2.time
|   |--- studentb02.1.log
|   |--- studentb02.1.time
|   |--- studentb02.2.log
|   |--- studentb02.2.time
|--- sem2/       
|   |--- fakestudent/           [Fake student used for testing]               
|   |--- studentc03.1/          [Another solution to homework 1]
|   |--- studentc03.2/          ...
|   |--- studentc03.3/          [Another solution to homework 1]
|   |--- studentd04.1/          [See below]
|   |--- ...                    [some configuration and record files as above]
|--- starter/                   [Starter code for homework 1]
```

Within each of the assignment folders (git repositories and provide folders) there will be a mixture of C++ and non C++ files. As mentioned previously, `moss` will ignore all non `.cpp` and non `.h` files in submitting a MOSS job. 

Note that the only code files in these directories are all blank and named `file1.h` and `file.cpp`. This is done intentionally as to not make any starter or solution code to any Tufts COMP 15 homework assignment public. Before running a real demo, replace these files in the demo with actual starter and solution code from an assignment. To see the type of copies that MOSS can detect, copy one solution and distribute them over multiple submission folders with changed names, reordered code, etc.

#### **What is special about `studentd04.1`?**

`studentd04.1` is a special case in that it contains a directory structure like: 

```
|--- studentd04.1/ 
|   |--- grading/
|   |   |--- file1.cpp
|   |   |--- file1.h
|   |   |--- Makefile
|   |   |--- README
|   |--- file1.cpp.bak
|   |--- file1.h.bak
|   |--- Makefile.bak
|   |--- README.bak
```

Tufts TAs used to use a utility called `grade` that would allow graders to edit students code in a subfolder called `grading` while retaining the student's original code in `.bak` files. `moss` will make copies of the C++ `.bak` files in a temporary directory that have their suffixes fixed to `.h` and `.cpp` and those will be submitted to MOSS.

#### **Running `moss`**

There are two additional essential files in `demo`.

`demo_custom.py` is our simple Python file:
```python
def simplify_folder(submission_path):
    return submission_path.lstrip("demo/")

def remove_fake(submission_filepath):
    return "fakestudent" not in submission_filepath
```

`demo.config` is our TOML configuration file:
```toml
name = "demo_assignment"
base = "demo/assignment/starter"
output = "demo/moss_results"
curr_sem = "demo/assignment/sem1"
assn_dirs = ["demo/assignment/sem2", "demo/assignment/githubs"]
download = true
match_formatter = "simplify_folder"
submission_filter = "remove_fake"
custom_file = "demo/demo_custom.py"
```

We run `moss` with:
```bash
moss demo/demo.config
```

This creates a folder named something like `demo_assignment_job_20230314_160933` in `demo/moss_results` (which could have already existed) and inside it, it inserts the following files:
```
moss.config
moss.url
```

`moss.config` is a copy of the configuration file you passed into `moss`, so it's okay if you misplace `moss` configuration files for future use. `moss.url` will look something like this:
```
http://moss.stanford.edu/results/0/123456789
Estimated expiration time: 03/28/2023 04:09 PM EST
```

In addition to these files, `moss` will also create a folder called `results` inside `demo_assignment_job_20230314_160933`. Inside there, it will place the match folders named as discussed [above](#what-should-match_formatter-look-like). Within those folders you will find four files named:

```
OPENME.html
match-top.html
match-0.html
match-1.html
```

These serve as an offline version of the MOSS results shown online. You should open `OPENME.html` in a browser to navigate the results as you would online. For more information on reaing MOSS results, see [here](http://moss.stanford.edu/general/format.html). Note that all of these files only rely on each other, hence these can be used offline in the future beyond the two week MOSS expiration time. These are also useful in the event the MOSS servers used to display results (and the main website at [moss.stanford.edu](https://theory.stanford.edu/~aiken/moss/)) go down. This can happen more often than expected. A good way of checking that the display servers are offline is by trying to `ping moss.stanford.edu`. Careful when trying to access it in a browser because of caching.

For this demonstration, since the input files we are sending to MOSS are blank, there are no actual match folders. You should run through actual submissions to see the results.

A file called `matches.tsv` is placed into the job folder next to `results`. This will list the matches for all the matches that were downloaded. **Remember, only matches for the current semester are downloaded into `results` and are placed into `matches.tsv`.** Inside `matches.tsv`, you will find it has seven columns described below. 

| Column | Description | 
|---|---|
| `Person1` | This has the formatted match folder corresponding to the first person in the match. This will be a submission directory path from an assignment directory passed through the user provided `match_formatter`. |
| `Person2` | Same as `Person1`, just for the second person in the match. |
| `Person1_Match_Perc` | MOSS reported percentage of Person 1's code that matches code in Person 2. |
| `Person2_Match_Perc` | MOSS reported percentage of Person 2's code that matches code in Person 1. |
| `Lines_Matched` | The number of lines matched between the two people. |
| `URL` | The online URL of the match. |
| `Results_Subfolder` | The subdirectory of `results` that corresponds to the match. |

`matches.tsv` is sorted in decreasing order on `Lines_Matched`. 

### Job Mode Example

For this example, pretend we did not set `download` to `true` in the previous example. We can download the matches for that job by setting up this configuration file: 
```TOML
job="demo/moss_results/demo_assignment_job_20230314_160933"
curr_sem = "demo/assignment/sem1"
match_formatter = "simplify_folder"
custom_file = "demo/demo_custom.py"
```

And then run `moss` with:
```bash
moss demo/demojob.config
```

## Debugging the Script

The script also provides a detailed log in a file called `.moss.log` inside the created job folder. Inside the log you can find the `moss.pl` command that is constructed by our script as well as the logs of the `moss.pl` run as well as our script's logging information. You can also see how long it takes to run MOSS jobs as well as if any submission folders were skipped due to permission errors. Here's an example log snippet: 

```text
2023-05-09 17:48:35,296 | [INFO] : Constructing moss.pl command ...
2023-05-09 17:48:35,317 | [INFO] : moss.pl command constructed.
2023-05-09 17:48:35,317 | [INFO] : Submitting MOSS job...
2023-05-09 17:48:35,320 | [DEBUG] : Running moss.pl -c "demo_assignment: job submitted at 05/09/2023 05:48 PM EST. Estimated expiration time: 05/23/2023 05:48 PM EST" -l cc -n 250 -m 10 -b demo/assignment/starter/file1.cpp -b demo/assignment/starter/file1.h -d demo/assignment/sem1/studenta01.2/file1.cpp demo/assignment/sem1/studenta01.2/file1.h demo/assignment/sem1/studentb02.2/file1.cpp demo/assignment/sem1/studentb02.2/file1.h demo/assignment/sem2/studentc03.3/file1.cpp demo/assignment/sem2/studentc03.3/file1.h demo/assignment/sem2/studentd04.1/.tmp_moss_dir/file1.cpp demo/assignment/sem2/studentd04.1/.tmp_moss_dir/file1.h demo/assignment/githubs/githubuser1/file1.cpp demo/assignment/githubs/githubuser1/file1.h
Checking files . . . 
OK
Uploading demo/assignment/starter/file1.cpp ...done.
Uploading demo/assignment/starter/file1.h ...done.
Uploading demo/assignment/sem1/studenta01.2/file1.cpp ...done.
Uploading demo/assignment/sem1/studenta01.2/file1.h ...done.
Uploading demo/assignment/sem1/studentb02.2/file1.cpp ...done.
Uploading demo/assignment/sem1/studentb02.2/file1.h ...done.
Uploading demo/assignment/sem2/studentc03.3/file1.cpp ...done.
Uploading demo/assignment/sem2/studentc03.3/file1.h ...done.
Uploading demo/assignment/sem2/studentd04.1/.tmp_moss_dir/file1.cpp ...done.
Uploading demo/assignment/sem2/studentd04.1/.tmp_moss_dir/file1.h ...done.
Uploading demo/assignment/githubs/githubuser1/file1.cpp ...done.
Uploading demo/assignment/githubs/githubuser1/file1.h ...done.
Query submitted.  Waiting for the server's response.
http://moss.stanford.edu/results/1/0123456789
2023-05-09 17:48:37,458 | [DEBUG] : Finished
2023-05-09 17:48:37,459 | [DEBUG] : MOSS job completion time: 0:00:06
2023-05-09 17:48:37,463 | [INFO] : Success! Results at http://moss.stanford.edu/results/1/0123456789
2023-05-09 17:48:37,463 | [DEBUG] : Estimated expiration time: 05/23/2023 05:48 PM EST
2023-05-09 17:48:37,465 | [DEBUG] : Running GET http://moss.stanford.edu/results/1/0123456789/index.html
2023-05-09 17:48:37,622 | [DEBUG] : Response saved to demo/moss_results/demo_assignment_job_20230509_174835/results/index.html
2023-05-09 17:48:37,625 | [INFO] : Downloading 0 matches...
```

### No Logged Errors but No URL Either

It is not uncommon to have `moss` (really `moss.pl`) crash and report that no `URL` could be identified, but `moss.pl` does not report any issue into `.moss.log`. 

The best one can do is look for `Query submitted.  Waiting for the server's response.` in the log. If that line does not appear, that means `moss.pl` failed to even upload all the files in the job. If this line does not appear, and most of the files got uploaded before `moss.pl` timed out, try rerunning `moss` again after a bit. 

If `Query submitted.  Waiting for the server's response.` is in the log and `moss.pl` still crashes, it is likely the server that's actually running the plagiarism detection software is down. In this case, a job with even a few submissions will not run. This is a good way to identify if the compute server is down. In this case, you may have to wait a longer period than above, maybe hours or days. 

Another issue I have encountered only on one occurrence with MOSS is the possibility that the URL is provided by MOSS and then immediately going to that URL reports the 404 error (i.e. requested resource/URL is not found on the server). I have no idea what this means, I guess it is possible that something went wrong with how the results on their end is getting posted to the server(s) that are used to provide results. My only solution to this is to wait a bit again (maybe a day or more) to rerun the job. It seems like those URLs never come back to life.

In my experience at Tufts, there has *never been an issue with the submitted files* in the event of a submission failure. When the servers are up, even with jobs that have hundreds of submissions usually complete *within fifteen minutes*.

## Parsing Old Results 

This script used to output things somewhat differently. The most important differences are listed here: 
* `match_formatter` did not exist, so the match folders were named in the long and unwieldy way discussed [previously](#what-should-match_formatter-look-like). 
* `moss.pl` output was split between two files `stdout.txt` and `stderr.txt`.
* `wget` downloading was split between two files inside job folders.
* `matches.tsv` was also split over two files ranked in decreasing order by lines matched and maximum similarity percentage between the two students in the match.
* In more recent versions, `matches.tsv` was inside the `results` folder.
* The way people are identified (e.g. in the `Person1` and `Person2` columns of `matches.tsv`) varies over time. Pre fall 2023, people were identified with their UTLNs. In fall 2023, they were identified by Gradescope submission IDs. Starting in spring 2024, they were identified with email. All in all, always have students enter their information in their files (name, UTLN, email, etc.). 

## Additional Notes

* There are two potential areas for instability in this script. First, the job submission component depends on the `moss.pl` configuration options not changing. However, I think this assumption is rather safe as they have not changed since fall 2019 when I first started using MOSS. Second, the match downloading component depends on how the MOSS results HTML file is formatted. If the way the matches, percentages, URLs, etc. are presented changes, `moss` would stop working properly. However, this also has not changed since fall 2019 and I would expect similar tools like Gradescope's "Review Similarity" to also break as I suspect that parses match delimiters in the HTML files as well.

## Potential Upgrades

* Downloads could be sped up by having each match download be done in a separate process. Match downloads are entirely independent from each other and no other aspect of the program depends on them. `matches.tsv` is created before the downloading process begins. I would particularly recommend using processes instead of threads to avoid GIL contention. I think this change would be easily made to `__download_match`, just make sure the `Process` objects are saved somewhere to be joined on. Would also have to deal with cross process logging to a file.

## Support
* Contact: Swaminathan.Lamelas@tufts.edu

## Authors
* [Chami Lamelas](https://sites.google.com/brandeis.edu/chamilamelas) -- Developer

## Acknowledgements
* [Matt Russell](https://www.linkedin.com/in/matthew-russell-152a4414/) -- I took the idea of allowing users to specify their own match formatting, submission filtering as functions in a Python file based on what Matt does with `canonicalizers.py` in his [CS 15 autograder](https://gitlab.cs.tufts.edu/mrussell/gradescope-autograder). I also used his approach of loading TOML files into Python dataclasses.
* Ryan Polhemus -- gave me the idea of using magic numbers (i.e. the Linux `file` command) to do better checks on files before uploading to MOSS via `moss.pl` to protect against the `x.java` zip file "exploit".

## Changelog

### 5.3.2024
* Update `moss` permissions information accessing to handle the case when a group or user name cannot be retrieved from a UID/GID. 

### 4.12.2024
* Cleanup permission handling. In particular, we now do explicit access checks for both the directory and the files inside. If the directory can't be accessed, that's one warning. If a file within the directory can't be accessed, that's another warning. All files within an accessible directory will still be collected now (previously only a subset would be). Furthermore, we add additional permissions information so one can see why a file can't be accessed (i.e. show the perms, owner, and group).

### 3.24.2024
* Patch bug related to `map`

### 3.22.2024
* Clean up configuration by loading TOML into a dataclass instead of a dictionary and then separately handling defaults. 
* Files that are collected to upload are now also checked to be text based on magic number in addition to extension to avoid the `X.java` bug.
* Magic number check is done to identify any source files that may be disguised (e.g. `x.cpp -> x`). This is done via the user supplying a conservative list of strings `source_file_types`. Any file with a type that contains at least one of those strings will be included regardless of the extension.
* Added more configuration options to enable more widespread use:
  * MOSS `-m` and `-n` options can be set.
  * MOSS language option can be set.
  * File types for submission (see above).
  * If above not specified, extensions.
  * Required groups can now be specified.
* Minor improvements to error reporting.
* Additional minor code refactoring.
* Bring demo up to date with previous changes
* README updates

### 3.21.2024
* Moved from [GitLab](https://gitlab.cs.tufts.edu/slamel01/comp15-moss) to [GitHub](https://github.com/ChamiLamelas/moss-wrapper).

### 3.12.2024
* Made log file not hidden for usability.

### 3.4.2024
* Changed `moss` to now enforce that the user running the script belongs to the `grade15` and `ta15` groups. You must be in these groups in order to access the `grading/` subfolders of some old semester folders in the Tufts system (e.g. `/g/15/2021f/grading`). Note, we enforce these groups because these `grading/` subfolders are often placed into the `assn_dirs` setting in MOSS configuration files.

### 2.27.2024
* Changed the downloading component to have `matches.tsv` be placed next to `results/` in a job folder instead of being placed inside the `results/` folder. In doing so, renamed the `Local_Folder` column in `matches.tsv` to `Results_Subfolder`.

### 2.26.2024 
* Patched bug where `moss`, when in non job mode (i.e. when a job folder is provided to download, the job folder would not be recognized if the user used `~` in palce of the home directory.
* Patched bug where `moss` would crash in non job mode because `submission_filter` was incorrectly both required and not allowed. 
* Patched bug where `moss` would incorrectly repeatedly download the same match file into `OPENME.html`, `match-0.html`, `match-1.html`, and `match-top.html`. This led to an infinite rendering bug when trying to display the files. I assume this is a result of [this update](#572023).

### 2.23.2024
* Patched bug where `moss` incorrectly identified a folder identified by email (as with our new hitme system) was a folder that was a `provide` folder (because of a period `.` being present). The fix is, we only mark folders as `provide` folders if they have a number following the period. Otherwise, even if a period is identified, that means we say it is not a `provide` folder.

### 7.31.2023
* Patched bug where `moss` crashed if one of `submission_filter` or `match_formatter` is not provided.

### 7.28.2023
* Patched bug where `moss` crashed if both `submission_filter` and `match_formatter` are not provided.

### 5.9.2023
* Patched bug with skipping `bak` files in  `grading` subfolder in old semesters.

### 5.7.2023
* Add `requirements.txt`.
* Change match downloads to be done with Python's `requests` instead of `wget`.

### 5.5.2023
* Patched bug with permission errors.

### 4.23.2023
* Patched bug with creating job folder.

### 3.14.2023

* Major refactoring to much cleaner implementation with more useful user feedback.
* Added ability to format match folder names to be more readable.
* Added ability to filter out certain submissions.
* Consolidated logging to a single file.
* Consolidated matches results to a single file. 
* Local folders in `results` added to `matches.tsv`.
* Rewrote README to be more user friendly.

### 3.7.2023

* Removed `ping_moss`, after some time it seems that pinging `moss.stanford.edu` is no longer a reliable way of determining if MOSS will respond to jobs successfully. Perhaps the website has been moved to a different server.

### 2.1.2023

* Minor README and documentation updates - notes for possible future improvements.

### 1.14.2023

* Used in Tufts COMP 15 in fall 2022. Planned for use in future semesters. First version moved to course repo.


