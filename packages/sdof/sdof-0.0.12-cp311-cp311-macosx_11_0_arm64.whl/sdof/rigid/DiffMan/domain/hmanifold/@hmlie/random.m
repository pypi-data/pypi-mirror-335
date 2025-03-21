function z = random(a)
% RANDOM - Creates a random object in the class HMLIE.
% function z = random(a)

% WRITTEN BY       : Kenth Eng�, 1998 Nov.
% LAST MODIFIED BY : Kenth Eng�, 2000.03.29

if isempty(a.shape), z = hmlie; return; end;

z = hmlie(a.shape);
dat = getdata(random(a.shape));
z.data = dat;
return;
