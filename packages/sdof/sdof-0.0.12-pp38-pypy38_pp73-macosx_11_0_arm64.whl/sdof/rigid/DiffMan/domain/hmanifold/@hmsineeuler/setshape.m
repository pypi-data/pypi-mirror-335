function [] = setshape(a,sh)
% SETSHAPE - Sets shape information in HMSINEEULER.

% WRITTEN BY       : Kenth Eng�, 1999 Mar.
% LAST MODIFIED BY : Kenth Eng�, 1999 Sept.

global DMARGCHK

name = inputname(1);
if DMARGCHK
  if isempty(name),
    error('First argument to set must be a named variable!');
  end;
end;

if isinteger(sh),
  if (rem(sh,2) ~= 1)|(sh < 3),
    error('Input must be an odd integer >= 3!');
  end;
  a.shape = lasl(sh*sh-1,'C');
elseif isa(sh,'lasl'),
  shsh = sqrt(getshape(sh)+1);
  if (rem(shsh,2) ~= 1)|(shsh < 3),
    error('Object must have a shape of the form n^2-1, n >= 3!');
  end;
  a.shape = sh;
end;
a.data  = [];
assignin('caller',name,a);
return;
