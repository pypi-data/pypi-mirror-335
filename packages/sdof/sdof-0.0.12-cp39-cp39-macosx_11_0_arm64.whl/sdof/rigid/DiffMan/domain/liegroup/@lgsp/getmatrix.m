function [mat] = getmatrix(a)
% GETMATRIX - Returns matrix representation in LGSP.
% function [mat] = getmatrix(a)

% WRITTEN BY       : Kenth Eng�, 1998 Nov.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

if isempty(a.data),
  mat = [];
  return;
end;
mat = a.data;
return;
