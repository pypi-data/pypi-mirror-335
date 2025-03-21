function [dat] = getdata(u)
% GETDATA - Returns the data representation of LGGL.
% function [dat] = getdata(u)

% WRITTEN BY       : Kenth Eng�, 1997.10.09
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

if isempty(u.data),
  dat = [];
  return;
end;
dat = u.data;
return;
