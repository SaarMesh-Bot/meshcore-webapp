package main

import "testing"

func TestPortAllowed(t *testing.T) {
	cases := []struct {
		spec string
		port int
		want bool
	}{
		{"5000-5005", 5000, true}, {"5000-5005", 5003, true}, {"5000-5005", 5005, true},
		{"5000-5005", 4999, false}, {"5000-5005", 5006, false}, {"5000-5005", 80, false},
		{"5000", 5000, true}, {"5000", 5001, false},
		{"5000, 6000-6002", 6001, true}, {"5000,6000-6002", 6003, false},
		{"*", 22, true}, {"abc-def", 5000, false}, {"", 5000, false},
	}
	for _, c := range cases {
		*allowedPorts = c.spec
		if got := portAllowed(c.port); got != c.want {
			t.Errorf("portAllowed(%q, %d) = %v, want %v", c.spec, c.port, got, c.want)
		}
	}
}
