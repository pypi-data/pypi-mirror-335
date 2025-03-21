%-*-text-*-
function [j] = sameshape(a,b)
% SAMESHAPE - Checks if 'a' and 'b' have the same shape.
% function [j] = sameshape(a,b)

% WRITTEN BY       : Kenth Eng�, 2000 Mar.
% LAST MODIFIED BY : None

global DMARGCHK

if DMARGCHK,
  if ~isa(b,'lgtangent'),
    error('Input is not from ''lgtangent''-class.');
  end;
end;

sh1 = shapestr(a.shape);
sh2 = shapestr(b.shape);
j = strcmp(sh1,sh2);
return;
