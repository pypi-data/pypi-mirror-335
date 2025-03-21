function [orig] = origin(a)
% ORIGIN - Returns the 'origin' in the HMTOP-space; { zeros(n,1) zeros(n,1)}.
% function [orig] = origin(a)

% WRITTEN BY       : Kenth Eng�, 1998.01.26
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

orig = hmtop(a);
vec = zeros(getshape(orig.shape),1);
orig.data = {vec vec};
return;
