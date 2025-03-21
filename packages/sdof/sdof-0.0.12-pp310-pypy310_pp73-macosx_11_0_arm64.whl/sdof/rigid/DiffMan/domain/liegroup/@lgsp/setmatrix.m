function [] = setmatrix(a,m)
% SETMATRIX - Sets matrix representation in LGSP.
% function [] = setmatrix(a,m)     

% WRITTEN BY       : Kenth Eng�, 1998 Nov.
% LAST MODIFIED BY : Kenth Eng�, 1999.04.07

global DMARGCHK
name = inputname(1);

if DMARGCHK,
  if isempty(name),
    error('First argument to set must be a named variable');
  end;
  if ~ismatrix(a,m),
    error('Input data is no matrix representation!');
  end;
end;

a.data = m;
assignin('caller',name,a);
return;
