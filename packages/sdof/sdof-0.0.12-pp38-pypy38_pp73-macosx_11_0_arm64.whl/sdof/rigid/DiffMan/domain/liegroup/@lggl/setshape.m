function [] = setshape(a,sh)
% SETSHAPE - Sets shape information in LGGL.
% function [] = setshape(a,sh)

% WRITTEN BY       : Kenth Eng�, 1997.10.09
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

global DMARGCHK

name = inputname(1);
if DMARGCHK,
  if isempty(name),
    error('First argument to set must be a named variable');
  end;
  if ~(isinteger(sh)),
    error('Shape should be an integer!');
  end;
  if sh<1,
    error('Shape should be positive!');
  end;
end;

% plug in the shape and the empty matrix in a:
a.shape = sh;
a.data  = [];
assignin('caller',name,a);
return;

