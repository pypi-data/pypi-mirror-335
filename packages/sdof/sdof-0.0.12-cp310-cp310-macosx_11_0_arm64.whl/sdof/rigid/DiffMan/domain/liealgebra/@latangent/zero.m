%-*-text-*-
function [w] = identity(obj)
% ZERO - Creates the zero object in LATANGENT.
% function [w] = identity(obj)

% WRITTEN BY       : Kenth Eng�, 2000 Mar.
% LAST MODIFIED BY : None

w = obj;
if iscellempty(obj.shape), return; end;
w.data = latzero(obj.shape);
return;
