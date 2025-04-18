package main

// Type1 is a struct
type Type1 struct {
	attribute1 int
	attribute2 int
}

// Type2 is an alias for int32
type Type2 = int32

// Type3 is an interface
type Type3 interface {
	function1()
	function2()
}

// method1 is a method of T1
func (*Type1) method1() {
  // do something
}

// method2 is a method of T1
func (Type1) method2() {
  // do something
}

// staticFunction is a static function
func staticFunction() {
  // do something
}
