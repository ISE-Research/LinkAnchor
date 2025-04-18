#!/bin/bash 

DEST_DIR=$1

# setup the git repo
mkdir -p "$DEST_DIR"
cd "$DEST_DIR" || exit 1
git init


touch main.go 
cat <<EOF > main.go
package main
import "fmt"

func greet() {
  fmt.Println("Hello, world!")
}

type Mamad struct {
  Name string
}

func (m *Mamad) SayHello() {
  fmt.Println("Hello, my name is", m.Name)
}
EOF
# first commit by user1
git checkout -b hello
git config user.name "user1"
git config user.email "user1@test.com"
git add main.go 
git commit -m "say hello"


cat <<EOF >> main.go

// SayGoodBye says goodbye
func (m Mamad) SayGoodBye() {
  fmt.Println("Bye, my name is", m.Name)
}
EOF
# second commit by user2
git checkout -b goodbye
git config user.name "user2"
git config user.email "user2@test.com"
git add main.go 
git commit -m "say goodbye"

