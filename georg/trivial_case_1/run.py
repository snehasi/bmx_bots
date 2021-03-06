#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# (C) Copyright 2018
# Georg Link <linkgeorg@gmail.com>
#
# SPDX-License-Identifier: MPL-2.0

#####
# run.py
#
# Trivial Case 1 - no variables
#####

from subprocess import check_output
import json
import sys
# import issuetracker
import person
import datetime

# Step 1: define the simulation parameters
print("start simulation, define parameter [DONE]")
number_of_workers = 10  # how many people we start with
# number_of_issues = 10  # how many issues we start with
# rate_of_new_issues = 3  # create x new issues every day
worker_starting_funds = 100  # how much money a worker starts with
funder_starting_funds = 999999999  # how much money a funder starts with
# file_for_issue_tracker_oracle = "./issues.csv"  #where to export the issue...
# ... tracker information to
simulation_time = 100  # how many days to simulate
# ...
# rebuild server in the past
print("reset bugmark", end="")
sys.stdout.flush()
check_output(["bmx", "host", "rebuild",
              "--affirm=destroy_all_data",
              "--with_day_offset=-"+str(simulation_time)])
print(" [DONE]")

# Step 2: load issue tracker
print("create repo", end="")
sys.stdout.flush()
# tracker = issuetracker.IssueTracker()
# for i = 1 to number of issues
# tracker.open_issue()  # (x10)
issues = 0
# create simulation trackersitory
print("reset bugmark", end="")
sys.stdout.flush()
tracker_name = "TrivialCase1Tracker"
tracker_rtn = check_output(["bmx", "tracker", "create",
                         tracker_name,
                         "--type=Test"])
tracker_obj = json.loads(tracker_rtn.decode("utf-8"))
tracker_uuid = tracker_obj["uuid"]
print(" [DONE]")

# Step 3: instantiate people (agents)
# Trivial Case 1 only has one funder
print("create funder", end="")
sys.stdout.flush()
email = "funder@bugmark.net"
funder = person.PTrivialCase1Funder(email)
print(" [DONE]")

# list of workers = new worker (x10)
print("create workers", end="")
sys.stdout.flush()
workers = []
for w in range(number_of_workers):
    print(" "+str(w), end="")
    sys.stdout.flush()
    email = "worker"+str(w)+"@bugmark.net"
    workers.append(person.PTrivialCase1Worker(email))
print(" [DONE]")

# Step 4: run simulation
# First: create 10 issues, create an unfixed offer, match by a worker
# Second: advance time by one day and pay out contracts
# end after simulation_time is expired
# return to First.
print("Simulation:")
for x in range(simulation_time):
    print(str(x)+":", end="")
    sys.stdout.flush()
    # get current system time
    host_rtn = check_output(["bmx", "host", "info"])
    host_obj = json.loads(host_rtn.decode("utf-8"))
    server_time = host_obj["host_time"][:-3]+host_obj["host_time"][-2:]
    host_time = datetime.datetime.strptime(server_time, "%Y-%m-%dT%H:%M:%S%z")
    maturation_datetime = host_time + datetime.timedelta(days=1)
    maturation = maturation_datetime.strftime("%y%m%d_%H%M")

    # create 10 of each: new issues, unfixed offers, and fixed offers
    for i in range(number_of_workers):
        print(" "+str(i), end="")
        sys.stdout.flush()
        # new issue
        issues = issues + 1
        issue_rtn = check_output(["bmx", "issue", "sync",
                                  str(issues),
                                  # "--type=Test",
                                  "--tracker-uuid="+tracker_uuid])
        issue_obj = json.loads(issue_rtn.decode("utf-8"))
        issue_uuid = issue_obj["uuid"]

        # funder creates offer
        funder.trade_bugmark(issue_uuid, maturation)

        # worker matches offer
        offer = workers[i].trade_bugmark(issue_uuid, maturation)

        # cross offers
        check_output(["bmx", "contract", "cross",
                      offer["offer_uuid"],
                      "--commit-type=expand"])

    # Advance server time by one day
    print(" (next day)", end="")
    sys.stdout.flush()
    check_output(["bmx", "host", "increment_day_offset"])
    # This should pay out maturing contracts
    print(" pay out", end="")
    contracts_rtn = check_output(["bmx", "contract", "list"])
    contracts_obj = json.loads(contracts_rtn.decode("utf-8"))
    for contract in contracts_obj:
        check_output(["bmx", "contract", "resolve", contract["uuid"]])
    #
    print(" [DONE]")

print("bot run success")
print("end simulation")
