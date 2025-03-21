function [] = setshape(a,sh)
% SETSHAPE - Sets the shape information in LGON_PQ.
% function [] = setshape(a,sh)

% WRITTEN BY       : Kenth Eng�, 1999 Apr.
% LAST MODIFIED BY : None

global DMARGCHK

name = inputname(1);
if DMARGCHK,
  if isempty(name),
    error('First argument to set must be a named variable');
  end;
  if ~(isinteger(sh) & (length(sh) == 2) & all(sh > 0)),
    error('Shape should be a positive integer 2-vector!'); 
  end;
end;

a.shape = sh;
a.data  = [];
assignin('caller',name,a);
return;

