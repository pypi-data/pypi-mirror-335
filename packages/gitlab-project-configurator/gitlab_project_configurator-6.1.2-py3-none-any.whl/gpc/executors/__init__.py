"""
Each 'executor' perform a single change on Gitlab Project or Group.

It is responsibible for performing the interaction with the Gitlab API using
Python-Gitlab library, reporting change done (comparison) and building its
mini-report.

In "apply" mode, it should execute as many change as possible while gathering
the issues encountered.
"""
