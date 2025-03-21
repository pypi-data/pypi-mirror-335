function [mat] = getmatrix(a)
% GETMATRIX - Returns the matrix representation in LGON.
% function [mat] = getmatrix(a)

% WRITTEN BY       : Kenth Eng�, 1997.10.09
% LAST MODIFIED BY : Kenth Eng�, 1999.04.12

if isempty(a.data), mat = []; return; end;
mat = a.data;
return;
