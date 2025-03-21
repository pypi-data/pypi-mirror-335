function [defaults] = getdefaults(f)
% GETDEFAULTS - Returns the default values of the flow object.

% WRITTEN BY       : Kenth Eng�, 1998 June.
% LAST MODIFIED BY : Kenth Eng�, 1999.03.05

global DMARGCHK

if DMARGCHK
end;

if isempty(f.defaults), defaults = []; return; end;
defaults = f.defaults;
return;
