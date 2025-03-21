function [oarray] = zeros(obj,sz)
% ZEROS - Overloaded version of 'zeros'.
% function [oarray] = zeros(obj,sz)

% WRITTEN BY       : Kenth Engø, 1997.11.13
% LAST MODIFIED BY : Kenth Engø, 1999.04.12

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


