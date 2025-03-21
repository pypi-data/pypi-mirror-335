function z = random(a)
% RANDOM - Creates a random object in LASU.
% function z = random(a)

% WRITTEN BY       : Kenth Eng�, 1999.04.09
% LAST MODIFIED BY : None

sh = a(1).shape;
z  = lasu(a);
zdata = rand(sh) + i*rand(sh);
z.data = project(a,zdata);
return;
