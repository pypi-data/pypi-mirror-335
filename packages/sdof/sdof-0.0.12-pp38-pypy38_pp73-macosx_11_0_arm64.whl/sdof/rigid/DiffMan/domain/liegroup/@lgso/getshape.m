function [s] = getshape(u)
% GETSHAPE - Returns the shape information in the Lie group LGSO.
% function [s] = getshape(u)

% WRITTEN BY       : Kenth Eng�, 1997.10.09
% LAST MODIFIED BY : Kenth Eng�, 1999.04.06

if isempty(u.shape), s = []; return; end;
s = u.shape;
return;
