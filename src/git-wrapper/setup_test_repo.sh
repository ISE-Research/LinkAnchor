#!/bin/bash 
DEST_DIR=$1

# setup the git repo
mkdir -p $DEST_DIR
cd $DEST_DIR
git init

touch README.md
# first commit by user1
git config user.name "user1"
git config user.email "user1@test.com"
echo "# Test Repo by user1 in master" >> README.md
git add README.md
git commit -m "first"

# second commit by user2
git config user.name "user2"
git config user.email "user2@test.com"
echo "# Test Repo by user2 in master" >> README.md
git add README.md
git commit -m "second"

# third commit in branch1 by user1
git checkout -b branch1
git config user.name "user1"
git config user.email "user1@test.com"
echo "# Test Repo by user1 in branch1" >> README.md
git add README.md
git commit -m "third"

# fourth commit in branch1 by user3
git config user.name "user3"
git config user.email "user3@test.com"
echo "# Test Repo by user3 in branch1" >> README.md
git add README.md
git commit -m "fourth"

# fifth commit in master by user3
git checkout master
git config user.name "user3"
git config user.email "user3@test.com"
echo "# Test Repo by user3 in master" >> README.md
git add README.md
git commit -m "fifth"

# sixth commit in master by user4
git checkout master
git config user.name "user4"
git config user.email "user4@test.com"
echo "# Test Repo by user4 in master" > OTHER.md
git add OTHER.md
git commit -m "sixth"
