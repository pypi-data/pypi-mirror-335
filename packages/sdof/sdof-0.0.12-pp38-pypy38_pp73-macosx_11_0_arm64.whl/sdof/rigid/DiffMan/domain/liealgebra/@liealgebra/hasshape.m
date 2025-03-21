function [bool] = hasshape(g)
% HASSHAPE - Checks if the Lie algebra has dynamic shape information.
% function [bool] = hasshape(g)
%
% Remark:
%    This function does not check if a shape has really been assigned to g. 

% WRITTEN BY       : Kenth Eng�, 1997 Sept.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

error(['Function not defined in class: ' class(g)]);
return;
