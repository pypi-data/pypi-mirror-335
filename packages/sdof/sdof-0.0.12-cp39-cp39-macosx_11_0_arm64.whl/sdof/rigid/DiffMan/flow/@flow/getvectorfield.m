function [vf] = getvectorfield(f)
% GETVECTORFIELD - Returns the vector field defining the flow.

% WRITTEN BY       : Kenth Eng�, 1997 Oct.
% LAST MODIFIED BY : Kenth Eng�, 1999.03.05

global DMARGCHK

if DMARGCHK
end;

if isempty(f.vectorfield), vf = []; return; end;
vf = f.vectorfield;
return;
