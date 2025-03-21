function [dat] = getdata(u)
% GETDATA - Returns the data representation of LGSP.
% function [dat] = getdata(u)

% WRITTEN BY       : Kenth Eng�, 1998 Nov.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

if isempty(u.data),
  dat = [];
  return;
end;
dat = u.data;
return;
