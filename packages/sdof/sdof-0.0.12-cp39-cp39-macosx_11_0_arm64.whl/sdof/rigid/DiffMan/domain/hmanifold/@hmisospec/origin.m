function [orig] = origin(a)
% ORIGIN - Returns the 'origin' amongst the R^(nxn) matrices.
% function [orig] = origin(a)

% WRITTEN BY       : Kenth Eng�, 1997.11.09
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

orig = hmisospec(a);
orig.data = zeros(getshape(a.shape));
return;
