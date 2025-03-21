function [sh] = getshape(a)
% GETSHAPE - Returns the shape information in LADIRPROD.
% function [sh] = getshape(a)

% WRITTEN BY       : Kenth Eng�, 1997 Sept.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.12

if iscellempty(a.shape), sh = cell(1,2); return; end;
sh = a(1).shape;
return;
