function [s] = getshape(u)
% GETSHAPE - Returns the shape information in LGRN.
% function [s] = getshape(u)

% WRITTEN BY       : Kenth Eng�, 1997 Oct.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

if isempty(u(1).shape), s = []; return; end;
s = u(1).shape;
return;
