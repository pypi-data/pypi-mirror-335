function [ts] = gettimestepper(f)
% GETTIMESTEPPER - Returns the timestepper used by the flow.

% WRITTEN BY       : Kenth Eng�, 1998 June.
% LAST MODIFIED BY : Kenth Eng�, 1999.03.05

global DMARGCHK

if DMARGCHK
end;

if isempty(f.timestepper), ts = []; return; end;
ts = f.timestepper;
return;
