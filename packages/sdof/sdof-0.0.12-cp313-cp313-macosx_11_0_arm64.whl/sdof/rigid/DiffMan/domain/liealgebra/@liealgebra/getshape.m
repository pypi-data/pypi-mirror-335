function [sh] = getshape(g)
% GETSHAPE - Returns shape information if the Lie algebra is dynamically subtyped.
% function [sh] = getshape(g)
%
% Precondition: hasshape(g) == 1

% WRITTEN BY       : Kenth Eng�, 1997 Sept.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

error(['Function not defined in class: ' class(g)]);
return;
