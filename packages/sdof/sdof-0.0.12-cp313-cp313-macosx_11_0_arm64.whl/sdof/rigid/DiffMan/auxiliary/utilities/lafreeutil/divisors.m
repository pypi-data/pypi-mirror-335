function [div] = divisors(n)
% DIVISORS - alldivisors of an integer
% [div] = divisors(n)

% written by: Hans Munthe-Kaas, 27/10/97
div = [];
for i = 1:n,
	if isinteger(n/i),
		div = [div i];
	end;
end;
return;
