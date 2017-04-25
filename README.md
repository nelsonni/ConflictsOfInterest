# *Conflicts-Of-Interest* Repository Miner
We're gonna crawl these repos like we're the freakin' Rugrats. This repository contains a Python-based repository miner that pulls repositories from GitHub and examines their version history to locate merge conflicts. We determine merge conflicts by speculatively merging commits (and their accompanying branch histories) contained within the `master` branch of a repository, obtaining the conflicting versions of each text section by parsing the unmerged sections resulting from the speculative merge, and using `diff` to determine whether portions of a merge conflict resolution existed.

The final report for the CS569: Empirical Methods of Software Engineering course (Spring 2016) can be found here: [report.pdf](https://github.com/nelsonni/ConflictsOfInterest/blob/master/FinalReport/report.pdf).

Required packages for successfully using the miner include:
* `gmail-sender` package required for email notifications: [paulchakravarti/gmail-sender](https://github.com/paulchakravarti/gmail-sender)
* `PyGithub` package required for `crawler.py`: [PyGithub/PyGithub](https://github.com/PyGithub/PyGithub)
  * Also available through `pip`: `pip install pygithub`
* `GitPython` package required for `puller.py`: [gitpython-developers/GitPython](https://github.com/gitpython-developers/GitPython)
  * Also available through `pip`: `pip install gitpython`
