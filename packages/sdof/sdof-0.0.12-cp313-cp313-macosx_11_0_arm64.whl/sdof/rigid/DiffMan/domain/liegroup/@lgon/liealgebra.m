function [g] = liealgebra(a)
% LIEALGEBRA - Routine for picking out the liealgebra to LGON. 
% function [g] = liealgebra(a)

% WRITTEN BY       : Kenth Eng�, 1997.11.07
% LAST MODIFIED BY : Kenth Eng�, 1999.04.12

sh = a.shape;
if isempty(sh), g = laso; else, g = laso(sh); end;
return;
