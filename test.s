
function A: void
var_input
a1: WORD;
a2: WORD;
end_var
var
b1:WORD;
b2:WORD;
end_var
FOR b1 = 0 TO 10
	funcall B(a1, a2, b2)
	a1:b1 = b2 
NEXT
end_function

function B: void
var_input
a1: WORD;
a2: WORD;
a3: *WORD;
end_var
*a3 = a1 + a2
end_function
