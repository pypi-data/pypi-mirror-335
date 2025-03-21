function z = random(a)
% RANDOM - Creates a random object in the class HMRN.
% function z = random(a)

% WRITTEN BY       : Kenth Eng�, 1998 Nov.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

if isempty(a.shape), z = hmrn; return; end; % Generic object.

z = a;
dat = rand(a.shape,1);
z.data = dat;
return;
