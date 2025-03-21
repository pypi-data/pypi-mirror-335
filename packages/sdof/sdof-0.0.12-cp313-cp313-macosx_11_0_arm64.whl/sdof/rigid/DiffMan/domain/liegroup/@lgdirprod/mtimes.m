function [w] = mtimes(u,v)
% MTIMES - Group multiplication in LGDIRPROD.
% function [w] = mtimes(u,v)

% WRITTEN BY       : Kenth Eng�, 1998.11.16
% LAST MODIFIED BY : Kenth Eng�, 1999.04.12

global DMARGCHK

if DMARGCHK,
  if ~sameshape(u,v)
    error('Input objects do not have the same shape');
  end;
end;

w = lgdirprod(u);
for i = 1:u.n,
  w.data{i} = lgdpmtimes(u.data{i},v.data{i},u.shape{2}(i,:));
end;
return;
