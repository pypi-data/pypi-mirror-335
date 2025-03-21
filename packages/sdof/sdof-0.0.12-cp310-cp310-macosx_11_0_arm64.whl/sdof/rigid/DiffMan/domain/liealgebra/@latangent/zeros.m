%-*-text-*-
function [oarray] = zeros(obj,sz)
% ZEROS - Overloaded version of 'zeros'.
% function [oarray] = zeros(obj,sz)

% WRITTEN BY       : Kenth Eng�, 2000 Mar.
% LAST MODIFIED BY : None

global DMARGCHK

if DMARGCHK,
  if ~isinteger(sz) & sz > 0,
    error('Second input argument is not an integer greater than zero.');
  end;
end;

zobj = zero(obj);
oarray(sz,1) = zobj;
for i = 1:sz-1,
  oarray(i) = zobj;
end;
return;


