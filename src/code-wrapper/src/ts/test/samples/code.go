package main

// Struct1 is a struct
type Struct1 struct {
	attribute1 int
	attribute2 int
}

// Alias1 is an alias for int32
type Alias1 = int32

// Interface1 is an interface
type Interface1 interface {
	function1()
	function2()
}

// method1 is a method of T1
func (*Struct1) method1() {
  // do something
}

// method2 is a method of T1
func (Struct1) method2() {
  // do something
}

// staticFunction is a static function
func staticFunction() {
  // do something
}
