%-*-text-*-
function [w] = identity(obj)
% ZERO - Creates the identity object in LGTANGENT.
% function [w] = identity(obj)

% WRITTEN BY       : Kenth Eng�, 2000 Mar.
% LAST MODIFIED BY : None

w = obj;
if iscellempty(obj.shape), return; end;
w.data = lgtidentity(obj.shape);
return;
