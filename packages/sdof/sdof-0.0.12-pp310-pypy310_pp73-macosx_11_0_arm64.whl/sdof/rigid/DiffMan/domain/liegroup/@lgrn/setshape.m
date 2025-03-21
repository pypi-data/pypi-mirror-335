function [] = setshape(a,sh)
% SETSHAPE - Sets the shape information in LGRN.
% function [] = setshape(a,sh)

% WRITTEN BY       : Kenth Eng�, 1997 Oct.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

global DMARGCHK

name = inputname(1);
if DMARGCHK,
  if isempty(name),
    error('First argument to set must be a named variable')
  end;
  if ~(isinteger(sh))&(sh<1),
    error('Shape should be integer and greater than 1!');
  end;
end;

len = length(a);
for i = 1:len
  a(i).shape = sh;
  a(i).data  = [];
end;
assignin('caller',name,a);
return;
