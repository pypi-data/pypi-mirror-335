function [] = setshape(a,sh)
% SETSHAPE - Sets shape information in LASP.
% function [] = setshape(a,sh)

% WRITTEN BY       : Kenth Eng�, 1998 Nov.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.06

global DMARGCHK

name = inputname(1);
if DMARGCHK,
  if isempty(name),
    error('First argument to set must be a named variable')
  end;
  if ~(isinteger(sh))&(sh < 1)&(~(mod(sh,2)==0)),
    error('Shape should be a positive even integer!');
  end;
end;

a.shape = sh;
a.data  = [];
assignin('caller',name,a);
return;

