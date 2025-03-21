function [d] = dimension(a)
% DIMENSION - Returns the dimension of the LASE vectorspace.
% function [d] = dimension(a)

% WRITTEN BY       : Kenth Eng�, 1998.01.15
% LAST MODIFIED BY : Kenth Eng�, 1999.04.12

n = a(1).shape;
if isempty(n), error('Element has no shape'); end;
d = n*(n-1)/2 + n;
return;

