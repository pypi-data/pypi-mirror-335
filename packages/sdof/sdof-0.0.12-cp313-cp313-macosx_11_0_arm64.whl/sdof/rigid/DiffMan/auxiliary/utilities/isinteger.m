function [T] = isinteger(A)
% ISINTEGER - Checks if a vector of reals consists of integers.
% function [T] = isinteger(A)

% WRITTEN BY       : Kenth Engø, 1998 Sept. 
% LAST MODIFIED BY : Kenth Engø, 1999.04.12

if isreal(A),
   T = all(A==floor(A));
else
   T = 0;
end;
