function [v] = getdata(g)
% GETDATA - Returns the data representation in LGDIRPROD.
% function [v] = getdata(g)

% WRITTEN BY       : Kenth Eng�, 1998.11.16
% LAST MODIFIED BY : Kenth Eng�, 1999.04.12

v = cell(g.n,1);
if isempty(g.data), return; end;
for i = 1:g.n,
  v{i} = g.data{i};
end;
return;
