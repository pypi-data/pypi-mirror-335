## Index

* [Places and links][places]
* [Testing][testing]
* [Release process][release-process]
* [Documentation][documentation]
* [Code-review process][code-review]


# Contributing

**We love seeing Pull Requests from anyone.**

For bigger or controversial changes, consider first discussing it via [issue][issues] or any other method with the maintainers of this repository. Otherwise, there's a risk they might disagree with it and you could spend time on it in vain. Or you can just open a Pull Request and keep the discussion there.

All code should work well with Python 3 and also be compatible with Python 2.7.

Code is [reviewed][code-review] by package maintainers.


### Sign Off

All commits must be signed-off on. Please use `git commit -s` to do that. This serves as a confirmation that you have the right to submit your changes. See [Developer Certificate of Origin][origin] for details.

[origin]: https://developercertificate.org/


### Other tips

You can increase the chance of your Pull Request being merged by:

* having good test coverage
* writing documentation
* following PEP 8 for code formatting
* don't have [bandit][bandit] complains
* writing [a good commit message][commit-message]

[commit-message]: https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
[bandit]: https://bandit.readthedocs.io


[places]:
## Places and links

* code is hosted on [Pagure][pagure] (upstream GIT)
* web documentation can be found [here][web-documentation]
* [issue tracker][issues]
* [Pull Requests][pull-requests] (PR)

[pagure]: https://pagure.io/rpkg
[issues]: https://pagure.io/rpkg/issues
[pull-requests]: https://pagure.io/rpkg/pull-requests


[testing]:
## Testing process

Unittests are implemented to prevent issues and cover the code. When a new [Pull Request][pull-requests] is created (or rebased), unit tests are triggered in [Jenkins][jenkins]. Test status is shown in the green (success) or red (failure) box on the Pull Request's page afterwards.

To see detailed test results, open the URL (click on the colour box), select `default` configuration and then `Console Output`.

How to run unit tests manually or offline, see the [initial][pagure] page or file `README.rst`.

[jenkins]: https://jenkins-fedora-infra.apps.ocp.ci.centos.org/job/pyrpkg/


[release-process]:
## Release process

A rpkg's release process could have two variants (both performed by maintainers):

1. A **new** rpkg's **release**.

    * the main version number is bumped, for example rpkg-1.63-4 --> rpkg-1.64-1
    * a new tarball is created (and additionally submitted to [PyPI][pypi])
    * [documentation][documentation] is generated
    * a tarball is uploaded to [dist-git][dist-git]
    * specfile is updated
    * packages are built in [Koji][koji]
    * updates are created in [Bodhi][bodhi]
    * tested by the community

2. A release of a **patch**.

    * a minor version number is bumped, for example rpkg-1.63-4 --> rpkg-1.63-5
    * a single or multiple fixes/features are taken (cherrypicked) from a rpkg's repository as patches. 
    * specfile is updated
    * packages are built in [Koji][koji]
    * updates are created in [Bodhi][bodhi]
    * tested by the community

Releases are irregular (usually once per few months). They depend on the number of unreleased features and fixes and the time since the last release.

Patches are usually requested by customers or provided when there is an urgent issue found.

[pypi]: https://pypi.org/project/rpkg/
[dist-git]: https://src.fedoraproject.org/rpms/rpkg/
[koji]: https://koji.fedoraproject.org/koji/packageinfo?packageID=12125
[bodhi]: https://bodhi.fedoraproject.org/updates/?packages=rpkg


[documentation]:
## Documentation

Rpkg contains the [web documentation][web-documentation]. It is generated from templates that are stored in the "doc" directory together with documentation-building scripts and Makefile. Anyone can contribute with changes, but final regeneration is done by the maintainer during a new version [release process][release-process].

Contributors can check results by regenerating documentation offline:

    cd doc
    dnf install python3-sphinx python3-sphinx_rtd_theme
    make html

[web-documentation]: https://pagure.io/docs/rpkg/


[code-review]:
## Code-review process

1. Motivation

    Code reviews performed by various team members should maintain a steady quality and satisfy the same requirements. This document contains the baseline of checks that should be part of a code review. It is a high-level guide.

2. Process

    When doing a code review, answer the questions in sections below.

    Code in a Pull Request needs approval from one of the rpkg's maintainers.

3. Requirements

    * Does the change fix the problem and satisfy requirements?

4. Best practices

    * Is the code formatted properly? Is it readable?
    * Are there no unnecessary changes?
    * Are errors handled correctly?
    * Is there an appropriate amount of comments?
    * Is the code understandable?
    * Is there enough documentation?
    * Is the code efficient enough? Do you see obvious performance issues?
    * Does the commit message follow conventions?

5. Testing

    * Do unit tests pass?
    * Is static application security testing reporting no problems?
    * Are there tests for the new code?
    * Did the author test the changes?

6. Security

    * Is all input correctly validated?
    * Is all output correctly escaped?
    * Is there a risk of exposing any private information?

7. BONUS: Security - Perform threat modelling

    * Who are the actors (people, services) who are going to interact with the new feature?
    * What is the attack surface: how does the feature get input? Network communication? Web interface? CLI?
    * Consider threats:
        * Spoofing: pretending you're someone you are not
        * Tampering: modifying data
        * Repudiation: Can someone change information without the system owner knowing about it ("I didn't do it, nobody saw me, can't prove anything")
        * Information disclosure: leaking private information
        * Denial of Service: stopping something from working or responding
        * Elevation of Privilege: Upgrade access level from user to admin
    * Document any findings in a comment on the Pull Request.

