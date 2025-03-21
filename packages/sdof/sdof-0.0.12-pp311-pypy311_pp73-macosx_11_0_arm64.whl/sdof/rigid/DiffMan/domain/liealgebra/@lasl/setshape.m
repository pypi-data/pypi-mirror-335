function [] = setshape(a,sh)
% SETSHAPE - Sets shape information in LASL.
% function [] = setshape(a,sh)

% WRITTEN BY       : Kenth Engø, 1997.09.10
% LAST MODIFIED BY : Kenth Engø, 1999.04.06

global DMARGCHK

name = inputname(1);
if DMARGCHK,
  if isempty(name),
    error('First argument to set must be a named variable')
  end;
  if ~(isinteger(sh))&(sh < 1),
    error('Shape should be a positive integer!');
  end;
end;

a.shape = sh;
a.data  = [];
assignin('caller',name,a);
return;

