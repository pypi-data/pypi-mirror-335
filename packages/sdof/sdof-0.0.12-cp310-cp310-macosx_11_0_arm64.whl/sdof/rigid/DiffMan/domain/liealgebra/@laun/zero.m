function z = zero(obj)
% ZERO - Create the zero object in LAUN.
% function z = zero(obj)

% WRITTEN BY       : Kenth Eng�, 1999.04.04
% LAST MODIFIED BY : Kenth Eng�, 1999.04.09

n   = obj.shape;
dat = zeros(n);
z   = laun(obj);
z.data = dat;
return;
